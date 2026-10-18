Summary of Polling in the Application
#	Context / Location	Frequency	Type	Cost Impact
1	Active Chat Messages Polling
(

App.jsx
: lines 669–678
)	Every 5 seconds	Frontend HTTP polling (GET /api/dashboard/conversations/:id/messages)	High: Constant API and Elasticsearch hits per active user/tab.
2	Elasticsearch Auto-Sync Background Daemon
(

main.py
: lines 31–118
 & 

whatsapp_dashboard/main.py
: lines 15–115
)	Every 3 seconds (24/7)	Backend DB polling (INDEX_CONVERSATIONS & INDEX_MESSAGES)	Critical: Runs continuously 24/7 on the server, even with 0 users online.
3	Message Delivery Status Wait Loop
(

router.py
: lines 245–274
)	Every 250ms (up to 3s per sent message)	Backend DB polling (get_message_status_by_id)	High during broadcasts: Fires 4–12 DB queries per sent message.
4	Campaign Stats Auto-Refresh Polling
(

CampaignsView.jsx
: lines 342–399
)	Every 3 seconds (previously enabled/commented)	Frontend HTTP polling (fetchCampaigns)	Medium-High: Constantly queries campaign aggregates.
Detailed Contexts
1. Context 1: Active Chat Messages Polling (Frontend)
Location: 

whatsapp_dashboard/react-frontend/src/App.jsx:669-678
Code:
javascript
// Auto-sync active chat messages every 5 seconds
useEffect(() => {
  if (activeTab !== 'inbox' || !currentChat?.conversation_id) return;
  const interval = setInterval(() => {
    if (currentChatRef.current?.conversation_id) {
      loadMessages(currentChatRef.current.conversation_id);
    }
  }, 5000);
  return () => clearInterval(interval);
}, [activeTab, currentChat?.conversation_id, loadMessages]);
Why it costs money: Every open chat tab fires a full HTTP request every 5 seconds fetching message history from Elasticsearch. If 10 support agents have chats open, that's 120 requests per minute hitting Elasticsearch.
Replacement with Webhooks: Meta already delivers incoming messages to your backend endpoint POST /webhook in 

whatsapp_dashboard/router.py:2734
. When a webhook arrives, the backend pushes "event": "new_message" over the existing WebSocket connection. The frontend already handles data.event === 'new_message' in 

App.jsx:480-535
, so this setInterval can be eliminated completely.
2. Context 2: Elasticsearch Auto-Sync Daemon (Backend)
Location:


main.py:31-118


whatsapp_dashboard/main.py:15-115
Code:
python
async def background_sync_daemon():
    es = get_es_client()
    while True:
        await asyncio.sleep(3)
        res_c = es.search(index=INDEX_CONVERSATIONS, size=20, sort=[{"timestamp": {"order": "desc"}}])
        for h in res_c.get("hits", {}).get("hits", []):
            ...
            res_m = es.search(index=INDEX_MESSAGES, ...)
Why it costs money: This is an infinite while True loop that queries Elasticsearch every 3 seconds, 24 hours a day, 7 days a week (~28,800 queries a day), regardless of whether anyone is logged in or any new messages have arrived. This prevents the server from idling and consumes Elasticsearch query capacity.
Replacement with Webhooks: This background daemon was originally created as a fallback to detect unindexed messages. In a pure webhook-driven architecture, when Meta posts an incoming message or status to POST /webhook, you process, store, and broadcast it immediately in the webhook handler. The background polling daemon can be safely turned off.
3. Context 3: Outgoing Message Status Wait Loop (Backend)
Location: 

router.py:245-274
Code:
python
async def wait_for_message_status(message_id: str, timeout_seconds: float = 3.0) -> dict:
    start_time = datetime.now().timestamp()
    interval = 0.25
    while (datetime.now().timestamp() - start_time) < timeout_seconds:
        doc = get_message_status_by_id(message_id)
        ...
        await asyncio.sleep(interval)
Where it is called: Used in send_otp, send_marketing, send_invoice, and send_utility (lines 498, 783, 1379, 1541).
Why it costs money: For each message sent, it queries Elasticsearch up to 12 times (every 250ms for 3 seconds) waiting for Meta's webhook to write 'delivered' or 'failed'. If you broadcast to 100 contacts, that creates hundreds of concurrent database queries.
Replacement with Webhooks: Instead of holding the HTTP request open with a polling loop, immediately return the message_id and status "sent". Let Meta's asynchronous webhook at POST /webhook update the database and broadcast the delivery status over WebSocket when received.
4. Context 4: Campaign Auto-Refresh Polling (Frontend)
Location: 

whatsapp_dashboard/react-frontend/src/components/CampaignsView.jsx:342-399
Code:
javascript
// Live Auto-Refresh polling timer and instant WebSocket sync
const syncCampaigns = () => {
  fetchCampaigns({ ... });
};
// const interval = setInterval(syncCampaigns, 3000);
Why it costs money: When active, it sends a full campaign list and aggregates query to the backend every 3 seconds.
Replacement with Webhooks: The webhook handler already recalculates campaign statistics and emits campaign_updated and message_status over WebSocket. CampaignsView.jsx already listens for dashboard_campaign_update events via window.addEventListener('dashboard_campaign_update'), making periodic polling redundant.
Non-Polling Timers (Safe to keep)
For completeness, the following timers in the codebase are purely client-side UI utilities and do not make network or database requests:

Relative Time Updater: 

App.jsx:78
 (setInterval(..., 30000)) – refreshes relative "time ago" labels.
OTP Resend Countdown: 

LoginView.jsx:27
 (setInterval(..., 1000)) – 60s resend button countdown.
Input Debouncing: 

InboxColumn.jsx:54
, 

CampaignsView.jsx:273
, 

LeadsView.jsx:86
 (setTimeout(..., 250-400ms)) – delays search while typing.
WebSocket Reconnect: 

App.jsx:586
 (setTimeout(connectWS, 3000)) – reconnects WebSocket only if the connection drops.
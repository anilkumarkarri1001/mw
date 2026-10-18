Step 6: Check whether the HTTP request succeeded
if (res.ok) {
  return data !== null ? data : { status: 'success' };
}
res.ok is a Boolean property of the Fetch API response.
true: HTTP status is between 200 and 299.
false: HTTP status is outside that range.

For example:
200 OK → res.ok is true.
201 Created → res.ok is true.
400 Bad Request → res.ok is false.
500 Internal Server Error → res.ok is false.

============================================================================>
Step 1: Check Node.js and npm
Run these commands in your current PowerShell terminal:
node -v
npm -v
If both show version numbers, they are installed.
If both show errors like CommandNotFoundException, continue to Step 2.
If node -v works but npm -v fails, npm may be missing or incorrectly configured.
Step 2: Install Node.js
Download Node.js (LTS)
Open the official website: 
https://nodejs.org/en/download
Download the Windows Installer (.msi) and install it. Keep the default options selected, including adding Node.js to PATH.
Step 3: Restart PowerShell
Close your current terminal.
Open a new PowerShell terminal.
Run:
node -v
npm -v
Step 4: Run your project
Navigate to your project folder:
cd C:\Users\DELL\Downloads\whatsapp_meta\whatsapp_meta
Then install the project dependencies:
npm install
After installation, check your project's package.json file to see which command starts the application. For example, if it contains a dev script:
npm run dev
Tell me what happens when you run these two commands:
node -v
npm -v
============================================================================>
Great! Your latest output confirms that Node.js and npm are working correctly in your current VS Code terminal. ✅
Node.js: v24.21.0
npm: 11.19.0
Node.js location: C:\Program Files\nodejs\node.exe 
with these commands : 
node -v 
npm -v 
where.exe node
============================================================================>
5. Interview-style answer

Q: Why do we use JSON.stringify()?
Answer: We use JSON.stringify() to convert an object or 
another non-string value into a string so that the error message has a 
consistent format.


Q: Why do we use the spread operator here?
Answer: We use the spread operator to preserve additional properties 
returned by the backend instead of discarding them.
============================================================================>
if (activeTab !== 'inbox' || !currentChat?.conversation_id) return;

Simple meaning: If the user is not on the Inbox tab OR there is no conversation ID for the current chat, stop executing the function immediately.
============================================================================>

  // ── Auto-sync active chat messages every 5 seconds ──────────
  useEffect(() => {
    if (activeTab !== 'inbox' || !currentChat?.conversation_id) return;
    const interval = setInterval(() => {
      if (currentChatRef.current?.conversation_id) {
        loadMessages(currentChatRef.current.conversation_id);
      }
    }, 5000);
    return () => clearInterval(interval);  # clearInterval	Stops the repeating timer.
  }, [activeTab, currentChat?.conversation_id, loadMessages]);

useEffect tells React to run this code as an effect after rendering, 
when the effect's dependencies require it.  

Interview answer: This useEffect implements periodic message polling.
 It starts a 5-second interval only when the Inbox tab is active and a conversation is selected.
   It loads messages using the latest conversation ID held in a ref and cleans up the interval
     when the effect reruns or the component unmounts.


============================================================================>
Step 1: Check whether the value exists
if (!value) return ['N/A'];
Here, !value checks whether the value is falsy, such as:
- undefined
- null
- '' (empty string)
- 0
- false
If the value is missing or falsy, the function immediately returns:
============================================================================>
Step 2: Define the event handler
const handleWsCampaignUpdate = (e) => {
  const data = e.detail;

Here:
- handleWsCampaignUpdate is a function that handles incoming campaign update events.
- e is the browser's event object.
- e.detail contains the data attached to the custom event.
============================================================================>
The spread operator ... copies object properties into a new object withiut effecting
 the origianl object when changes ar made to the duplicated cobject 
============================================================================>
Step 6: Register the event listener  :

window.addEventListener(
  'dashboard_campaign_update',
  handleWsCampaignUpdate
);

This tells the browser:
"When the event named dashboard_campaign_update occurs, execute handleWsCampaignUpdate."
============================================================================>
This is a separate event handler.
- ws.onopen handles a successfully opened connection.
- ws.onclose handles a closed connection.
- ws.onmessage handles incoming WebSocket messages.
============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>

============================================================================>
in the above campignes page  :  
routers.py file  :  
campain_view.jsx file codde 
now in this page i want to add the delete icon to each capign and to delete campign and after user clik on teh delete icon on that campain please show the pop with cancel and delete with meniang full message adn buttons if cancle the close the pop up if dlete then delete that template from teh database or elastic srach database 
to get this funtcoinality in the above which block of the code i need to reaplce as what
To add the delete functionality with a confirmation popup, you need to make changes in two files:
Backend (routers.py) — Add a delete endpoint
Frontend (CampaignsView.jsx) — Add the delete icon, confirmation popup, and API call
1. Backend Change (routers.py)
Add this new endpoint after the create_dashboard_campaign endpoint (around line where /api/dashboard/campaigns POST is defined).
python
@router.delete("/api/dashboard/campaigns/{campaign_id}")
async def delete_dashboard_campaign(campaign_id: str, user: dict = Depends(get_current_user)):
    """Deletes a campaign from Elasticsearch by its campaign_id."""
    from db import get_es_client, INDEX_CAMPAIGNS
    es = get_es_client()
    try:
        if es.exists(index=INDEX_CAMPAIGNS, id=campaign_id):
            # Optional: verify user has access to this campaign's app
            doc = es.get(index=INDEX_CAMPAIGNS, id=campaign_id)["_source"]
            check_user_app_access(user, doc.get("app_name"))
            es.delete(index=INDEX_CAMPAIGNS, id=campaign_id)
            return {"status": "success", "message": "Campaign deleted successfully"}
        # Fallback: try query-based delete if ID isn't the doc _id
        query = {"term": {"campaign_id.keyword": campaign_id}}
        res = es.search(index=INDEX_CAMPAIGNS, query=query, size=10)
        hits = res.get("hits", {}).get("hits", [])
        if hits:
            for hit in hits:
                doc = hit["_source"]
                check_user_app_access(user, doc.get("app_name"))
                es.delete(index=INDEX_CAMPAIGNS, id=hit["_id"])
            return {"status": "success", "message": f"Deleted {len(hits)} campaign(s)"}
        raise HTTPException(status_code=404, detail="Campaign not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete campaign: {str(e)}")
Note: Make sure INDEX_CAMPAIGNS is imported from your db.py. If your DB module uses a different index name for campaigns (e.g. INDEX_CAMPAIGN), replace accordingly.
2. Frontend API Helper (api.js / api.ts)
Add a new export in your API helper file (wherever createCampaign, fetchCampaigns, etc. live):
js
export const deleteCampaign = async (campaignId) => {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/campaigns/${campaignId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to delete campaign');
  }
  return res.json();
};
Then update the import in CampaignsView.jsx:
jsx
import { fetchTemplates, fetchCampaigns, createCampaign, createContact, fetchConversations, uploadHeaderFile, exportCampaignsCsv, deleteCampaign } from '../api';
3. Frontend CampaignsView.jsx Changes
A. Add state for the delete confirmation popup
Replace this block (near the top of the component, around the confirmedCampaign state):
jsx
// Campaign Confirmation/Progress View State
const [confirmedCampaign, setConfirmedCampaign] = useState(null);
With:
jsx
// Campaign Confirmation/Progress View State
const [confirmedCampaign, setConfirmedCampaign] = useState(null);
// Delete Confirmation Popup State
const [deleteTarget, setDeleteTarget] = useState(null);
const [deleting, setDeleting] = useState(false);
B. Add the delete handler function
Add this function inside the component, right after handleCreateCampaignSubmit (or anywhere in the component body before the return):
jsx
const handleDeleteCampaign = async () => {
  if (!deleteTarget) return;
  setDeleting(true);
  try {
    await deleteCampaign(deleteTarget.campaign_id);
    // Remove from local list instantly
    setCampaigns(prev => prev.filter(c => c.campaign_id !== deleteTarget.campaign_id));
    setTotalCampaigns(prev => Math.max(0, prev - 1));
    setDeleteTarget(null);
    setExportToast('Campaign deleted successfully');
  } catch (err) {
    alert('Failed to delete campaign: ' + err.message);
  } finally {
    setDeleting(false);
  }
};
C. Add the delete icon in the Actions column
Replace this block inside the campaigns table <tbody>:
jsx
<td>
  <button
    className="secondary-btn"
    style={{ padding: '4px 8px', fontSize: '0.75rem' }}
    onClick={() => setConfirmedCampaign(camp)}
  >
    Analytics
  </button>
</td>
With:
jsx
<td>
  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
    <button
      className="secondary-btn"
      style={{ padding: '4px 8px', fontSize: '0.75rem' }}
      onClick={() => setConfirmedCampaign(camp)}
    >
      Analytics
    </button>
    {currentUser?.can_send !== false && (
      <button
        title="Delete campaign"
        aria-label="Delete campaign"
        onClick={() => setDeleteTarget(camp)}
        style={{
          padding: '5px 7px',
          fontSize: '0.75rem',
          border: '1px solid var(--border)',
          borderRadius: 6,
          background: 'var(--bg-panel)',
          color: '#ef4444',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Trash2 size={14} />
      </button>
    )}
  </div>
</td>
D. Add the Delete Confirmation Popup
Add this JSX block right before the closing </div> of the main component (just after the confirmedCampaign && (...) block, before the final </div>):
jsx
{/* Delete Campaign Confirmation Popup */}
{deleteTarget && (
  <div
    className="confirmation-overlay"
    onClick={() => !deleting && setDeleteTarget(null)}
  >
    <div
      className="confirmation-modal"
      style={{ width: 480, maxWidth: '92%' }}
      onClick={(e) => e.stopPropagation()}
    >
      <div style={{ padding: '22px 24px 16px', display: 'flex', gap: 14, alignItems: 'flex-start' }}>
        <div style={{
          width: 42, height: 42, borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.12)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0
        }}>
          <AlertCircle size={22} color="#ef4444" />
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
            Delete this campaign?
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '8px 0 0', lineHeight: 1.5 }}>
            You are about to permanently delete the campaign{' '}
            <strong style={{ color: 'var(--text-main)' }}>"{deleteTarget.name}"</strong>.
            This action cannot be undone and all associated analytics data will be removed.
          </p>
        </div>
      </div>
      <div style={{
        display: 'flex', gap: 10, padding: '12px 24px 20px',
        borderTop: '1px solid var(--border)', marginTop: 6
      }}>
        <button
          type="button"
          onClick={() => setDeleteTarget(null)}
          disabled={deleting}
          className="filter-btn"
          style={{ flex: 1, padding: '10px', opacity: deleting ? 0.6 : 1 }}
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleDeleteCampaign}
          disabled={deleting}
          style={{
            flex: 1,
            padding: '10px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: deleting ? 'not-allowed' : 'pointer',
            opacity: deleting ? 0.7 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6
          }}
        >
          <Trash2 size={14} />
          {deleting ? 'Deleting...' : 'Delete Campaign'}
        </button>
      </div>
    </div>
  </div>
)}
Summary of What Changed
#	File	Block to Modify	Purpose
1	routers.py	Add new endpoint after create_dashboard_campaign	Backend delete API
2	api.js	Add deleteCampaign export	API helper
3	CampaignsView.jsx	Import line (top)	Import deleteCampaign
4	CampaignsView.jsx	State block near confirmedCampaign	Add popup state
5	CampaignsView.jsx	After handleCreateCampaignSubmit	Add handleDeleteCampaign
6	CampaignsView.jsx	Actions <td> in table	Add delete icon
7	CampaignsView.jsx	Before final </div>	Add confirmation popup
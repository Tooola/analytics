"""Applications page — view, add, and manage API keys."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# dashboard/ on sys.path → share the central API client (PLAN.md V4)
_DASHBOARD_DIR = Path(__file__).resolve().parent.parent
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

from api_client import delete as _delete  # noqa: E402
from api_client import get as _get
from api_client import get_api_base as _get_api_base
from api_client import post as _post


st.title("Applications")
st.markdown("Register and manage applications that consume the analytics API.")

# ─── Persistent Notifications Box ────────────────────────
if "app_notification" in st.session_state and st.session_state["app_notification"]:
    notif = st.session_state["app_notification"]
    notif_type = notif.get("type", "info")
    if notif_type == "success":
        st.success(notif["msg"])
    elif notif_type == "warning":
        st.warning(notif["msg"])
    elif notif_type == "error":
        st.error(notif["msg"])
    
    if "key" in notif and notif["key"]:
        st.warning("🔑 **Save your API Key now — it will not be shown again!**")
        st.code(notif["key"], language="text")

    # Displayed once only — otherwise the raw API key would stay in the DOM
    # for the whole session, contradicting the message above.
    st.session_state["app_notification"] = None

# ─── Register new application ──────────────────────────

with st.expander("Register New Application", expanded=False):
    with st.form("create_app", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Farmtinz")
        description = st.text_area("Description", placeholder="Brief description")
        submitted = st.form_submit_button("Create Application")

        if submitted:
            if not name or not name.strip():
                st.error("Please enter an application name.")
            else:
                with st.spinner("Creating application..."):
                    resp = _post("/api/v1/applications", json_data={
                        "name": name.strip(),
                        "description": description.strip() if description else None,
                    })
                if resp is not None and resp.status_code == 201:
                    data = resp.json()
                    new_key = data.get("api_key", "")
                    st.session_state["api_key"] = new_key
                    st.session_state["app_notification"] = {
                        "type": "success",
                        "msg": f"✅ Application '{data['name']}' (slug: `{data['slug']}`) created successfully!",
                        "key": new_key,
                    }
                    st.rerun()
                elif resp is not None and resp.status_code == 409:
                    st.error("⚠️ An application with this name already exists.")
                else:
                    err_msg = resp.json().get("detail", resp.text) if (resp and resp.headers.get("content-type") == "application/json") else (resp.text if resp else "Connection Error")
                    st.error(f"❌ Failed to create application: {err_msg}")

# ─── Application list ──────────────────────────────────

st.markdown("---")
st.subheader("Registered Applications")

resp = _get("/api/v1/applications")
if resp is not None and resp.status_code == 200:
    apps = resp.json()
    if not apps:
        st.info("No applications registered yet. Create one above.")
    else:
        import pandas as pd
        df = pd.DataFrame(apps)
        display_cols = [c for c in ["name", "slug", "status", "description", "created_at"] if c in df.columns]
        st.dataframe(df[display_cols], width='stretch', hide_index=True)

        st.markdown("---")
        st.subheader("Manage API Keys & Applications")

        app_options = {f"{a['name']} ({a['slug']})": a for a in apps}
        selected = st.selectbox("Select Application", list(app_options.keys()))

        if selected:
            app = app_options[selected]

            # Two-step confirmation for destructive actions (PLAN.md V2).
            # Bound to the app id: changing the selection cancels it.
            pending = st.session_state.get("confirm_action")
            if pending and pending.get("app_id") != app["id"]:
                st.session_state.pop("confirm_action", None)
                pending = None

            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Regenerate API Key", type="secondary", key="regen_btn"):
                    with st.spinner("Regenerating API Key..."):
                        r = _post(f"/api/v1/applications/{app['id']}/regenerate-key")
                    if r is not None and r.status_code == 200:
                        new_key = r.json()["api_key"]
                        st.session_state["api_key"] = new_key
                        st.session_state["app_notification"] = {
                            "type": "success",
                            "msg": f"✅ API Key regenerated for '{app['name']}'!",
                            "key": new_key,
                        }
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to regenerate key: HTTP {r.status_code if r else 'connection error'}")

            with col2:
                if pending and pending.get("action") == "revoke":
                    st.warning(
                        f"⚠️ Revoke the API key of **{app['name']}**? "
                        "Every client still using it will be rejected."
                    )
                    yes, no = st.columns(2)
                    with yes:
                        if st.button("Yes, revoke", key="revoke_confirm_yes", type="primary"):
                            st.session_state.pop("confirm_action", None)
                            with st.spinner("Revoking API Key..."):
                                r = _post(f"/api/v1/applications/{app['id']}/revoke-key")
                            if r is not None and r.status_code == 204:
                                st.session_state["app_notification"] = {
                                    "type": "warning",
                                    "msg": f"⚠️ API Key for '{app['name']}' has been revoked.",
                                }
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to revoke key: HTTP {r.status_code if r else 'connection error'}")
                    with no:
                        if st.button("Cancel", key="revoke_confirm_no"):
                            st.session_state.pop("confirm_action", None)
                            st.rerun()
                elif st.button("Revoke API Key", type="primary", key="revoke_btn"):
                    st.session_state["confirm_action"] = {"action": "revoke", "app_id": app["id"]}
                    st.rerun()

            with col3:
                if pending and pending.get("action") == "delete":
                    st.warning(
                        f"⚠️ Delete **{app['name']}** and all its datasets/analyses? "
                        "This cannot be undone."
                    )
                    yes, no = st.columns(2)
                    with yes:
                        if st.button("Yes, delete", key="delete_confirm_yes", type="primary"):
                            st.session_state.pop("confirm_action", None)
                            with st.spinner("Deleting Application..."):
                                r = _delete(f"/api/v1/applications/{app['id']}")
                            if r is not None and r.status_code == 204:
                                st.session_state["app_notification"] = {
                                    "type": "warning",
                                    "msg": f"🗑️ Application '{app['name']}' has been deleted.",
                                }
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete application: HTTP {r.status_code if r else 'connection error'}")
                    with no:
                        if st.button("Cancel", key="delete_confirm_no"):
                            st.session_state.pop("confirm_action", None)
                            st.rerun()
                elif st.button("Delete Application", type="primary", key="delete_btn"):
                    st.session_state["confirm_action"] = {"action": "delete", "app_id": app["id"]}
                    st.rerun()
elif resp is not None and resp.status_code == 401:
    if not st.session_state.get("api_key"):
        st.info(
            "🔑 **No API key yet** — create your first application above. "
            "Your key is stored automatically for this session."
        )
    else:
        st.warning(
            "❌ **Invalid or revoked API key** — update it in the sidebar "
            "**Settings** panel."
        )
else:
    st.warning("Cannot reach the API. Make sure the backend is running at " + _get_api_base())

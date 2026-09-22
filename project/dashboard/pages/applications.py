"""Applications page — view, add, and manage API keys."""

from __future__ import annotations

import requests as _r
import streamlit as st

API = st.session_state.get("api_base", "http://localhost:8000")


def _get_headers():
    key = st.session_state.get("api_key", "")
    return {"X-API-Key": key} if key else {}


def _get(path):
    try:
        return _r.get(f"{API}{path}", headers=_get_headers(), timeout=10)
    except _r.ConnectionError:
        return None


def _post(path, json_data=None):
    try:
        return _r.post(f"{API}{path}", json=json_data, headers=_get_headers(), timeout=10)
    except _r.ConnectionError:
        return None


def _delete(path):
    try:
        return _r.delete(f"{API}{path}", headers=_get_headers(), timeout=10)
    except _r.ConnectionError:
        return None


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
                if resp and resp.status_code == 201:
                    data = resp.json()
                    new_key = data.get("api_key", "")
                    st.session_state["api_key"] = new_key
                    st.session_state["app_notification"] = {
                        "type": "success",
                        "msg": f"✅ Application '{data['name']}' (slug: `{data['slug']}`) created successfully!",
                        "key": new_key,
                    }
                    st.rerun()
                elif resp and resp.status_code == 409:
                    st.error("⚠️ An application with this name already exists.")
                else:
                    err_msg = resp.json().get("detail", resp.text) if (resp and resp.headers.get("content-type") == "application/json") else (resp.text if resp else "Connection Error")
                    st.error(f"❌ Failed to create application: {err_msg}")

# ─── Application list ──────────────────────────────────

st.markdown("---")
st.subheader("Registered Applications")

resp = _get("/api/v1/applications")
if resp and resp.status_code == 200:
    apps = resp.json()
    if not apps:
        st.info("No applications registered yet. Create one above.")
    else:
        import pandas as pd
        df = pd.DataFrame(apps)
        display_cols = [c for c in ["name", "slug", "status", "description", "created_at"] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Manage API Keys & Applications")

        app_options = {f"{a['name']} ({a['slug']})": a for a in apps}
        selected = st.selectbox("Select Application", list(app_options.keys()))

        if selected:
            app = app_options[selected]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Regenerate API Key", type="secondary", key="regen_btn"):
                    with st.spinner("Regenerating API Key..."):
                        r = _post(f"/api/v1/applications/{app['id']}/regenerate-key")
                    if r and r.status_code == 200:
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
                if st.button("Revoke API Key", type="primary", key="revoke_btn"):
                    with st.spinner("Revoking API Key..."):
                        r = _post(f"/api/v1/applications/{app['id']}/revoke-key")
                    if r and r.status_code == 204:
                        st.session_state["app_notification"] = {
                            "type": "warning",
                            "msg": f"⚠️ API Key for '{app['name']}' has been revoked.",
                        }
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to revoke key: HTTP {r.status_code if r else 'connection error'}")

            with col3:
                if st.button("Delete Application", type="primary", key="delete_btn"):
                    with st.spinner("Deleting Application..."):
                        r = _delete(f"/api/v1/applications/{app['id']}")
                    if r and r.status_code == 204:
                        st.session_state["app_notification"] = {
                            "type": "warning",
                            "msg": f"🗑️ Application '{app['name']}' has been deleted.",
                        }
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to delete application: HTTP {r.status_code if r else 'connection error'}")
elif resp and resp.status_code == 401:
    st.warning("API Key authentication required. Enter your X-API-Key in sidebar Settings.")
else:
    st.warning("Cannot reach the API. Make sure the backend is running at " + API)

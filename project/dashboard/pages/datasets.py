"""Datasets page — enregistrer des datasets et visualiser ceux liés à une application."""

from __future__ import annotations

import json
import requests as _r
import streamlit as st


def _get_api_base():
    api = st.session_state.get("api_base")
    if not api or api in ["http://localhost:8000", "http://127.0.0.1:8000"]:
        return "https://scintillating-kindness-production-d038.up.railway.app"
    return api


def _get_headers():
    key = st.session_state.get("api_key", "")
    return {"X-API-Key": key} if key else {}


def _get(path):
    try:
        return _r.get(f"{_get_api_base()}{path}", headers=_get_headers(), timeout=10)
    except _r.ConnectionError:
        return None


def _post(path, json_data=None, custom_headers=None):
    headers = _get_headers()
    if custom_headers:
        headers.update(custom_headers)
    try:
        return _r.post(f"{_get_api_base()}{path}", json=json_data, headers=headers, timeout=10)
    except _r.ConnectionError:
        return None


def _delete(path):
    try:
        return _r.delete(f"{_get_api_base()}{path}", headers=_get_headers(), timeout=10)
    except _r.ConnectionError:
        return None


st.title("Datasets")
st.markdown("Enregistrez des datasets liés à une application et visualisez leurs schémas de champs.")

# ─── Notifications ─────────────────────────────────────
if "ds_notification" in st.session_state and st.session_state["ds_notification"]:
    notif = st.session_state["ds_notification"]
    notif_type = notif.get("type", "info")
    if notif_type == "success":
        st.success(notif["msg"])
    elif notif_type == "warning":
        st.warning(notif["msg"])
    elif notif_type == "error":
        st.error(notif["msg"])
    st.session_state["ds_notification"] = None

# ─── Charger les applications disponibles ──────────────
apps_resp = _get("/api/v1/applications")
apps = apps_resp.json() if apps_resp and apps_resp.status_code == 200 else []
app_map = {a["slug"]: a for a in apps}  # slug → app dict

# ─── Register New Dataset ──────────────────────────────
with st.expander("Enregistrer un nouveau Dataset", expanded=True if not apps else False):
    if not apps:
        st.warning("Aucune application enregistrée. Créez d'abord une application dans la page **Applications**.")
    else:
        # Sélecteur d'application dans le formulaire
        app_slug_options = [a["slug"] for a in apps]

        # Pré-sélectionner l'app dont la clé API est dans la session
        default_index = 0
        current_key = st.session_state.get("api_key", "")

        with st.form("create_dataset_form", clear_on_submit=True):
            # Sélection de l'application
            selected_app_slug = st.selectbox(
                "Application cible",
                options=app_slug_options,
                index=default_index,
                help="Le dataset sera rattaché à cette application. Vous devez avoir la clé API correspondante.",
            )
            selected_app_info = app_map.get(selected_app_slug)
            if selected_app_info:
                st.caption(f"📌 App ID : `{selected_app_info['id']}` — Statut : `{selected_app_info['status']}`")

            ds_name = st.text_input("Nom du Dataset", placeholder="ex: Ventes Q1")
            ds_slug = st.text_input("Slug du Dataset", placeholder="ex: ventes-q1")
            ds_desc = st.text_area("Description", placeholder="Brève description du dataset")

            DEFAULT_FIELDS_EXAMPLE = '[\n  {"name": "revenue", "technical_type": "float", "semantic_type": "revenue", "unit": "EUR", "required": true},\n  {"name": "quantity", "technical_type": "integer", "semantic_type": "quantity", "unit": "units", "required": true}\n]'
            fields_json = st.text_area(
                "Définition des champs (tableau JSON — au moins 1 champ requis)",
                value=DEFAULT_FIELDS_EXAMPLE,
                height=130,
            )

            # Clé API pour l'app sélectionnée
            api_key_for_app = st.text_input(
                "Clé API de l'application sélectionnée (X-API-Key)",
                value=current_key,
                type="password",
                placeholder="anal_...",
                help="La clé API doit appartenir à l'application sélectionnée ci-dessus.",
            )

            ds_submitted = st.form_submit_button("Enregistrer le Dataset")

            if ds_submitted:
                if not ds_name or not ds_slug:
                    st.error("Veuillez renseigner le Nom et le Slug du dataset.")
                elif not api_key_for_app:
                    st.error("La clé API est requise pour enregistrer un dataset.")
                else:
                    try:
                        parsed_fields = json.loads(fields_json) if fields_json.strip() else []
                    except Exception as e:
                        st.error(f"Format JSON invalide dans la définition des champs : {e}")
                        parsed_fields = None

                    if parsed_fields is not None:
                        if not isinstance(parsed_fields, list) or len(parsed_fields) == 0:
                            st.error("Au moins un champ est requis dans le tableau JSON.")
                        else:
                            with st.spinner("Enregistrement du dataset..."):
                                resp = _post(
                                    "/api/v1/datasets",
                                    json_data={
                                        "name": ds_name.strip(),
                                        "slug": ds_slug.strip(),
                                        "description": ds_desc.strip() if ds_desc else None,
                                        "fields": parsed_fields,
                                    },
                                    custom_headers={"X-API-Key": api_key_for_app},
                                )
                            if resp and resp.status_code == 201:
                                # Mettre à jour la clé en session si elle a changé
                                st.session_state["api_key"] = api_key_for_app
                                st.session_state["ds_notification"] = {
                                    "type": "success",
                                    "msg": f"Dataset '{ds_name}' (`{ds_slug}`) enregistré pour l'application **{selected_app_slug}** !",
                                }
                                st.rerun()
                            elif resp and resp.status_code == 409:
                                st.error("Un dataset avec ce slug existe déjà pour cette application.")
                            elif resp and resp.status_code == 401:
                                st.error("Clé API invalide ou ne correspondant pas à l'application sélectionnée.")
                            else:
                                try:
                                    detail = resp.json().get("detail") if resp else None
                                    if isinstance(detail, list):
                                        errors_str = ", ".join(
                                            f"{e.get('loc', [])[-1]}: {e.get('msg')}" for e in detail
                                        )
                                        st.error(f"Erreur de validation : {errors_str}")
                                    else:
                                        st.error(f"Échec : {detail or (resp.text if resp else 'Erreur de connexion')}")
                                except Exception:
                                    st.error("Échec de l'enregistrement du dataset.")

st.markdown("---")

# ─── Filtrer par application ────────────────────────────
st.subheader("Datasets enregistrés")

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    filter_app = st.selectbox(
        "Filtrer par application",
        options=["Toutes les applications"] + [a["slug"] for a in apps],
        index=0,
    )
with filter_col2:
    st.markdown("<br>", unsafe_allow_html=True)

# Charger les datasets selon le filtre
if filter_app == "Toutes les applications":
    resp = _get("/api/v1/datasets/all")
else:
    resp = _get(f"/api/v1/datasets/by-app/{filter_app}")

if not resp:
    st.warning(f"Impossible de joindre l'API sur {_get_api_base()}. Le backend est-il démarré ?")
    st.stop()
elif resp.status_code != 200:
    st.warning(f"Impossible de récupérer les datasets (HTTP {resp.status_code}).")
    st.stop()

datasets = resp.json()

if not datasets:
    if filter_app == "Toutes les applications":
        st.info("Aucun dataset enregistré. Utilisez le formulaire ci-dessus pour en créer un.")
    else:
        st.info(f"Aucun dataset pour l'application **{filter_app}**. Enregistrez-en un ci-dessus.")
    st.stop()

st.caption(f"{len(datasets)} dataset(s) trouvé(s)")

import pandas as pd

# Grouper par application si vue globale
if filter_app == "Toutes les applications":
    # Construire un mapping id → name pour les apps
    app_id_to_slug = {a["id"]: a["slug"] for a in apps}

    # Grouper les datasets
    from collections import defaultdict
    grouped: dict[str, list] = defaultdict(list)
    for ds in datasets:
        app_id = ds.get("application_id", "unknown")
        app_label = app_id_to_slug.get(app_id, app_id)
        grouped[app_label].append(ds)

    for app_label, ds_list in grouped.items():
        st.markdown(f"### Application : `{app_label}`")
        for ds in ds_list:
            with st.expander(f"**{ds['name']}** — slug : `{ds['slug']}`", expanded=False):
                st.write(ds.get("description") or "_Aucune description_")
                fields = ds.get("fields", [])
                if fields:
                    field_df = pd.DataFrame([
                        {
                            "Champ": f["name"],
                            "Type technique": f["technical_type"],
                            "Type sémantique": f.get("semantic_type") or "—",
                            "Unité": f.get("unit") or "—",
                            "Requis": " " if f.get("required", True) else "",
                        }
                        for f in fields
                    ])
                    st.dataframe(field_df, use_container_width=True, hide_index=True)
                else:
                    st.caption("Aucun champ défini.")
                st.caption(f"ID : `{ds['id']}` | Créé le : {ds.get('created_at', '—')[:10]}")
else:
    for ds in datasets:
        with st.expander(f"**{ds['name']}** — slug : `{ds['slug']}`", expanded=False):
            st.write(ds.get("description") or "_Aucune description_")
            fields = ds.get("fields", [])
            if fields:
                field_df = pd.DataFrame([
                    {
                        "Champ": f["name"],
                        "Type technique": f["technical_type"],
                        "Type sémantique": f.get("semantic_type") or "—",
                        "Unité": f.get("unit") or "—",
                        "Requis": "" if f.get("required", True) else "",
                    }
                    for f in fields
                ])
                st.dataframe(field_df, use_container_width=True, hide_index=True)
            else:
                st.caption("Aucun champ défini.")
            st.caption(f"ID : `{ds['id']}` | Créé le : {ds.get('created_at', '—')[:10]}")


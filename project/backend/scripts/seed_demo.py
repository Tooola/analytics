"""Seed de démonstration : 7 applications métiers, 14 jeux de données réalistes.

But : alimenter une instance locale de T-ola avec des données crédibles
(agriculture, entrepreneuriat, commerce, gouvernement, e-commerce, santé,
éducation) pour que le dashboard puisse être exploré de A à Z :
sélection de l'application → exécution → segments, corrélations, anomalies,
avis IA — le tout en francs CFA (XOF) avec des trajectoires plausibles.

Caractéristiques des données (tout est déterministe, seed fixe) :
- saisonnalité réelle (Ramadan, campagnes des pluies, paludisme, fêtes) ;
- tendances nettes (croissance e-commerce, décroissance d'une startup…) ;
- anomalies volontaires plantées pour l'équipement de détection
  (rupture de stock à Sikasso, panne de passerelle, grève fiscale…).
- les colonnes sont déclarées dans le schéma officiel (types, unités,
  descriptions) : la validation /analyze passe, et l'IA reçoit le contexte
  métier complet (BLOC 1).

Usage (backend démarré sur 127.0.0.1:8000) :
    .venv/Scripts/python.exe scripts/seed_demo.py

Idempotent : les applications/datasets déjà présents sont ignorés ; les clés
API rencontrées sont conservées. Sortie : frontend/public/demo-samples.json
(non versionné — clés locales de démo) consommé par la page « Exécution
d'Analyse » du dashboard pour pré-remplir données + clé à la sélection.
"""

from __future__ import annotations

import json
import random
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
OUT_FILE = Path(__file__).resolve().parents[2] / "frontend" / "public" / "demo-samples.json"
M12 = [f"2025-{m:02d}" for m in range(1, 13)]


# ─── Transport HTTP (stdlib only) ─────────────────────────────────────────

class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(f"HTTP {status} : {detail}")
        self.status = status
        self.detail = detail


def call(method: str, path: str, payload=None, api_key: str | None = None):
    """Appel JSON vers l'API. Retourne la body parsée ; lève ApiError sinon."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(
        BASE_URL + path,
        method=method,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers=headers,
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else None
    except urllib.error.HTTPError as exc:  # noqa: BLE001 — remonté tel quel
        body = exc.read().decode("utf-8", "replace")
        try:
            detail = json.loads(body).get("detail", body)
        except Exception:
            detail = body
        raise ApiError(exc.code, str(detail)) from None


def slugify_app(name: str) -> str:
    """Reprend la règle du dépôt (application_repo._slugify)."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


# ─── Générateurs — 1. Agriculture ─────────────────────────────────────────

def gen_recoltes() -> list[dict]:
    r = random.Random(101)
    cultures = {
        "Maïs": dict(surface=820, rend=5.85,
                     shares=[0.02, 0.02, 0.02, 0.02, 0.03, 0.05, 0.10, 0.18, 0.22, 0.18, 0.10, 0.06]),
        "Riz pluvial": dict(surface=540, rend=5.95,
                            shares=[0.02, 0.02, 0.02, 0.02, 0.02, 0.03, 0.05, 0.12, 0.20, 0.24, 0.16, 0.10]),
        "Sorgho": dict(surface=950, rend=2.75,
                       shares=[0.03, 0.03, 0.02, 0.02, 0.02, 0.03, 0.05, 0.10, 0.16, 0.20, 0.18, 0.16]),
    }
    rows = []
    for culture, cfg in cultures.items():
        for i, mois in enumerate(M12):
            rend = cfg["rend"] * (1 + r.uniform(-0.05, 0.05))
            if culture == "Sorgho" and mois in ("2025-09", "2025-10"):
                rend *= 0.85  # sécheresse pré-récolte sur la culture pluviale
            surface = cfg["surface"] * (1 + r.uniform(-0.01, 0.01))
            rows.append({
                "mois": mois,
                "culture": culture,
                "surface_ha": round(surface, 1),
                "rendement_t_ha": round(rend, 2),
                "recolte_t": round(surface * rend * cfg["shares"][i], 1),
            })
    return rows


def gen_ventes_gerance() -> list[dict]:
    r = random.Random(102)
    q_base = [180, 160, 195, 175, 165, 150, 145, 210, 340, 420, 380, 300]
    rows = []
    for i, mois in enumerate(M12):
        prix = 175_000 * (1.011 ** i)
        if mois == "2025-03":
            prix *= 1.06  # pic de demande pendant le Ramadan
        qte = q_base[i] * (1 + r.uniform(-0.05, 0.05))
        rows.append({
            "mois": mois,
            "quantite_vendue_t": round(qte, 1),
            "prix_tonne_fcfa": int(round(prix / 500) * 500),
            "recette_fcfa": int(round(qte * prix / 1_000) * 1_000),
        })
    return rows


def gen_pluviometrie() -> list[dict]:
    r = random.Random(103)
    mm_base = [2, 1, 5, 12, 48, 130, 152, 268, 180, 62, 8, 1]
    temp_base = [28.2, 31.4, 34.1, 36.2, 35.0, 32.1, 29.4, 28.6, 29.3, 31.2, 30.1, 28.3]
    rows = []
    for i, mois in enumerate(M12):
        mm = mm_base[i] * (1 + r.uniform(-0.08, 0.08))
        rows.append({
            "mois": mois,
            "precipitations_mm": round(mm, 1),
            "jours_pluie": max(0, int(round(mm / 9))),
            "temperature_moy_c": round(temp_base[i] + r.uniform(-0.8, 0.8), 1),
        })
    return rows


# ─── Générateurs — 2. Entrepreneuriat ─────────────────────────────────────

STARTUPS = {
    # arr = revenu récurrent mensuel (FCFA), clients = compte payant
    "NalaPay": dict(
        arr=[1_200_000, 1_450_000, 1_800_000, 2_250_000, 2_800_000, 3_400_000,
             4_100_000, 4_900_000, 5_300_000, 5_900_000, 6_400_000, 7_000_000],
        burn=3_800_000, clients=[310, 395, 480, 610, 760, 910, 1080, 1260, 1400, 1560, 1700, 1850],
        effectif=(9, 14), profil="Fintech de paiement marchand"),
    "DjaMoto": dict(
        arr=[1_500_000, 1_550_000, 1_620_000, 1_600_000, 1_680_000, 1_710_000,
             1_750_000, 1_780_000, 1_810_000, 1_850_000, 1_880_000, 1_920_000],
        burn=2_600_000, clients=[890, 905, 918, 925, 938, 947, 955, 962, 970, 982, 994, 1010],
        effectif=(6, 7), profil="Mobilité & livraison deux-roues"),
    "Kaléko Santé": dict(
        arr=[800_000, 950_000, 1_200_000, 1_550_000, 2_000_000, 2_600_000,
             3_200_000, 3_900_000, 4_400_000, 4_900_000, 5_300_000, 5_750_000],
        burn=3_400_000, clients=[210, 260, 335, 430, 560, 720, 890, 1080, 1250, 1420, 1550, 1620],
        effectif=(8, 13), profil="Télémédecine rurale"),
    "Zabu Agri": dict(
        arr=[2_200_000, 2_150_000, 2_050_000, 1_900_000, 1_750_000, 1_600_000,
             1_450_000, 1_350_000, 1_250_000, 1_150_000, 1_050_000, 950_000],
        burn=2_500_000, clients=[640, 622, 601, 560, 522, 481, 445, 421, 400, 388, 382, 380],
        effectif=(7, 5), profil="Agtech — courtage intrants (décroissance)"),
    "Toma EdTech": dict(
        arr=[1_800_000, 1_850_000, 1_950_000, 2_050_000, 2_100_000, 2_200_000,
             2_300_000, 2_400_000, 2_450_000, 2_550_000, 2_600_000, 2_700_000],
        burn=2_100_000, clients=[420, 432, 448, 462, 470, 484, 496, 508, 517, 532, 545, 560],
        effectif=(5, 6), profil="EdTech — préparation aux concours"),
}


def gen_suivi_startups() -> list[dict]:
    r = random.Random(201)
    rows = []
    for name, s in STARTUPS.items():
        for i, mois in enumerate(M12):
            effectif = round(s["effectif"][0] + (s["effectif"][1] - s["effectif"][0]) * i / 11)
            rows.append({
                "mois": mois,
                "startup": name,
                "arr_mensuel_fcfa": int(round(s["arr"][i] * (1 + r.uniform(-0.02, 0.02)))),
                "depenses_fcfa": int(round(s["burn"] * (1 + r.uniform(-0.06, 0.06)))),
                "nb_clients_payants": int(round(s["clients"][i] * (1 + r.uniform(-0.02, 0.02)))),
                "effectif": effectif,
            })
    return rows


def gen_acquisition() -> list[dict]:
    r = random.Random(202)
    dep = [2_800_000, 2_600_000, 3_100_000, 3_400_000, 3_200_000, 3_500_000,
           3_800_000, 4_000_000, 4_200_000, 4_400_000, 4_600_000, 5_000_000]
    rows = []
    for i, mois in enumerate(M12):
        d = dep[i] * (1 + r.uniform(-0.06, 0.06))
        leads = int(round(d / 420 * (1 + r.uniform(-0.08, 0.08))))
        conv = round(2.6 + 0.065 * i + r.uniform(-0.15, 0.15), 2)
        rows.append({
            "mois": mois,
            "depenses_publicitaires_fcfa": int(round(d)),
            "leads_generes": leads,
            "taux_conversion_pct": conv,
            "nouveaux_clients": int(round(leads * conv / 100)),
        })
    return rows


# ─── Générateurs — 3. Commerce ────────────────────────────────────────────

BOUTIQUES = {
    "Bamako-Grand-Bazaar": dict(ca=14_500_000, tickets=1150),
    "Sikasso-Centre": dict(ca=8_200_000, tickets=720),
    "Mopti-Riverain": dict(ca=6_400_000, tickets=560),
    "Kayes-Centre": dict(ca=5_100_000, tickets=480),
}
SAISON = [0.95, 0.92, 1.22, 1.02, 0.98, 0.95, 0.90, 0.93, 0.97, 1.02, 1.08, 1.30]


def gen_mousso() -> tuple[list[dict], list[dict], dict[str, int]]:
    """Retourne (ventes, approvisionnement, CA total par mois)."""
    r = random.Random(301)
    ventes, ca_total = [], {m: 0 for m in M12}
    for boutique, cfg in BOUTIQUES.items():
        for i, mois in enumerate(M12):
            ca = cfg["ca"] * SAISON[i] * (1 + r.uniform(-0.05, 0.05))
            tickets = cfg["tickets"] * (SAISON[i] ** 0.8) * (1 + r.uniform(-0.04, 0.04))
            if boutique == "Sikasso-Centre" and mois == "2025-08":
                ca *= 0.35   # rupture de stock 3 semaines
                tickets *= 0.40
            ca_total[mois] += ca
            ventes.append({
                "mois": mois,
                "boutique": boutique,
                "ca_fcfa": int(round(ca)),
                "nb_tickets": int(round(tickets)),
                "panier_moyen_fcfa": int(round(ca / tickets)),
            })
    r2 = random.Random(302)
    delai = [4.2, 4.0, 5.8, 4.6, 4.3, 4.1, 4.4, 8.9, 5.1, 4.5, 4.8, 6.2]
    dispo = [95.2, 94.8, 92.4, 94.1, 95.0, 95.4, 94.6, 81.3, 92.8, 94.9, 94.2, 91.5]
    appro = []
    for i, mois in enumerate(M12):
        appro.append({
            "mois": mois,
            "depenses_approvisionnement_fcfa": int(round(ca_total[mois] * 0.62 * (1 + r2.uniform(-0.12, 0.12)))),
            "delai_appro_jours": round(delai[i] * (1 + r2.uniform(-0.05, 0.05)), 1),
            "taux_disponibilite_pct": round(dispo[i] * (1 + r2.uniform(-0.01, 0.01)), 1),
        })
    return ventes, appro, ca_total


# ─── Générateurs — 4. Gouvernement ────────────────────────────────────────

def gen_recettes_commune() -> list[dict]:
    r = random.Random(401)
    transferts = [95, 60, 180, 80, 70, 175, 85, 65, 185, 75, 70, 190]   # millions
    dons = [0, 18, 5, 42, 8, 3, 60, 12, 5, 80, 15, 22]                  # millions
    rows = []
    for i, mois in enumerate(M12):
        plan = {
            "Fiscalité-locale": 145_000_000,
            "Transferts-Etat": 120_000_000,
            "Dons-partenaires": 25_000_000,
            "Activités-marchés": 38_000_000,
        }
        for rubrique, prevu in plan.items():
            if rubrique == "Fiscalité-locale":
                realise = prevu * 0.88 * (1 + r.uniform(-0.06, 0.06))
                if mois == "2025-06":
                    realise *= 0.45  # grève des collecteurs
            elif rubrique == "Transferts-Etat":
                realise = transferts[i] * 1_000_000 * (1 + r.uniform(-0.04, 0.04))
            elif rubrique == "Dons-partenaires":
                realise = dons[i] * 1_000_000 * (1 + r.uniform(-0.15, 0.15))
            else:
                realise = prevu * 0.92 * (1 + r.uniform(-0.05, 0.05))
                if mois == "2025-12":
                    realise *= 1.25
            rows.append({
                "mois": mois,
                "rubrique": rubrique,
                "montant_prevu_fcfa": int(prevu),
                "montant_realise_fcfa": int(round(realise)),
                "taux_execution_pct": round(realise / prevu * 100, 1),
            })
    return rows


def gen_depenses_commune() -> list[dict]:
    r = random.Random(402)
    invest = [55, 40, 120, 70, 50, 45, 130, 80, 60, 150, 110, 190]      # millions
    communautaires = [28, 25, 30, 27, 26, 32, 29, 24, 35, 30, 28, 40]   # millions
    rows = []
    for i, mois in enumerate(M12):
        plan = {
            "Personnel": 165_000_000,
            "Investissements": 95_000_000,
            "Fonctionnement": 62_000_000,
            "Transferts-communautaires": 30_000_000,
        }
        for rubrique, prevu in plan.items():
            if rubrique == "Personnel":
                realise = prevu * 0.995 * (1 + r.uniform(-0.01, 0.01))
            elif rubrique == "Investissements":
                realise = invest[i] * 1_000_000 * (1 + r.uniform(-0.08, 0.08))
            elif rubrique == "Fonctionnement":
                realise = prevu * 0.90 * (1 + r.uniform(-0.06, 0.06))
                if mois == "2025-03":
                    realise *= 1.08
            else:
                realise = communautaires[i] * 1_000_000 * (1 + r.uniform(-0.05, 0.05))
            rows.append({
                "mois": mois,
                "rubrique": rubrique,
                "montant_prevu_fcfa": int(prevu),
                "montant_realise_fcfa": int(round(realise)),
                "taux_execution_pct": round(realise / prevu * 100, 1),
            })
    return rows


# ─── Générateurs — 5. E-commerce ──────────────────────────────────────────

def gen_commandes() -> list[dict]:
    canaux = {
        "Web": dict(
            cmd=[3200, 3050, 3950, 2400, 3500, 3600, 3700, 3900, 4100, 4400, 4900, 6200],
            panier=[14_500, 14_800, 15_200, 13_900, 15_100, 15_300, 15_500, 15_700, 15_900, 16_000, 16_200, 16_800],
            conv=[2.4, 2.3, 2.9, 1.4, 2.6, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.3]),
        "Mobile": dict(
            cmd=[620, 660, 850, 520, 900, 980, 1050, 1180, 1320, 1500, 1800, 2400],
            panier=[9_800, 9_900, 10_200, 9_500, 10_300, 10_400, 10_600, 10_800, 11_000, 11_200, 11_500, 12_000],
            conv=[1.8, 1.8, 2.2, 1.1, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9]),
        "WhatsApp-B2B": dict(
            cmd=[42, 45, 58, 38, 62, 66, 70, 78, 85, 95, 108, 130],
            panier=[165_000, 168_000, 172_000, 160_000, 175_000, 178_000,
                    182_000, 186_000, 190_000, 195_000, 200_000, 210_000],
            conv=[7.8, 8.0, 9.2, 6.9, 9.5, 9.8, 10.1, 10.4, 10.8, 11.0, 11.4, 11.9]),
    }
    r = random.Random(501)
    rows = []
    for canal, s in canaux.items():
        for i, mois in enumerate(M12):
            cmd = s["cmd"][i] * (1 + r.uniform(-0.03, 0.03))
            panier = s["panier"][i] * (1 + r.uniform(-0.02, 0.02))
            rows.append({
                "mois": mois,
                "canal": canal,
                "nb_commandes": int(round(cmd)),
                "panier_moyen_fcfa": int(round(panier)),
                "taux_conversion_pct": round(s["conv"][i] * (1 + r.uniform(-0.04, 0.04)), 2),
                "ca_fcfa": int(round(cmd * panier)),
            })
    return rows


def gen_logistique() -> list[dict]:
    r = random.Random(502)
    delai = [2.8, 2.9, 3.6, 3.1, 2.9, 2.8, 3.0, 3.1, 2.9, 3.2, 3.5, 4.2]
    reussie = [93, 92, 86, 89, 92, 93, 92, 91, 93, 92, 90, 84]
    retours = [7.5, 7.8, 9.6, 11.2, 8.2, 7.6, 7.4, 7.9, 7.2, 7.6, 8.1, 9.8]
    cout = [1450, 1460, 1520, 1490, 1480, 1500, 1530, 1560, 1580, 1620, 1680, 1750]
    rows = []
    for i, mois in enumerate(M12):
        rows.append({
            "mois": mois,
            "delai_moyen_jours": round(delai[i] * (1 + r.uniform(-0.04, 0.04)), 1),
            "taux_livraison_reussie_pct": round(reussie[i] * (1 + r.uniform(-0.01, 0.01)), 1),
            "taux_retours_pct": round(retours[i] * (1 + r.uniform(-0.05, 0.05)), 1),
            "cout_livraison_moyen_fcfa": int(round(cout[i] * (1 + r.uniform(-0.02, 0.02)))),
        })
    return rows


# ─── Générateurs — 6. Santé ───────────────────────────────────────────────

def gen_consultations() -> list[dict]:
    services = {
        "Pédiatrie": dict(base=480, tarif=8_500, duree=18,
                          saison=[0.85, 0.80, 0.85, 0.90, 0.95, 1.15, 1.90, 2.30, 2.10, 1.60, 1.10, 0.95]),
        "Médecine-générale": dict(base=620, tarif=12_000, duree=24,
                                  saison=[1.05, 1.00, 1.00, 0.95, 0.90, 0.95, 1.10, 1.15, 1.10, 1.05, 1.00, 1.05]),
        "Maternité": dict(base=340, tarif=15_000, duree=32,
                          saison=[0.95, 0.96, 0.97, 0.98, 0.99, 1.00, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06]),
        "Laboratoire": dict(base=290, tarif=22_000, duree=15,
                            saison=[0.90, 0.88, 0.92, 0.95, 1.00, 1.20, 1.75, 2.05, 1.90, 1.45, 1.05, 0.92]),
    }
    r = random.Random(601)
    rows = []
    for service, cfg in services.items():
        for i, mois in enumerate(M12):
            nb = cfg["base"] * cfg["saison"][i] * (1 + r.uniform(-0.04, 0.04))
            rows.append({
                "mois": mois,
                "service": service,
                "nb_consultations": int(round(nb)),
                "recette_fcfa": int(round(nb * cfg["tarif"] * (1 + r.uniform(-0.03, 0.03)))),
                "duree_moyenne_min": round(cfg["duree"] * (1 + r.uniform(-0.05, 0.05)), 1),
            })
    return rows


def gen_pharmacie() -> list[dict]:
    bases = {
        "Pédiatrie": dict(stock=3_800_000, refs=230, rupt=3, palu=0.55),
        "Médecine-générale": dict(stock=5_200_000, refs=260, rupt=2, palu=0.15),
        "Maternité": dict(stock=4_100_000, refs=240, rupt=2, palu=0.10),
        "Laboratoire": dict(stock=2_600_000, refs=210, rupt=4, palu=0.45),
    }
    pic = [0.9, 0.88, 0.9, 0.92, 0.95, 1.1, 1.6, 1.85, 1.7, 1.35, 1.0, 0.92]
    r = random.Random(602)
    rows = []
    for service, cfg in bases.items():
        for i, mois in enumerate(M12):
            crise = 1 + (pic[i] - 1) * cfg["palu"]
            rows.append({
                "mois": mois,
                "service": service,
                "valeur_stock_fcfa": int(round(cfg["stock"] * crise * (1 + r.uniform(-0.05, 0.05)))),
                "nb_references_disponibles": int(round(cfg["refs"] / crise * (1 + r.uniform(-0.03, 0.03)))),
                "nb_ruptures": int(round(cfg["rupt"] * crise * (1 + r.uniform(-0.2, 0.2)))),
            })
    return rows


# ─── Générateurs — 7. Éducation ───────────────────────────────────────────

def gen_inscriptions() -> list[dict]:
    filieres = {
        "Génie-informatique": dict(inscrits=[120, 165, 230, 315, 410], rr=[62, 64, 61, 55, 68], frais=85_000),
        "Agro-environnement": dict(inscrits=[90, 102, 118, 130, 142], rr=[58, 57, 60, 54, 63], frais=75_000),
        "Génie-civil": dict(inscrits=[80, 84, 88, 92, 96], rr=[55, 58, 56, 52, 60], frais=80_000),
        "Gestion-administration": dict(inscrits=[150, 158, 166, 172, 164], rr=[70, 71, 69, 62, 72], frais=70_000),
    }
    annees = ["2021", "2022", "2023", "2024", "2025"]
    r = random.Random(701)
    rows = []
    for filiere, cfg in filieres.items():
        for i, annee in enumerate(annees):
            rows.append({
                "annee": annee,
                "filiere": filiere,
                "nb_inscrits": int(round(cfg["inscrits"][i] * (1 + r.uniform(-0.02, 0.02)))),
                "frais_percus_fcfa": int(round(cfg["inscrits"][i] * cfg["frais"] * (1 + r.uniform(-0.04, 0.04)))),
                "taux_reussite_pct": round(cfg["rr"][i] * (1 + r.uniform(-0.02, 0.02)), 1),
            })
    return rows


def gen_resultats() -> list[dict]:
    candidats = [720, 810, 890, 975, 1030]
    admis = [468, 535, 628, 742, 856]
    budget = [245_000_000, 262_000_000, 285_000_000, 310_000_000, 345_000_000]
    annees = ["2021", "2022", "2023", "2024", "2025"]
    return [{
        "annee": annees[i],
        "nb_candidats": candidats[i],
        "nb_admis": admis[i],
        "taux_admission_pct": round(admis[i] / candidats[i] * 100, 1),
        "budget_pedagogique_fcfa": budget[i],
    } for i in range(5)]


# ─── Catalogue ────────────────────────────────────────────────────────────

def f(name, ttype, semantic=None, unit=None, desc=None):
    return {"name": name, "technical_type": ttype, "semantic_type": semantic,
            "unit": unit, "description": desc, "required": True}


def build_apps() -> list[dict]:
    ventes, appro, _ = gen_mousso()
    return [
        {
            "name": "Coop Sahel Vert Cereales",
            "description": (
                "Coopérative céréalière de 1 200 producteurs basée à Ségou (Mali). "
                "Suivi de la campagne 2025 : récoltes par culture, ventes de la gérance "
                "(maïs, riz pluvial, sorgho) et données pluviométriques de la station. "
                "Tous les montants sont en francs CFA (XOF)."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Récoltes par culture", "slug": "recoltes-par-culture",
                    "description": "Récoltes mensuelles 2025 par culture : surface cultivée, rendement et tonnage récolté.",
                    "groupBy": "culture",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("culture", "string", "catégorie", None, "Culture principale : maïs, riz pluvial ou sorgho"),
                        f("surface_ha", "float", "mesure", "hectares", "Surface effective récoltée"),
                        f("rendement_t_ha", "float", "mesure", "tonnes/ha", "Rendement moyen constaté"),
                        f("recolte_t", "float", "mesure", "tonnes", "Tonnage total récolté"),
                    ],
                    "rows": gen_recoltes(),
                },
                {
                    "name": "Ventes de la gérance", "slug": "ventes-gerance",
                    "description": "Ventes mensuelles de céréales par la gérance : quantités, prix de la tonne et recette encaissée.",
                    "groupBy": None,
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("quantite_vendue_t", "float", "mesure", "tonnes", "Quantité vendue sur le mois"),
                        f("prix_tonne_fcfa", "integer", "montant", "FCFA/tonne", "Prix moyen de la tonne"),
                        f("recette_fcfa", "integer", "montant", "FCFA", "Recette nette encaissée"),
                    ],
                    "rows": gen_ventes_gerance(),
                },
                {
                    "name": "Pluviométrie station", "slug": "pluviometrie-station",
                    "description": "Relevés mensuels de la pluviométrie et de la température de la station de Ségou.",
                    "groupBy": None,
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("precipitations_mm", "float", "mesure", "mm", "Cumul mensuel des précipitations"),
                        f("jours_pluie", "integer", "compteur", "jours", "Nombre de jours de pluie"),
                        f("temperature_moy_c", "float", "mesure", "°C", "Température moyenne du mois"),
                    ],
                    "rows": gen_pluviometrie(),
                },
            ],
        },
        {
            "name": "Inkubator Kounda Startups",
            "description": (
                "Incubateur d'entreprises tech de Bamako : portefeuille de 5 startups suivies "
                "mensuellement (revenu récurrent, brûlage de trésorerie, clients payants, effectif) "
                "et campagnes d'acquisition. Montants en francs CFA (XOF)."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Suivi des startups", "slug": "suivi-startups",
                    "description": "Suivi mensuel par startup du revenu récurrent (ARR), des dépenses, des clients payants et de l'effectif.",
                    "groupBy": "startup",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("startup", "string", "catégorie", None, "Startup du portefeuille"),
                        f("arr_mensuel_fcfa", "integer", "montant", "FCFA/mois", "Revenu récurrent mensuel (MRR)"),
                        f("depenses_fcfa", "integer", "montant", "FCFA/mois", "Brûlage de trésorerie (burn) mensuel"),
                        f("nb_clients_payants", "integer", "compteur", "clients", "Clients actifs payants en fin de mois"),
                        f("effectif", "integer", "compteur", "personnes", "Effectif salarié en fin de mois"),
                    ],
                    "rows": gen_suivi_startups(),
                },
                {
                    "name": "Acquisition marketing", "slug": "acquisition-marketing",
                    "description": "Campagnes d'acquisition de l'incubateur : dépenses publicitaires, leads générés et conversion en clients.",
                    "groupBy": None,
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("depenses_publicitaires_fcfa", "integer", "montant", "FCFA/mois", "Budget publicitaire consommé"),
                        f("leads_generes", "integer", "compteur", "leads", "Leads qualifiés générés"),
                        f("taux_conversion_pct", "float", "ratio", "%", "Taux de conversion lead → client"),
                        f("nouveaux_clients", "integer", "compteur", "clients", "Nouveaux clients signés"),
                    ],
                    "rows": gen_acquisition(),
                },
            ],
        },
        {
            "name": "Groupe Mousso Distribution",
            "description": (
                "Réseau de 4 boutiques de distribution générale (Bamako, Sikasso, Mopti, Kayes) : "
                "chiffre d'affaires, tickets, panier moyen et approvisionnement. "
                "Tous les montants sont en francs CFA (XOF)."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Ventes par boutique", "slug": "ventes-boutiques",
                    "description": "Chiffre d'affaires mensuel par boutique : CA, nombre de tickets et panier moyen.",
                    "groupBy": "boutique",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("boutique", "string", "catégorie", None, "Point de vente"),
                        f("ca_fcfa", "integer", "montant", "FCFA/mois", "Chiffre d'affaires TTC encaissé"),
                        f("nb_tickets", "integer", "compteur", "tickets", "Nombre de tickets de caisse"),
                        f("panier_moyen_fcfa", "integer", "montant", "FCFA/ticket", "Panier moyen par ticket"),
                    ],
                    "rows": ventes,
                },
                {
                    "name": "Approvisionnement", "slug": "approvisionnement",
                    "description": "Approvisionnement centralisé : dépenses d'achat, délai fournisseur et taux de disponibilité en rayon.",
                    "groupBy": None,
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("depenses_approvisionnement_fcfa", "integer", "montant", "FCFA/mois", "Achats centraux réalisés"),
                        f("delai_appro_jours", "float", "mesure", "jours", "Délai moyen de réapprovisionnement"),
                        f("taux_disponibilite_pct", "float", "ratio", "%", "Taux de produits disponibles en rayon"),
                    ],
                    "rows": appro,
                },
            ],
        },
        {
            "name": "Commune de Segou Budget",
            "description": (
                "Commune de Ségou (Mali) — exécution du budget 2025 : recettes par rubrique "
                "(fiscalité locale, transferts de l'État, dons de partenaires, marchés) et dépenses "
                "(personnel, investissements, fonctionnement, transferts communautaires). Montants en francs CFA (XOF)."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Recettes de la commune", "slug": "recettes-commune",
                    "description": "Exécution mensuelle des recettes budgétaires : montant prévu, montant réalisé et taux d'exécution.",
                    "groupBy": "rubrique",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("rubrique", "string", "catégorie", None, "Rubrique de recette"),
                        f("montant_prevu_fcfa", "integer", "montant", "FCFA/mois", "Recette prévue au budget"),
                        f("montant_realise_fcfa", "integer", "montant", "FCFA/mois", "Recette réellement encaissée"),
                        f("taux_execution_pct", "float", "ratio", "%", "Rapport réalisé / prévu"),
                    ],
                    "rows": gen_recettes_commune(),
                },
                {
                    "name": "Dépenses de la commune", "slug": "depenses-commune",
                    "description": "Exécution mensuelle des dépenses budgétaires : montant prévu, montant réalisé et taux d'exécution.",
                    "groupBy": "rubrique",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("rubrique", "string", "catégorie", None, "Rubrique de dépense"),
                        f("montant_prevu_fcfa", "integer", "montant", "FCFA/mois", "Dépense prévue au budget"),
                        f("montant_realise_fcfa", "integer", "montant", "FCFA/mois", "Dépense réellement engagée"),
                        f("taux_execution_pct", "float", "ratio", "%", "Rapport réalisé / prévu"),
                    ],
                    "rows": gen_depenses_commune(),
                },
            ],
        },
        {
            "name": "KabaMarket Place de Vente",
            "description": (
                "Place de marché en ligne au Sahel : commandes par canal (Web, Mobile, WhatsApp B2B), "
                "taux de conversion, panier moyen et performance logistique. Montants en francs CFA (XOF)."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Commandes par canal", "slug": "commandes-canaux",
                    "description": "Commandes mensuelles par canal d'acquisition : volume, panier moyen, conversion et chiffre d'affaires.",
                    "groupBy": "canal",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("canal", "string", "catégorie", None, "Canal de commande : Web, Mobile ou WhatsApp-B2B"),
                        f("nb_commandes", "integer", "compteur", "commandes", "Nombre de commandes validées"),
                        f("panier_moyen_fcfa", "integer", "montant", "FCFA/commande", "Panier moyen par commande"),
                        f("taux_conversion_pct", "float", "ratio", "%", "Taux de conversion des sessions"),
                        f("ca_fcfa", "integer", "montant", "FCFA/mois", "Chiffre d'affaires du canal"),
                    ],
                    "rows": gen_commandes(),
                },
                {
                    "name": "Logistique livraisons", "slug": "logistique-livraisons",
                    "description": "Qualité du service logistique mensuel : délai moyen de livraison, livraisons réussies, retours et coût.",
                    "groupBy": None,
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("delai_moyen_jours", "float", "mesure", "jours", "Délai moyen commande → livraison"),
                        f("taux_livraison_reussie_pct", "float", "ratio", "%", "Part des livraisons réussies au premier passage"),
                        f("taux_retours_pct", "float", "ratio", "%", "Part des commandes retournées ou annulées"),
                        f("cout_livraison_moyen_fcfa", "integer", "montant", "FCFA/livraison", "Coût moyen d'une livraison"),
                    ],
                    "rows": gen_logistique(),
                },
            ],
        },
        {
            "name": "Reseau Cliniques Bakoro",
            "description": (
                "Réseau de 4 cliniques privées (pédiatrie, médecine générale, maternité, laboratoire) : "
                "consultations, recettes, durée moyenne des actes et gestion des stocks de pharmacie. "
                "Montants en francs CFA (XOF). Pic saisonnier de paludisme de juillet à octobre."
            ),
            "joinKey": "mois",
            "datasets": [
                {
                    "name": "Consultations par service", "slug": "consultations-services",
                    "description": "Consultations mensuelles par service clinique : fréquentation, recette et durée moyenne des actes.",
                    "groupBy": "service",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("service", "string", "catégorie", None, "Service clinique"),
                        f("nb_consultations", "integer", "compteur", "consultations", "Nombre de consultations réalisées"),
                        f("recette_fcfa", "integer", "montant", "FCFA/mois", "Recette du service"),
                        f("duree_moyenne_min", "float", "mesure", "minutes", "Durée moyenne d'un acte"),
                    ],
                    "rows": gen_consultations(),
                },
                {
                    "name": "Stocks de pharmacie", "slug": "pharmacie-stocks",
                    "description": "Gestion mensuelle des stocks par service : valeur immobilisée, références disponibles et ruptures.",
                    "groupBy": "service",
                    "fields": [
                        f("mois", "string", "période", "mois (AAAA-MM)", "Mois de rattachement"),
                        f("service", "string", "catégorie", None, "Service clinique"),
                        f("valeur_stock_fcfa", "integer", "montant", "FCFA", "Valeur du stock immobilisé"),
                        f("nb_references_disponibles", "integer", "compteur", "références", "Références medicamenteuses disponibles"),
                        f("nb_ruptures", "integer", "compteur", "références", "Références en rupture sur le mois"),
                    ],
                    "rows": gen_pharmacie(),
                },
            ],
        },
        {
            "name": "Universite Polytechnique de Segou",
            "description": (
                "Université polytechnique de Ségou : pilotage académique par filière "
                "(génie informatique, agro-environnement, génie civil, gestion) — inscriptions, "
                "frais perçus, taux de réussite et résultats aux concours d'accès. Montants en francs CFA (XOF)."
            ),
            "joinKey": "annee",
            "datasets": [
                {
                    "name": "Inscriptions par filière", "slug": "inscriptions-filieres",
                    "description": "Inscriptions annuelles par filière : effectifs, frais perçus et taux de réussite aux examens.",
                    "groupBy": "filiere",
                    "fields": [
                        f("annee", "string", "période", "année", "Année universitaire"),
                        f("filiere", "string", "catégorie", None, "Filière de formation"),
                        f("nb_inscrits", "integer", "compteur", "étudiants", "Étudiants inscrits"),
                        f("frais_percus_fcfa", "integer", "montant", "FCFA/an", "Frais d'inscription perçus"),
                        f("taux_reussite_pct", "float", "ratio", "%", "Taux de réussite aux examens"),
                    ],
                    "rows": gen_inscriptions(),
                },
                {
                    "name": "Concours d'accès", "slug": "concours-acces",
                    "description": "Résultats annuels des concours d'accès : candidats, admis, taux d'admission et budget pédagogique.",
                    "groupBy": None,
                    "fields": [
                        f("annee", "string", "période", "année", "Année du concours"),
                        f("nb_candidats", "integer", "compteur", "candidats", "Candidats inscrits au concours"),
                        f("nb_admis", "integer", "compteur", "admis", "Candidats admis"),
                        f("taux_admission_pct", "float", "ratio", "%", "Taux d'admission global"),
                        f("budget_pedagogique_fcfa", "integer", "montant", "FCFA/an", "Budget pédagogique de l'année"),
                    ],
                    "rows": gen_resultats(),
                },
            ],
        },
    ]


# ─── Orchestration ────────────────────────────────────────────────────────

def load_saved() -> dict[str, dict]:
    if OUT_FILE.exists():
        try:
            data = json.loads(OUT_FILE.read_text(encoding="utf-8"))
            return {a["slug"]: a for a in data.get("apps", [])}
        except Exception:
            pass
    return {}


def main() -> int:
    try:
        call("GET", "/api/v1/health")
    except ApiError as exc:
        print(f"Backend injoignable sur {BASE_URL} ({exc}). Démarrez-le d'abord.")
        return 1

    saved = load_saved()
    out_apps = []
    print(f"{'Application':38} {'Datasets':10} Statut")
    print("─" * 78)

    for spec in build_apps():
        slug = slugify_app(spec["name"])
        api_key = (saved.get(slug) or {}).get("apiKey")
        app_statut = "existante"
        if api_key is None:
            try:
                created = call("POST", "/api/v1/applications",
                               {"name": spec["name"], "description": spec["description"]})
                api_key = created["api_key"]
                slug = created["slug"]
                app_statut = "créée"
            except ApiError as exc:
                if exc.status == 409:
                    print(f"  ! « {spec['name']} » existe déjà mais sa clé est inconnue "
                          f"(demo-samples.json manquant) — relancez avec TOLA_ADMIN_PASSWORD pour la régénérer.")
                    print(f"    ({exc.detail})")
                    continue
                raise

        existing_slugs = {d["slug"] for d in (call("GET", "/api/v1/datasets", api_key=api_key) or [])}
        ds_out = []
        for ds in spec["datasets"]:
            if ds["slug"] in existing_slugs:
                ds_out.append(ds)
                continue
            call("POST", "/api/v1/datasets",
                 {"name": ds["name"], "slug": ds["slug"], "description": ds["description"],
                  "fields": ds["fields"]},
                 api_key=api_key)
            ds_out.append(ds)

        out_apps.append({
            "name": spec["name"], "slug": slug, "apiKey": api_key,
            "joinKey": spec["joinKey"],
            "datasets": [{
                "name": d["name"], "slug": d["slug"], "groupBy": d["groupBy"],
                "rowCount": len(d["rows"]), "rows": d["rows"],
            } for d in ds_out],
        })
        n_rows = sum(len(d["rows"]) for d in ds_out)
        print(f"{spec['name']:38} {len(ds_out)} ({n_rows:>3} lignes)  {app_statut}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps({
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": "Données de démonstration générées par project/backend/scripts/seed_demo.py — usage local uniquement.",
        "apps": out_apps,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("─" * 78)
    total_rows = sum(ds["rowCount"] for a in out_apps for ds in a["datasets"])
    print(f"{len(out_apps)} applications · "
          f"{sum(len(a['datasets']) for a in out_apps)} datasets · {total_rows} lignes")
    print(f"Échantillons écrits : {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

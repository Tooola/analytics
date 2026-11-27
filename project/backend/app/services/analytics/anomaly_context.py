"""Génération de diagnostics et recommandations opérationnelles contextuelles pour les anomalies.

Remplace les messages génériques ("Vérifier les données / erreur de saisie") par des
analyses de cause et des leviers d'action adaptés au domaine métier (agriculture,
santé, commerce, logistique, industrie, finances).
"""

from __future__ import annotations

import re
from typing import Tuple
from app.utils.humanize import humanize_column


def get_anomaly_insight(
    column: str,
    val: float,
    mean: float,
    language: str = "fr",
) -> Tuple[str, str]:
    """Retourne (reason, recommendation) contextualisés pour une métrique donnée."""
    col_norm = column.lower().strip()
    is_high = val > mean
    label = humanize_column(column)
    val_str = f"{val:,.1f}".replace(",", " ").replace(".", ",") if language == "fr" else f"{val:,.1f}"
    mean_str = f"{mean:,.1f}".replace(",", " ").replace(".", ",") if language == "fr" else f"{mean:,.1f}"

    # 1. AGRICULTURE & CLIMAT : Pluviométrie / Pluie / Rain
    if any(k in col_norm for k in ("pluvio", "pluie", "rain", "precipit")):
        if is_high:
            if language == "en":
                return (
                    f"Exceptional rainfall peak ({val_str} vs normal average {mean_str}).",
                    "Inspect drainage on low-lying plots and suspend artificial irrigation to prevent root hypoxia and waterlogging; check rain gauge calibration if the cumulative amount appears aberrant.",
                )
            return (
                f"Pic pluviométrique exceptionnel ({val_str} vs moyenne habituelle {mean_str}).",
                "Contrôler le drainage des parcelles basses et suspendre l'irrigation artificielle pour éviter l'asphyxie racinaire ; vérifier l'étalonnage du pluviomètre en cas de cumul aberrant.",
            )
        else:
            if language == "en":
                return (
                    f"Severe water deficit ({val_str} vs normal average {mean_str}).",
                    "Trigger priority supplemental irrigation on sensitive crops and monitor leaf water stress to avoid yield loss.",
                )
            return (
                f"Déficit hydrique marqué ({val_str} vs moyenne habituelle {mean_str}).",
                "Déclencher l'irrigation d'appoint prioritaire sur les cultures sensibles et surveiller le stress hydrique foliaire pour préserver la floraison.",
            )

    # 2. AGRICULTURE : Rendement / Récolte / Production agricole / Harvest
    if any(k in col_norm for k in ("rendement", "recolte", "harvest", "yield", "quintaux")):
        if is_high:
            if language == "en":
                return (
                    f"Record yield spike ({val_str} vs normal average {mean_str}).",
                    "Mobilize additional storage capacity and harvesting logistics to secure grain quality and prevent post-harvest spoilage.",
                )
            return (
                f"Pic de rendement record ({val_str} vs moyenne habituelle {mean_str}).",
                "Mobiliser des capacités de stockage et d'évacuation logistique supplémentaires pour sécuriser la collecte et éviter les pertes post-récolte.",
            )
        else:
            if language == "en":
                return (
                    f"Sharp yield drop ({val_str} vs normal average {mean_str}).",
                    "Inspect plot phytosanitary health (pest attacks, nutrient deficiency, fungal disease) and isolate impacted parcels.",
                )
            return (
                f"Chute brutale de rendement ({val_str} vs moyenne habituelle {mean_str}).",
                "Inspecter immédiatement l'état phytosanitaire des parcelles (attaques de ravageurs, carence azotée ou maladie fongique) et isoler les zones touchées.",
            )

    # 3. CLIMAT : Température
    if any(k in col_norm for k in ("temperat", "temp_")):
        if is_high:
            if language == "en":
                return (
                    f"Extreme thermal spike ({val_str} vs average {mean_str}).",
                    "Deploy active shading, increase greenhouse ventilation and monitor crop evapotranspiration rates.",
                )
            return (
                f"Pic thermique extrême ({val_str} vs moyenne {mean_str}).",
                "Activer l'ombrage, renforcer la ventilation des serres et intensifier la surveillance de l'évapotranspiration des cultures.",
            )
        else:
            if language == "en":
                return (
                    f"Sudden thermal drop ({val_str} vs average {mean_str}).",
                    "Activate frost protection devices (wind machines, heaters) and delay sensitive agronomic operations.",
                )
            return (
                f"Chute thermique soudaine ({val_str} vs moyenne {mean_str}).",
                "Activer les dispositifs de lutte antigel (aspersion, bougies) et différer les opérations de fertilisation sensibles.",
            )

    # 4. SANTÉ / MÉDICAL : Consultations / Patients / Admissions / Urgences
    if any(k in col_norm for k in ("consultation", "patient", "admission", "urgence", "visite", "entree")):
        if is_high:
            if language == "en":
                return (
                    f"Patient surge significantly above typical capacity ({val_str} vs average {mean_str}).",
                    "Reinforce on-call medical staff, open overflow consultation units and restock emergency consumables.",
                )
            return (
                f"Pic d'affluence médicale au-dessus des flux normaux ({val_str} vs moyenne {mean_str}).",
                "Renforcer les effectifs de garde médicale, ouvrir des box de consultation d'appoint et réapprovisionner les consommables d'urgence.",
            )
        else:
            if language == "en":
                return (
                    f"Unusual attendance drop below expected baseline ({val_str} vs average {mean_str}).",
                    "Review clinic duty schedules, verify practitioner availability and audit intake channels.",
                )
            return (
                f"Chute inhabituelle de fréquentation ({val_str} vs moyenne {mean_str}).",
                "Vérifier le planning de permanence médicale, la disponibilité des praticiens ou d'éventuels blocages dans la prise de rendez-vous.",
            )

    # 5. SANTÉ : Durée / Temps d'attente / Prise en charge
    if any(k in col_norm for k in ("duree", "attente", "wait", "delay", "minute")):
        if is_high:
            if language == "en":
                return (
                    f"Critical lengthening of patient wait times ({val_str} vs average {mean_str}).",
                    "Reassign triage personnel to fast-track intake, streamline billing and expedite discharge procedures.",
                )
            return (
                f"Allongement critique des temps de prise en charge ({val_str} vs moyenne {mean_str}).",
                "Affecter un infirmier supplémentaire au tri d'accueil, fluidifier l'enregistrement administratif et activer le circuit court ambulatoire.",
            )
        else:
            if language == "en":
                return (
                    f"Exceptionally rapid intake duration ({val_str} vs average {mean_str}).",
                    "Document efficient shift practices and ensure clinical handover standards were fully respected.",
                )
            return (
                f"Durée de prise en charge remarquablement courte ({val_str} vs moyenne {mean_str}).",
                "Capitaliser sur les bonnes pratiques de cette équipe et valider la complétude du dossier médical.",
            )

    # 6. COMMERCE / VENTES : Chiffre d'affaires, Recettes, Ventes
    if any(k in col_norm for k in ("recette", "chiffre_affaire", "vente", "revenue", "sales", "montant")):
        if is_high:
            if language == "en":
                return (
                    f"Exceptional sales peak ({val_str} vs average {mean_str}).",
                    "Secure inventory replenishment to prevent out-of-stock events and allocate extra fulfillment staffing.",
                )
            return (
                f"Pic de recettes exceptionnel ({val_str} vs moyenne {mean_str}).",
                "Sécuriser le réapprovisionnement des stocks pour éviter les ruptures et mobiliser des renforts en caisse et logistique.",
            )
        else:
            if language == "en":
                return (
                    f"Severe revenue downturn ({val_str} vs average {mean_str}).",
                    "Audit promotional pipeline, test checkout flow and launch targeted reactivation incentives.",
                )
            return (
                f"Décrochage sévère des recettes ({val_str} vs moyenne {mean_str}).",
                "Vérifier le tunnel d'achat, auditer l'attractivité de l'offre et déclencher une opération promotionnelle ciblée.",
            )

    # 7. COMMERCE : Panier moyen / Order value
    if any(k in col_norm for k in ("panier", "basket", "aov", "ticket")):
        if is_high:
            if language == "en":
                return (
                    f"Outlier high average order value ({val_str} vs average {mean_str}).",
                    "Identify key basket drivers, replicate top bundled offers and monitor high-value payment clearance.",
                )
            return (
                f"Panier moyen exceptionnellement élevé ({val_str} vs moyenne {mean_str}).",
                "Identifier les offres groupées motrices pour répliquer le modèle et sécuriser le recouvrement des gros montants.",
            )
        else:
            if language == "en":
                return (
                    f"Abnormal drop in basket size ({val_str} vs average {mean_str}).",
                    "Introduce relevant cross-selling suggestions at checkout and review discounting thresholds.",
                )
            return (
                f"Érosion anormale du panier moyen ({val_str} vs moyenne {mean_str}).",
                "Renforcer les suggestions de vente croisée (cross-selling) et réajuster les paliers de remises.",
            )

    # 8. LOGISTIQUE & TECHNIQUE : Stocks / Ruptures / Consommation
    if any(k in col_norm for k in ("stock", "inventaire", "conso", "energie", "kwh", "carburant")):
        if is_high:
            if language == "en":
                return (
                    f"Unusually high consumption level ({val_str} vs average {mean_str}).",
                    "Audit operational efficiency, inspect machinery for leakage/overload and optimize operating cycles.",
                )
            return (
                f"Surconsommation inhabituelle constatée ({val_str} vs moyenne {mean_str}).",
                "Auditer le rendement des équipements, rechercher d'éventuelles fuites ou surcharges et optimiser les plages de fonctionnement.",
            )
        else:
            if language == "en":
                return (
                    f"Critically low reserve or consumption level ({val_str} vs average {mean_str}).",
                    "Trigger replenishment orders before safety stock depletion and verify supply route continuity.",
                )
            return (
                f"Niveau anormalement bas de réserve ou consommation ({val_str} vs moyenne {mean_str}).",
                "Déclencher le réapprovisionnement avant rupture du stock de sécurité et contrôler les délais des transporteurs.",
            )

    # 9. DÉFAUT GÉNÉRIQUE INTELLIGENT (orienté gestion et décision)
    if is_high:
        if language == "en":
            return (
                f"Exceptional high level recorded on {label} ({val_str} vs average {mean_str}).",
                f"Assess operational capacity constraints and capitalize on growth factors driving {label} while monitoring resource strain.",
            )
        return (
            f"Niveau exceptionnellement haut constaté sur {label} ({val_str} vs moyenne {mean_str}).",
            f"Évaluer la charge opérationnelle induite par ce pic sur {label} et adapter les ressources nécessaires pour maintenir la qualité de service.",
        )
    else:
        if language == "en":
            return (
                f"Unusual downturn observed on {label} ({val_str} vs average {mean_str}).",
                f"Identify operational friction points causing this drop on {label} and deploy prompt corrective adjustments.",
            )
        return (
            f"Décrochage inhabituel constaté sur {label} ({val_str} vs moyenne {mean_str}).",
            f"Identifier les freins opérationnels à l'origine de ce repli sur {label} et engager les corrections de processus adaptées.",
        )

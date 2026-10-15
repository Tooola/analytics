# 🎤 Présentation du projet au DG — T-ola / Open Analytics AI

> **Ce document est votre script.** Il contient tout ce que vous devez DIRE, dans l'ordre,
> pour présenter le projet au Directeur Général — récit d'abord, preuve technique ensuite
> (vos interlocuteurs sont informaticiens : on ne leur simplifie pas la technique, on la
> *met en récit*).
>
> - 🗣️ = **phrase à dire telle quelle** (vous pouvez la lire)
> - 🎬 = **mise en scène** (ce que vous faites / ce que vous montrez)
> - 📎 = **secours** : chiffre ou explication à sortir si on vous creuse la question
>
> ⏱️ Durée totale : **12 à 15 minutes** (récit 4 min · démo 6 min · technique+valeur 4 min).
> Version courte de **5 minutes** : [§9](#9--version-5-minutes--si-le-dg-n-a-pas-le-temps).

---

## Sommaire

| § | Moment | Durée |
|---|--------|-------|
| 1 | [Ouverture — le récit](#1--ouverture--le-récit) | 2 min |
| 2 | [Le problème, en trois points](#2--le-problème-en-trois-points) | 1 min |
| 3 | [La réponse — ce que c'est](#3--la-réponse--ce-que-cest) | 1,5 min |
| 4 | [La démonstration — script pas-à-pas](#4--la-démonstration--script-pas-à-pas) | 6 min |
| 5 | [Comment c'est fait — la profondeur technique](#5--comment-cest-fait--la-profondeur-technique) | 2,5 min |
| 6 | [La sécurité](#6--la-sécurité) | 1 min |
| 7 | [La valeur métier](#7--la-valeur-métier) | 1 min |
| 8 | [Où on en est & feuille de route](#8--où-on-en-est--feuille-de-route) | 1 min |
| 9 | [Version 5 minutes](#9--version-5-minutes--si-le-dg-n-a-pas-le-temps) | 5 min |
| 10 | [Questions du DG — réponses prêtes](#10--questions-du-dg--réponses-prêtes) | — |
| 11 | [« Pourquoi cette méthode ? » — la réponse pour chaque analyse](#11--pourquoi-cette-méthode--la-réponse-pour-chaque-analyse) | — |
| 12 | [Annexes : glossaire & repères](#12--annexes--glossaire--repères) | — |

---

## Avant de commencer — les 4 règles

1. **On montre avant d'expliquer.** La démo (§4) fait plus de mal qu'un discours : lancez-la *tôt*.
2. **Un seul chiffre par idée.** Choisissez-le dans ce document, répétez-le, ne noyez pas.
3. **Le jargon attend le §5.** Jusque-là : « données », « corrélations », « IA ». Ensuite seulement : Pearson, IQR, JWT.
4. **Terminer par une demande.** Une présentation sans *ask* est un compte-rendu. Le vôtre est en §8.

🎬 **Mise en place** : dashboard local ouvert sur la page de login (`http://localhost:5173`),
onglet Swagger (`/docs`) prêt dans une seconde fenêtre, et la démo multi pré-chargée
(application `structure-finance-demo`, dataset `ventes-terrain`).

---

## 1️⃣ Ouverture — le récit

🗣️ **« Bonjour. Je vais vous présenter en quinze minutes ce que nous appelons le cerveau
analytique du groupe.**

**Aujourd'hui, chaque application que nous construisons — Farmtinz, et bientôt les
suivantes — produit des données tous les jours. Des milliers de lignes. Des ventes, des
achats, des relevés. Le paradoxe, c'est que plus nos applications produisent, et moins
personne n'a de recul. Chaque équipe refait son petit tableur, son petit rapport. Les
données sont partout ; la vision est nulle part.**

**Nous avons inversé la logique. Au lieu de reconstruire l'analyse dans chaque
application, nous l'avons mise dans une seule plateforme centrale. Une seule. Toutes nos
applications lui parlent, et elle répond en trois temps : voici ce qui se passe, voici ce
qui cloche, voici ce qu'il faut en penser. Avec l'aide de l'IA — mais une IA sage, qui ne
voit jamais vos données brutes.**

**Je vais vous le montrer en direct. »**

🎬 *Lancez la démo (§4) sans attendre. Le récit ci-dessus sert d'intro pendant que le
dashboard s'ouvre.*

---

## 2️⃣ Le problème, en trois points

🗣️ **« Le problème que nous résolvons tient en trois mots : silos, retard, coût. »**

| # | Le mot | Ce que ça veut dire | Ce que ça coûte |
|---|--------|--------------------|-----------------|
| 1 | **Silos** | Farmtinz a ses données, le CRM les siennes, la finance les siennes. Personne ne les regarde ensemble. | On prend des décisions sur **un quart** du tableau de bord. |
| 2 | **Retard** | Une anomalie — un pic de charge, une baisse de vente, une fuite — se voit dans le rapport du mois suivant. | La découverte arrive **après** la perte. |
| 3 | **Coût** | Chaque nouvelle analyse = un développement spécifique, à refaire pour chaque application. | Des semaines de dev pour des moyennes et des graphiques. |

🗣️ **« Nous avons décidé que ce métier-là serait fait une seule fois, pour toutes nos
applications, à jamais. »**

---

## 3️⃣ La réponse — ce que c'est

🗣️ **« T-ola — Open Analytics AI — est une plateforme d'analyse décisionnelle et
d'interpretation IA, réutilisable par n'importe quelle application du groupe. Une
application branche son flux de données, et obtient instantanément trois choses : »**

| Capacité | Ce qu'elle fait | L'exemple parlant |
|----------|----------------|-------------------|
| **Analyser** | Statistiques, tendances, prévisions sur n'importe quel tableau | *« Ventes +62,5 % en six mois, direction confirmée »* |
| **Détecter** | Anomalies (méthodes robustes, pas de règle arbitraire) | *« Ce montant dépasse tout ce que l'historique autorise »* |
| **Raconter** | L'IA transforme les chiffres en phrases de management | *« Les ventes et l'électricité montent ensemble : r = 0,95 »* |

🗣️ **« Et le tout tient en un seul appel API. Trois appels, en fait : créer son
application, déclarer son tableau de données, envoyer les lignes. Un développeur branch
Farmtinz dessus en moins de trente minutes — c'est écrit dans notre guide, et c'est
validé. »**

📎 **Chiffres à dire maintenant ou plus tard** :
- **Version `v1.0.0`** taguée — le projet est versionné et livrable.
- **140 tests automatisés** au vert (sécurité, isolation multi-tenant, non-régression).
- **26 endpoints** versionnés (`/api/v1`), documentation `api.md` + Swagger auto.
- **Analyse complète en < 1 seconde** sans IA, **~7 secondes** avec l'interprétation IA.

---

## 4️⃣ La démonstration — script pas-à-pas

> 🎬 À préparer : données de démo déjà en base (`structure-finance-demo`, datasets
> `ventes-terrain`, `achats-maison`, `electricite`). Sinon, le guide d'intégration §3-§5
> permet de les rejouer en 3 minutes.

### Étape 1 — La porte d'entrée : une connexion, pas un mot de passe dans un fichier

🎬 *Affichez la page de login, connectez-vous.*

🗣️ **« L'accès est par identifiants. La session dure douze heures, le jeton est signé —
c'est la même discipline que pour une banque en ligne. Les identifiants ne sont jamais
dans le code : ils sont injectés dans l'environnement de production. »**

### Étape 2 — Les applications : une clé par locataire

🎬 *Onglet Applications : montrez l'application, le bouton « régénérer la clé ».*

🗣️ **« Chaque application cliente possède sa propre clé API. Cette clé est **hashée** en
base : nous-mêmes ne pouvons pas la relire. Elle s'affiche une seule fois, à la création.
Si elle fuit, un clic la remplace — l'ancienne meurt immédiatement. Et surtout :
l'isolation est totale. La clé de Farmtinz ne verra **jamais** les données d'une autre
application. Si elle essaie, elle reçoit un « introuvable » — pas un « refusé » — pour ne
même pas révéler l'existence d'autrui. »**

### Étape 3 — L'analyse simple : des lignes brutes en verdict

🎬 *Onglet Analytics : lancez une analyse simple sur `ventes-terrain`
(6 mois, `summary`/`trend`/`anomaly`).*

🗣️ **« Je viens d'envoyer six lignes — deux colonnes, mois et montant. En moins d'une
seconde, la plateforme m'a dit : moyenne à 15 983, trajectoire haussière de +62,5 % sur
six périodes, aucune anomalie détectée. Et elle l'a écrit en clair : "Progression de
+62,5 % — trajectoire positive confirmée." Tout est historisé : chaque analyse laisse une
trace consultable, avec son statut et son résultat. »**

### Étape 4 — Le morceau de bravoure : l'analyse consolidée multi-datasets

🎬 *Activez le **mode multi**, cochez les datasets, clé de jointure `mois`, lancez avec IA.*

🗣️ **« Maintenant, la vraie démonstration. J'envoie **plusieurs tableaux en même temps** :
les ventes, et l'électricité. La plateforme fait trois choses d'un coup.**

**Premièrement : elle analyse chaque tableau pour lui-même.**

**Deuxièmement — et c'est nouveau — elle cherche les liens **entre** les tableaux.
En alignant les mois, elle calcule la corrélation entre les colonnes : elle trouve un
coefficient de 0,95 entre nos ventes et notre facture d'électricité. Traduction : quand
l'un monte, l'autre monte. Deux séries qui évoluent ensemble, mises en évidence sans
qu'un analyste ait touché un tableur.**

**Troisièmement : elle tranche. Un verdict : "positif". Avec une phrase écrite toute
seule : "2 jeux de données analysés en une seule passe, alignés sur mois. Tendance —
ventes : hausse, électricité : stable. Lien le plus fort : r = 0,95. Verdict : dynamique
globale positive."**

**Et sous le capot : l'IA de Groq a lu **tout** ça et rend un rapport de management —
conclusions, recommandations, plan d'action. En sept secondes. »**

🎬 *Montrez le panneau consolidé : verdict 🟢, tableau des liens, et le bloc IA affiché.*

🗣️ **« Point important pour la conformité : l'IA n'a jamais vu vos lignes. Elle ne
reçoit que des agrégats anonymisés — moyennes, pentes, nombres d'anomalies. La structure
de ce qu'on lui envoie est écrite dans le code et relisible en une minute. »**

### Étape 5 — L'historique : tout est tracé

🎬 *Onglet historique / liste des analyses.*

🗣️ **« Chaque analyse laisse une run horodatée, par jeu de données, avec son résultat
et ses insights. Rien ne se fait dans le noir. »**

🎬 *Transition :* 🗣️ **« Voilà ce que ça fait. Deux minutes maintenant sur ce que c'est,
techniquement. »**

---

## 5️⃣ Comment c'est fait — la profondeur technique

> 🗣️ **« Côté architecture, c'est volontairement classique et boring — c'est un
> compliment. »**

### L'architecture

```
Apps du groupe (Farmtinz, CRMTinz, …)          Dashboard React (JWT)
        │  X-API-Key                                  │  Bearer
        └──────────────┬──────────────────────────────┘
                       ▼
        API FastAPI (Python) — /api/v1 — 26 endpoints
        ├── Auth : clés API hashées + JWT dashboard + rate limiting
        ├── Moteur statistique (maison, sans dépendance lourde)
        ├── Moteur d'insights (règles métier déterministes)
        ├── Synthèse décisionnelle (multi-datasets)
        ├── IA — moteur débranchable (Groq par défaut, mock en secours)
        └── PostgreSQL (traces : applications, datasets, runs, insights)
```

| Brique | Choix | Pourquoi |
|--------|-------|----------|
| Backend | **FastAPI** + SQLAlchemy + Pydantic | Typage strict → les schémas sont la spécification |
| Frontend | **React** + Vite (dashboard unique) | Un seul front : l'admin et la BI au même endroit |
| Base | **PostgreSQL** | Les runs sont horodatées et interrogables |
| API | REST versionnée `/api/v1` | Contrat stable pour les équipes d'intégration |
| Tests | **140 tests pytest** au vert | Isolation multi-tenant, sécurité, régression |

### Le moteur statistique — des méthodes, pas des opinions

🗣️ **« Rien n'est arbitraire : chaque chiffre a une méthode derrière, connue et
explicable. »**

| Fonction | Méthode |
|----------|---------|
| Tendances | Régression sur périodes : direction, pente, % d'évolution |
| Anomalies | **Ensemble IQR + MAD + isolation forest** — trois méthodes qui votent, pour éviter les faux positifs d'une seule règle |
| Corrélations | **Pearson**, avec test de significativité : \|r\| ≥ 0,4 **et** p < 0,05 — on refuse les corrélations de hasard |
| Liens inter-datasets | Alignement sur clé de jointure (`mois`, `date`…), jointure extérieure, top 20 des liens |
| Synthèse | Règles explicites et hiérarchisées : `positif` < `équilibre` < `tension` < `surveiller` — **un verdict lisible, pas une boîte noire** |
| Prévisions | Projection sur les périodes suivantes (tendance linéaire) |

### L'IA — puissante, mais en laisse

- **Provider débranchable** : Groq en production (modèle `openai/gpt-oss-120b`), mock en
  secours, Gemini/Ollama compatibles. Si le provider tombe : **les statistiques sont
  toujours servies**, seule l'interprétation manque — dégradation gracieuse, jamais une
  erreur.
- **Privacy-first par conception** : l'objet envoyé au LLM (`AnalyticalContext`) ne
  contient que moyennes, pentes, anomalies et insights — **jamais une ligne brute**. C'est
  vérifiable dans le code, et **des tests le garantissent**.
- L'IA répond en structure JSON (conclusions, recommandations, plan d'action, risques,
  score de confiance) — pas un pavé de texte à relire.

### La qualité, en preuves

- **`v1.0.0`** taguée ; commits conventionnels ; historique lisible (`git log` = le récit
  du projet).
- **140/140 tests verts**, dont : fuite de clé, croisement de locataires, débordement de
  quotas, échec de provider IA, non-régression de l'endpoint historique.
- **Zéro secret en dur** — politique appliquée et **vérifiée par test**.
- **Un guide d'intégration** pour développeurs, dont chaque commande a été **exécutée en
  live** avant d'être écrite.

---

## 6️⃣ La sécurité

🗣️ **« Sur la sécurité, cinq verrous, tous testés : »**

| Verrou | Détail |
|--------|--------|
| 🔑 **Clés hashées** | Affichées une fois, jamais relisibles, régénérables/révocables en un clic |
| 🏘️ **Isolation stricte** | Ressource d'un autre locataire → `404`, jamais de confirmation d'existence |
| 🚫 **Zéro secret en dur** | Variables d'environnement uniquement, contrôle par test automatisé |
| 🧭 **Rate limiting** | Quotas par clé (20 analyses/min, 10 analyses multi/min, 5 logins/min) |
| 🔒 **RGPD / privacy-first** | L'IA ne reçoit que des agrégats anonymisés ; HTTPS partout ; purge possible par application |

---

## 7️⃣ La valeur métier

🗣️ **« Ce que la direction y gagne, en trois lignes : »**

| Pour la direction | Concrètement |
|-------------------|--------------|
| **Décider plus vite** | Un verdict en moins de dix secondes, au lieu du rapport du mois prochain |
| **Voir en 360°** | Les corrélations croisées révèlent ce qu'aucun rapport par application ne montre (ventes ↔ électricité, achat ↔ marge…) |
| **Gagner du dev** | Analyser une nouvelle application = **3 appels API**, pas un projet. Gain estimé à **−70 % de temps** sur les fonctionnalités analytics |
| **Sécuriser l'information** | Isolation par conception, clés révocables, IA sans données brutes |

---

## 8️⃣ Où on en est & feuille de route

🗣️ **« Le projet est en version 1.0.0, fonctionnel de bout en bout, avec sa démo, ses
tests et sa documentation. Ce qui reste à traiter est un chantier d'exploitation, pas de
conception. »**

**Fait (à cocher à voix haute) :**
- ✅ API complète versionnée + **guide d'intégration validé en live**
- ✅ Dashboard React unique avec **authentification JWT**
- ✅ Analyse consolidée **multi-datasets** : liens croisés + verdict + synthèse IA
- ✅ Politique **zéro secret** appliquée et testée
- ✅ **140 tests** verts ; tag **`v1.0.0`**

**Le plan sur les prochaines semaines :**

| Priorité | Action | Statut |
|----------|--------|--------|
| P0 | Synchroniser le dépôt (9 commits locaux en attente de push) | ⏳ En attente |
| P0 | Remettre la production Railway en route (panne de passerelle) | ⏳ Action infra |
| P0 | Resserrer le CORS en production (origines déclarées) | ⏳ À faire |
| P1 | Alerte automatique (email / webhook) sur anomalie critique | 📋 Prévu |
| P1 | Export PDF / Excel des rapports décisionnels | 📋 Prévu |
| P2 | Regroupement `group_by` (analyses par catégorie) | 📋 Prévu |
| P2 | **Connecteur pilote Farmtinz** (première application cliente réelle) | 📋 À prioriser |

🗣️ **« Ma demande à la direction est double : valider le redémissement en production de
notre infrastructure, et nous laisser enchaîner sur le connecteur Farmtinz — le pilote
qui prouvera le modèle sur une application réelle. »**

---

## 9️⃣ Version 5 minutes — si le DG n'a pas le temps

🗣️ **« Nous avons bâti le cerveau analytique du groupe : une plateforme unique qui
écoute toutes nos applications et répond en langage clair.**

**Le problème qu'elle règle : nos données sont en silos, nos rapports arrivent trop
tard, et chaque analyse coûte un développement.**

**La démonstration que vous venez de voir : six lignes envoyées, un verdict "positif"
en dix secondes, deux tableaux corrélés entre eux (ventes et électricité : r = 0,95), et
un rapport de management rédigé par l'IA — sans qu'elle ait jamais vu une donnée brute.**

**Le socle est sérieux : version 1.0.0, 140 tests, isolation multi-tenant stricte,
politique zéro secret, guide d'intégration prêt pour nos développeurs.**

**Ce que je demande : remettre notre production en route, et valider le connecteur
Farmtinz comme pilote. »**

---

## 🔟 Questions du DG — réponses prêtes

| La question | Votre réponse |
|-------------|---------------|
| **« Où sont mes données ? »** | Dans notre base PostgreSQL, chez nous. Vers l'IA partent **uniquement des statistiques anonymisées** — c'est écrit dans le code et couvert par des tests. |
| **« Et si l'IA tombe ? »** | Dégradation gracieuse : les statistiques, détections et verdicts continuent d'être servis ; seule l'interprétation de style manquant, et le dashboard l'affiche. Le provider se remplace en un fichier de configuration (Groq, Gemini, Ollama, mock). |
| **« Combien ça coûte ? »** | Aucune licence : code maison. Infrastructure = un serveur Railway + une clé Groq (offre gratuite à notre débit). Le coût réel est le temps de dev — déjà engagé. |
| **« Pourquoi pas directement dans Farmtinz ?** | Parce qu'on aurait à le refaire dans chaque application. Ici, la version, la sécurité et les méthodes sont écrites **une fois** ; Farmtinz n'a que trois appels à faire. |
| **« Quel effort pour brancher une nouvelle application ?** | Trois appels API : créer l'app, déclarer le schéma, envoyer les lignes. C'est dans un guide pas-à-pas ; on l'a validé en trente minutes sur une vraie application de test. |
| **« Quelle charge peut-il encaisser ?** | 10 000 lignes par appel, 10 tableaux par analyse consolidée, quotas par locataire (ex. 20 analyses/min) — tous réglables par variable d'environnement. L'API est sans état : on monte en puissance horizontalement. |
| **« Les corrélations, c'est fiable ?** | On n'affiche que des corrélations **significatives** : coefficient ≥ 0,4 **et** p < 0,05, sur au moins cinq points alignés. Le reste est rejeté par construction — pas d'histoire de corrélation de hasard. |
| **« L'IA peut-elle se tromper ?** | Oui — c'est pour ça qu'elle n'est jamais seule : chaque rapport IA est accompagné des chiffres bruts qui l'ont produit, d'un score de confiance, et le verdict de synthèse est **calculé par des règles explicites**, pas par l'IA. |
| **« Le code est-il propre ?** | 140 tests verts, historique git conventionnel, tag `v1.0.0`, documentation API générée et guide d'intégration dont chaque exemple a été exécuté en live avant publication. |
| **« Pourquoi une API et pas un logiciel ?** | Parce que nos produits sont des applications, pas des tableaux de bord. Une API s'intègre partout — React, mobile, Python — et le dashboard de direction est déjà fourni par-dessus. |
| **« On peut voir sans vous ?** | Oui : Swagger interactif sur `/docs`, guide d'intégration copier-coller, et la documentation technique dans le dépôt. |

---

## 11️⃣ « Pourquoi cette méthode ? » — la réponse pour chaque analyse

> 🗣️ **La question attendue, formulée autrement** : *« Pourquoi l'anomalie plutôt que… ? »*
> *« Pourquoi ce calcul ? »* *« D'où vient ce chiffre ? »*
> Voici la réponse pour **chacune** des six analyses — le rôle, la méthode réelle (celle du
> code, pas celle de la plaquette), et la phrase à dire. Si on vous enfonce : la **réplique**
> est sous chaque tableau.

### Le tableau d'ensemble (à retenir pour l'oral)

| Analyse | Son rôle en un trait | La méthode réelle | Pourquoi elle, en une phrase |
|---------|---------------------|-------------------|------------------------------|
| **summary** | L'état des lieux | count / moyenne / médiane / min / max / écart-type (pandas) | La base factuelle dont tout le reste se raconte — moyenne **et** médiane ensemble pour sentir les extrêmes |
| **trend** | La direction | Régression linéaire (moindres carrés, scipy) + R² + p-value | On ne dit « ça monte » que si c'est **statistiquement significatif**, pas une impression sur deux points |
| **anomaly** | Ce qui cloche | **Ensemble** : IQR + z-score modifié (MAD) + isolation forest, à la majorité | Une seule méthode a des angles morts ; trois méthodes qui **votent** tuent les fausses alertes |
| **correlation** | Les liens cachés | Pearson + seuils \|r\| ≥ 0,4 **et** p < 0,05 | Sans test de significativité, on trouve toujours une corrélation nulle part |
| **distribution** | La forme des données | Asymétrie, aplatissement, déciles + test de normalité (Shapiro-Wilk) | La moyenne suppose une symétrie — on vérifie qu'elle mérite d'être crue |
| **forecast** | La suite probable | Prolongement de la régression, 3 périodes, **intervalle** t-student | Une prévision sans marge d'erreur est un pari ; on livre un ordre de grandeur borné |

---

### 📊 summary — « Pourquoi des moyennes et des écart-types ? »

**Son rôle** : poser le socle factuel — *« voilà où on est »* — sur lequel toutes les
autres analyses construisent leur récit.

**Ce qui se passe vraiment** : sur chaque colonne numérique (telles que déclarées dans le
schéma — aucune inférence), le moteur calcule `count`, moyenne, médiane, min, max et
l'écart-type d'échantillon, arrondis à4 décimales. `std = 0` pour une seule valeur (pas
de dispersion à estimer).

🗣️ **À dire** : *« Le résumé, c'est l'état des lieux. Notez qu'on calcule la moyenne **et**
la médianensemble — parce que la moyenne ment dès qu'un extrême apparaît, et l'écart
entre les deux nous signale justement qu'il y en a un. L'écart-type donne la largeur :
c'est lui qui, plus loin, permettra de dire d'un chiffre s'il est hors norme. »*

🔎 **Si on insiste** (« un tableur fait ça ») : *« Oui — et c'est le but : c'est le métier le
plus banal, fait une fois, avec des colonnes typées et validées côté serveur, pour
n'importe quelle application. Ce qui change, c'est que ce socle alimente
automatiquement les détections suivantes. »*

---

### 📈 trend — « Pourquoi une régression et pas 'dernier moins premier' ? »

**Son rôle** : la direction — répondre à la question du manager *« est-ce que ça monte ? »*
avec une **preuve**, pas une impression.

**Ce qui se passe vraiment** : régression linéaire des moindres carrés (`scipy.stats.linregress`)
sur l'index de période, produisant la pente, le R² et la p-value. La direction `up`/`down`
n'est affirmée que si **p < 0,05 ET R² ≥ 0,25** (seuil anti-bruit codé en dur) ; sinon la
réponse est `stable`. Sous5 périodes, un repli honnête : variation > 1 % minimum. Le
`change_pct` vient de (premier → dernier).

🗣️ **À dire** : *« Si je vous disais 'les ventes ont monté de 62 %', je pourrais vous
mentir avec deux points de données au mauvais endroit. La régression, elle, utilise
toutes les périodes pour tracer la droite qui les représente, et surtout elle fournit une
p-value : on n'affirme 'hausse' que si le mouvement est statistiquement significatif —
moins de5 %de risque que ce soit du hasard — et si la tendance explique au moins25 %
de la variation. Tout le reste est classé 'stable'. C'est ce qui nous empêche de raconter
une histoire sur du bruit. »*

🔎 **Si on insiste** (« pourquoi pas une moyenne mobile ? ») : *« Une moyenne mobile
lisse, c'est vrai — mais elle ne fournit aucun test de significativité. Nous avons choisi
la régression pour la p-value, qui est notre garde-fou. »*

---

### 🚨 anomaly — « Pourquoi trois méthodes au lieu d'une ? »

**Son rôle** : la fuite de valeur — alerter **avant** que l'anormal ne coûte cher.

**Ce qui se passe vraiment** : pour chaque colonne (≥4 points), **trois** détecteurs
travaillent : IQR (hors `[Q1 −1,5×IQR ; Q3 +1,5×IQR]`), z-score **modifié** sur MAD
(`0,6745·|x − médiane|/MAD > 3,5` — la version robuste du z-score), et isolation forest
(scikit-learn, contamination5 %, **`random_state=42`** → reproductible), activée à partir
de15 points. **Vote** : une alerte ne remonte que si **≥2 méthodes sont d'accord** ; la
`confidence_score` est exactement `votes / méthodes exécutées`. Chaque alerte liste ses
méthodes (`detected_by`) et son z-score.

🗣️ **À dire** : *« Nous ne faisons pas confiance à une seule méthode de détection, parce
qu'elles ont toutes un angle mort : l'IQR suppose une répartition à peu près symétrique ;
l'isolation forest a besoin de volume ; et le z-score classique — la moyenne et
l'écart-type — se laisse précisément déformer par les extrêmes qu'il est censé trouver,
c'est pourquoi on le calcule sur la médiane et le MAD, robustes par nature. Alors on fait
voter les trois : une alerte n'existe que si au moins deux méthodes signent dessus, et la
confiance affichée est le ratio de votes. Résultat : les fausses alertes meurent en
coulisse. Une direction qui se trompe une fois paie en crédibilité — nous, on préfère le
silence à l'alerte qui crie au loup. »*

🔎 **Si on insiste** (« pourquoi pas un simple z-score ? ») : *« Parce qu'il suppose la
cloche et qu'il est non robuste — et qu'il reste univarié. Le vote combine le simple
(médianes) et le sophistiqué (forêt isole les profils bizarres) : c'est la raison pour
laquelle notre détection marche aussi sur six lignes que sur dix mille. »*

---

### 🔗 correlation — « Pourquoi seuiller les corrélations ? »

**Son rôle** : révéler ce qu'aucun rapport par application ne montre — les colonnes qui
**bougent ensemble**.

**Ce qui se passe vraiment** : toutes les paires de colonnes numériques (≥2), calcul de
Pearson (`scipy.stats.pearsonr`) sur les lignes valides, **≥5 points**. N'affiche **que**
les liens avec `|r| ≥ 0,4` **et** `p < 0,05`. Étiquette : `strong` si `|r| ≥ 0,7`, sinon
`moderate`.

🗣️ **À dire** : *« Pearson est la mesure canonique du co-mouvement — et scipy nous donne
sa p-value avec. Le vrai choix, ici, n'est pas la formule : c'est le refus. Nous
n'affichons un lien que s'il est à la fois substantiel — coefficient d'au moins0,4 — et
significativement — moins de5 %de risque que ce soit un hasard. Sans ce double filtre,
avec assez de colonnes, on trouve toujours une corrélation par pure chance — et une
corrélation de hasard est pire qu'aucune information. »*

🔎 **Si on insiste** (« et les relations non linéaires ? ») : *« Pearson capte le linéaire,
notre cas d'usage. Pour les relations monotones non linéaires, Spearman est la suite
logique — c'est identifié en feuille de route. Nous préférons publier une méthode tenue
que six approximées. »*

---

### 📐 distribution — « À quoi ça sert concrètement ? »

**Son rôle** : le test de lucidité des autres chiffres — est-ce que la moyenne mérite
d'être crue telle quelle ?

**Ce qui se passe vraiment** : par colonne (≥3 points) : asymétrie (`skewness`,0=symétrique),
aplatissement (`kurtosis`,0=loi normale, positif=queues épaisses = extrêmes fréquents),
déciles `p10/p25/p50/p75/p90`, et test de normalité **Shapiro-Wilk** (entre3et5000points,
au-delà : `null` plutôt qu'un chiffre de comptoir).

🗣️ **À dire** : *« La moyenne est un raccourci qui suppose une certaine symétrie. La
distribution vérifie cette hypothèse : on mesure l'asymétrie, l'épaisseur des queues, les
déciles — et on teste même la normalité avec Shapiro-Wilk. Deux exemples qui parlent :
deux marchés, l'un gros et l'autre petit — la moyenne ne correspond à aucun des deux, et
les déciles le montrent ; des données à queues épaisses signifient que les extrêmes sont
fréquents, donc que la moyenne sous-estime le risque. »*

🔎 **Si on insiste** (« pourquoi un test de normalité ? ») : *« Parce que la moitié des
statistiques que l'on cite part en coulisse d'une hypothèse de normalité. Nous, on
l'écrit noir sur blanc — et quand elle échoue, on s'abstient plutôt que de mentir :
Shapiro-Wilk est borné à5000points, au-delà le champ est `null`, volontairement. »*

---

### 🔮 forecast — « Vous pouvez vraiment prédire ? »

**Son rôle** : la suite probable — un **ordre de grandeur borné** pour budgétiser et
arbitrer, pas une boule de cristal.

**Ce qui se passe vraiment** : prolongement de la droite de régression sur **3 périodes**
(horizon court par défaut), avec **intervalle de prédiction** : marge `t-critique(0,975;
n−2) · σ · √(1 +1/n + (x₀−x̄)²/Sxx)`, où σ est l'écart-type des résidus — et non
`linregress.stderr`, qui mesure l'erreur de la **pente**. Le quantile `t` de Student
(plutôt que `1,96`) évite de sous-estimer l'intervalle sur petits échantillons. L'intervalle
s'élargit mécaniquement avec l'horizon.

🗣️ **À dire** : *« On prolonge la tendance sur trois périodes — court, exprès : au-delà,
l'incertitude explose et la prévision devient un slogan. Et surtout : nous ne livrons
jamais un chiffre nu, toujours un intervalle. Cet intervalle est calculé sur les résidus
avec la loi de Student, et il s'élargit quand on s'éloigne — ce qui est la définition
même de l'honnêteté d'une prévision. Si vous devez budgéter, vous prenez le milieu ;
si vous devez parer au risque, vous prenez les bornes. »*

🔎 **Si on insiste** (« et si la tendance casse ? ») : *« Exactement — et c'est pour ça
que la prévision n'est jamais donnée seule : elle arrive avec le verdict, les anomalies
et l'IA qui commentent le contexte. Une régression décrit la trajectoire, pas l'avenir du
monde. »*

---

### 🧩 La couche consolidée (multi) — « Pourquoi un verdict par règles, pas par IA ? »

**Son rôle** : trancher sur **plusieurs** tableaux à la fois — liens croisés + verdict.

**Ce qui se passe vraiment** : alignement des datasets sur la `join_key` (jointure
extérieure), mêmes seuils de Pearson, top20 des liens. La synthèse classe la direction
dominante par jeu, détecte les divergences, collecte les risques (anomalies) et produit un
verdict par **hiérarchie explicite** : `surveiller` (un risque existe) > `tension`
(divergence ou négatif) > `équilibre` (majorité stable) > `positif`.

🗣️ **À dire** : *« Deux choix méritent d'être expliqués. Premierement : la clé de
jointure — mois, date — est **demandée**, jamais devinée. Aligner deux séries est une
décision métier ; laisser la machine chercher des liens partout, c'est fabriquer des
corrélations de hasard. Deuxièmement : le verdict n'est pas une opinion d'IA. C'est une
hiérarchie de règles écrites — un risque l'emporte sur une divergence, qui l'emporte sur
une tendance négative. L'IA **raconte**, les règles **tranche** — c'est ce qui rend la
décision reproductible, auditable, et défendable devant un client ou un commissaire aux
comptes. »*

🔎 **Si on insiste** (« l'IA peut-elle donner un autre verdict ? ») : *« Non : elle ne reçoit
pas le verdict en entrée, elle le commente. Si son avis diverge, les chiffres qui l'ont
produit sont à côté dans la même réponse — chacun vérifie. »*

---

### 🎯 La phrase de synthèse (si vous ne retenez qu'une chose)

🗣️ *« Derrière chaque analyse, il y a une méthode choisie pour une raison explicitable :
la régression parce qu'elle teste sa propre significance, l'ensemble de détection parce
qu'une seule méthode a un angle mort, le seuillage parce que le hasard fabrique des
corrélations, l'intervalle de prévision parce qu'un chiffre nu est un pari. Rien n'est
découvert au hasard — et tout est relisible dans le code. »*

---

## 12️⃣ Annexes — glossaire & repères

### Glossaire en un trait (si un mot bloque)

| Terme | En un trait |
|-------|-------------|
| **Dataset** | Un tableau déclaré : ses colonnes, leurs types, ses règles |
| **Clé de jointure** (`join_key`) | La colonne commune qui aligne deux tableaux (`mois`, `date`…) |
| **Corrélation (r)** | De -1 à +1 : à quel point deux séries bougent ensemble. 0,95 = presque à l'unisson |
| **p-value** | La probabilité que ce lien soit un pur hasard. On exige < 0,05 (moins de 5 chances sur 100) |
| **IQR / MAD** | Deux méthodes statistiques robustes pour repérer l'aberrant — utilisées ensemble avec l'isolation forest |
| **JWT** | Jeton de session signé, à durée limitée (12 h ici) |
| **Rate limiting** | Plafond d'appels par fenêtre glissante, par locataire |
| **Privacy-first** | Par conception, l'IA reçoit des agrégats — jamais des données brutes |

### Trois chiffres à retenir pour l'oral

1. **`v1.0.0`** — le projet est versionné, livrable.
2. **140 tests** — la qualité est mesurée, pas alléguée.
3. **`r = 0,95`** — la démo parle d'elle-même : deux tableaux, un lien trouvé en une passe.

### Où regarder dans le dépôt

| Besoin | Fichier |
|--------|---------|
| Référence API exhaustive | `project/docs/api.md` |
| Guide d'intégration copier-coller | `project/docs/GUIDE_INTEGRATION_DEV.md` |
| Architecture technique | `project/docs/architecture.md` |
| Déploiement Railway + kit collègues | `project/docs/RAILWAY_ET_KIT_COLLEGUES.md` |
| Historique du projet | `git log --oneline` |

---

> 🎯 **Rappel final** : une démo réussie ne se termine pas par « avez-vous des questions »
> mais par **« ma demande est la suivante »** (§8). Bonne présentation.

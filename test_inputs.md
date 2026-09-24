# Données et Valeurs à Copier/Coller Directement dans vos Champs de Test

Voici des valeurs prêtes à l'emploi triées par type de champ pour vos tests manuels ou automatisés.

---

## 1. Utilisateurs & Authentification

| Champ | Valeur à copier / coller |
| :--- | :--- |
| **Email Valide (User 1)** | `alice.dupont@example.com` |
| **Email Valide (User 2)** | `jean.martin@example.com` |
| **Email Valide (Admin)** | `admin.analytics@test.com` |
| **Email avec caractères spéciaux** | `user+test.analytics@sub.domain.co.fr` |
| **Mot de passe fort** | `P@ssw0rd2026!SecuRe` |
| **Mot de passe simple** | `Test1234!` |
| **Nom complet** | `Jean-Pierre D'Arcy-Lévêque` |
| **Prénom** | `Élodie` |
| **Nom** | `Martin` |

---

## 2. IDs & Identifiants Uniques (UUID, Slugs, Keys)

| Champ | Valeur à copier / coller |
| :--- | :--- |
| **UUID v4** | `f47ac10b-58cc-4372-a567-0e02b2c3d479` |
| **ID Utilisateur (String)** | `usr_89234190` |
| **ID Session** | `sess_99382104` |
| **ID Evénement** | `evt_77120394` |
| **API Key fictive** | `sk_test_51MzQ92eXyzABC1234567890987654321` |
| **Token Bearer JWT fictif** | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c` |

---

## 3. URLs, Domaines & IPs

| Champ | Valeur à copier / coller |
| :--- | :--- |
| **URL HTTPS simple** | `https://analytics.example.com/dashboard` |
| **URL avec paramètres Query** | `https://analytics.example.com/events?filter=page_view&range=7d&sort=desc` |
| **URL Webhook** | `https://api.example.com/v1/webhooks/receive` |
| **Adresse IPv4** | `192.168.1.45` |
| **Adresse IPv4 Publique** | `82.165.197.1` |
| **User Agent Desktop** | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36` |
| **User Agent Mobile** | `Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1` |

---

## 4. Dates & Timestamps

| Format | Valeur à copier / coller |
| :--- | :--- |
| **ISO 8601 UTC** | `2026-09-24T11:20:00Z` |
| **Date seulement (YYYY-MM-DD)** | `2026-09-24` |
| **Date FR (DD/MM/YYYY)** | `24/09/2026` |
| **Timestamp Unix (secondes)** | `1790248800` |
| **Timestamp Unix (ms)** | `1790248800000` |
| **Plage de dates (Début)** | `2026-09-01T00:00:00Z` |
| **Plage de dates (Fin)** | `2026-09-24T23:59:59Z` |

---

## 5. Payloads JSON & Objets Evénements

### Payload d'Événement Analytics (à coller dans une zone de texte JSON)
```json
{
  "event_type": "button_click",
  "user_id": "usr_89234190",
  "session_id": "sess_99382104",
  "page_url": "https://analytics.example.com/pricing",
  "timestamp": "2026-09-24T11:20:00Z",
  "properties": {
    "button_id": "subscribe_pro_annual",
    "currency": "EUR",
    "amount": 199.99,
    "discount_code": "WELCOME2026"
  }
}
```

### Payload Filtre Analytics
```json
{
  "date_range": {
    "start": "2026-09-01",
    "end": "2026-09-24"
  },
  "metrics": ["page_views", "unique_visitors", "bounce_rate"],
  "group_by": ["country", "device_type"],
  "limit": 50
}
```

---

## 6. Cas Limites (Edge Cases & Validation)

| Type de Test | Valeur à copier / coller |
| :--- | :--- |
| **Texte Long / Paragraph (Lorem Ipsum)** | `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.` |
| **Inject HTML / XSS Test** | `<script>alert('XSS')</script>` |
| **Injection SQL Test** | `' OR '1'='1` |
| **Caractères Spéciaux & Emojis** | `François & Cécile 🚀📊 (Test %$#@! & <>)` |
| **Nombre Décimal (Prix)** | `1499.99` |
| **Grand Nombre (Analytics)** | `999999999` |
| **Zéro / Vide** | `0` |

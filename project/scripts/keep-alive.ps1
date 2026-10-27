<#
.SYNOPSIS
    Keep-Alive — ping répété de /api/v1/health pour empêcher le cold start.

.DESCRIPTION
    La grille gratuite Render met le service en veille après ~15 min sans
    trafic (prochain appel : 30-60 s de réveil). Un ping toutes les 10 min
    réinitialise le timer d'inactivité — l'instance reste chaude.

    Ce script sert à être exécuté :
      1) soit en boucle dans un terminal (par défaut),
      2) soit EN UNE SEULE FOIS via l'ordonnanceur Windows (schTASKS),
         qui se charge lui-même de la récurrence.

.EXEMPLE (ordonnanceur — toutes les 10 min, sans ouvrir de fenêtre) :
    schtasks /create /tn "T-ola Keep-Alive" /sc minute /mo 10 /tr ^
      "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%CD%\keep-alive.ps1\" -Url https://open-analytics-ai-backend.onrender.com -Once"

.EXEMPLE (terminal, en boucle) :
    .\keep-alive.ps1 -Url https://open-analytics-ai-backend.onrender.com

    Alternative sans rien installer : le workflow GitHub Actions
    `.github/workflows/keep-alive.yml` (ping automatique toutes les 10 min
    depuis GitHub, indépendant de votre machine). UptimeRobot (gratuit,
    checks toutes les 5 min) fait aussi l'affaire.
#>
param(
    # URL de base du backend (Render : sans /api/v1/health à la fin).
    [string]$Url = "https://open-analytics-ai-backend.onrender.com",
    # Minutes entre deux pings en mode boucle.
    [int]$IntervalMinutes = 10,
    # Un seul ping puis sortie (usage : ordonnanceur Windows).
    [switch]$Once
)

function Ping-Backend {
    $stamp = Get-Date -Format "HH:mm:ss"
    try {
        # --TimeoutSec : le premier ping peut attendre le réveil (~60 s).
        $r = Invoke-WebRequest -Uri "$Url/api/v1/health" -UseBasicParsing -TimeoutSec 90
        Write-Host "[$stamp] HTTP $($r.StatusCode) —OK ($Url)"
    } catch {
        $code = $null
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        if ($code) {
            Write-Host "[$stamp] HTTP $code —service réveillé mais non sain (déploiement ?)" -ForegroundColor Yellow
        } else {
            Write-Host "[$stamp] ECHEC — $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Ping-Backend
if ($Once) { exit 0 }

Write-Host "Ping toutes les $IntervalMinutes min — Ctrl+C pour arrêter."
while ($true) {
    Start-Sleep -Seconds ($IntervalMinutes * 60)
    Ping-Backend
}

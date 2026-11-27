import React, { useState } from 'react';
import { Code2, Copy, Check, Terminal, ExternalLink } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';

export default function ApiSnippetModal({ isOpen, onClose, endpoint = '/api/v1/analyze', samplePayload = null, apiKey = 'VOTRE_API_KEY' }) {
  const { language } = useLanguage();
  const isEn = language === 'en';
  const [selectedLang, setSelectedLang] = useState('curl');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const baseUrl = window.location.origin.includes('5173') ? 'http://127.0.0.1:8000' : window.location.origin;
  const fullUrl = `${baseUrl}${endpoint}`;

  const payloadJson = samplePayload 
    ? JSON.stringify(samplePayload, null, 2)
    : JSON.stringify({
        application: "votre-app-slug",
        dataset: "votre-dataset-slug",
        analysis: ["summary", "trend", "anomaly", "forecast"],
        include_ai: true,
        language: isEn ? "en" : "fr",
        data: [
          { "date": "2026-01-01", "valeur": 1250 },
          { "date": "2026-02-01", "valeur": 1420 },
          { "date": "2026-03-01", "valeur": 1680 }
        ]
      }, null, 2);

  const snippets = {
    curl: `curl -X POST "${fullUrl}" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: ${apiKey}" \\
  -d '${payloadJson.replace(/'/g, "'\\''")}'`,

    python: `import requests

url = "${fullUrl}"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "${apiKey}"
}
payload = ${payloadJson}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print("Status:", response.status_code)
print("Insights:", len(data.get("insights", [])))
if data.get("ai_interpretation"):
    print("AI Summary:", data["ai_interpretation"])`,

    javascript: `// JavaScript / Node.js (fetch)
const url = "${fullUrl}";
const payload = ${payloadJson};

async function runAnalysis() {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "${apiKey}"
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  console.log("Insights:", data.insights);
  if (data.ai_interpretation) {
    console.log("AI Summary:", data.ai_interpretation);
  }
}

runAnalysis();`,

    php: `<?php
// PHP cURL
$url = "${fullUrl}";
$apiKey = "${apiKey}";
$payload = json_encode(${payloadJson});

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: ' . $apiKey
]);

$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);
print_r($data['insights'] ?? []);
?>`
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(snippets[selectedLang]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const languages = [
    { id: 'curl', label: 'cURL' },
    { id: 'python', label: 'Python' },
    { id: 'javascript', label: 'Node / JS' },
    { id: 'php', label: 'PHP' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-2xl w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden transition-all flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/30">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800/80 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Terminal className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                {isEn ? 'Developer API Integration' : 'Intégration API Développeur'}
              </h3>
              <p className="text-[11px] text-slate-400">
                {isEn ? 'Ready-to-use snippets for your backend' : 'Extraits prêts à l’emploi pour votre application'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 px-2 py-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Lang Selector Tabs */}
        <div className="px-6 py-2 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-100/50 dark:bg-slate-950/50">
          <div className="flex items-center gap-1">
            {languages.map((l) => (
              <button
                key={l.id}
                onClick={() => setSelectedLang(l.id)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  selectedLang === l.id
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-slate-800'
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5 text-slate-400" />}
            <span>{copied ? (isEn ? 'Copied!' : 'Copié !') : (isEn ? 'Copy' : 'Copier')}</span>
          </button>
        </div>

        {/* Code View */}
        <div className="p-4 flex-1 overflow-auto bg-slate-950 text-slate-100 font-mono text-xs leading-relaxed">
          <pre className="whitespace-pre-wrap selection:bg-indigo-500 selection:text-white">
            {snippets[selectedLang]}
          </pre>
        </div>

        {/* Footer info */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950 text-[11px] text-slate-400">
          <span>
            {isEn ? 'Support language header:' : 'Support multi-langue:'}{' '}
            <code className="text-indigo-400">language: "en" | "fr"</code>
          </span>
          <span className="text-slate-500 font-sans">
            Auth: Header <code className="text-slate-300">X-API-Key</code>
          </span>
        </div>
      </div>
    </div>
  );
}

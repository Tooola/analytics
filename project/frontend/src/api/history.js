/**
 * Local analysis history — localStorage-backed, newest first.
 *
 * The API persists per-dataset runs, but the consolidated multi pass
 * (synthesis + cross links + the AI verdict on the whole picture) lives
 * only in the response: this module keeps every COMPLETE report on the
 * client so leaving the page never loses an analysis. Capped at the 50
 * latest runs (oldest pruned); a storage failure never breaks a run.
 */
const KEY = 'oak_history';
const MAX_ENTRIES = 50;

export function listHistory() {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function write(list) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    // Quota exceeded: keep the most recent half and retry once.
    try {
      localStorage.setItem(
        KEY,
        JSON.stringify(list.slice(0, Math.floor(MAX_ENTRIES / 2)))
      );
    } catch {
      /* a lost history entry must never break the run itself */
    }
  }
}

/**
 * Persist one completed run. Entry shape:
 * { id, savedAt, kind: 'quick'|'single'|'multi', title, app, datasets, rows,
 *   analyses, aiStatus, verdict?, groupBy?, joinKey?,
 *   report?, payloads? }  — `res` replaces `report` for multi.
 */
export function saveHistory(entry) {
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const list = [{ ...entry, id, savedAt: Date.now() }, ...listHistory()];
  write(list.slice(0, MAX_ENTRIES));
  return id;
}

export function deleteHistoryEntry(id) {
  write(listHistory().filter((e) => e.id !== id));
}

export function clearHistory() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
}

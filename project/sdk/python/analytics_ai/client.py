"""Open Analytics AI — Lightweight Python Client."""

from __future__ import annotations

import json
from typing import Any
import urllib.error
import urllib.request


class AnalyticsError(Exception):
    """Raised when an API call fails."""

    def __init__(self, message: str, status_code: int | None = None, response_body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AnalyticsClient:
    """Python Client for Open Analytics AI API.

    Simple, zero-dependency client that communicates directly with
    an Open Analytics AI server.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        path: str,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
        use_api_key: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "OpenAnalyticsAI-PythonSDK/0.1.0",
        }
        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key

        data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                if not resp_bytes:
                    return {}
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = None
            try:
                err_body = json.loads(exc.read().decode("utf-8"))
            except Exception:
                pass
            msg = f"HTTP {exc.code}: {exc.reason}"
            if isinstance(err_body, dict) and "detail" in err_body:
                msg = f"HTTP {exc.code}: {err_body['detail']}"
            raise AnalyticsError(msg, status_code=exc.code, response_body=err_body) from exc
        except urllib.error.URLError as exc:
            raise AnalyticsError(f"Connection error to {self.base_url}: {exc.reason}") from exc

    def health(self) -> dict[str, Any]:
        """Check API health status."""
        return self._request("/api/v1/health", method="GET", use_api_key=False)

    def quick_analyze(
        self,
        data: list[dict[str, Any]],
        analysis: list[str] = ["auto"],
        include_ai: bool = True,
        label: str = "quick-test",
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Run instant analysis on raw JSON rows without prior registration."""
        payload: dict[str, Any] = {
            "data": data,
            "analysis": analysis,
            "include_ai": include_ai,
            "label": label,
        }
        if group_by:
            payload["group_by"] = group_by
        return self._request("/api/v1/analyze/quick", method="POST", payload=payload, use_api_key=False)

    def analyze(
        self,
        application: str,
        dataset: str,
        data: list[dict[str, Any]],
        analysis: list[str] = ["auto"],
        include_ai: bool = True,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Submit data to a registered application and dataset.

        Requires self.api_key to be set.
        """
        if not self.api_key:
            raise AnalyticsError("api_key is required for analyze(). Pass api_key to AnalyticsClient.")
        payload: dict[str, Any] = {
            "application": application,
            "dataset": dataset,
            "data": data,
            "analysis": analysis,
            "include_ai": include_ai,
        }
        if group_by:
            payload["group_by"] = group_by
        return self._request("/api/v1/analyze", method="POST", payload=payload, use_api_key=True)

    def analyze_multi(
        self,
        application: str,
        datasets: list[str],
        payloads: dict[str, list[dict[str, Any]]],
        join_key: str | None = None,
        analysis: list[str] = ["auto"],
        include_ai: bool = True,
        group_by: str | None = None,
    ) -> dict[str, Any]:
        """Analyze multiple datasets in one single consolidated pass."""
        if not self.api_key:
            raise AnalyticsError("api_key is required for analyze_multi().")
        payload: dict[str, Any] = {
            "application": application,
            "datasets": datasets,
            "payloads": payloads,
            "analysis": analysis,
            "include_ai": include_ai,
        }
        if join_key:
            payload["join_key"] = join_key
        if group_by:
            payload["group_by"] = group_by
        return self._request("/api/v1/analyze/multi", method="POST", payload=payload, use_api_key=True)

    def compare(
        self,
        period_a: dict[str, Any] | list[dict[str, Any]],
        period_b: dict[str, Any] | list[dict[str, Any]],
        period_a_label: str = "Période A",
        period_b_label: str = "Période B",
        label: str = "comparatif-temporel",
        include_ai: bool = True,
    ) -> dict[str, Any]:
        """Compare two periods (Period A vs Period B).

        Produces:
        - What improved (Ce qui s'est amélioré)
        - What degraded (Ce qui s'est dégradé)
        - New points of attention (Points de vigilance)
        """
        # Normalize period inputs
        if isinstance(period_a, list):
            norm_a = {"label": period_a_label, "data": period_a}
        elif isinstance(period_a, dict) and "data" in period_a:
            norm_a = period_a
        else:
            norm_a = {"label": period_a_label, "data": [period_a]}

        if isinstance(period_b, list):
            norm_b = {"label": period_b_label, "data": period_b}
        elif isinstance(period_b, dict) and "data" in period_b:
            norm_b = period_b
        else:
            norm_b = {"label": period_b_label, "data": [period_b]}

        payload = {
            "period_a": norm_a,
            "period_b": norm_b,
            "label": label,
            "include_ai": include_ai,
        }
        return self._request("/api/v1/analyze/quick/compare", method="POST", payload=payload, use_api_key=False)

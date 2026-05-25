from __future__ import annotations

import html
import json
import os
import sys
import tempfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote_plus, urlparse

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

RUNTIME_DIR = Path(tempfile.gettempdir()) / "ti_aggregator" if os.getenv("VERCEL") else ROOT_DIR
os.environ.setdefault("TI_DATA_DIR", str(RUNTIME_DIR / "data"))

from main import run_pipeline  # noqa: E402

OUTPUT_DIR = RUNTIME_DIR / "outputs"
UPLOAD_DIR = RUNTIME_DIR / "uploads"
DATA_DIR = RUNTIME_DIR / "data"
LAST_RUN_FILE = OUTPUT_DIR / "last_run.json"
RUN_STATUS_FILE = OUTPUT_DIR / "run_status.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_and_persist(trigger: str, config_path: str) -> None:
    started_at = datetime.now().isoformat(timespec="seconds")
    try:
        result = run_pipeline(config_path, str(OUTPUT_DIR))
        _save_json(LAST_RUN_FILE, result)
        _save_json(
            RUN_STATUS_FILE,
            {
                "last_run": started_at,
                "trigger": trigger,
                "status": "ok",
                "feeds_processed": len(result.get("feed_stats", [])),
            },
        )
    except Exception as exc:
        _save_json(
            RUN_STATUS_FILE,
            {
                "last_run": started_at,
                "trigger": trigger,
                "status": "failed",
                "error": str(exc),
            },
        )


def _safe_filename(name: str) -> str:
    base = os.path.basename(name or "uploaded_feed.txt")
    safe = "".join(ch for ch in base if ch.isalnum() or ch in {"-", "_", "."})
    return safe or "uploaded_feed.txt"


def _build_custom_config(file_path: Path, fmt: str) -> Path:
    feeds = []
    feeds.append(
        {
            "name": f"uploaded_{file_path.stem}",
            "source_type": "file",
            "location": str(file_path),
            "format": fmt,
            "category": "uploaded",
        }
    )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    config_path = UPLOAD_DIR / "custom_feeds.json"
    config_path.write_text(json.dumps(feeds, indent=2), encoding="utf-8")
    return config_path


def _parse_multipart_form(content_type: str, body: bytes):
    fields = {}
    files = {}
    if "boundary=" not in content_type:
        return fields, files

    boundary = content_type.split("boundary=", 1)[1].strip().strip('"')
    marker = ("--" + boundary).encode("utf-8")

    for part in body.split(marker):
        part = part.strip()
        if not part or part == b"--" or b"\r\n\r\n" not in part:
            continue

        header_blob, value_blob = part.split(b"\r\n\r\n", 1)
        value = value_blob.rstrip(b"\r\n")
        headers = header_blob.decode("utf-8", errors="ignore").split("\r\n")
        disposition = next((h for h in headers if h.lower().startswith("content-disposition:")), "")
        if not disposition:
            continue

        params = {}
        for chunk in disposition.split(";")[1:]:
            if "=" in chunk:
                key, raw_value = chunk.strip().split("=", 1)
                params[key.strip().lower()] = raw_value.strip().strip('"')

        name = params.get("name")
        filename = params.get("filename")
        if not name:
            continue
        if filename:
            files[name] = (filename, value)
        else:
            fields[name] = value.decode("utf-8", errors="ignore")

    return fields, files


def _parse_post_form(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    body = handler.rfile.read(length) if length > 0 else b""
    content_type = (handler.headers.get("Content-Type") or "").lower()

    if content_type.startswith("multipart/form-data"):
        return _parse_multipart_form(content_type, body)
    if content_type.startswith("application/x-www-form-urlencoded"):
        parsed = parse_qs(body.decode("utf-8", errors="ignore"), keep_blank_values=True)
        return ({key: unquote_plus(values[0]) for key, values in parsed.items() if values}, {})
    return {}, {}


def _download_path(filename: str) -> Path | None:
    safe_name = os.path.basename(filename)
    candidates = [OUTPUT_DIR / safe_name, DATA_DIR / safe_name]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _output_links(outputs: dict[str, str]) -> str:
    links = []
    seen_names = set()
    for key, path in outputs.items():
        file_path = Path(path)
        if file_path.exists():
            links.append(f"<li><a href='/download?file={html.escape(file_path.name)}'>{html.escape(key)}</a></li>")
            seen_names.add(file_path.name)

    for file_path in sorted(OUTPUT_DIR.glob("*")):
        if file_path.is_file() and file_path.name not in seen_names:
            links.append(f"<li><a href='/download?file={html.escape(file_path.name)}'>{html.escape(file_path.stem)}</a></li>")
            seen_names.add(file_path.name)

    db_file = DATA_DIR / "ti_aggregator.db"
    if db_file.exists():
        links.append("<li><a href='/download?file=ti_aggregator.db'>normalized_ioc_database</a></li>")

    return "".join(links) or "<li>No output files yet</li>"


def _html_page(content: str) -> bytes:
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Threat Intelligence Aggregator</title>
  <style>
    :root {{ --bg:#101214; --panel:#181c20; --text:#eef2f6; --muted:#aab4bf; --border:#2a3038; --accent:#5dd3b3; --danger:#f87171; }}
    body.light {{ --bg:#f6f7f9; --panel:#ffffff; --text:#17202a; --muted:#5b6673; --border:#d8dee6; --accent:#0f766e; --danger:#dc2626; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Segoe UI,Arial,sans-serif; background:var(--bg); color:var(--text); }}
    .nav {{ border-bottom:1px solid var(--border); background:var(--panel); position:sticky; top:0; z-index:10; }}
    .nav-inner {{ max-width:1160px; margin:0 auto; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; gap:12px; }}
    .wrap {{ max-width:1160px; margin:0 auto; padding:18px; }}
    .nav a,.icon-btn {{ color:var(--text); border:1px solid var(--border); background:transparent; height:36px; min-width:36px; border-radius:6px; display:inline-flex; align-items:center; justify-content:center; text-decoration:none; padding:0 10px; cursor:pointer; }}
    .actions {{ display:flex; gap:8px; flex-wrap:wrap; }}
    .panel,.card {{ background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:14px; }}
    .panel {{ margin-top:14px; overflow:auto; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:14px 0; }}
    .input-grid {{ display:grid; grid-template-columns:2fr 1fr; gap:12px; }}
    .field {{ display:flex; flex-direction:column; gap:6px; }}
    input,select {{ background:var(--panel); color:var(--text); border:1px solid var(--border); border-radius:6px; padding:9px; }}
    option {{ background:var(--panel); color:var(--text); }}
    button {{ border:0; border-radius:6px; padding:10px 12px; font-weight:600; cursor:pointer; }}
    .btn {{ background:var(--accent); color:#08231d; }}
    .btn-secondary {{ background:#64748b; color:white; }}
    .btn-danger {{ background:var(--danger); color:white; }}
    .small {{ color:var(--muted); font-size:13px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid var(--border); padding:8px; text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); }}
    footer {{ color:var(--muted); border-top:1px solid var(--border); margin-top:18px; padding-top:12px; font-size:13px; }}
    @media (max-width:700px) {{ .input-grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body id="page-body">
  <nav class="nav">
    <div class="nav-inner">
      <strong>Threat Intelligence Aggregator</strong>
      <div class="actions">
        <a href="#feed-processing">Feeds</a>
        <a href="#correlation-results">Correlation</a>
        <a href="#downloads">Outputs</a>
        <button class="icon-btn" id="theme-toggle" type="button">Theme</button>
      </div>
    </div>
  </nav>
  <main class="wrap">{content}<footer>Load feeds -> Parse indicators -> Normalize data -> Correlate IOCs -> Generate blocklists -> Export report</footer></main>
  <script>
    const body = document.getElementById('page-body');
    const toggle = document.getElementById('theme-toggle');
    const saved = localStorage.getItem('ti_theme') || 'dark';
    function applyTheme(mode) {{
      body.classList.toggle('light', mode === 'light');
      toggle.textContent = mode === 'light' ? 'Light' : 'Dark';
    }}
    applyTheme(saved);
    toggle.addEventListener('click', () => {{
      const next = body.classList.contains('light') ? 'dark' : 'light';
      localStorage.setItem('ti_theme', next);
      applyTheme(next);
    }});
  </script>
</body>
</html>"""
    return page.encode("utf-8")


def _render_dashboard() -> str:
    last_run = _load_json(LAST_RUN_FILE, {})
    run_status = _load_json(RUN_STATUS_FILE, {})
    report = _load_json(OUTPUT_DIR / "threat_report.json", {})
    correlated = _load_json(OUTPUT_DIR / "correlated_iocs.json", [])

    feeds = report.get("feeds_processed", [])
    severity = report.get("severity_breakdown", {"High": 0, "Medium": 0, "Low": 0})
    outputs = last_run.get("outputs", {})

    feed_rows = "".join(
        f"<tr><td>{html.escape(feed.get('name',''))}</td><td>{html.escape(feed.get('status',''))}</td><td>{feed.get('rows',0)}</td><td>{feed.get('iocs',0)}</td></tr>"
        for feed in feeds
    )
    corr_rows = "".join(
        f"<tr><td>{html.escape(row.get('indicator',''))}</td><td>{html.escape(row.get('ioc_type',''))}</td><td>{row.get('source_count',0)}</td><td>{row.get('total_mentions',0)}</td><td>{html.escape(row.get('severity',''))}</td></tr>"
        for row in correlated[:100]
    )

    status_line = f"Last run: {html.escape(run_status.get('last_run','-'))} | Status: {html.escape(run_status.get('status','not run'))}"

    return f"""
<section>
  <h1>Threat Intelligence Aggregator (Non-AI)</h1>
  <div class="small">{status_line}</div>
</section>

<section class="panel">
  <h3>Feed Input</h3>
  <form method="post" action="/run-custom" enctype="multipart/form-data">
    <div class="input-grid">
      <div class="field">
        <label>Upload IOC File (CSV, TXT, JSON, STIX)</label>
        <input type="file" name="feed_file" />
      </div>
      <div class="field">
        <label>Format</label>
        <select name="feed_format">
          <option value="txt">TXT</option>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="stix">STIX</option>
        </select>
      </div>
    </div>
    <div class="actions" style="margin-top:12px;">
      <button class="btn" type="submit">Run Analysis</button>
      <button class="btn-secondary" formaction="/run-default" type="submit">Run Sample Feeds</button>
      <button class="btn-danger" formaction="/clear-results" type="submit">Clear Results</button>
    </div>
  </form>
</section>

<section class="cards">
  <div class="card"><div class="small">Feeds Processed</div><h2>{len(feeds)}</h2></div>
  <div class="card"><div class="small">Normalized IOCs</div><h2>{report.get('total_normalized_iocs',0)}</h2></div>
  <div class="card"><div class="small">Unique Indicators</div><h2>{report.get('total_unique_iocs',0)}</h2></div>
  <div class="card"><div class="small">High Severity</div><h2>{severity.get('High',0)}</h2></div>
</section>

<section class="panel" id="feed-processing">
  <h3>Feed Processing Summary</h3>
  <table>
    <thead><tr><th>Feed</th><th>Status</th><th>Rows</th><th>IOCs</th></tr></thead>
    <tbody>{feed_rows or '<tr><td colspan="4">No analysis run yet</td></tr>'}</tbody>
  </table>
</section>

<section class="panel" id="correlation-results">
  <h3>Correlation Results</h3>
  <table>
    <thead><tr><th>Indicator</th><th>Type</th><th>Sources</th><th>Mentions</th><th>Severity</th></tr></thead>
    <tbody>{corr_rows or '<tr><td colspan="5">No correlation data yet</td></tr>'}</tbody>
  </table>
</section>

<section class="panel" id="downloads">
  <h3>Outputs</h3>
  <ul>{_output_links(outputs)}</ul>
</section>
"""


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_html_page(_render_dashboard()))
            return

        if parsed.path == "/download":
            filename = (parse_qs(parsed.query).get("file") or [""])[0]
            file_path = _download_path(filename)
            if not file_path:
                self.send_error(404, "File not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename={file_path.name}")
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/run-default":
            _run_and_persist("sample-feeds", str(ROOT_DIR / "examples" / "feeds.json"))
            self._redirect_home()
            return

        if parsed.path == "/run-custom":
            fields, files = _parse_post_form(self)
            feed_format = (fields.get("feed_format") or "txt").strip().lower()

            uploaded_path = None
            if "feed_file" in files:
                filename, file_bytes = files["feed_file"]
                if filename:
                    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                    uploaded_path = UPLOAD_DIR / _safe_filename(filename)
                    uploaded_path.write_bytes(file_bytes)

            if uploaded_path:
                config_path = _build_custom_config(uploaded_path, feed_format)
                _run_and_persist("custom-feed", str(config_path))

            self._redirect_home()
            return

        if parsed.path == "/clear-results":
            for item in OUTPUT_DIR.glob("*"):
                if item.is_file():
                    item.unlink(missing_ok=True)
            self._redirect_home()
            return

        self.send_error(404)

    def _redirect_home(self):
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8000), AppHandler)
    print("TI Aggregator web app running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()

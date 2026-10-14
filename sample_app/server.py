import http.server
import socketserver
import urllib.parse
import json
from pathlib import Path

PORT = 5001
HTML_FILE = Path(__file__).resolve().parent / "templates" / "index.html"
MODE_FILE = Path(__file__).resolve().parent / "current_mode.txt"

def get_current_mode() -> str:
    if MODE_FILE.exists():
        try:
            return MODE_FILE.read_text(encoding="utf-8").strip() or "clean"
        except Exception:
            pass
    return "clean"

def set_current_mode(mode: str):
    MODE_FILE.write_text(mode, encoding="utf-8")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class SampleAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            mode = query.get("mode", [None])[0] or get_current_mode()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Connection", "close")
            self.end_headers()
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            # Inject active mode into script
            content = content.replace('let currentMode = "clean";', f'let currentMode = "{mode}";')
            if mode == "drift":
                content = content.replace(
                    '<button id="run-optimizer-btn" class="btn-action" onclick="handleAction()">Run Omnichannel AI Optimizer</button>',
                    '<button id="launch-forecast-btn" class="btn-action" onclick="handleAction()">Launch Forecast Model</button>'
                )
                content = content.replace(
                    '<span id="current-mode-label" style="color: #38bdf8;">Clean Baseline</span>',
                    '<span id="current-mode-label" style="color: #38bdf8;">Commit: UI Drift (Button Renamed to "launch-forecast-btn")</span>'
                )
            elif mode == "bug":
                content = content.replace(
                    '<span id="current-mode-label" style="color: #38bdf8;">Clean Baseline</span>',
                    '<span id="current-mode-label" style="color: #38bdf8;">Commit: App Bug (Crash on submit)</span>'
                )
            self.wfile.write(content.encode("utf-8"))
        elif path == "/set-mode":
            mode = query.get("mode", ["clean"])[0]
            set_current_mode(mode)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "mode": mode}).encode("utf-8"))
        elif path == "/mode":
            mode = get_current_mode()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(json.dumps({"mode": mode}).encode("utf-8"))
        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b'{"status": "running", "app": "Chryselys Sample Web App"}')
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

def run_server():
    server = ThreadedHTTPServer(("", PORT), SampleAppHandler)
    print(f"Threaded Sample App running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping sample server...")

if __name__ == "__main__":
    run_server()

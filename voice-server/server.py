#!/usr/bin/env python3
"""Local voice server for the Command Centre.

Speaks any text in the voice of the reference clip at voices/jarvis.wav (and its
transcript voices/jarvis.txt), using F5-TTS (free) on this Mac. Nothing leaves the machine.

Run:  ~/jarvis-voice/.venv-f5/bin/python voice-server/server.py
Then pick "Jarvis Local" in the Command Centre voice panel (Chrome on this Mac).
"""
import hashlib, io, json, os, struct, sys, threading, wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.environ.get("JARVIS_REF", os.path.join(HERE, "voices", "jarvis.wav"))
CACHE = os.path.join(os.path.expanduser("~"), "jarvis-voice", "cache")
PORT = int(os.environ.get("JARVIS_PORT", "8787"))
ALLOW = {"https://1jenson.github.io", "http://localhost:8793", "http://127.0.0.1:8793"}
os.makedirs(CACHE, exist_ok=True)

_model = None
_lock = threading.Lock()
REF_TXT = os.environ.get("JARVIS_REF_TEXT", os.path.splitext(REF)[0] + ".txt")
STEPS = int(os.environ.get("JARVIS_STEPS", "16"))  # lower = faster; 14-32 sound much the same


def load_model():
    global _model
    if _model is not None:
        return _model
    import torch
    from f5_tts.api import F5TTS
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    _model = F5TTS(model="F5TTS_v1_Base", device=dev)
    print(f"model ready on {dev}", flush=True)
    if os.path.exists(REF):  # warm-up so the first real line is not slow
        try:
            _model.infer(REF, ref_text(), "Ready.", nfe_step=STEPS, seed=7, show_info=lambda *a: None, progress=None)
            print("warm", flush=True)
        except Exception as e:
            print("warm-up failed:", e, flush=True)
    return _model


def ref_text():
    try:
        return open(REF_TXT).read().strip()
    except OSError:
        return ""  # F5 transcribes the clip itself (downloads a small speech model once)


def to_wav(samples, sr):
    import numpy as np
    pcm = (np.clip(np.asarray(samples, dtype="float32"), -1, 1) * 32767).astype("<i2").tobytes()
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm)
    return out.getvalue()


def synth(text):
    stamp = str(os.path.getmtime(REF)) + ref_text() + str(STEPS)
    key = hashlib.sha1(f"{text}|{stamp}".encode()).hexdigest()
    path = os.path.join(CACHE, key + ".wav")
    if os.path.exists(path):
        return open(path, "rb").read()
    with _lock:
        m = load_model()
        wav, sr, _ = m.infer(REF, ref_text(), text, nfe_step=STEPS, seed=7, show_info=lambda *a: None, progress=None)
        data = to_wav(wav, sr)
    open(path, "wb").write(data)
    return data


class H(BaseHTTPRequestHandler):
    def _cors(self):
        o = self.headers.get("Origin", "")
        if o in ALLOW:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "content-type")

    def _send(self, code, body=b"", ctype="application/json"):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            self._send(200, json.dumps({"ok": True, "ref": os.path.exists(REF), "ready": _model is not None}).encode())
        elif u.path == "/tts":
            text = (parse_qs(u.query).get("text") or [""])[0].strip()[:600]
            if not text:
                return self._send(400, b'{"error":"no text"}')
            if not os.path.exists(REF):
                return self._send(409, b'{"error":"no reference clip at voice-server/voices/jarvis.wav"}')
            try:
                self._send(200, synth(text), "audio/wav")
            except Exception as e:  # keep serving; the page falls back to another voice
                print("synth error:", e, file=sys.stderr, flush=True)
                self._send(500, json.dumps({"error": str(e)[:200]}).encode())
        else:
            self._send(404, b"{}")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"Jarvis voice server on http://127.0.0.1:{PORT}  (reference: {REF})", flush=True)
    threading.Thread(target=load_model, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()

# Jarvis Local voice server

Speaks the Command Centre's text in the voice of a reference clip, using
[Chatterbox](https://github.com/resemble-ai/chatterbox) (free, MIT licence).
Runs on this Mac only. Nothing is sent anywhere.

## One-off setup (already done on Jenson's Mac)
```bash
brew install uv
mkdir -p ~/jarvis-voice && cd ~/jarvis-voice
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python chatterbox-tts
```

## The reference clip
Put a clean clip of the voice at `voice-server/voices/jarvis.wav`:
10 to 30 seconds, one speaker, no music or background noise, mono or stereo WAV.
Use a recording you have the right to use, for personal use only.
The cleaner the clip, the better the clone.

## Start it
```bash
~/jarvis-voice/.venv/bin/python voice-server/server.py
```
The first start downloads the model (about 3 GB, once). Leave it running, open the
Command Centre in Chrome on this Mac, pick **Jarvis Local** in the voice panel and tap Test voice.

Phrases are cached in `~/jarvis-voice/cache`, so repeats are instant.
If the server is not running the page falls back to the system Jarvis voice.

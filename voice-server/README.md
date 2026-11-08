# Jarvis Local voice server

Speaks the Command Centre's text in the voice of a reference clip, using
[F5-TTS](https://github.com/SWivid/F5-TTS) (free). It copies accent and tone from the
clip much more faithfully than Chatterbox, which came out with an American accent
on the same clip. Runs on this Mac only. Nothing is sent anywhere.

## One-off setup (already done on Jenson's Mac)
```bash
brew install uv
mkdir -p ~/jarvis-voice && cd ~/jarvis-voice
uv venv --python 3.11 .venv-f5
uv pip install --python .venv-f5/bin/python f5-tts "setuptools<81" soundfile
```

## The reference clip
- `voice-server/voices/jarvis.wav`: 8 to 12 seconds of the voice, one speaker, no music or noise.
- `voice-server/voices/jarvis.txt`: exactly what is said in that clip, as plain text.
Use a recording you have the right to use, for personal use only. These files are not committed.
The cleaner the clip and the more exact the text, the closer the clone.

## Start it
```bash
~/jarvis-voice/.venv-f5/bin/python voice-server/server.py
```
The first start downloads the model (about 1.5 GB, once). Leave it running, open the
Command Centre in Chrome on this Mac, pick **Jarvis Local** in the voice panel and tap Test voice.
Chrome asks once to allow connecting to devices on your local network: choose Allow.

Phrases are cached in `~/jarvis-voice/cache`, so repeats are instant.
If the server is not running the page falls back to the system Jarvis voice.
`JARVIS_STEPS` (default 16) trades speed for polish.

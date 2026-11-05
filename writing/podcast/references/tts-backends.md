# TTS backends

Checked 2026-11-05 against the sources named in each section. Providers change; re-read the official page before a large run.

## Config file

Keep it outside the repository. Environment variables override it: `PODCAST_TTS_BACKEND`, `PODCAST_TTS_BASE_URL`, `PODCAST_TTS_API_KEY`, `PODCAST_TTS_MODEL`, and `PODCAST_TTS_CONFIG` (path). The key may also be read from the variable named by `api_key_env`.

```json
{
  "backend": "mimo",
  "model": "mimo-v2.5-tts",
  "voices": {"A": "冰糖", "B": {"voice": "苏打", "speed": 1.0}, "C": "白桦"},
  "style_mode": "auto",
  "format": "wav",
  "max_chars": 150,
  "default_pause": 0.35,
  "price_per_1k_chars": 0
}
```

`base_url` is deliberately absent: set it in the environment. `backend` is `mimo` or `openai`. `style_mode`: `auto` (tag for mimo, instruction for openai), `tag`, `instruction`, or `none`. `price_per_1k_chars` only feeds the dry-run estimate.

## Xiaomi MiMo TTS

Source: the official MiMo API docs, "Speech Synthesis (MiMo-V2.5-TTS Series)", under mimo.mi.com (also reached from platform.xiaomimimo.com); the docs index is at mimo.mi.com/llms.txt. Confirmed from that page:

- Models: `mimo-v2.5-tts` (built-in voices; supports singing; no design or cloning), `mimo-v2.5-tts-voicedesign` (voice from a text description; the user message is required), `mimo-v2.5-tts-voiceclone` (voice from an audio sample as base64 `data:audio/mpeg;base64,...` or `audio/wav`, at most 10 MB of base64, mp3 or wav only). The older `mimo-v2-tts` name appears in earlier pages.
- Endpoint: OpenAI-style chat completions at `https://api.xiaomimimo.com/v1/chat/completions` (the docs use this base for the OpenAI SDK). Auth header `api-key: $MIMO_API_KEY`. The user's own base URL goes in the environment; this skill never hardcodes it.
- Request: `messages` plus `audio: {"format": "wav", "voice": "<id>"}`. The text to speak must be in the **assistant** message, never the user message. An optional user message carries a natural-language style instruction or history and is not spoken.
- Response (non-streaming): `choices[0].message.audio.data`, base64 audio. Streaming: set `stream: true` and `format: "pcm16"`; the docs describe 24 kHz PCM16 mono chunks to concatenate. Low-latency streaming is stated for `mimo-v2.5-tts` only; voice design and clone currently return the whole result at once in streaming form. synthesize.py uses the non-streaming call.
- Built-in voices (ID equals name): Chinese female 冰糖 and 茉莉, Chinese male 苏打 and 白桦, English female Mia and Chloe, English male Milo and Dean; `mimo_default` is 冰糖 on the China cluster and Mia elsewhere.
- Style, two ways. Natural language in the user message (a sentence, or a "director" block with character, scene, and guidance). Or tags in the assistant text: a leading `(style1 style2)` (half- or full-width parentheses, or square brackets; multiple styles in one pair with any separator), and inline `[tag]`-style cues anywhere for whisper, laugh, sigh, breath, pause, cough, speed. Recommended style families listed: basic emotions (happy, sad, angry, calm ...), complex emotions, overall tone (gentle, cold, serious ...), timbre, character tone, dialects (Northeast, Sichuan, Henan, Cantonese), role-play, and singing, where `(唱歌)` must be the very first thing in the text. The English page is a translation; for Chinese lines use Chinese tag words, which is an inference from the `(唱歌)` example and should be tested.
- Pricing: the page said "Free for a limited time" at check time. Rate limits and a maximum text length per request were not stated on that page; synthesize.py defaults to 150 characters per request to stay safe. Treat both as unverified.

In the script, put the style in the line's `[style]` slot; with `style_mode: tag` it becomes the leading `(style)`. For sung or heavily styled lines, test first.

## OpenAI-compatible servers

Request: `POST {base_url}/audio/speech` with JSON `model`, `input`, `voice`, `response_format` (wav, mp3, opus, flac, pcm), optional `speed`, and optional `instructions` (honoured by instruction-following models; many local servers ignore unknown fields). Auth `Authorization: Bearer <key>` when the server needs one. The body is the audio bytes. This is the OpenAI speech API shape; the OpenAI docs are the reference for it, and local servers vary on which voices and formats they accept, so read the server's own README. Input limits are server-specific; OpenAI's documents 4096 characters, so check yours.

## Local models (not installed by this skill)

Licences read from each repository on 2026-11-05. Read the licence file again before any non-private use; none of this is legal advice.

| Model | Languages and strengths (per its README) | Licence found | Serving |
| --- | --- | --- | --- |
| CosyVoice (Fun-CosyVoice 3.0), github.com/FunAudioLLM/CosyVoice | Chinese, English and 7 more, 18+ Chinese dialects, zero-shot cloning, pinyin inpainting, streaming | Apache-2.0 (code); check the model card for weights | FastAPI server and client in repo; not OpenAI-shaped, wrap it |
| ChatTTS, github.com/2noise/ChatTTS | Chinese and English dialogue, laughter and pause control | code AGPL-3.0, model CC BY-NC 4.0 (non-commercial) | Python API and WebUI; wrap it |
| Fish Speech, github.com/fishaudio/fish-speech | multi-speaker generation, cloning, natural-language control | Fish Audio Community License (research and non-commercial free; commercial under a revenue threshold; hosted services excluded); some weights under a separate research licence | API server and WebUI in repo |
| IndexTTS, github.com/index-tts/index-tts | Chinese and English, emotion control, pinyin control | bilibili Model Use License (very large companies need a separate licence; restrictions on training other models with outputs) | Python API and WebUI; wrap it |
| Kokoro-FastAPI, github.com/remsky/Kokoro-FastAPI | OpenAI-compatible wrapper for Kokoro; limited Chinese | Apache-2.0 (wrapper) | OpenAI-shaped `/v1/audio/speech` |

For a model without an OpenAI-shaped server, a thin wrapper that accepts the `/audio/speech` JSON above is the easiest way to plug it into synthesize.py. For a multi-host show, pick one distinct voice per host (or a reference clip per host); clone only voices you own or have consent for.

## Volcengine / Doubao

The Doubao podcast capability is reported to be available to developers as a dedicated podcast TTS service (dialogue mode from a topic or a link). Only third-party descriptions were found; this skill has no adapter for it. Use the vendor's docs if the user wants it.

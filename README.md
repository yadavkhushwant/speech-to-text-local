# Speech to Text

A simple Python script that converts an audio file into text. Every segment of the text comes with a start time and an end time.

It uses faster-whisper for transcription and FFmpeg for audio handling. Everything runs on your own machine, on CPU or GPU.

## Requirements

- Python 3.9 or above
- FFmpeg
- faster-whisper

## Setup

Install FFmpeg (Ubuntu/Debian):

```bash
sudo apt install ffmpeg
```

Create a virtual environment and install the library:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python transcribe.py audio.mp3
```

You can choose the model size, the device and the compute type:

```bash
# CPU, small model, int8 (default)
python transcribe.py audio.mp3 --model small --device cpu --compute-type int8

# GPU, large model
python transcribe.py audio.mp3 --model large-v3 --device cuda --compute-type float16
```

| Option | What it does | Default |
|---|---|---|
| `--model` | Model size: tiny, base, small, medium, large-v3 | small |
| `--device` | `cpu` or `cuda` | cpu |
| `--compute-type` | int8, float16 or float32 | int8 |

Smaller models and int8 are faster and use less memory. Bigger models are more accurate.

## Output

The output is JSON. Times are in seconds.

```json
{
  "language": "en",
  "segments": [
    {
      "start": 0.5,
      "end": 2.5,
      "text": "Hello everyone. Good morning."
    },
    {
      "start": 3.18,
      "end": 9.5,
      "text": "Today I am going to talk about a very interesting topic. The topic is artificial intelligence also known as AI."
    }
  ]
}
```

## How it works

1. Convert the input file to 16 kHz mono WAV using FFmpeg.
2. Split the audio into 10 minute parts.
3. Transcribe each part with faster-whisper.
4. Add the start time of the part to each segment, so the times match the original file.
5. Print the result as JSON.

## Different audio formats

Any file (mp3, wav, m4a, flac, ogg, even mp4 video) is first converted to 16 kHz mono WAV with FFmpeg. After that, the rest of the code works with only one format. If FFmpeg cannot read the file, the script shows an error message.

## Long audio files

The audio is split into 10 minute parts and the parts are transcribed one by one. This keeps the memory usage low even for very long files. Each part starts from zero, so the start time of the part is added to every segment. For example, a segment at 5 seconds in the third part is saved as 1205 seconds.

## Why these choices

- **faster-whisper:** free, open source, runs locally and is fast on CPU.
- **FFmpeg:** reads almost every audio and video format, so no separate code is needed for each format.
- **16 kHz mono WAV:** this is the format the Whisper models expect.
- **Model loaded one time:** loading is slow, so it is done once for all parts.
- **VAD filter on:** it skips silence, which saves time and gives cleaner text.
- **Command line options:** the same code can run on CPU or GPU, with any model size and compute type.

## Files

```
transcribe.py      main script
requirements.txt   python dependency
README.md
```
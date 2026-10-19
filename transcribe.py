"""Simple audio -> timestamped text pipeline using faster-whisper.

Usage:
    python simple_transcribe.py audio.mp3
    python simple_transcribe.py audio.mp3 --model small --device cpu --compute-type int8
    python simple_transcribe.py audio.mp3 --model large-v3 --device cuda --compute-type float16
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

CHUNK_SECONDS = 180  # long files are cut into 3 minute pieces


def convert_to_wav(src, dst):
    """Any format (mp3, m4a, flac, mp4...) -> 16 kHz mono WAV, which Whisper expects."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(dst)],
        check=True, capture_output=True,
    )


def split_audio(wav, out_dir):
    """Cut the WAV into CHUNK_SECONDS pieces. A short file just gives one chunk."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-f", "segment",
         "-segment_time", str(CHUNK_SECONDS), "-c", "copy",
         str(out_dir / "chunk_%04d.wav")],
        check=True, capture_output=True,
    )
    return sorted(out_dir.glob("chunk_*.wav"))


def transcribe(audio_path, model_name, device, compute_type):
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wav = tmp / "audio.wav"
        convert_to_wav(audio_path, wav)
        chunks = split_audio(wav, tmp)

        for i, chunk in enumerate(chunks):
            offset = i * CHUNK_SECONDS
            chunk_segments, info = model.transcribe(str(chunk), vad_filter=True)
            for seg in chunk_segments:
                segments.append({
                    "start": round(seg.start + offset, 2),
                    "end": round(seg.end + offset, 2),
                    "text": seg.text.strip(),
                })

    return {"language": info.language, "segments": segments}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("--model", default="small")        # tiny/base/small/medium/large-v3
    parser.add_argument("--device", default="cpu")         # cpu or cuda
    parser.add_argument("--compute-type", default="int8")  # int8, float16, float32 ...
    args = parser.parse_args()

    if not Path(args.audio).is_file():
        raise SystemExit(f"File not found: {args.audio}")

    try:
        result = transcribe(args.audio, args.model, args.device, args.compute_type)
    except subprocess.CalledProcessError:
        raise SystemExit("ffmpeg could not read this file (corrupt or unsupported format).")

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
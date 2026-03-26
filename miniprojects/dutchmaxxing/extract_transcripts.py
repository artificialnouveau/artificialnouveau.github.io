#!/usr/bin/env python3
"""
Extract question and answer text from NT2 exercise video clips using OCR.
Reads from the left (white/question) and right (green/answer) sides of each frame.
Outputs a JSON file with all transcripts.
"""

import cv2
import easyocr
import numpy as np
import json
import re
import sys
from pathlib import Path


def extract_text_from_region(reader, region):
    """Run OCR on an image region and return combined text."""
    results = reader.readtext(region)
    # Filter out low-confidence results and logos
    lines = []
    for bbox, text, conf in results:
        text = text.strip()
        if conf < 0.3:
            continue
        # Skip logo text
        if text.upper() in ['AD APPEL', 'ADAPPEL', 'APPEL']:
            continue
        if 'appel' in text.lower() and len(text) < 15:
            continue
        if len(text) < 2:
            continue
        lines.append(text)
    return '\n'.join(lines)


def extract_transcript(reader, video_path):
    """
    Extract question and answer text from an exercise video clip.
    - Question: from an early frame (left/white side)
    - Answer: from a late frame (right/green side)
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None, None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    if duration < 2:
        cap.release()
        return None, None

    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # Regions: skip header (top ~7%) and exercise bar (bottom ~8%)
    header_bottom = int(h * 0.07)
    bar_top = int(h * 0.92)
    mid_x = w // 2

    # Extract question from early frame (left side)
    question_text = None
    for t in [3, 5, 8]:
        if t >= duration:
            continue
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            continue
        left_region = frame[header_bottom:bar_top, 0:mid_x]
        text = extract_text_from_region(reader, left_region)
        if text and len(text) > 10:
            question_text = text
            break

    # Extract answer from late frame (right side)
    answer_text = None
    for t_ratio in [0.95, 0.9, 0.85, 0.75]:
        t = duration * t_ratio
        if t < 5:
            continue
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            continue
        right_region = frame[header_bottom:bar_top, mid_x:w]
        text = extract_text_from_region(reader, right_region)
        if text and len(text) > 5:
            answer_text = text
            break

    cap.release()
    return question_text, answer_text


def parse_exercise_filename(filename):
    """Extract set number and exercise number from filename."""
    # Pattern: "Staatsexamen B1 - Examenopgaven Set 1 - Spreken_exercise_03.webm"
    set_match = re.search(r'Set\s+(\d+)', filename)
    ex_match = re.search(r'exercise_(\d+)', filename)

    set_num = int(set_match.group(1)) if set_match else None
    ex_num = int(ex_match.group(1)) if ex_match else None

    return set_num, ex_num


def process_folder(folder_path, exam_type):
    """Process all exercise clips in a folder's split_by_exercise directory."""
    folder = Path(folder_path)
    split_dir = folder / "split_by_exercise"

    if not split_dir.exists():
        print(f"No split_by_exercise folder in {folder}")
        return {}

    video_files = sorted(
        list(split_dir.glob("*.webm")) +
        list(split_dir.glob("*.mp4")) +
        list(split_dir.glob("*.mkv"))
    )

    if not video_files:
        print(f"No video files found in {split_dir}")
        return {}

    print(f"\nProcessing {len(video_files)} exercise clips for {exam_type}")
    print("=" * 60)

    # Initialize EasyOCR reader (once for all files)
    reader = easyocr.Reader(['nl', 'en'], gpu=True, verbose=False)

    data = {}  # set_num -> exercise_num -> {question, answer}

    for i, video_file in enumerate(video_files):
        set_num, ex_num = parse_exercise_filename(video_file.name)
        if set_num is None or ex_num is None:
            print(f"  Skipping {video_file.name} (couldn't parse)")
            continue

        print(f"  [{i+1}/{len(video_files)}] Set {set_num}, Exercise {ex_num}...", end='', flush=True)

        question, answer = extract_transcript(reader, video_file)

        if set_num not in data:
            data[set_num] = {}

        data[set_num][ex_num] = {
            "question": question or "",
            "answer": answer or "",
            "video": video_file.name
        }

        q_preview = (question or "")[:40].replace('\n', ' ')
        a_preview = (answer or "")[:40].replace('\n', ' ')
        print(f" Q: {q_preview}... | A: {a_preview}...")

    return data


def main():
    base_dir = Path(__file__).parent

    all_data = {}

    # Process Spreken
    spreken_dir = base_dir / "Staatsexamen NT2 Examenopgaven Spreken B1"
    if spreken_dir.exists():
        all_data["spreken"] = process_folder(spreken_dir, "Spreken")

    # Process Schrijven
    schrijven_dir = base_dir / "Staatsexamen NT2 Examenopgaven Schrijven B1"
    if schrijven_dir.exists():
        all_data["schrijven"] = process_folder(schrijven_dir, "Schrijven")

    # Convert keys to strings for JSON serialization
    def stringify_keys(d):
        if isinstance(d, dict):
            return {str(k): stringify_keys(v) for k, v in d.items()}
        return d

    output = stringify_keys(all_data)

    output_path = base_dir / "exercise_transcripts.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nTranscripts saved to {output_path}")

    # Print summary
    for exam_type, sets in all_data.items():
        total_exercises = sum(len(exs) for exs in sets.values())
        print(f"  {exam_type}: {len(sets)} sets, {total_exercises} exercises")


if __name__ == "__main__":
    main()

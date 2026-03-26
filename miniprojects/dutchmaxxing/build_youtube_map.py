#!/usr/bin/env python3
"""
Build a JSON mapping of YouTube video IDs and exercise timestamps
for the NT2 B1 Oefenen page.
"""
import json
import re
from pathlib import Path
from split_exercises import find_exercise_transitions

# YouTube video IDs per set (from playlist)
SPREKEN_IDS = {
    1: '8vMLZj2V08Y', 2: 'O61Tj4RU_0o', 3: 'i-kPc-gjWCo', 4: 'NZsiS6sSczI',
    5: 'jl42kH-SSf4', 6: 'DhbgEzpfhOU', 7: 'H5fRO8pYSDs', 8: 'YqUs49iKZzE',
    9: 'WYjnHt70XrM', 10: 'IQWehMsYS-U', 11: 'DZViUdIFHwk', 12: 'k149hm76Upo',
    13: 'IdkwwW3ZNl4', 14: 'dbbx7znYrqY', 15: 'dFLPotcDNj8', 16: '6Flj4pJDGG4',
    17: 'i9ZVtytM8lM', 18: '3tsN8fKA2R4', 19: 'nMTilnWc9P8', 20: 'rZAx-Yiv0ZY',
    21: 'cuSdpkcWwVE', 22: 'WN3XKYo6ylg', 23: 'rdxqvxWVjus', 24: 'zSq58FiI80I',
    25: 'fljFkgFT-KA', 26: 'W2Lu1tNa7RI', 27: 'o75WVhGXmzU', 28: 'jD2dgfo0pYM',
    29: 'U9rT411Pipk', 30: '4oC_XdlZgxc',
}

SCHRIJVEN_IDS = {
    1: 'YaJqAjxV1L8', 2: 'tmKDXePekxQ', 3: '87b9QagMAd8', 4: 'vVmBclhNFq8',
    5: 'QQ4BEy8pUz4', 6: 'T3HTHQwynG4', 7: 'tz9OXUfKfc4', 8: 'jIp0IPrrlno',
    9: 'QJMwdiLg-lQ', 10: 'ymhs2f2nQyA', 11: 'TvWRL4XOAH8', 12: 'hEHJzt5fric',
    13: 'EIhi_Ym_9YI', 14: 'fcOjR4J5jPs', 15: 'r9J-0uIek-I', 16: 'si4Y7skDXbM',
    17: 'Bw3zDX3hCXY', 18: 'S509O5ccexA', 19: '3WJ1ix6f5cs', 20: 'pGh75DslSwo',
    21: 'AC-aYeRS4P4', 22: '2H8tzZaXVc8', 23: '87S3dzKqJB4', 24: 'wDRRwqVeEFo',
    25: 'kY4BhOfuKa8', 26: '6yV5p59EjBQ', 27: 'KC9LYTeGzoo', 28: 'BsN5-6ba8VI',
    29: 'GMPB_jHNsx8', 30: 'yvTiaNoUjj0', 31: 'p2pOOEr0lYM', 32: 'tWY95JiUJYQ',
    33: 'N8ild6qamoY',
}

import cv2

def get_video_duration(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return frames / fps if fps > 0 else 0


def process_type(folder_name, yt_ids, type_name):
    base = Path(__file__).parent
    folder = base / folder_name
    result = {}

    for set_num, yt_id in sorted(yt_ids.items()):
        # Find the video file
        patterns = [
            f"*Set {set_num} - {type_name}*",
            f"*Set {set_num} *{type_name}*",
        ]
        video_file = None
        for pat in patterns:
            matches = list(folder.glob(pat))
            if matches:
                video_file = matches[0]
                break

        if not video_file:
            print(f"  Warning: No video found for {type_name} Set {set_num}")
            result[str(set_num)] = {"youtube_id": yt_id, "exercises": {}}
            continue

        print(f"  Set {set_num}: {video_file.name}")
        duration = get_video_duration(str(video_file))
        transitions = find_exercise_transitions(str(video_file), num_exercises=12, sample_interval=2.0)

        exercises = {}
        for i, (start_time, ex_num) in enumerate(transitions):
            end_time = transitions[i + 1][0] if i + 1 < len(transitions) else duration
            exercises[str(ex_num)] = {
                "start": round(start_time),
                "end": round(end_time),
            }

        result[str(set_num)] = {
            "youtube_id": yt_id,
            "exercises": exercises,
        }

    return result


def main():
    base = Path(__file__).parent
    data = {}

    print("Processing Spreken...")
    data["spreken"] = process_type(
        "Staatsexamen NT2 Examenopgaven Spreken B1", SPREKEN_IDS, "Spreken"
    )

    print("\nProcessing Schrijven...")
    data["schrijven"] = process_type(
        "Staatsexamen NT2 Examenopgaven Schrijven B1", SCHRIJVEN_IDS, "Schrijven"
    )

    output_path = base / "youtube_timestamps.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()

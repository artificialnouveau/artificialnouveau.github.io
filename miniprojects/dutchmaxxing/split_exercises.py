#!/usr/bin/env python3
"""
Split NT2 Staatsexamen videos by exercise number.
Detects the green-highlighted exercise number in the bottom navigation bar
and splits the video at transition points.
"""

import cv2
import numpy as np
import subprocess
import sys
import os
import json
from pathlib import Path


def extract_frame(video_path, timestamp_sec):
    """Extract a single frame at a given timestamp."""
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def detect_green_exercise(frame, num_exercises=12, debug=False):
    """
    Detect which exercise number is highlighted green in the bottom bar.
    Uses calibrated box positions (for 1920x1080 video).
    Returns the exercise number (1-based) or None if not detected.
    """
    h, w = frame.shape[:2]

    # The exercise bar is at the very bottom of the frame
    # Crop bottom ~8% of the frame
    bar_top = int(h * 0.92)
    bar = frame[bar_top:h, :, :]
    bar_h, bar_w = bar.shape[:2]

    # Convert to HSV for green detection
    hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)

    # Green color range in HSV
    lower_green = np.array([35, 80, 80])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Also check that the exercise bar is present by looking for the
    # characteristic pink/red background (HSV: hue ~170, sat ~100+, val ~150+)
    lower_pink = np.array([140, 40, 100])
    upper_pink = np.array([180, 255, 255])
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    pink_ratio = np.sum(pink_mask > 0) / (bar_h * bar_w)

    # If less than 10% of the bar is pink, the exercise bar probably isn't showing
    if pink_ratio < 0.10:
        return None

    # Calibrated positions (based on 1920px width):
    # Exercise box width ≈ 131px, first center at x=247
    # Scale to actual frame width
    scale = bar_w / 1920.0
    box_width = 131.0 * scale
    first_center = 247.0 * scale

    # Check each exercise box region for green pixels
    best_exercise = None
    best_green_count = 0
    min_green_threshold = box_width * bar_h * 0.15  # At least 15% of box area should be green

    for ex in range(1, num_exercises + 1):
        center_x = first_center + (ex - 1) * box_width
        left = max(0, int(center_x - box_width * 0.45))
        right = min(bar_w, int(center_x + box_width * 0.45))

        green_count = np.sum(mask[:, left:right] > 0)
        if green_count > best_green_count and green_count > min_green_threshold:
            best_green_count = green_count
            best_exercise = ex

    if debug and best_exercise:
        cv2.imwrite("debug_bar.png", bar)
        cv2.imwrite("debug_mask.png", mask)

    return best_exercise


def find_exercise_transitions(video_path, num_exercises=12, sample_interval=0.5, debug=False):
    """
    Scan through a video and find timestamps where the exercise number changes.
    Returns a list of (timestamp, exercise_number) tuples.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"  Video: {Path(video_path).name}")
    print(f"  Duration: {duration:.1f}s, FPS: {fps:.1f}, Exercises: {num_exercises}")

    # Scan through the video using a single capture object
    transitions = []
    prev_exercise = None
    t = 0

    while t < duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret or frame is None:
            t += sample_interval
            continue

        exercise = detect_green_exercise(frame, num_exercises=num_exercises,
                                          debug=(debug and t < 2))

        if exercise is not None and exercise != prev_exercise:
            # Verify by checking the next frame too
            cap.set(cv2.CAP_PROP_POS_MSEC, (t + sample_interval * 0.5) * 1000)
            ret2, verify_frame = cap.read()
            if ret2 and verify_frame is not None:
                verify_exercise = detect_green_exercise(verify_frame,
                                                         num_exercises=num_exercises)
                if verify_exercise == exercise:
                    transitions.append((t, exercise))
                    prev_exercise = exercise
                    if debug:
                        print(f"  t={t:.1f}s: Exercise {exercise}")

        t += sample_interval

    cap.release()

    # Post-process: filter out non-sequential transitions
    # Exercises should go 1→N sequentially. Remove backward jumps and
    # any detections before the first exercise 1.
    if transitions:
        # Find the first occurrence of exercise 1
        first_ex1_idx = None
        for i, (t, ex) in enumerate(transitions):
            if ex == 1:
                first_ex1_idx = i
                break

        if first_ex1_idx is not None:
            # Start from exercise 1
            filtered = [transitions[first_ex1_idx]]
            for i in range(first_ex1_idx + 1, len(transitions)):
                t, ex = transitions[i]
                # Only keep if exercise number is strictly increasing
                if ex > filtered[-1][1]:
                    filtered.append((t, ex))
            transitions = filtered

    return transitions


def split_video(video_path, transitions, output_dir):
    """
    Split a video at the given transition points using ffmpeg.
    """
    if not transitions:
        print(f"  No transitions found, skipping {video_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    video_name = Path(video_path).stem
    ext = Path(video_path).suffix

    # Get video duration
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    cap.release()

    for i, (start_time, exercise_num) in enumerate(transitions):
        # End time is start of next transition or end of video
        if i + 1 < len(transitions):
            end_time = transitions[i + 1][0]
        else:
            end_time = duration

        segment_duration = end_time - start_time
        if segment_duration < 1:  # Skip very short segments
            continue

        output_file = os.path.join(output_dir, f"{video_name}_exercise_{exercise_num:02d}{ext}")

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", str(video_path),
            "-t", str(segment_duration),
            "-c", "copy",  # No re-encoding for speed
            "-avoid_negative_ts", "make_zero",
            output_file
        ]

        print(f"  Splitting exercise {exercise_num}: {start_time:.1f}s - {end_time:.1f}s -> {Path(output_file).name}")
        subprocess.run(cmd, capture_output=True)


def process_folder(folder_path, num_exercises=12, debug=False):
    """Process all videos in a folder."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return

    video_files = sorted(list(folder.glob("*.webm")) + list(folder.glob("*.mp4")) + list(folder.glob("*.mkv")))

    if not video_files:
        print(f"No video files found in {folder}")
        return

    print(f"\nProcessing {len(video_files)} videos in {folder.name}")
    print("=" * 60)

    output_dir = folder / "split_by_exercise"

    for video_file in video_files:
        print(f"\n--- {video_file.name} ---")
        transitions = find_exercise_transitions(video_file, num_exercises=num_exercises,
                                                 sample_interval=0.5, debug=debug)

        if transitions:
            print(f"  Found {len(transitions)} exercise transitions:")
            for t, ex in transitions:
                print(f"    Exercise {ex} starts at {t:.1f}s")

            split_video(video_file, transitions, str(output_dir))
        else:
            print("  No exercise transitions detected")


def calibrate(video_path):
    """
    Run calibration on a single video to check detection accuracy.
    Saves debug images and prints detailed info.
    """
    print(f"Calibrating on: {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    cap.release()

    print(f"Duration: {duration:.1f}s, FPS: {fps}")

    # Extract frames at various points and save debug images
    debug_dir = Path("debug_frames")
    debug_dir.mkdir(exist_ok=True)

    for t in [5, 30, 60, 120, duration/2]:
        if t >= duration:
            continue
        frame = extract_frame(video_path, t)
        if frame is None:
            continue

        h, w = frame.shape[:2]

        # Save full frame
        cv2.imwrite(str(debug_dir / f"frame_t{int(t)}.png"), frame)

        # Save bottom bar
        bar_top = int(h * 0.92)
        bar = frame[bar_top:h, :, :]
        cv2.imwrite(str(debug_dir / f"bar_t{int(t)}.png"), bar)

        # Save green mask
        hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 80, 80])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        cv2.imwrite(str(debug_dir / f"green_mask_t{int(t)}.png"), mask)

        exercise = detect_green_exercise(frame, num_exercises=12)

        print(f"\n  t={t:.0f}s:")
        print(f"    Frame size: {w}x{h}")
        print(f"    Bar region: y={bar_top} to {h}")
        print(f"    Detected exercise: {exercise}")

    print(f"\nDebug images saved to {debug_dir}/")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Split NT2 exam videos by exercise")
    parser.add_argument("path", nargs="?", help="Video file or folder to process")
    parser.add_argument("--calibrate", action="store_true", help="Run calibration mode on a single video")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--all", action="store_true", help="Process both Spreken and Schrijven folders")

    args = parser.parse_args()

    base_dir = Path(__file__).parent

    if args.all:
        for folder_name in ["Staatsexamen NT2 Examenopgaven Spreken B1",
                           "Staatsexamen NT2 Examenopgaven Schrijven B1"]:
            process_folder(base_dir / folder_name, debug=args.debug)
    elif args.calibrate and args.path:
        calibrate(args.path)
    elif args.path:
        path = Path(args.path)
        if path.is_dir():
            process_folder(path, debug=args.debug)
        else:
            transitions = find_exercise_transitions(str(path), debug=args.debug)
            if transitions:
                output_dir = path.parent / "split_by_exercise"
                split_video(str(path), transitions, str(output_dir))
    else:
        parser.print_help()

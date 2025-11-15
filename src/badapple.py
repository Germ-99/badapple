#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import time
import shutil
from pathlib import Path


CACHE_DIR = Path.home() / ".bapple-cache"
VIDEO_FILE = CACHE_DIR / "badapple.mp4"
FRAMES_DIR = CACHE_DIR / "frames"
AUDIO_FILE = CACHE_DIR / "audio.m4a"


def check_dependency(command):
    return shutil.which(command) is not None


def check_dependencies():
    missing = []
    
    dependencies = {
        'ffmpeg': 'ffmpeg',
        'ffprobe': 'ffmpeg',
        'chafa': 'chafa',
        'ffplay': 'ffmpeg'
    }
    
    for cmd, pkg in dependencies.items():
        if not check_dependency(cmd):
            missing.append(f"  - {cmd} (from {pkg})")
    
    if missing:
        print("Error: Missing required dependencies:", file=sys.stderr)
        for dep in missing:
            print(dep, file=sys.stderr)
        sys.exit(1)


def extract_frames(width, height, fps, force=False):
    if FRAMES_DIR.exists() and not force:
        frame_count = len(list(FRAMES_DIR.glob('frame_*.png')))
        if frame_count > 0:
            print(f"Using {frame_count} cached frames")
            return frame_count
    
    print("Rendering frames...")
    print(f"Settings: {width}x{height} @ {fps}fps")
    
    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)
    
    cmd = [
        'ffmpeg',
        '-i', str(VIDEO_FILE),
        '-vf', f'fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease',
        '-pix_fmt', 'rgb24',
        str(FRAMES_DIR / 'frame_%05d.png'),
        '-loglevel', 'error',
        '-stats'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        frame_count = len(list(FRAMES_DIR.glob('frame_*.png')))
        print(f"Extracted {frame_count} frames")
        return frame_count
    except subprocess.CalledProcessError:
        print("Frame extraction failed!", file=sys.stderr)
        sys.exit(1)


def extract_audio(force=False):
    if AUDIO_FILE.exists() and not force:
        return
    
    print("Extracting audio...")
    cmd = [
        'ffmpeg',
        '-i', str(VIDEO_FILE),
        '-vn',
        '-acodec', 'copy',
        '-y',
        str(AUDIO_FILE),
        '-loglevel', 'error'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Audio extracted")
    except subprocess.CalledProcessError:
        print("Audio extraction failed (continuing without audio)", file=sys.stderr)


def play_animation(width, height, fps, play_audio, chafa_args):
    frames = sorted(FRAMES_DIR.glob('frame_*.png'))
    frame_count = len(frames)
    
    if frame_count == 0:
        print("Error: No frames found!", file=sys.stderr)
        sys.exit(1)
    
    print(f"Ready: {frame_count} frames")
    print("Press Ctrl+C to stop")
    print()
    
    audio_process = None
    
    try:
        print('\033[?25l', end='')
        
        if play_audio and AUDIO_FILE.exists():
            audio_process = subprocess.Popen(
                ['ffplay', '-nodisp', '-autoexit', str(AUDIO_FILE), '-loglevel', 'quiet'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print('\033[2J', end='')
        
        start_time = time.time()
        frame_num = 0
        
        while True:
            for frame_file in frames:
                print('\033[H', end='')
                
                cmd = [
                    'chafa',
                    '--format', 'symbols',
                    '--size', f'{width}x{height}',
                    '--animate', 'off',
                ] + chafa_args.split() + [str(frame_file)]
                
                try:
                    output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
                    print(output, end='')
                except subprocess.CalledProcessError:
                    pass
                
                frame_num += 1
                expected_time = frame_num / fps
                current_time = time.time() - start_time
                sleep_time = expected_time - current_time
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            frame_num = 0
            start_time = time.time()
    
    except KeyboardInterrupt:
        pass
    finally:
        print('\033[?25h', end='')
        
        if audio_process:
            audio_process.terminate()
            audio_process.wait()
        
        print('\033[2J\033[H', end='')


def main():
    parser = argparse.ArgumentParser(description='Bad Apple!! ASCII Player')
    
    parser.add_argument('-w', '--width', type=int, default=80)
    parser.add_argument('--height', type=int, default=40, dest='height')
    parser.add_argument('-f', '--fps', type=int, default=30)
    parser.add_argument('--no-audio', action='store_true')
    parser.add_argument('--force-render', action='store_true')
    parser.add_argument('--chafa-args', type=str, default='--symbols ascii --fg-only')
    
    args = parser.parse_args()
    
    check_dependencies()
    
    if not VIDEO_FILE.exists():
        print(f"Error: Video not found at {VIDEO_FILE}", file=sys.stderr)
        print("Run the download script first:", file=sys.stderr)
        print("  curl -fsSL https://raw.githubusercontent.com/Germ-99/badapple/main/src/download.sh | bash", file=sys.stderr)
        sys.exit(1)
    
    extract_frames(args.width, args.height, args.fps, force=args.force_render)
    
    if not args.no_audio:
        extract_audio(force=args.force_render)
    
    print()
    play_animation(args.width, args.height, args.fps, not args.no_audio, args.chafa_args)


if __name__ == '__main__':
    main()
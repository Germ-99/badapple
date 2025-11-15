#!/usr/bin/env python3

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


def get_terminal_size():
    try:
        cols = int(subprocess.check_output(['tput', 'cols']).decode().strip())
        lines = int(subprocess.check_output(['tput', 'lines']).decode().strip())
        width = cols
        height = lines * 2
        return width, height
    except:
        return 80, 48


def extract_frames(width, height, fps):
    cache_key = f"{width}x{height}_{fps}fps"
    marker_file = FRAMES_DIR / f".cache_{cache_key}"
    
    if marker_file.exists():
        frame_count = len(list(FRAMES_DIR.glob('frame_*.png')))
        if frame_count > 0:
            return frame_count
    
    print("Rendering frames for your terminal size...")
    
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
        marker_file.touch()
        return frame_count
    except subprocess.CalledProcessError:
        print("Frame extraction failed!", file=sys.stderr)
        sys.exit(1)


def extract_audio():
    if AUDIO_FILE.exists():
        return
    
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
    except subprocess.CalledProcessError:
        pass


def play_animation(width, height, fps):
    frames = sorted(FRAMES_DIR.glob('frame_*.png'))
    frame_count = len(frames)
    
    if frame_count == 0:
        print("Error: No frames found!", file=sys.stderr)
        sys.exit(1)
    
    audio_process = None
    
    try:
        print('\033[?25l', end='')
        
        if AUDIO_FILE.exists():
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
                    '--symbols', 'ascii',
                    '--colors', '2',
                    '--animate', 'off',
                    '--fg-only',
                    str(frame_file)
                ]
                
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
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print("This software is written by Bryson Kelly, source code can be found at https://github.com/Germ-99/badapple")
            sys.exit(0)
        else:
            print('pssst! This command doesn\'t have any arguments, it\'s only purpose is to play bad apple. Simply just type "badapple" in your terminal or run "badapple -h" to find the source code!')
            sys.exit(1)
    
    check_dependencies()
    
    if not VIDEO_FILE.exists():
        print(f"Error: Video not found at {VIDEO_FILE}", file=sys.stderr)
        print("Run the download script first:", file=sys.stderr)
        print("  curl -fsSL https://raw.githubusercontent.com/Germ-99/badapple/main/src/download.sh | bash", file=sys.stderr)
        sys.exit(1)
    
    width, height = get_terminal_size()
    fps = 30
    
    extract_frames(width, height, fps)
    extract_audio()
    
    play_animation(width, height, fps)


if __name__ == '__main__':
    main()
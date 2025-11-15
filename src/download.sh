#!/bin/bash

set -e

CACHE_DIR="$HOME/.bapple-cache"
VIDEO_URL="https://youtu.be/FtutLA63Cp8"
VIDEO_FILE="$CACHE_DIR/badapple.mp4"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if ! command -v yt-dlp &> /dev/null; then
    echo -e "${RED}Error: yt-dlp is not installed.${NC}"
    echo "Install it with: pip install yt-dlp"
    exit 1
fi

mkdir -p "$CACHE_DIR"

if [ -f "$VIDEO_FILE" ]; then
    echo -e "${YELLOW}Video already exists at: $VIDEO_FILE${NC}"
    read -p "Re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing video."
        exit 0
    fi
    rm -f "$VIDEO_FILE"
fi

echo "Downloading video..."
echo "URL: $VIDEO_URL"
echo "Destination: $VIDEO_FILE"
echo

yt-dlp \
    -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' \
    --merge-output-format mp4 \
    -o "$VIDEO_FILE" \
    "$VIDEO_URL"

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN} Download complete!${NC}"
    echo "Video saved to: $VIDEO_FILE"
else
    echo -e "${RED} Download failed!${NC}"
    exit 1
fi
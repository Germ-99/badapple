#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_URL="https://github.com/Germ-99/badapple"
DOWNLOAD_SCRIPT_URL="https://raw.githubusercontent.com/Germ-99/badapple/main/src/download.sh"
INSTALL_DIR="/tmp/badapple-install"
BIN_DIR="/usr/local/bin"

echo -e "${GREEN}Bapple command${NC}"
echo "================================"
echo

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

echo "Downloading video..."
curl -fsSL "$DOWNLOAD_SCRIPT_URL" | bash
echo

echo "Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi
git clone "$REPO_URL" "$INSTALL_DIR"
echo

echo "Installing command..."
if [ ! -w "$BIN_DIR" ]; then
    echo -e "${YELLOW}Installing to $BIN_DIR requires sudo${NC}"
    sudo cp "$INSTALL_DIR/badapple.py" "$BIN_DIR/badapple"
    sudo chmod +x "$BIN_DIR/badapple"
else
    cp "$INSTALL_DIR/badapple.py" "$BIN_DIR/badapple"
    chmod +x "$BIN_DIR/badapple"
fi
echo

rm -rf "$INSTALL_DIR"

echo -e "${GREEN} Installation complete!${NC}"
echo
echo "Run 'badapple' to play Bad Apple"
echo
echo "Options:"
echo "  badapple -w 120 --height 60    # Higher resolution"
echo "  badapple -f 24                 # Different framerate"
echo "  badapple --no-audio            # Without audio"
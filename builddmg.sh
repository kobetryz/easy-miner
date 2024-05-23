#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/easy miner.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/easy miner.dmg" && rm "dist/easy miner.dmg"
create-dmg \
  --volname "easy miner" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "easy miner.app" 175 120 \
  --hide-extension "easy miner.app" \
  --app-drop-link 425 120 \
  "dist/easy miner.dmg" \
  "dist/dmg/"
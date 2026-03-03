#!/bin/bash
# make_dmg.sh — Creates Packrat-1.0.0.dmg from dist/Packrat.app
set -e

APP="$(cd "$(dirname "$0")/dist" && pwd)/Packrat.app"
OUT="$(pwd)/Packrat-1.0.0.dmg"

if [ ! -d "$APP" ]; then
  echo "❌  Packrat.app not found at $APP"
  echo "   Run: python3 setup.py py2app"
  exit 1
fi

echo "📦  Creating DMG from $APP"
echo "    App size: $(du -sh "$APP" | awk '{print $1}')"

TMP_DMG="/tmp/packrat_build.dmg"
MOUNT="/tmp/packrat_vol"

# Cleanup
rm -f "$TMP_DMG" "$OUT"
rm -rf "$MOUNT"

# Size = app + 80 MB headroom
SIZE_KB=$(du -sk "$APP" | awk '{print $1}')
SIZE_MB=$(( SIZE_KB / 1024 + 80 ))
echo "    Allocating ${SIZE_MB} MB..."

# Create writable image
hdiutil create -size "${SIZE_MB}m" \
               -fs HFS+ \
               -volname "Packrat 1.0.0" \
               -o "$TMP_DMG" \
               -quiet

# Mount
hdiutil attach "$TMP_DMG" \
               -mountpoint "$MOUNT" \
               -noautoopen \
               -quiet

# Copy app + Applications alias
echo "    Copying files…"
cp -R "$APP" "$MOUNT/"
ln -s /Applications "$MOUNT/Applications"

# Style the window via AppleScript (best-effort)
osascript 2>/dev/null <<EOF || true
tell application "Finder"
  tell disk "Packrat 1.0.0"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set bounds of container window to {200, 150, 800, 480}
    set icon size of icon view options of container window to 100
    set arrangement of icon view options of container window to not arranged
    set position of item "Packrat.app"   of container window to {160, 200}
    set position of item "Applications" of container window to {440, 200}
    close
    open
    update without registering applications
    delay 1
  end tell
end tell
EOF

sync
sleep 1
hdiutil detach "$MOUNT" -quiet

# Compress to final read-only DMG
echo "    Compressing…"
hdiutil convert "$TMP_DMG" \
               -format UDZO \
               -imagekey zlib-level=9 \
               -o "$OUT" \
               -quiet

rm -f "$TMP_DMG"

SIZE=$(du -sh "$OUT" | awk '{print $1}')
echo ""
echo "✅  Done! Packrat-1.0.0.dmg (${SIZE}) created at:"
echo "    $OUT"
echo ""
echo "    Open it to install:  open \"$OUT\""

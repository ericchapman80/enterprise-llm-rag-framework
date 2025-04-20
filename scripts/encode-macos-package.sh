
set -e

echo "=== Encoding macOS Fix Package for Sharing ==="

if [ ! -f "macos-memory-fix-package.zip" ]; then
    echo "Error: macos-memory-fix-package.zip not found"
    echo "Please run ./scripts/macos-fix-package.sh first"
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    base64 -i macos-memory-fix-package.zip > macos-memory-fix-package.b64
else
    base64 macos-memory-fix-package.zip > macos-memory-fix-package.b64
fi

split -b 4000 macos-memory-fix-package.b64 macos-fix-part-

echo "Package encoded and split into parts:"
ls -la macos-fix-part-*

echo "To share with users, send all the macos-fix-part-* files"
echo "Users can reassemble and decode with:"
echo ""
echo "cat macos-fix-part-* > macos-memory-fix-package.b64"
echo "base64 --decode macos-memory-fix-package.b64 > macos-memory-fix-package.zip"
echo "unzip macos-memory-fix-package.zip"

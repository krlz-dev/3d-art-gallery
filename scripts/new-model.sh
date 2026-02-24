#!/usr/bin/env bash
# Scaffold a new gallery model
# Usage: ./scripts/new-model.sh <model-id>
# Example: ./scripts/new-model.sh campfire

set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/new-model.sh <model-id>"
  echo "Example: ./scripts/new-model.sh campfire"
  exit 1
fi

MODEL_ID="$1"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GENERATOR="$PROJECT_ROOT/generators/generate_${MODEL_ID}.py"

if [ -f "$GENERATOR" ]; then
  echo "Error: $GENERATOR already exists"
  exit 1
fi

# Copy template
cp "$PROJECT_ROOT/generators/_template.py" "$GENERATOR"

# Replace MODEL_ID in the new file
sed -i "s/MODEL_ID = \"example\"/MODEL_ID = \"${MODEL_ID}\"/" "$GENERATOR"

echo "Created: generators/generate_${MODEL_ID}.py"
echo ""
echo "Next steps:"
echo "  1. Edit generators/generate_${MODEL_ID}.py — build your geometry"
echo "  2. Run:  blender -b --python generators/generate_${MODEL_ID}.py"
echo "  3. Add entry to src/data/models.js:"
echo ""
echo "     {"
echo "       id: \"${MODEL_ID}\","
echo "       name: \"Your Model Name\","
echo "       description: \"Short description\","
echo "       thumb: \`\${BASE}thumbnails/${MODEL_ID}.png\`,"
echo "       model: \`\${BASE}models/${MODEL_ID}.glb\`,"
echo "       tags: [\"low-poly\"],"
echo "       vertices: \"~???\","
echo "       generator: \"generators/generate_${MODEL_ID}.py\","
echo "     },"
echo ""
echo "  4. npm run dev  — test locally"
echo "  5. git add . && git commit && git push  — deploy"

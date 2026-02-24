const BASE = import.meta.env.BASE_URL

const models = [
  {
    id: "tree",
    name: "Winter Pine Tree",
    description: "Low-poly pine with snow caps, organic displacement, and ground base",
    thumb: `${BASE}thumbnails/tree.png`,
    model: `${BASE}models/tree.glb`,
    tags: ["low-poly", "vegetation", "winter"],
    vertices: "~400",
    generator: "generators/generate_tree.py",
  },
  {
    id: "adventurer",
    name: "Adventurer",
    description: "Low-poly adventurer with backpack — 24 animations including idle, walk, run, combat, and more",
    thumb: `${BASE}thumbnails/adventurer.png`,
    model: `${BASE}models/adventurer.glb`,
    tags: ["low-poly", "character", "animated", "adventure"],
    vertices: "~5,300",
  },
  // To add a new model:
  // 1. Create generators/generate_<name>.py
  // 2. Run: npm run generate:<name>
  // 3. Add entry here following the pattern above
]

export default models

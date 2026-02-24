"""
Generator template — copy this to create a new model.

Usage:
  1. cp generators/_template.py generators/generate_<name>.py
  2. Edit the script: change MODEL_ID, build your geometry
  3. Add to package.json:  "generate:<name>": "blender -b --python generators/generate_<name>.py"
  4. Run: npm run generate:<name>
  5. Add entry to src/data/models.js
  6. Done! Push to deploy.

Run: blender -b --python generators/generate_<name>.py
"""
import bpy
import bmesh
import random
import math
import os

# ── Config ──────────────────────────────────────────────
MODEL_ID = "example"       # <-- Change this: used for filenames
SEED = 42

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "public", "models", f"{MODEL_ID}.glb")
THUMBNAIL_FILE = os.path.join(PROJECT_ROOT, "public", "thumbnails", f"{MODEL_ID}.png")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(THUMBNAIL_FILE), exist_ok=True)

random.seed(SEED)


# ── Clear scene ─────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)


# ── Helper: create a flat-color material ────────────────
def make_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


# ── BUILD YOUR GEOMETRY HERE ────────────────────────────
# Example: a simple cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = "MyCube"

mat = make_material("CubeMat", (0.8, 0.2, 0.1, 1.0))
obj.data.materials.append(mat)

for poly in obj.data.polygons:
    poly.use_smooth = False


# ── Export to GLB ───────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_FILE,
    export_format='GLB',
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False,
    export_apply=True,
    check_existing=False,
)

print(f"\n✓ Exported GLB to: {OUTPUT_FILE}")
print(f"  Objects: {len(bpy.data.objects)}")
print(f"  Materials: {len(bpy.data.materials)}")


# ── Render thumbnail ────────────────────────────────────
# Camera — adjust position based on your model's size
bpy.ops.object.camera_add(location=(3, -3, 2.5))
camera = bpy.context.active_object
camera.name = "ThumbCamera"

track = camera.constraints.new(type='TRACK_TO')
track.target = obj
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.scene.camera = camera

# Sun light
bpy.ops.object.light_add(type='SUN', location=(5, -3, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.data.color = (0.9, 0.92, 1.0)

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-4, 3, 6))
fill = bpy.context.active_object
fill.data.energy = 50.0
fill.data.color = (0.7, 0.8, 1.0)

# Render settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 600
scene.render.resolution_y = 600
scene.render.film_transparent = True
scene.render.filepath = THUMBNAIL_FILE
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

bpy.ops.render.render(write_still=True)

print(f"✓ Rendered thumbnail to: {THUMBNAIL_FILE}")

# ── NEXT STEP: Add to src/data/models.js ────────────────
print(f"""
📋 Now add this to src/data/models.js:

  {{
    id: "{MODEL_ID}",
    name: "Your Model Name",
    description: "Short description of the model",
    thumb: `${{BASE}}thumbnails/{MODEL_ID}.png`,
    model: `${{BASE}}models/{MODEL_ID}.glb`,
    tags: ["low-poly", "your-tag"],
    vertices: "~???",
    generator: "generators/generate_{MODEL_ID}.py",
  }},
""")

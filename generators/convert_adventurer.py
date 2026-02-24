"""
Import Adventurer.glb, fix skinning weights (limit to 4 influences),
re-export clean GLB, and render thumbnail.

Usage: blender -b --python generators/convert_adventurer.py
"""
import bpy
import math
import os
import mathutils

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = "/home/krlz/Desktop/Adventurer.glb"
OUTPUT_GLB = os.path.join(PROJECT_ROOT, "public", "models", "adventurer.glb")
OUTPUT_THUMB = os.path.join(PROJECT_ROOT, "public", "thumbnails", "adventurer.png")

os.makedirs(os.path.dirname(OUTPUT_GLB), exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_THUMB), exist_ok=True)

# ── Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Import GLB
bpy.ops.import_scene.gltf(filepath=INPUT_FILE)

# ── Fix vertex weights: limit each vertex to max 4 influences ──
# This prevents shoe/mesh deformation artifacts in Babylon.js
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for obj in meshes:
    if not obj.vertex_groups:
        continue
    has_armature = any(m.type == 'ARMATURE' for m in obj.modifiers)
    if not has_armature:
        continue
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Limit vertex groups to 4 per vertex (glTF spec)
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    print(f"  Fixed weights: {obj.name}")

print(f"✓ Fixed vertex weights (max 4 influences) on {len(meshes)} meshes")

# ── Export clean GLB
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_materials='EXPORT',
    export_animations=True,
    export_cameras=False,
    export_lights=False,
    export_apply=False,
    check_existing=False,
)

file_size = os.path.getsize(OUTPUT_GLB)
print(f"✓ Exported GLB to: {OUTPUT_GLB} ({file_size // 1024} KB)")

# ── Bounding box for camera
min_co = mathutils.Vector((float('inf'),) * 3)
max_co = mathutils.Vector((float('-inf'),) * 3)
for obj in meshes:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ mathutils.Vector(v)
        for i in range(3):
            min_co[i] = min(min_co[i], world_v[i])
            max_co[i] = max(max_co[i], world_v[i])
center = (min_co + max_co) / 2
size = max_co - min_co

# ── Render thumbnail
bpy.context.scene.frame_set(1)

bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
cam_target = bpy.context.active_object

cam_dist = max(size.x, size.z) * 1.8
bpy.ops.object.camera_add(location=(
    center.x + cam_dist * 0.7,
    center.y - cam_dist * 0.7,
    center.z + size.z * 0.15
))
camera = bpy.context.active_object
track = camera.constraints.new(type='TRACK_TO')
track.target = cam_target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
bpy.context.scene.camera = camera

# Bright three-point lighting
bpy.ops.object.light_add(type='SUN', location=(5, -3, 10))
bpy.context.active_object.data.energy = 6.0
bpy.context.active_object.data.color = (1.0, 0.97, 0.95)

bpy.ops.object.light_add(type='AREA', location=(-4, 2, 5))
bpy.context.active_object.data.energy = 150.0
bpy.context.active_object.data.size = 6.0
bpy.context.active_object.data.color = (0.85, 0.88, 1.0)

bpy.ops.object.light_add(type='AREA', location=(3, 4, 3))
bpy.context.active_object.data.energy = 100.0
bpy.context.active_object.data.size = 4.0

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 600
scene.render.resolution_y = 600
scene.render.film_transparent = True
scene.render.filepath = OUTPUT_THUMB
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

bpy.ops.render.render(write_still=True)
print(f"✓ Rendered thumbnail to: {OUTPUT_THUMB}")

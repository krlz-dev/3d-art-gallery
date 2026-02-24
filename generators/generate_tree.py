"""
Low-poly winter pine tree generator for Blender CLI.
Usage: blender -b --python generators/generate_tree.py
Outputs: models/tree.glb + thumbnails/tree.png
"""
import bpy
import bmesh
import random
import math
import os
import sys

# ── Config ──────────────────────────────────────────────
SEED = 42
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "public", "models", "tree.glb")
THUMBNAIL_FILE = os.path.join(PROJECT_ROOT, "public", "thumbnails", "tree.png")

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


# ── Materials ───────────────────────────────────────────
def make_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

bark_mat = make_material("Bark", (0.30, 0.18, 0.08, 1.0), roughness=0.95)
leaves_dark = make_material("LeavesDark", (0.08, 0.28, 0.06, 1.0), roughness=0.9)
leaves_mid = make_material("LeavesMid", (0.10, 0.38, 0.08, 1.0), roughness=0.85)
leaves_light = make_material("LeavesLight", (0.15, 0.45, 0.10, 1.0), roughness=0.85)
snow_mat = make_material("Snow", (0.92, 0.94, 0.98, 1.0), roughness=0.7)
ground_mat = make_material("Ground", (0.85, 0.88, 0.92, 1.0), roughness=0.6)


# ── Trunk ───────────────────────────────────────────────
trunk_height = 3.5
trunk_radius_base = 0.18
trunk_radius_top = 0.08

bpy.ops.mesh.primitive_cone_add(
    vertices=7,
    radius1=trunk_radius_base,
    radius2=trunk_radius_top,
    depth=trunk_height,
    location=(0, 0, trunk_height / 2),
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Slight random displacement on trunk vertices for organic feel
bm = bmesh.new()
bm.from_mesh(trunk.data)
for v in bm.verts:
    if abs(v.co.z) < trunk_height * 0.48:  # don't displace tips
        v.co.x += random.uniform(-0.02, 0.02)
        v.co.y += random.uniform(-0.02, 0.02)
bm.to_mesh(trunk.data)
bm.free()

trunk.data.materials.append(bark_mat)

# Flat shading
for poly in trunk.data.polygons:
    poly.use_smooth = False


# ── Branch layers (cone tiers) ──────────────────────────
layers = [
    # (z_offset, radius, height, material)
    (1.2, 1.8, 1.6, leaves_dark),
    (2.0, 1.5, 1.5, leaves_dark),
    (2.7, 1.2, 1.4, leaves_mid),
    (3.3, 0.95, 1.2, leaves_mid),
    (3.8, 0.7, 1.0, leaves_light),
    (4.2, 0.45, 0.8, leaves_light),
]

leaf_objects = []

for i, (z, radius, height, mat) in enumerate(layers):
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=radius,
        radius2=0.0,
        depth=height,
        location=(0, 0, z + height / 2),
    )
    layer_obj = bpy.context.active_object
    layer_obj.name = f"Branches_{i}"

    # Displace vertices for organic shape
    bm = bmesh.new()
    bm.from_mesh(layer_obj.data)
    for v in bm.verts:
        if v.co.z < height * 0.3:  # bottom ring
            displacement = random.uniform(-0.15, 0.2) * radius
            angle = math.atan2(v.co.y, v.co.x)
            v.co.x += math.cos(angle) * displacement
            v.co.y += math.sin(angle) * displacement
            v.co.z += random.uniform(-0.1, 0.05)
    bm.to_mesh(layer_obj.data)
    bm.free()

    layer_obj.data.materials.append(mat)
    for poly in layer_obj.data.polygons:
        poly.use_smooth = False

    leaf_objects.append(layer_obj)


# ── Snow caps on top layers ─────────────────────────────
for i, (z, radius, height, _) in enumerate(layers[2:], start=2):
    snow_radius = radius * 0.7
    snow_height = 0.15
    bpy.ops.mesh.primitive_cone_add(
        vertices=8,
        radius1=snow_radius,
        radius2=snow_radius * 0.3,
        depth=snow_height,
        location=(0, 0, z + height * 0.65),
    )
    snow_cap = bpy.context.active_object
    snow_cap.name = f"SnowCap_{i}"

    # Displace snow slightly
    bm = bmesh.new()
    bm.from_mesh(snow_cap.data)
    for v in bm.verts:
        v.co.x += random.uniform(-0.03, 0.03)
        v.co.y += random.uniform(-0.03, 0.03)
        v.co.z += random.uniform(0, 0.04)
    bm.to_mesh(snow_cap.data)
    bm.free()

    snow_cap.data.materials.append(snow_mat)
    for poly in snow_cap.data.polygons:
        poly.use_smooth = False

    leaf_objects.append(snow_cap)

# Snow on the very top
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=1, radius=0.12,
    location=(0, 0, layers[-1][0] + layers[-1][2] * 0.9)
)
top_snow = bpy.context.active_object
top_snow.name = "SnowTop"
top_snow.data.materials.append(snow_mat)
for poly in top_snow.data.polygons:
    poly.use_smooth = False
leaf_objects.append(top_snow)


# ── Ground plane with snow ──────────────────────────────
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=3.0,
    depth=0.15,
    location=(0, 0, -0.075),
)
ground = bpy.context.active_object
ground.name = "SnowGround"

# Slight displacement for organic ground
bm = bmesh.new()
bm.from_mesh(ground.data)
for v in bm.verts:
    if abs(v.co.z) > 0.05:  # top face
        v.co.z += random.uniform(0, 0.08)
    v.co.x += random.uniform(-0.05, 0.05)
    v.co.y += random.uniform(-0.05, 0.05)
bm.to_mesh(ground.data)
bm.free()

ground.data.materials.append(ground_mat)
for poly in ground.data.polygons:
    poly.use_smooth = False


# ── Small rocks around base ─────────────────────────────
for i in range(4):
    angle = (i / 4) * math.pi * 2 + random.uniform(-0.3, 0.3)
    dist = random.uniform(0.8, 2.0)
    rx, ry = math.cos(angle) * dist, math.sin(angle) * dist

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=random.uniform(0.08, 0.18),
        location=(rx, ry, 0.05),
    )
    rock = bpy.context.active_object
    rock.name = f"Rock_{i}"
    rock.scale = (
        random.uniform(0.7, 1.4),
        random.uniform(0.7, 1.4),
        random.uniform(0.4, 0.8),
    )
    bpy.ops.object.transform_apply(scale=True)

    # Displace
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    for v in bm.verts:
        v.co += v.normal * random.uniform(-0.03, 0.05)
    bm.to_mesh(rock.data)
    bm.free()

    rock_mat = make_material(
        f"Rock_{i}",
        (0.4 + random.uniform(-0.1, 0.1),) * 3 + (1.0,),
        roughness=0.95,
    )
    rock.data.materials.append(rock_mat)
    for poly in rock.data.polygons:
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
# Camera
bpy.ops.object.camera_add(location=(5.5, -5.5, 4.5))
camera = bpy.context.active_object
camera.name = "ThumbCamera"

# Point camera at tree center
track = camera.constraints.new(type='TRACK_TO')
track.target = trunk
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.scene.camera = camera

# Sun light for clean render
bpy.ops.object.light_add(type='SUN', location=(5, -3, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (0.9, 0.92, 1.0)

# Ambient fill
bpy.ops.object.light_add(type='AREA', location=(-4, 3, 6))
fill = bpy.context.active_object
fill.name = "Fill"
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

# Render
bpy.ops.render.render(write_still=True)

print(f"✓ Rendered thumbnail to: {THUMBNAIL_FILE}")

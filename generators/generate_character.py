"""
Low-poly casual guy generator with walking animation for Blender CLI.
Detailed version: sculpted face, volumetric hair, hoodie with hood/zipper,
tapered limbs, sneaker shoes.

Usage: blender -b --python generators/generate_character.py
Outputs: public/models/character.glb + public/thumbnails/character.png
"""
import bpy
import bmesh
import math
import random
import os
from mathutils import Vector, Euler, Matrix

# ── Config ──────────────────────────────────────────────
MODEL_ID = "character"
SEED = 42
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "public", "models", f"{MODEL_ID}.glb")
THUMBNAIL_FILE = os.path.join(PROJECT_ROOT, "public", "thumbnails", f"{MODEL_ID}.png")

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(THUMBNAIL_FILE), exist_ok=True)

random.seed(SEED)
WALK_FRAMES = 24

# ── Clear scene ─────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)
for arm in bpy.data.armatures:
    bpy.data.armatures.remove(arm)
for action in bpy.data.actions:
    bpy.data.actions.remove(action)


# ── Materials ───────────────────────────────────────────
def make_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

skin_mat = make_material("Skin", (0.88, 0.73, 0.59, 1.0), roughness=0.65)
hoodie_mat = make_material("Hoodie", (0.72, 0.16, 0.14, 1.0), roughness=0.82)
hoodie_dark = make_material("HoodieDark", (0.52, 0.11, 0.10, 1.0), roughness=0.85)
shirt_mat = make_material("Shirt", (0.78, 0.78, 0.80, 1.0), roughness=0.75)
jeans_mat = make_material("Jeans", (0.16, 0.24, 0.34, 1.0), roughness=0.88)
jeans_dark = make_material("JeansDark", (0.12, 0.18, 0.26, 1.0), roughness=0.90)
shoe_mat = make_material("Shoes", (0.15, 0.15, 0.17, 1.0), roughness=0.65)
shoe_sole = make_material("Sole", (0.90, 0.90, 0.88, 1.0), roughness=0.70)
shoe_accent = make_material("ShoeAccent", (0.3, 0.3, 0.32, 1.0), roughness=0.7)
hair_mat = make_material("Hair", (0.25, 0.15, 0.07, 1.0), roughness=0.88)
hair_dark = make_material("HairDark", (0.15, 0.08, 0.03, 1.0), roughness=0.90)
zipper_mat = make_material("Zipper", (0.4, 0.42, 0.45, 1.0), roughness=0.4, metallic=0.3)
string_mat = make_material("String", (0.30, 0.30, 0.32, 1.0), roughness=0.8)


# ── Helpers ─────────────────────────────────────────────
def make_obj_from_pydata(name, verts, faces, mat):
    """Create an object from raw vertex/face data."""
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata([Vector(v) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def make_part(name, mat):
    """Tag active object with name, material, and flat shading."""
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def apply_scale(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    obj.select_set(False)


def taper_cylinder(obj, top_factor=0.8, bot_factor=1.0):
    """Taper a cylinder: scale top and bottom rings."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    zs = [v.co.z for v in bm.verts]
    zmin, zmax = min(zs), max(zs)
    zmid = (zmin + zmax) / 2
    for v in bm.verts:
        t = (v.co.z - zmin) / (zmax - zmin) if zmax > zmin else 0.5
        factor = bot_factor + (top_factor - bot_factor) * t
        v.co.x *= factor
        v.co.y *= factor
    bm.to_mesh(obj.data)
    bm.free()


# ── Character proportions ──────────────────────────────
# Total height ~1.75 units
HEAD_W = 0.20
HEAD_D = 0.22
HEAD_H = 0.24
NECK_H = 0.06

TORSO_W = 0.40
TORSO_D = 0.22
TORSO_H = 0.50

UPPER_ARM_LEN = 0.34
LOWER_ARM_LEN = 0.30
ARM_RAD_TOP = 0.065
ARM_RAD_BOT = 0.050

UPPER_LEG_LEN = 0.40
LOWER_LEG_LEN = 0.38
LEG_RAD_TOP = 0.075
LEG_RAD_BOT = 0.055

HAND_W = 0.045
HAND_D = 0.030
HAND_H = 0.080

FOOT_W = 0.085
FOOT_H = 0.10
FOOT_L = 0.22

HIP_SPREAD = 0.11
SHOULDER_X = TORSO_W / 2 + 0.02

# Vertical positions (bottom-up)
GROUND = 0.0
FOOT_Z = GROUND + FOOT_H / 2
ANKLE_Z = GROUND + FOOT_H
KNEE_Z = ANKLE_Z + LOWER_LEG_LEN
HIP_Z = KNEE_Z + UPPER_LEG_LEN
TORSO_Z = HIP_Z + TORSO_H / 2
SHOULDER_Z = HIP_Z + TORSO_H
NECK_Z = SHOULDER_Z + NECK_H
HEAD_Z = NECK_Z + HEAD_H / 2 + 0.03

UPPER_ARM_Z = SHOULDER_Z - UPPER_ARM_LEN / 2
ELBOW_Z = SHOULDER_Z - UPPER_ARM_LEN
LOWER_ARM_Z = ELBOW_Z - LOWER_ARM_LEN / 2
WRIST_Z = ELBOW_Z - LOWER_ARM_LEN
HAND_Z = WRIST_Z - HAND_H / 2

all_mesh_objects = []


# ════════════════════════════════════════════════════════
# HEAD — sculpted box with jawline, chin, brow ridge
# ════════════════════════════════════════════════════════
hw, hd, hh = HEAD_W/2, HEAD_D/2, HEAD_H/2
jaw_in = 0.82   # jaw narrowing factor
chin_in = 0.60  # chin narrowing
brow_out = 1.05 # slight brow ridge

head_verts = [
    # 0-3: top face
    (-hw, -hd, hh),  (hw, -hd, hh),  (hw, hd, hh),  (-hw, hd, hh),
    # 4-7: brow level (slightly wider)
    (-hw*brow_out, -hd*1.02, hh*0.3),
    ( hw*brow_out, -hd*1.02, hh*0.3),
    ( hw*brow_out,  hd*0.95, hh*0.3),
    (-hw*brow_out,  hd*0.95, hh*0.3),
    # 8-11: cheek level
    (-hw*0.95, -hd*0.95, -hh*0.1),
    ( hw*0.95, -hd*0.95, -hh*0.1),
    ( hw*0.95,  hd*0.90, -hh*0.1),
    (-hw*0.95,  hd*0.90, -hh*0.1),
    # 12-15: jaw level (narrower)
    (-hw*jaw_in, -hd*0.85, -hh*0.55),
    ( hw*jaw_in, -hd*0.85, -hh*0.55),
    ( hw*jaw_in,  hd*0.80, -hh*0.55),
    (-hw*jaw_in,  hd*0.80, -hh*0.55),
    # 16-17: chin (two verts, narrow)
    (-hw*chin_in, -hd*0.65, -hh),
    ( hw*chin_in, -hd*0.65, -hh),
    # 18: nose tip (small bump on front face)
    (0, -hd*1.08, hh*0.05),
]

head_faces = [
    # Top
    (0, 1, 2, 3),
    # Front upper (brow to top)
    (0, 4, 5, 1),
    # Front mid (brow to cheek)
    (4, 8, 9, 5),
    # Front lower-left (cheek to jaw)
    (8, 12, 13, 9),
    # Jaw to chin
    (12, 16, 17, 13),
    # Back upper
    (2, 6, 7, 3),
    # Back mid
    (6, 10, 11, 7),
    # Back lower
    (10, 14, 15, 11),
    # Back jaw
    (14, 16, 15),  # simplified — chin wraps around
    (14, 17, 16),
    # Right side upper
    (1, 5, 6, 2),
    # Right side mid
    (5, 9, 10, 6),
    # Right side lower
    (9, 13, 14, 10),
    # Right chin
    (13, 17, 14),
    # Left side upper
    (3, 7, 4, 0),
    # Left side mid
    (7, 11, 8, 4),
    # Left side lower
    (11, 15, 12, 8),
    # Left chin
    (15, 16, 12),
    # Nose triangles (front face detail)
    (4, 18, 5),
    (4, 8, 18),
    (5, 18, 9),
    (8, 9, 18),
    # Bottom (close chin)
    (16, 17, 14, 15),  # needed to close underside
]

# Offset to HEAD_Z
head_verts = [(x, y, z + HEAD_Z) for x, y, z in head_verts]
head_obj = make_obj_from_pydata("Head", head_verts, head_faces, skin_mat)
all_mesh_objects.append(head_obj)


# ════════════════════════════════════════════════════════
# HAIR — volumetric, swept style with side part
# ════════════════════════════════════════════════════════
hair_base_z = HEAD_Z + hh * 0.15   # starts at brow level
hair_top_z = HEAD_Z + hh + 0.06    # extends above head

# Main hair volume — shaped cap
hv = []
hf = []

# Bottom ring (follows head shape, slightly larger)
n_ring = 8
for i in range(n_ring):
    angle = (2 * math.pi / n_ring) * i
    # Asymmetric: hair is fuller on the right side
    rx = hw * 1.12 + (0.03 if math.cos(angle) > 0 else 0.0)
    ry = hd * 1.10
    x = math.cos(angle) * rx
    y = math.sin(angle) * ry
    hv.append((x, y, hair_base_z))

# Mid ring (fuller)
for i in range(n_ring):
    angle = (2 * math.pi / n_ring) * i
    rx = hw * 1.18 + (0.04 if math.cos(angle) > 0 else 0.01)
    ry = hd * 1.15
    x = math.cos(angle) * rx
    y = math.sin(angle) * ry
    hv.append((x, y, HEAD_Z + hh * 0.7))

# Top ring (narrows)
for i in range(n_ring):
    angle = (2 * math.pi / n_ring) * i
    rx = hw * 0.95 + (0.02 if math.cos(angle) > 0 else 0.0)
    ry = hd * 0.90
    x = math.cos(angle) * rx
    y = math.sin(angle) * ry
    hv.append((x, y, hair_top_z - 0.02))

# Crown vertex
hv.append((0.02, -0.01, hair_top_z))
crown_idx = len(hv) - 1

# Faces: connect rings
for i in range(n_ring):
    ni = (i + 1) % n_ring
    # Bottom to mid
    hf.append((i, ni, n_ring + ni, n_ring + i))
    # Mid to top
    hf.append((n_ring + i, n_ring + ni, 2*n_ring + ni, 2*n_ring + i))
    # Top to crown
    hf.append((2*n_ring + i, 2*n_ring + ni, crown_idx))

# Bottom cap (inner, we skip it — hair sits on head)

hair_obj = make_obj_from_pydata("Hair", hv, hf, hair_mat)
all_mesh_objects.append(hair_obj)

# Side bangs — a small wedge that hangs over the forehead
bang_verts = [
    (hw * 0.4, -hd * 1.05, HEAD_Z + hh * 0.6),
    (hw * 1.15, -hd * 0.85, HEAD_Z + hh * 0.7),
    (hw * 1.2, -hd * 1.05, HEAD_Z + hh * 0.95),
    (hw * 0.3, -hd * 1.1, HEAD_Z + hh * 0.95),
    # Tip hanging down
    (hw * 0.85, -hd * 1.12, HEAD_Z + hh * 0.25),
]
bang_faces = [
    (0, 1, 2, 3),  # front face
    (0, 4, 1),      # lower triangle
    (0, 3, 4),
    (3, 2, 4),
    (1, 4, 2),
]
bang_obj = make_obj_from_pydata("HairBang", bang_verts, bang_faces, hair_mat)
all_mesh_objects.append(bang_obj)

# Back hair tuft — extends behind the head
back_hair_verts = [
    (-hw * 0.7, hd * 0.9, HEAD_Z + hh * 0.4),
    ( hw * 0.7, hd * 0.9, HEAD_Z + hh * 0.4),
    ( hw * 0.6, hd * 1.15, HEAD_Z + hh * 0.85),
    (-hw * 0.6, hd * 1.15, HEAD_Z + hh * 0.85),
    ( 0, hd * 1.08, HEAD_Z + hh * 0.15),  # nape point
]
back_hair_faces = [
    (0, 1, 2, 3),
    (0, 4, 1),
    (0, 3, 4),
    (3, 2, 4),
    (1, 4, 2),
]
back_hair_obj = make_obj_from_pydata("HairBack", back_hair_verts, back_hair_faces, hair_dark)
all_mesh_objects.append(back_hair_obj)


# ════════════════════════════════════════════════════════
# NECK
# ════════════════════════════════════════════════════════
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6, radius=0.065, depth=NECK_H + 0.04,
    location=(0, 0, SHOULDER_Z + NECK_H / 2))
neck_obj = make_part("Neck", skin_mat)
all_mesh_objects.append(neck_obj)


# ════════════════════════════════════════════════════════
# TORSO — hoodie body with shoulder taper and waist narrowing
# ════════════════════════════════════════════════════════
tw, td, th = TORSO_W/2, TORSO_D/2, TORSO_H/2
# Subdivided box for better shape control
torso_verts = [
    # 0-3: bottom (hip level, slightly narrower)
    (-tw*0.88, -td*0.90, -th),  (tw*0.88, -td*0.90, -th),
    (tw*0.88, td*0.90, -th),    (-tw*0.88, td*0.90, -th),
    # 4-7: waist level (narrowest)
    (-tw*0.82, -td*0.88, -th*0.3),  (tw*0.82, -td*0.88, -th*0.3),
    (tw*0.82, td*0.88, -th*0.3),    (-tw*0.82, td*0.88, -th*0.3),
    # 8-11: chest level (widest)
    (-tw*1.05, -td*1.0, th*0.3),  (tw*1.05, -td*1.0, th*0.3),
    (tw*1.05, td*1.0, th*0.3),    (-tw*1.05, td*1.0, th*0.3),
    # 12-15: shoulder level
    (-tw*1.0, -td*0.95, th),   (tw*1.0, -td*0.95, th),
    (tw*1.0, td*0.95, th),     (-tw*1.0, td*0.95, th),
]

torso_faces = [
    # Bottom
    (0, 3, 2, 1),
    # Front
    (0, 1, 5, 4), (4, 5, 9, 8), (8, 9, 13, 12),
    # Right
    (1, 2, 6, 5), (5, 6, 10, 9), (9, 10, 14, 13),
    # Back
    (2, 3, 7, 6), (6, 7, 11, 10), (10, 11, 15, 14),
    # Left
    (3, 0, 4, 7), (7, 4, 8, 11), (11, 8, 12, 15),
    # Top
    (12, 13, 14, 15),
]

# Offset to torso center
torso_verts = [(x, y, z + TORSO_Z) for x, y, z in torso_verts]
torso_obj = make_obj_from_pydata("Torso", torso_verts, torso_faces, hoodie_mat)
all_mesh_objects.append(torso_obj)


# ── Hood bump on back of neck ──────────────────────────
hood_verts = [
    (-0.09, td*0.85, SHOULDER_Z - 0.02),
    ( 0.09, td*0.85, SHOULDER_Z - 0.02),
    ( 0.08, td*1.10, SHOULDER_Z + 0.06),
    (-0.08, td*1.10, SHOULDER_Z + 0.06),
    ( 0.06, td*1.05, SHOULDER_Z + 0.14),
    (-0.06, td*1.05, SHOULDER_Z + 0.14),
    ( 0.04, td*0.75, SHOULDER_Z + 0.12),
    (-0.04, td*0.75, SHOULDER_Z + 0.12),
]
hood_faces = [
    (0, 1, 2, 3),
    (3, 2, 4, 5),
    (5, 4, 6, 7),
    (0, 3, 5, 7),
    (1, 4, 2),  # Close side
    (1, 6, 4),
    (0, 7, 6, 1),
]
hood_obj = make_obj_from_pydata("Hood", hood_verts, hood_faces, hoodie_mat)
all_mesh_objects.append(hood_obj)


# ── Visible t-shirt at neckline ────────────────────────
collar_w = 0.10
collar_d = td * 0.96
collar_z_top = SHOULDER_Z + 0.01
collar_z_bot = SHOULDER_Z - 0.10

shirt_verts = [
    (-collar_w, -collar_d, collar_z_top),
    ( collar_w, -collar_d, collar_z_top),
    ( collar_w * 1.5, -collar_d, collar_z_top - 0.03),
    (-collar_w * 1.5, -collar_d, collar_z_top - 0.03),
    ( 0, -collar_d - 0.005, collar_z_bot),
    (-collar_w * 0.3, -collar_d, collar_z_bot + 0.02),
    ( collar_w * 0.3, -collar_d, collar_z_bot + 0.02),
]
shirt_faces = [
    (3, 0, 5, 4),  # left V
    (0, 1, 6, 5),  # center
    (1, 2, 4, 6),  # right V
    (5, 6, 4),      # bottom triangle
]
shirt_obj = make_obj_from_pydata("Shirt", shirt_verts, shirt_faces, shirt_mat)
all_mesh_objects.append(shirt_obj)


# ── Zipper line down front ─────────────────────────────
zip_w = 0.005
zip_front = -td * 0.91
zip_verts = [
    (-zip_w, zip_front, SHOULDER_Z - 0.06),
    ( zip_w, zip_front, SHOULDER_Z - 0.06),
    ( zip_w, zip_front, HIP_Z + 0.02),
    (-zip_w, zip_front, HIP_Z + 0.02),
]
zip_faces = [(0, 1, 2, 3)]
zip_obj = make_obj_from_pydata("Zipper", zip_verts, zip_faces, zipper_mat)
all_mesh_objects.append(zip_obj)


# ── Drawstrings (thin quad strips) ─────────────────────
for side, sx in [("L", -1), ("R", 1)]:
    dx = sx * 0.02
    sw = 0.004  # string half-width
    pts = [
        (dx, -collar_d - 0.005, collar_z_top - 0.02),
        (dx + sx * 0.005, -collar_d - 0.008, collar_z_top - 0.10),
        (dx + sx * 0.01, -collar_d - 0.006, collar_z_top - 0.18),
        (dx + sx * 0.008, -collar_d - 0.008, collar_z_top - 0.23),
    ]
    # Build a thin ribbon from the path points
    sv = []
    for px, py, pz in pts:
        sv.append((px - sw, py, pz))
        sv.append((px + sw, py, pz))
    sf = []
    for j in range(len(pts) - 1):
        b = j * 2
        sf.append((b, b+1, b+3, b+2))
    string_obj = make_obj_from_pydata(f"String.{side}", sv, sf, string_mat)
    all_mesh_objects.append(string_obj)


# ════════════════════════════════════════════════════════
# ARMS — tapered cylinders with hoodie/skin split
# ════════════════════════════════════════════════════════
for side, sx in [("L", -1), ("R", 1)]:
    ax = sx * SHOULDER_X

    # Upper arm (hoodie sleeve) — tapered
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=ARM_RAD_TOP, depth=UPPER_ARM_LEN,
        location=(ax, 0, UPPER_ARM_Z))
    ua = make_part(f"UpperArm.{side}", hoodie_mat)
    taper_cylinder(ua, top_factor=1.0, bot_factor=0.80)
    all_mesh_objects.append(ua)

    # Sleeve cuff ring (slightly wider, darker)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=ARM_RAD_TOP * 0.88, depth=0.025,
        location=(ax, 0, ELBOW_Z + 0.012))
    cuff = make_part(f"SleeveCuff.{side}", hoodie_dark)
    all_mesh_objects.append(cuff)

    # Lower arm (skin) — tapered
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=ARM_RAD_BOT * 1.05, depth=LOWER_ARM_LEN,
        location=(ax, 0, LOWER_ARM_Z))
    la = make_part(f"LowerArm.{side}", skin_mat)
    taper_cylinder(la, top_factor=1.0, bot_factor=0.80)
    all_mesh_objects.append(la)

    # Hand — small box with finger suggestion
    hand_verts = [
        # Palm (4 verts)
        (-HAND_W, -HAND_D, HAND_H/2),
        ( HAND_W, -HAND_D, HAND_H/2),
        ( HAND_W,  HAND_D, HAND_H/2),
        (-HAND_W,  HAND_D, HAND_H/2),
        # Finger tips (narrower, slightly forward)
        (-HAND_W*0.8, -HAND_D*1.1, -HAND_H/2),
        ( HAND_W*0.8, -HAND_D*1.1, -HAND_H/2),
        ( HAND_W*0.5,  HAND_D*0.8, -HAND_H/2),
        (-HAND_W*0.5,  HAND_D*0.8, -HAND_H/2),
        # Thumb bump (one side)
        (HAND_W*1.3 * sx, -HAND_D*0.3, HAND_H*0.1),
    ]
    # Offset to hand position
    hand_verts = [(x + ax, y, z + HAND_Z) for x, y, z in hand_verts]

    hand_faces = [
        (0, 1, 2, 3),   # top
        (4, 7, 6, 5),   # bottom
        (0, 4, 5, 1),   # front
        (2, 6, 7, 3),   # back
        (0, 3, 7, 4),   # left
        (1, 5, 6, 2),   # right
        # Thumb
        (0, 8, 1) if sx > 0 else (0, 1, 8),
        (0, 8, 4) if sx > 0 else (4, 8, 0),
        (1, 8, 5) if sx < 0 else (5, 8, 1),
    ]
    hand_obj = make_obj_from_pydata(f"Hand.{side}", hand_verts, hand_faces, skin_mat)
    all_mesh_objects.append(hand_obj)


# ════════════════════════════════════════════════════════
# LEGS — tapered jeans
# ════════════════════════════════════════════════════════
for side, sx in [("L", -1), ("R", 1)]:
    lx = sx * HIP_SPREAD

    # Upper leg (jeans) — tapered
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=LEG_RAD_TOP, depth=UPPER_LEG_LEN,
        location=(lx, 0, KNEE_Z + UPPER_LEG_LEN / 2))
    ul = make_part(f"UpperLeg.{side}", jeans_mat)
    taper_cylinder(ul, top_factor=1.15, bot_factor=0.85)
    all_mesh_objects.append(ul)

    # Lower leg (jeans, slightly darker at bottom) — tapered
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=LEG_RAD_BOT * 1.1, depth=LOWER_LEG_LEN,
        location=(lx, 0, ANKLE_Z + LOWER_LEG_LEN / 2))
    ll = make_part(f"LowerLeg.{side}", jeans_mat)
    taper_cylinder(ll, top_factor=1.1, bot_factor=0.82)
    all_mesh_objects.append(ll)

    # Jean cuff
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=LEG_RAD_BOT * 0.93, depth=0.025,
        location=(lx, 0, ANKLE_Z + 0.02))
    jcuff = make_part(f"JeanCuff.{side}", jeans_dark)
    all_mesh_objects.append(jcuff)

    # ── Shoe — sneaker shape from raw verts ──
    fx = lx
    # Shoe body
    shoe_verts = [
        # Sole bottom (0-5)
        (-FOOT_W,     -FOOT_L*0.35, 0.0),     # 0: back-left bottom
        ( FOOT_W,     -FOOT_L*0.35, 0.0),     # 1: back-right bottom
        ( FOOT_W*0.9,  FOOT_L*0.55, 0.0),     # 2: front-right bottom
        ( FOOT_W*0.75, FOOT_L*0.65, 0.0),     # 3: toe-right bottom
        (-FOOT_W*0.75, FOOT_L*0.65, 0.0),     # 4: toe-left bottom
        (-FOOT_W*0.9,  FOOT_L*0.55, 0.0),     # 5: front-left bottom
        # Sole top / shoe base (6-11)
        (-FOOT_W,     -FOOT_L*0.35, 0.025),   # 6: back-left sole top
        ( FOOT_W,     -FOOT_L*0.35, 0.025),   # 7: back-right sole top
        ( FOOT_W*0.9,  FOOT_L*0.55, 0.025),   # 8: front-right sole top
        ( FOOT_W*0.75, FOOT_L*0.65, 0.02),    # 9: toe-right sole top
        (-FOOT_W*0.75, FOOT_L*0.65, 0.02),    # 10: toe-left sole top
        (-FOOT_W*0.9,  FOOT_L*0.55, 0.025),   # 11: front-left sole top
        # Upper shoe (12-17)
        (-FOOT_W*0.92, -FOOT_L*0.32, FOOT_H),       # 12: back-left top
        ( FOOT_W*0.92, -FOOT_L*0.32, FOOT_H),       # 13: back-right top
        ( FOOT_W*0.82,  FOOT_L*0.35, FOOT_H*0.65),  # 14: mid-right top
        ( FOOT_W*0.65,  FOOT_L*0.55, FOOT_H*0.40),  # 15: toe-right top
        (-FOOT_W*0.65,  FOOT_L*0.55, FOOT_H*0.40),  # 16: toe-left top
        (-FOOT_W*0.82,  FOOT_L*0.35, FOOT_H*0.65),  # 17: mid-left top
        # Tongue peak (18)
        (0, FOOT_L*0.10, FOOT_H*1.05),
    ]
    shoe_verts = [(x + fx, y, z) for x, y, z in shoe_verts]

    shoe_faces = [
        # Sole bottom (triangulated — no n-gons)
        (0, 5, 1), (5, 4, 1), (4, 3, 1), (3, 2, 1),
        # Sole sides
        (0, 1, 7, 6), (1, 2, 8, 7), (2, 3, 9, 8),
        (3, 4, 10, 9), (4, 5, 11, 10), (5, 0, 6, 11),
        # Shoe body sides (sole top to upper)
        (6, 7, 13, 12), (7, 8, 14, 13), (8, 9, 15, 14),
        (9, 10, 16, 15), (10, 11, 17, 16), (11, 6, 12, 17),
        # Toe cap
        (15, 16, 10, 9),
        # Tongue area
        (12, 13, 18),
        (13, 14, 18),
        (17, 12, 18),
        # Top closure
        (14, 15, 16, 17),
        (17, 18, 14),
    ]
    shoe_obj = make_obj_from_pydata(f"Shoe.{side}", shoe_verts, shoe_faces, shoe_mat)
    # Fix mesh topology and normals
    shoe_obj.data.validate(verbose=False, clean_customdata=False)
    bm = bmesh.new()
    bm.from_mesh(shoe_obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
    bm.to_mesh(shoe_obj.data)
    bm.free()
    shoe_obj.data.update()
    all_mesh_objects.append(shoe_obj)

    # Sole accent (white stripe)
    sole_verts = [
        (-FOOT_W*1.01, -FOOT_L*0.33, 0.005),
        ( FOOT_W*1.01, -FOOT_L*0.33, 0.005),
        ( FOOT_W*0.92,  FOOT_L*0.56, 0.005),
        (-FOOT_W*0.92,  FOOT_L*0.56, 0.005),
        (-FOOT_W*1.01, -FOOT_L*0.33, 0.022),
        ( FOOT_W*1.01, -FOOT_L*0.33, 0.022),
        ( FOOT_W*0.92,  FOOT_L*0.56, 0.018),
        (-FOOT_W*0.92,  FOOT_L*0.56, 0.018),
    ]
    sole_verts = [(x + fx, y, z) for x, y, z in sole_verts]
    sole_faces = [
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        (4, 5, 6, 7),  # top
    ]
    sole_obj = make_obj_from_pydata(f"SoleStripe.{side}", sole_verts, sole_faces, shoe_sole)
    all_mesh_objects.append(sole_obj)


# ════════════════════════════════════════════════════════
# ARMATURE
# ════════════════════════════════════════════════════════
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
armature_obj = bpy.context.active_object
armature_obj.name = "CharacterRig"
armature = armature_obj.data
armature.name = "CharacterArmature"

# Remove default bone
armature.edit_bones.remove(armature.edit_bones[0])


def add_bone(name, head, tail, parent_name=None, connect=False):
    bone = armature.edit_bones.new(name)
    bone.head = Vector(head)
    bone.tail = Vector(tail)
    if parent_name and parent_name in armature.edit_bones:
        bone.parent = armature.edit_bones[parent_name]
        bone.use_connect = connect
    return bone


# Spine chain
add_bone("Spine", (0, 0, HIP_Z), (0, 0, TORSO_Z))
add_bone("Chest", (0, 0, TORSO_Z), (0, 0, SHOULDER_Z), "Spine", connect=True)
add_bone("Neck", (0, 0, SHOULDER_Z), (0, 0, NECK_Z), "Chest", connect=True)
add_bone("Head", (0, 0, NECK_Z), (0, 0, HEAD_Z + HEAD_H), "Neck", connect=True)

# Arms
for side, sx in [("L", -1), ("R", 1)]:
    ax = sx * SHOULDER_X
    add_bone(f"UpperArm.{side}",
             (ax, 0, SHOULDER_Z), (ax, 0, ELBOW_Z), "Chest")
    add_bone(f"LowerArm.{side}",
             (ax, 0, ELBOW_Z), (ax, 0, WRIST_Z),
             f"UpperArm.{side}", connect=True)
    add_bone(f"Hand.{side}",
             (ax, 0, WRIST_Z), (ax, 0, WRIST_Z - HAND_H),
             f"LowerArm.{side}", connect=True)

# Legs
for side, sx in [("L", -1), ("R", 1)]:
    lx = sx * HIP_SPREAD
    add_bone(f"UpperLeg.{side}",
             (lx, 0, HIP_Z), (lx, 0, KNEE_Z), "Spine")
    add_bone(f"LowerLeg.{side}",
             (lx, 0, KNEE_Z), (lx, 0, ANKLE_Z),
             f"UpperLeg.{side}", connect=True)
    add_bone(f"Foot.{side}",
             (lx, 0, ANKLE_Z), (lx, 0.12, ANKLE_Z),
             f"LowerLeg.{side}", connect=True)

bpy.ops.object.mode_set(mode='OBJECT')


# ════════════════════════════════════════════════════════
# PARENT MESHES TO ARMATURE
# ════════════════════════════════════════════════════════
mesh_bone_map = {
    "Head": "Head",
    "Hair": "Head",
    "HairBang": "Head",
    "HairBack": "Head",
    "Neck": "Neck",
    "Torso": "Chest",
    "Hood": "Chest",
    "Shirt": "Chest",
    "Zipper": "Chest",
    "String.L": "Chest",
    "String.R": "Chest",
}
for side in ["L", "R"]:
    mesh_bone_map[f"UpperArm.{side}"] = f"UpperArm.{side}"
    mesh_bone_map[f"SleeveCuff.{side}"] = f"UpperArm.{side}"
    mesh_bone_map[f"LowerArm.{side}"] = f"LowerArm.{side}"
    mesh_bone_map[f"Hand.{side}"] = f"Hand.{side}"
    mesh_bone_map[f"UpperLeg.{side}"] = f"UpperLeg.{side}"
    mesh_bone_map[f"LowerLeg.{side}"] = f"LowerLeg.{side}"
    mesh_bone_map[f"JeanCuff.{side}"] = f"LowerLeg.{side}"
    mesh_bone_map[f"Shoe.{side}"] = f"Foot.{side}"
    mesh_bone_map[f"SoleStripe.{side}"] = f"Foot.{side}"

for mesh_obj in all_mesh_objects:
    bone_name = mesh_bone_map.get(mesh_obj.name)
    if not bone_name:
        continue

    mesh_obj.parent = armature_obj
    mesh_obj.parent_type = 'OBJECT'

    # Add armature modifier (only for real meshes, not edge-only)
    if mesh_obj.data.polygons:
        mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = armature_obj

    vg = mesh_obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(mesh_obj.data.vertices))), 1.0, 'REPLACE')


# ════════════════════════════════════════════════════════
# WALK CYCLE ANIMATION
# ════════════════════════════════════════════════════════
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = WALK_FRAMES
scene.render.fps = 24

action = bpy.data.actions.new("WalkCycle")
armature_obj.animation_data_create()
armature_obj.animation_data.action = action

bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='POSE')

pose_bones = armature_obj.pose.bones

for pb in pose_bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)


def set_keyframe(bone_name, frame, rotation_euler, loc=None):
    pb = pose_bones[bone_name]
    pb.rotation_euler = Euler(rotation_euler)
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert(data_path="location", frame=frame)


# Walk cycle parameters
LEG_SWING = 0.42
ARM_SWING = 0.32
TORSO_BOB = 0.010
CHEST_TWIST = 0.055
HEAD_SWAY = 0.03

frames = [1, 7, 13, 19, WALK_FRAMES + 1]

r_uleg  = [ LEG_SWING,  0.0,  -LEG_SWING,  0.0,   LEG_SWING]
l_uleg  = [-LEG_SWING,  0.0,   LEG_SWING,  0.0,  -LEG_SWING]
r_lleg  = [-0.20,      -0.55, -0.10,       -0.55, -0.20]
l_lleg  = [-0.10,      -0.55, -0.20,       -0.55, -0.10]
r_uarm  = [-ARM_SWING,  0.0,   ARM_SWING,   0.0,  -ARM_SWING]
l_uarm  = [ ARM_SWING,  0.0,  -ARM_SWING,   0.0,   ARM_SWING]
r_larm  = [ 0.12,       0.30,  0.08,        0.30,  0.12]
l_larm  = [ 0.08,       0.30,  0.12,        0.30,  0.08]
sp_bob  = [-TORSO_BOB,  TORSO_BOB, -TORSO_BOB, TORSO_BOB, -TORSO_BOB]
ch_twst = [ CHEST_TWIST, 0.0, -CHEST_TWIST, 0.0,   CHEST_TWIST]
hd_sway = [ HEAD_SWAY,  0.0,  -HEAD_SWAY,   0.0,   HEAD_SWAY]

for i, f in enumerate(frames):
    set_keyframe("UpperLeg.R", f, (r_uleg[i], 0, 0))
    set_keyframe("UpperLeg.L", f, (l_uleg[i], 0, 0))
    set_keyframe("LowerLeg.R", f, (r_lleg[i], 0, 0))
    set_keyframe("LowerLeg.L", f, (l_lleg[i], 0, 0))
    set_keyframe("UpperArm.R", f, (r_uarm[i], 0, 0))
    set_keyframe("UpperArm.L", f, (l_uarm[i], 0, 0))
    set_keyframe("LowerArm.R", f, (r_larm[i], 0, 0))
    set_keyframe("LowerArm.L", f, (l_larm[i], 0, 0))
    set_keyframe("Spine", f, (0, 0, 0), loc=(0, 0, sp_bob[i]))
    set_keyframe("Chest", f, (0, 0, ch_twst[i]))
    set_keyframe("Head", f, (sp_bob[i] * 1.5, 0, hd_sway[i]))


# Make F-curves cyclic (Blender 5.0+ layered action API)
def get_fcurves_from_action(act):
    if hasattr(act, 'layers'):
        fcurves = []
        for layer in act.layers:
            for strip in layer.strips:
                for channelbag in strip.channelbags:
                    fcurves.extend(channelbag.fcurves)
        return fcurves
    if hasattr(act, 'fcurves'):
        return list(act.fcurves)
    return []

for fcurve in get_fcurves_from_action(action):
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'
    mod = fcurve.modifiers.new(type='CYCLES')
    mod.mode_before = 'REPEAT'
    mod.mode_after = 'REPEAT'

bpy.ops.object.mode_set(mode='OBJECT')


# ════════════════════════════════════════════════════════
# EXPORT GLB
# ════════════════════════════════════════════════════════
bpy.ops.object.select_all(action='SELECT')

bpy.ops.export_scene.gltf(
    filepath=OUTPUT_FILE,
    export_format='GLB',
    export_materials='EXPORT',
    export_animations=True,
    export_cameras=False,
    export_lights=False,
    export_apply=False,
    check_existing=False,
)

mesh_count = len([o for o in bpy.data.objects if o.type == 'MESH'])
vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
print(f"\n✓ Exported GLB to: {OUTPUT_FILE}")
print(f"  Meshes: {mesh_count}  Verts: {vert_count}  Bones: {len(armature.bones)}")
print(f"  Materials: {len(bpy.data.materials)}")


# ════════════════════════════════════════════════════════
# RENDER THUMBNAIL
# ════════════════════════════════════════════════════════
scene.frame_set(1)

# Camera target empty at character center
char_center_z = (HEAD_Z + GROUND) / 2
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, char_center_z))
cam_target = bpy.context.active_object
cam_target.name = "CamTarget"

bpy.ops.object.camera_add(location=(3.8, -3.8, 1.5))
camera = bpy.context.active_object
camera.name = "ThumbCamera"

cam_track = camera.constraints.new(type='TRACK_TO')
cam_track.target = cam_target
cam_track.track_axis = 'TRACK_NEGATIVE_Z'
cam_track.up_axis = 'UP_Y'

scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(5, -3, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (0.95, 0.93, 1.0)

bpy.ops.object.light_add(type='AREA', location=(-4, 3, 6))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 60.0
fill.data.color = (0.7, 0.8, 1.0)

# Rim light for edge definition
bpy.ops.object.light_add(type='SPOT', location=(-1, 3, 4))
rim = bpy.context.active_object
rim.name = "Rim"
rim.data.energy = 150.0
rim.data.spot_size = math.radians(45)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 600
scene.render.resolution_y = 600
scene.render.film_transparent = True
scene.render.filepath = THUMBNAIL_FILE
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

bpy.ops.render.render(write_still=True)

print(f"✓ Rendered thumbnail to: {THUMBNAIL_FILE}")

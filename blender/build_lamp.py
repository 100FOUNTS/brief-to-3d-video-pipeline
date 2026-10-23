"""The "Arco" lamp in Blender, built with code (bpy). Phase 4 of the exercise.

Usage (headless):
    blender -b --factory-startup -P blender/build_lamp.py -- --out out/blender [--frames 5] [--glb out/lamp.glb] [--blend out/blender/lamp.blend]
                                                           [--anim] [--res 1280x720] [--samples 64] [--no-render]

Convention: Z up (Blender). The lamp lies in the XZ plane and the camera looks from -Y.
The glTF is exported with Y up, like the Three.js viewer (Blender x,y,z -> glTF x,z,-y).
Hierarchy (so the unfolding can be animated):
    lamp (root empty)
      base
      pivot-1 (on top of the base, rotates a1)
        lower-arm
        pivot-2 (at the end of the lower arm, rotates a2-a1)
          lower-joint, upper-arm
          pivot-3 (at the end of the upper arm, rotates a3-a2)
            upper-joint, shade, bulb (+ light)
"""
import sys
import math
import argparse
import bpy
import bmesh
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- parameters
POSE = dict(a1=-30.0, a2=58.0, a3=162.0, length1=2.4, length2=2.3, shade_length=1.1)   # degrees from the vertical
FOLDED = dict(a1=-4.0, a2=104.0, a3=172.0)                                               # starting pose of the animation
JOINT0_HEIGHT = 0.26                                                                     # above the base collar
COLORS = dict(background="#0f1115", black="#242933", brass="#b8893a", floor="#1d2129", warm_light="#ffb703")


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="out/blender")
    p.add_argument("--frames", type=int, default=5)
    p.add_argument("--glb", default="")
    p.add_argument("--blend", default="")
    p.add_argument("--anim", action="store_true", help="renders the unfolding animation (5 s) instead of the camera orbit")
    p.add_argument("--res", default="1280x720")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--brief", default="", help="brief.json: the palette (background, metal, brass, floor, accent) comes from there")
    return p.parse_args(argv)


def hex_to_rgba(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    srgb_to_linear = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), a)


# ---------------------------------------------------------------- materials
def material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = hex_to_rgba(color)
    n.inputs["Metallic"].default_value = metallic
    n.inputs["Roughness"].default_value = roughness
    if emission:
        n.inputs["Emission Color"].default_value = hex_to_rgba(emission)
        n.inputs["Emission Strength"].default_value = emission_strength
    return m


# ---------------------------------------------------------------- geometry
def object_from_bmesh(name, bm, mat, smooth=True, parent=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    if bevel > 0:
        b = ob.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 4
        b.limit_method = "ANGLE"
    if parent is not None:
        ob.parent = parent
    return ob


def cylinder(name, r1, r2, depth, center, mat, parent, segments=64, open_ended=False):
    """Truncated cone with a local Z axis: r1 at the -Z end, r2 at the +Z end."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=not open_ended, cap_tris=False, segments=segments, radius1=r1, radius2=r2, depth=depth,
                          matrix=Matrix.Translation(center))
    return object_from_bmesh(name, bm, mat, parent=parent)


def box(name, width, length, center, mat, parent, bevel):
    """Box with its long side along local Z, with a bevel."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(center) @ Matrix.Diagonal((width, width, length, 1.0)))
    return object_from_bmesh(name, bm, mat, smooth=False, parent=parent, bevel=bevel)


def sphere(name, radius, center, mat, parent):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius, matrix=Matrix.Translation(center))
    return object_from_bmesh(name, bm, mat, parent=parent)


def ring(name, major, minor, center, mat, parent, normal="Y"):
    """Hand-built torus. normal='Y': the ring faces the camera (joints); 'Z': horizontal (base)."""
    bm = bmesh.new()
    seg_major, seg_minor = 64, 12
    verts = []
    for i in range(seg_major):
        a = 2 * math.pi * i / seg_major
        row = []
        for j in range(seg_minor):
            b = 2 * math.pi * j / seg_minor
            x = (major + minor * math.cos(b)) * math.cos(a)
            y = (major + minor * math.cos(b)) * math.sin(a)
            z = minor * math.sin(b)
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for i in range(seg_major):
        for j in range(seg_minor):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg_major][j], verts[(i + 1) % seg_major][(j + 1) % seg_minor], verts[i][(j + 1) % seg_minor]))
    rot = Matrix.Rotation(math.pi / 2, 4, "X") if normal == "Y" else Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(center) @ rot, verts=bm.verts)
    return object_from_bmesh(name, bm, mat, parent=parent)


def empty(name, parent=None, loc=(0, 0, 0), rot_y_degrees=0.0):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.2
    e.location = loc
    e.rotation_euler = (0, math.radians(rot_y_degrees), 0)
    bpy.context.collection.objects.link(e)
    if parent is not None:
        e.parent = parent
    return e


# ---------------------------------------------------------------- the lamp
def build_lamp(mats):
    p = POSE
    root = empty("lamp")

    # 1. Base
    base = empty("base", root)
    cylinder("base-body", 1.08, 1.0, 0.16, (0, 0, 0.08), mats["black"], base)
    cylinder("base-collar", 0.42, 0.34, 0.2, (0, 0, 0.17), mats["black"], base, segments=48)
    ring("base-ring", 0.4, 0.035, (0, 0, 0.27), mats["brass"], base, normal="Z")

    # 2. Articulated chain: each pivot inherits the rotation of the previous one
    pivot1 = empty("pivot-1", root, (0, 0, JOINT0_HEIGHT), p["a1"])
    lower_arm = empty("lower-arm", pivot1)
    box("lower-arm-body", 0.2, p["length1"], (0, 0, p["length1"] / 2), mats["black"], lower_arm, bevel=0.05)

    pivot2 = empty("pivot-2", pivot1, (0, 0, p["length1"]), p["a2"] - p["a1"])
    joint1 = empty("lower-joint", pivot2)
    sphere("lower-joint-sphere", 0.26, (0, 0, 0), mats["black"], joint1)
    ring("lower-joint-ring", 0.27, 0.035, (0, 0, 0), mats["brass"], joint1)
    upper_arm = empty("upper-arm", pivot2)
    box("upper-arm-body", 0.18, p["length2"], (0, 0, p["length2"] / 2), mats["black"], upper_arm, bevel=0.045)

    pivot3 = empty("pivot-3", pivot2, (0, 0, p["length2"]), p["a3"] - p["a2"])
    joint2 = empty("upper-joint", pivot3)
    sphere("upper-joint-sphere", 0.23, (0, 0, 0), mats["black"], joint2)
    ring("upper-joint-ring", 0.24, 0.035, (0, 0, 0), mats["brass"], joint2)

    # 3. Shade: open cone, narrow next to the joint (local +Z axis = light direction)
    L = p["shade_length"]
    shade = empty("shade", pivot3)
    outer = cylinder("shade-outer", 0.2, 0.64, L, (0, 0, L / 2 + 0.05), mats["brass"], shade, open_ended=True)
    inner = cylinder("shade-inner", 0.195, 0.635, L - 0.01, (0, 0, L / 2 + 0.05), mats["inside"], shade, open_ended=True)
    for o in (outer, inner):
        sol = o.modifiers.new("Thickness", "SOLIDIFY")
        sol.thickness = 0.02 if o is outer else 0.005
    cylinder("shade-neck", 0.17, 0.2, 0.18, (0, 0, 0.07), mats["black"], shade, segments=32)

    # 4. Bulb and its light
    bulb = empty("bulb", pivot3, (0, 0, L * 0.72))
    bulb_sphere = sphere("bulb-sphere", 0.24, (0, 0, 0), mats["bulb"], bulb)
    bulb_sphere.visible_shadow = False        # the light is inside the sphere: without this the bulb itself blocks its light
    light = bpy.data.lights.new("bulb-light", "POINT")
    light.color = hex_to_rgba(COLORS["warm_light"])[:3]
    light.energy = 750.0        # with more power, the AgX tone mapping desaturates the glow to gray
    light.shadow_soft_size = 0.2
    light_ob = bpy.data.objects.new("bulb-light", light)
    bpy.context.collection.objects.link(light_ob)
    light_ob.parent = bulb
    light_ob.location = (0, 0, 0.12)
    return dict(root=root, p1=pivot1, p2=pivot2, p3=pivot3, bulb=bulb)


# ---------------------------------------------------------------- scene
def area_light(name, loc, energy, size, color="#ffffff", target=Vector((0.2, 0, 1.9))):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.size = energy, size
    d.color = hex_to_rgba(color)[:3]
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def apply_brief(path):
    """Replaces the colors with those of brief.json (palette.background/metal/brass/floor/accent)."""
    import json
    pal = json.load(open(path, encoding="utf-8"))["palette"]
    COLORS.update(background=pal["background"], black=pal["metal"], brass=pal["brass"], floor=pal["floor"], warm_light=pal["accent"])


def prepare_scene(args):
    if args.brief:
        apply_brief(args.brief)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    width, height = (int(v) for v in args.res.lower().split("x"))
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = width, height, 100
    sc.eevee.taa_render_samples = args.samples
    sc.eevee.use_raytracing = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "None"

    # dark world (brief tone) with little ambient light
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hex_to_rgba(COLORS["background"])
    bg.inputs["Strength"].default_value = 0.5
    sc.world = world

    mats = dict(
        black=material("matte-black-metal", COLORS["black"], metallic=0.85, roughness=0.42),
        brass=material("brushed-brass", COLORS["brass"], metallic=1.0, roughness=0.3),
        inside=material("shade-inside", "#f4e3b8", roughness=0.8, emission=COLORS["warm_light"], emission_strength=0.5),
        bulb=material("led-bulb", "#fff3d6", roughness=0.4, emission=COLORS["warm_light"], emission_strength=25.0),
        floor=material("floor", COLORS["floor"], roughness=0.55),
    )

    # floor
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=300.0)   # huge: the edge is never visible
    object_from_bmesh("floor", bm, mats["floor"], smooth=False)

    lamp = build_lamp(mats)

    # three lights: key (warm, front-left), fill (cool, right), rim (behind)
    area_light("light-key", (-5.0, -6.0, 6.5), 190, 4.0, "#fff1dc")
    area_light("light-fill", (6.5, -4.0, 3.0), 70, 5.0, "#cfe0ff")
    area_light("light-rim", (1.5, 6.0, 5.5), 250, 3.0, "#ffffff")

    # camera looking at the center of the lamp
    center = bpy.data.objects.new("camera-center", None)
    center.location = (0.2, 0.0, 1.9)
    bpy.context.collection.objects.link(center)
    cam_d = bpy.data.cameras.new("camera")
    cam_d.lens = 50
    cam = bpy.data.objects.new("camera", cam_d)
    bpy.context.collection.objects.link(cam)
    t = cam.constraints.new("TRACK_TO")
    t.target, t.track_axis, t.up_axis = center, "TRACK_NEGATIVE_Z", "UP_Y"
    sc.camera = cam
    return sc, cam, center, lamp


def place_camera(cam, center, azimuth_degrees, elevation_degrees=12.0, radius=12.0):
    az, el = math.radians(azimuth_degrees), math.radians(elevation_degrees)
    cam.location = center.location + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * radius


def render(sc, path):
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("RENDER", path)


def animate_unfolding(lamp, sc, fps=24, seconds=5.0):
    """Keyframes of the three pivots: from the folded pose to the unfolded one, with a short pause at the start and at the end."""
    sc.render.fps = fps
    f0, f1 = 1, int(fps * seconds)
    key = lambda ob, ang, f: (setattr(ob, "rotation_euler", (0, math.radians(ang), 0)), ob.keyframe_insert("rotation_euler", frame=f))
    rel = lambda a, b: a - b
    folded = (FOLDED["a1"], rel(FOLDED["a2"], FOLDED["a1"]), rel(FOLDED["a3"], FOLDED["a2"]))
    final = (POSE["a1"], rel(POSE["a2"], POSE["a1"]), rel(POSE["a3"], POSE["a2"]))
    for ob, start, end in zip((lamp["p1"], lamp["p2"], lamp["p3"]), folded, final):
        key(ob, start, f0); key(ob, start, f0 + int(fps * 0.5)); key(ob, end, f1 - int(fps * 0.5)); key(ob, end, f1)
        for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, "fcurves") else []:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
    sc.frame_start, sc.frame_end = f0, f1


def main():
    args = parse_args()
    import os
    os.makedirs(args.out, exist_ok=True)
    sc, cam, center, lamp = prepare_scene(args)
    place_camera(cam, center, -25.0, 12.0)      # default pose: so the saved .blend opens with a useful camera (it used to stay at the origin)

    if args.blend:
        os.makedirs(os.path.dirname(os.path.abspath(args.blend)), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.blend))

    if args.glb:
        os.makedirs(os.path.dirname(os.path.abspath(args.glb)), exist_ok=True)
        # the glTF carries only the lamp; it is exported with modifiers applied and without the camera or area lights
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob.name == "lamp" or ob.parent is not None and _descends_from(ob, "lamp"):
                ob.select_set(True)
        bpy.ops.export_scene.gltf(filepath=os.path.abspath(args.glb), export_format="GLB", use_selection=True, export_apply=True,
                                  export_yup=True, export_lights=True, export_animations=False)
        print("GLB", args.glb)

    if args.no_render:
        return
    if args.anim:
        animate_unfolding(lamp, sc)
        place_camera(cam, center, -25.0, 12.0)
        sc.render.filepath = os.path.abspath(os.path.join(args.out, "unfold_"))
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
        print("ANIM", sc.frame_start, sc.frame_end)
        return
    n = max(1, args.frames)
    for i in range(n):
        az = -55.0 + 110.0 * (i / (n - 1) if n > 1 else 0.5)      # partial camera orbit: from -55° to +55°
        place_camera(cam, center, az)
        render(sc, os.path.abspath(os.path.join(args.out, f"turn_{i:02d}.png")))


def _descends_from(ob, name):
    p = ob.parent
    while p is not None:
        if p.name == name:
            return True
        p = p.parent
    return False


main()

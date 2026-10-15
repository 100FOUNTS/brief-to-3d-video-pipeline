"""Lámpara "Arco" en Blender por código (bpy). Fase 4 del ejercicio.

Uso (sin ventana):
    blender -b --factory-startup -P blender/build_lamp.py -- --out out/blender [--frames 5] [--glb out/lampara.glb] [--blend out/blender/lampara.blend]
                                                           [--anim] [--res 1280x720] [--samples 64] [--sin-render]

Convención: Z hacia arriba (Blender). La lámpara está en el plano XZ y la cámara mira desde -Y.
El glTF se exporta con Y hacia arriba, igual que el visor de Three.js (Blender x,y,z -> glTF x,z,-y).
Jerarquía (para poder animar el despliegue):
    lampara (vacío raíz)
      base
      pivote-1 (en lo alto de la base, gira a1)
        brazo-inferior
        pivote-2 (al final del brazo inferior, gira a2-a1)
          articulacion-inferior, brazo-superior
          pivote-3 (al final del brazo superior, gira a3-a2)
            articulacion-superior, pantalla, bombilla (+ luz)
"""
import sys
import math
import argparse
import bpy
import bmesh
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- parámetros
POSE = dict(a1=-30.0, a2=58.0, a3=162.0, largo1=2.4, largo2=2.3, largo_pantalla=1.1)   # grados desde la vertical
PLEGADA = dict(a1=-4.0, a2=104.0, a3=172.0)                                              # postura de partida de la animación
ALTURA_J0 = 0.26                                                                         # arriba del collar de la base
COLORES = dict(fondo="#0f1115", negro="#242933", laton="#b8893a", suelo="#1d2129", luz_calida="#ffb703")


def argumentos():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="out/blender")
    p.add_argument("--frames", type=int, default=5)
    p.add_argument("--glb", default="")
    p.add_argument("--blend", default="")
    p.add_argument("--anim", action="store_true", help="renderiza la animación de despliegue (5 s) en vez de la vuelta de cámara")
    p.add_argument("--res", default="1280x720")
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--sin-render", action="store_true")
    return p.parse_args(argv)


def hex_a_rgba(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    srgb_a_lineal = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (srgb_a_lineal(r), srgb_a_lineal(g), srgb_a_lineal(b), a)


# ---------------------------------------------------------------- materiales
def material(nombre, color, metalico=0.0, rugosidad=0.5, emision=None, intensidad_emision=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = hex_a_rgba(color)
    n.inputs["Metallic"].default_value = metalico
    n.inputs["Roughness"].default_value = rugosidad
    if emision:
        n.inputs["Emission Color"].default_value = hex_a_rgba(emision)
        n.inputs["Emission Strength"].default_value = intensidad_emision
    return m


# ---------------------------------------------------------------- geometría
def objeto_desde_bmesh(nombre, bm, mat, suave=True, padre=None, bisel=0.0):
    me = bpy.data.meshes.new(nombre)
    if suave:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    if bisel > 0:
        b = ob.modifiers.new("Bisel", "BEVEL")
        b.width = bisel
        b.segments = 4
        b.limit_method = "ANGLE"
    if padre is not None:
        ob.parent = padre
    return ob


def cilindro(nombre, r1, r2, prof, centro, mat, padre, segmentos=64, abierto=False):
    """Cono truncado con eje Z local: r1 en el extremo -Z, r2 en el +Z."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=not abierto, cap_tris=False, segments=segmentos, radius1=r1, radius2=r2, depth=prof,
                          matrix=Matrix.Translation(centro))
    return objeto_desde_bmesh(nombre, bm, mat, padre=padre)


def caja(nombre, ancho, largo, centro, mat, padre, bisel):
    """Caja con el lado largo en Z local, con bisel."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(centro) @ Matrix.Diagonal((ancho, ancho, largo, 1.0)))
    return objeto_desde_bmesh(nombre, bm, mat, suave=False, padre=padre, bisel=bisel)


def esfera(nombre, radio, centro, mat, padre):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radio, matrix=Matrix.Translation(centro))
    return objeto_desde_bmesh(nombre, bm, mat, padre=padre)


def anillo(nombre, mayor, menor, centro, mat, padre, normal="Y"):
    """Toro construido a mano. normal='Y': el anillo mira hacia la cámara (articulaciones); 'Z': horizontal (base)."""
    bm = bmesh.new()
    seg_m, seg_n = 64, 12
    verts = []
    for i in range(seg_m):
        a = 2 * math.pi * i / seg_m
        fila = []
        for j in range(seg_n):
            b = 2 * math.pi * j / seg_n
            x = (mayor + menor * math.cos(b)) * math.cos(a)
            y = (mayor + menor * math.cos(b)) * math.sin(a)
            z = menor * math.sin(b)
            fila.append(bm.verts.new((x, y, z)))
        verts.append(fila)
    for i in range(seg_m):
        for j in range(seg_n):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg_m][j], verts[(i + 1) % seg_m][(j + 1) % seg_n], verts[i][(j + 1) % seg_n]))
    rot = Matrix.Rotation(math.pi / 2, 4, "X") if normal == "Y" else Matrix.Identity(4)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(centro) @ rot, verts=bm.verts)
    return objeto_desde_bmesh(nombre, bm, mat, padre=padre)


def vacio(nombre, padre=None, loc=(0, 0, 0), rot_y_grados=0.0):
    e = bpy.data.objects.new(nombre, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = 0.2
    e.location = loc
    e.rotation_euler = (0, math.radians(rot_y_grados), 0)
    bpy.context.collection.objects.link(e)
    if padre is not None:
        e.parent = padre
    return e


# ---------------------------------------------------------------- la lámpara
def construir_lampara(mats):
    p = POSE
    raiz = vacio("lampara")

    # 1. Base
    base = vacio("base", raiz)
    cilindro("base-cuerpo", 1.08, 1.0, 0.16, (0, 0, 0.08), mats["negro"], base)
    cilindro("base-collar", 0.42, 0.34, 0.2, (0, 0, 0.17), mats["negro"], base, segmentos=48)
    anillo("base-anillo", 0.4, 0.035, (0, 0, 0.27), mats["laton"], base, normal="Z")

    # 2. Cadena articulada: cada pivote hereda la rotación del anterior
    pivote1 = vacio("pivote-1", raiz, (0, 0, ALTURA_J0), p["a1"])
    brazo_inf = vacio("brazo-inferior", pivote1)
    caja("brazo-inferior-cuerpo", 0.2, p["largo1"], (0, 0, p["largo1"] / 2), mats["negro"], brazo_inf, bisel=0.05)

    pivote2 = vacio("pivote-2", pivote1, (0, 0, p["largo1"]), p["a2"] - p["a1"])
    art1 = vacio("articulacion-inferior", pivote2)
    esfera("articulacion-inferior-esfera", 0.26, (0, 0, 0), mats["negro"], art1)
    anillo("articulacion-inferior-anillo", 0.27, 0.035, (0, 0, 0), mats["laton"], art1)
    brazo_sup = vacio("brazo-superior", pivote2)
    caja("brazo-superior-cuerpo", 0.18, p["largo2"], (0, 0, p["largo2"] / 2), mats["negro"], brazo_sup, bisel=0.045)

    pivote3 = vacio("pivote-3", pivote2, (0, 0, p["largo2"]), p["a3"] - p["a2"])
    art2 = vacio("articulacion-superior", pivote3)
    esfera("articulacion-superior-esfera", 0.23, (0, 0, 0), mats["negro"], art2)
    anillo("articulacion-superior-anillo", 0.24, 0.035, (0, 0, 0), mats["laton"], art2)

    # 3. Pantalla: cono abierto, estrecho junto a la articulación (eje +Z local = dirección de la luz)
    L = p["largo_pantalla"]
    pantalla = vacio("pantalla", pivote3)
    ext = cilindro("pantalla-exterior", 0.2, 0.64, L, (0, 0, L / 2 + 0.05), mats["laton"], pantalla, abierto=True)
    inte = cilindro("pantalla-interior", 0.195, 0.635, L - 0.01, (0, 0, L / 2 + 0.05), mats["interior"], pantalla, abierto=True)
    for o in (ext, inte):
        sol = o.modifiers.new("Grosor", "SOLIDIFY")
        sol.thickness = 0.02 if o is ext else 0.005
    cilindro("pantalla-cuello", 0.17, 0.2, 0.18, (0, 0, 0.07), mats["negro"], pantalla, segmentos=32)

    # 4. Bombilla y su luz
    bombilla = vacio("bombilla", pivote3, (0, 0, L * 0.72))
    esf_b = esfera("bombilla-esfera", 0.24, (0, 0, 0), mats["bombilla"], bombilla)
    esf_b.visible_shadow = False        # la luz está dentro de la esfera: sin esto la propia bombilla le tapa la luz
    luz = bpy.data.lights.new("luz-bombilla", "POINT")
    luz.color = hex_a_rgba(COLORES["luz_calida"])[:3]
    luz.energy = 750.0        # con más potencia, el tono AgX desatura el brillo hasta dejarlo gris
    luz.shadow_soft_size = 0.2
    lob = bpy.data.objects.new("luz-bombilla", luz)
    bpy.context.collection.objects.link(lob)
    lob.parent = bombilla
    lob.location = (0, 0, 0.12)
    return dict(raiz=raiz, p1=pivote1, p2=pivote2, p3=pivote3, bombilla=bombilla)


# ---------------------------------------------------------------- escena
def luz_area(nombre, loc, energia, tam, color="#ffffff", objetivo=Vector((0.2, 0, 1.9))):
    d = bpy.data.lights.new(nombre, "AREA")
    d.energy, d.size = energia, tam
    d.color = hex_a_rgba(color)[:3]
    o = bpy.data.objects.new(nombre, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (objetivo - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


def preparar_escena(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    ancho, alto = (int(v) for v in args.res.lower().split("x"))
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = ancho, alto, 100
    sc.eevee.taa_render_samples = args.samples
    sc.eevee.use_raytracing = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "None"

    # mundo oscuro (tono del brief) con poca luz ambiente
    mundo = bpy.data.worlds.new("mundo")
    mundo.use_nodes = True
    bg = mundo.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hex_a_rgba(COLORES["fondo"])
    bg.inputs["Strength"].default_value = 0.5
    sc.world = mundo

    mats = dict(
        negro=material("metal-negro-mate", COLORES["negro"], metalico=0.85, rugosidad=0.42),
        laton=material("laton-cepillado", COLORES["laton"], metalico=1.0, rugosidad=0.3),
        interior=material("pantalla-interior", "#f4e3b8", rugosidad=0.8, emision=COLORES["luz_calida"], intensidad_emision=0.5),
        bombilla=material("bombilla-led", "#fff3d6", rugosidad=0.4, emision=COLORES["luz_calida"], intensidad_emision=25.0),
        suelo=material("suelo", COLORES["suelo"], rugosidad=0.55),
    )

    # suelo
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=300.0)   # enorme: el borde no se ve
    suelo = objeto_desde_bmesh("suelo", bm, mats["suelo"], suave=False)

    lamp = construir_lampara(mats)

    # tres luces: principal (cálida, delante-izquierda), relleno (fría, derecha), contorno (detrás)
    luz_area("luz-principal", (-5.0, -6.0, 6.5), 190, 4.0, "#fff1dc")
    luz_area("luz-relleno", (6.5, -4.0, 3.0), 70, 5.0, "#cfe0ff")
    luz_area("luz-contorno", (1.5, 6.0, 5.5), 250, 3.0, "#ffffff")

    # cámara que mira al centro de la lámpara
    centro = bpy.data.objects.new("centro-camara", None)
    centro.location = (0.2, 0.0, 1.9)
    bpy.context.collection.objects.link(centro)
    cam_d = bpy.data.cameras.new("camara")
    cam_d.lens = 50
    cam = bpy.data.objects.new("camara", cam_d)
    bpy.context.collection.objects.link(cam)
    t = cam.constraints.new("TRACK_TO")
    t.target, t.track_axis, t.up_axis = centro, "TRACK_NEGATIVE_Z", "UP_Y"
    sc.camera = cam
    return sc, cam, centro, lamp


def poner_camara(cam, centro, azimut_grados, elevacion_grados=12.0, radio=12.0):
    az, el = math.radians(azimut_grados), math.radians(elevacion_grados)
    cam.location = centro.location + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * radio


def renderizar(sc, ruta):
    sc.render.filepath = ruta
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("RENDER", ruta)


def animar_despliegue(lamp, sc, fps=24, segundos=5.0):
    """Keyframes de los tres pivotes: de la postura plegada a la desplegada, con una pequeña pausa al principio y al final."""
    sc.render.fps = fps
    f0, f1 = 1, int(fps * segundos)
    dentro = lambda ob, ang, f: (setattr(ob, "rotation_euler", (0, math.radians(ang), 0)), ob.keyframe_insert("rotation_euler", frame=f))
    rel = lambda a, b: a - b
    plegada = (PLEGADA["a1"], rel(PLEGADA["a2"], PLEGADA["a1"]), rel(PLEGADA["a3"], PLEGADA["a2"]))
    final = (POSE["a1"], rel(POSE["a2"], POSE["a1"]), rel(POSE["a3"], POSE["a2"]))
    for ob, ini, fin in zip((lamp["p1"], lamp["p2"], lamp["p3"]), plegada, final):
        dentro(ob, ini, f0); dentro(ob, ini, f0 + int(fps * 0.5)); dentro(ob, fin, f1 - int(fps * 0.5)); dentro(ob, fin, f1)
        for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, "fcurves") else []:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
    sc.frame_start, sc.frame_end = f0, f1


def main():
    args = argumentos()
    import os
    os.makedirs(args.out, exist_ok=True)
    sc, cam, centro, lamp = preparar_escena(args)
    poner_camara(cam, centro, -25.0, 12.0)      # postura por defecto: así el .blend guardado abre con una cámara útil (antes quedaba en el origen)

    if args.blend:
        os.makedirs(os.path.dirname(os.path.abspath(args.blend)), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.blend))

    if args.glb:
        os.makedirs(os.path.dirname(os.path.abspath(args.glb)), exist_ok=True)
        # el glTF solo lleva la lámpara; se exporta con los modificadores aplicados y sin cámara ni luces de área
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob.name == "lampara" or ob.parent is not None and _desciende_de(ob, "lampara"):
                ob.select_set(True)
        bpy.ops.export_scene.gltf(filepath=os.path.abspath(args.glb), export_format="GLB", use_selection=True, export_apply=True,
                                  export_yup=True, export_lights=True, export_animations=False)
        print("GLB", args.glb)

    if args.sin_render:
        return
    if args.anim:
        animar_despliegue(lamp, sc)
        poner_camara(cam, centro, -25.0, 12.0)
        sc.render.filepath = os.path.abspath(os.path.join(args.out, "despliegue_"))
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
        print("ANIM", sc.frame_start, sc.frame_end)
        return
    n = max(1, args.frames)
    for i in range(n):
        az = -55.0 + 110.0 * (i / (n - 1) if n > 1 else 0.5)      # vuelta parcial de la cámara: de -55° a +55°
        poner_camara(cam, centro, az)
        renderizar(sc, os.path.abspath(os.path.join(args.out, f"vuelta_{i:02d}.png")))


def _desciende_de(ob, nombre):
    p = ob.parent
    while p is not None:
        if p.name == nombre:
            return True
        p = p.parent
    return False


main()

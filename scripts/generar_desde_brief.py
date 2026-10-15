#!/usr/bin/env python3
"""Genera TODO lo que depende del producto a partir de UN solo archivo: brief.json (Fase 6).

Lee el brief, lo valida (avisa si un texto no cabe o un color no tiene contraste) y escribe:
  - hyperframes/promo/index.html   <- plantillas/hyperframes-promo.template.html (FUERA del proyecto de HyperFrames: dos index con data-composition-id en la misma carpeta hacen fallar `hyperframes check`)
  - docs/guion.json                <- guion de la voz, una frase por escena, con su segundo de inicio y su ventana
  - viewer/src/brief.generated.js  <- nombre, lema y paleta para el visor 3D
Blender (blender/build_lamp.py --brief) y la música (audio/music.py --brief) leen el brief directamente.

Uso:  python3 scripts/generar_desde_brief.py [--brief brief.json] [--check | --validar]
      --check    no escribe nada: comprueba que los archivos generados ya están al día (sale con 1 si no).
      --validar  solo valida el brief (no escribe nada): para briefs de variantes, que no deben tocar los archivos del proyecto principal.

Límites (lo que el brief NO puede cambiar): la geometría de la lámpara, la estructura de 5 escenas y los 20 s de duración.
"""
import argparse, html, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
COLORES_OBLIGATORIOS = ["fondo", "fondo2", "texto", "acento", "acento_etiqueta", "laton", "metal", "suelo", "luz_neutra", "halo_bombilla"]
# Máximos de caracteres para que el texto quepa en 1920 px con la tipografía del vídeo (medidos con Montserrat 900 / IBM Plex Mono)
LIMITES = {"nombre": 7, "lema": 40, "palabra": 12, "detalle": 40, "voz_frase": 90}


def luminancia(hexa):
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb(hexa):
    return ",".join(str(int(hexa[i:i + 2], 16)) for i in (1, 3, 5))


def validar(b):
    errores, avisos = [], []
    try:
        p, ben, voz, pal = b["producto"], b["beneficios"], b["voz"], b["paleta"]
    except KeyError as e:
        return [f"falta la sección {e} en el brief"], []
    if len(ben) != 3:
        errores.append(f"el vídeo tiene 3 escenas de beneficios y el brief trae {len(ben)}")
    for clave, lim in (("nombre", LIMITES["nombre"]), ("lema", LIMITES["lema"])):
        if not p.get(clave): errores.append(f"producto.{clave} vacío")
        elif len(p[clave]) > lim: errores.append(f"producto.{clave} tiene {len(p[clave])} caracteres (máximo {lim} para que quepa en pantalla)")
    for i, x in enumerate(ben, 1):
        for clave, lim in (("palabra", LIMITES["palabra"]), ("detalle", LIMITES["detalle"]), ("voz", LIMITES["voz_frase"])):
            if not x.get(clave): errores.append(f"beneficios[{i}].{clave} vacío")
            elif len(x[clave]) > lim: errores.append(f"beneficios[{i}].{clave} tiene {len(x[clave])} caracteres (máximo {lim})")
        if not re.fullmatch(r"[a-z0-9-]+", x.get("id", "")): errores.append(f"beneficios[{i}].id debe ser minúsculas/números/guiones")
    for clave in ("apertura", "cierre", "motor", "nombre"):
        if not voz.get(clave): errores.append(f"voz.{clave} vacío")
    if voz.get("motor") not in ("kokoro", "qwen3"): errores.append("voz.motor debe ser 'kokoro' o 'qwen3'")
    for clave in COLORES_OBLIGATORIOS:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", pal.get(clave, "")): errores.append(f"paleta.{clave} debe ser un color #rrggbb")
    if not errores:
        # contraste como en 'hyperframes check' (WCAG AA): texto 4.5:1, etiquetas y acento 3:1
        if contraste(pal["texto"], pal["fondo"]) < 4.5: errores.append(f"texto sobre fondo: contraste {contraste(pal['texto'], pal['fondo']):.2f}:1 (mínimo 4.5)")
        if contraste(pal["acento_etiqueta"], pal["fondo"]) < 3: errores.append(f"acento_etiqueta sobre fondo: contraste {contraste(pal['acento_etiqueta'], pal['fondo']):.2f}:1 (mínimo 3)")
        if contraste(pal["acento"], pal["fondo"]) < 3: avisos.append(f"acento sobre fondo: contraste {contraste(pal['acento'], pal['fondo']):.2f}:1 (bajo)")
        if b.get("video", {}).get("duracion", 20) != 20: errores.append("la duración del vídeo está fija en 20 s en esta versión")
    return errores, avisos


def e(t):
    return html.escape(t, quote=False)


def render_hyperframes(b):
    plantilla = (RAIZ / "plantillas/hyperframes-promo.template.html").read_text(encoding="utf-8")
    p, pal = b["producto"], b["paleta"]
    v = {"NOMBRE": e(p["nombre"]), "LEMA": e(p["lema"]), "TEXTO": pal["texto"], "FONDO": pal["fondo"], "FONDO2": pal["fondo2"], "ACENTO": pal["acento"],
         "ACENTO_ETIQUETA": pal["acento_etiqueta"], "LATON": pal["laton"], "LUZ_NEUTRA": pal["luz_neutra"],
         "ACENTO_RGB": rgb(pal["acento"]), "LUZ_NEUTRA_RGB": rgb(pal["luz_neutra"]), "HALO_BOMBILLA_RGB": rgb(pal["halo_bombilla"])}
    for i, x in enumerate(b["beneficios"], 1):
        v[f"B{i}_PALABRA"], v[f"B{i}_DETALLE"] = e(x["palabra"]), e(x["detalle"])
    salida = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: v[m.group(1)], plantilla)
    assert "{{" not in salida
    return salida


def guion(b):
    # Una frase por escena. 'inicio' = segundo en que empieza a hablar; 'ventana' = tiempo disponible hasta la siguiente escena.
    seg = [{"id": "s1-titulo", "texto": b["voz"]["apertura"], "inicio": 2.5, "ventana": 4.2}]
    for i, x in enumerate(b["beneficios"]):
        seg.append({"id": f"s{i + 2}-{x['id']}", "texto": x["voz"], "inicio": 5.5 + 4 * i, "ventana": 3.2})
    seg.append({"id": "s5-cierre", "texto": b["voz"]["cierre"], "inicio": 17.4, "ventana": 2.0})
    return {"nota": "GENERADO por scripts/generar_desde_brief.py desde brief.json; no editar a mano. 'inicio' = segundo en que empieza a hablar; 'ventana' = segundos disponibles hasta la siguiente escena.",
            "segmentos": seg}


def visor(b):
    datos = {"nombre": b["producto"]["nombre"], "lema": b["producto"]["lema"], "descripcion": b["producto"].get("descripcion", ""), "paleta": b["paleta"]}
    return "// GENERADO por scripts/generar_desde_brief.py desde brief.json: no editar a mano.\nexport const BRIEF = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="brief.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--validar", action="store_true")
    a = ap.parse_args()
    ruta = (RAIZ / a.brief) if not pathlib.Path(a.brief).is_absolute() else pathlib.Path(a.brief)
    b = json.loads(ruta.read_text(encoding="utf-8"))
    errores, avisos = validar(b)
    for x in avisos: print("AVISO:", x)
    if errores:
        print("El brief no es válido:\n  - " + "\n  - ".join(errores)); sys.exit(2)
    if a.validar:
        print(f"OK {a.brief}: brief válido (producto '{b['producto']['nombre']}')"); sys.exit(0)
    salidas = {
        "hyperframes/promo/index.html": render_hyperframes(b),
        "docs/guion.json": json.dumps(guion(b), ensure_ascii=False, indent=2) + "\n",
        "viewer/src/brief.generated.js": visor(b),
    }
    desfasados = []
    for rel, contenido in salidas.items():
        destino = RAIZ / rel
        actual = destino.read_text(encoding="utf-8") if destino.exists() else None
        if actual != contenido:
            desfasados.append(rel)
            if not a.check: destino.write_text(contenido, encoding="utf-8")
    if a.check:
        print("al día" if not desfasados else "DESFASADOS: " + ", ".join(desfasados)); sys.exit(1 if desfasados else 0)
    print(f"OK {a.brief}: producto '{b['producto']['nombre']}' · " + (f"actualizados {len(desfasados)}: " + ", ".join(desfasados) if desfasados else "todo estaba al día"))


if __name__ == "__main__":
    main()

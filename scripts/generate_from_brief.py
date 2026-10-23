#!/usr/bin/env python3
"""Generates EVERYTHING that depends on the product from ONE file: brief.json (Phase 6).

Reads the brief, validates it (warns if a text does not fit or a color lacks contrast) and writes:
  - hyperframes/promo/index.html   <- templates/hyperframes-promo.template.html (OUTSIDE the HyperFrames project: two index files with data-composition-id in the same folder make `hyperframes check` fail)
  - docs/script.json               <- the voice script, one sentence per scene, with its start second and its window
  - viewer/src/brief.generated.js  <- name, tagline and palette for the 3D viewer
Blender (blender/build_lamp.py --brief) and the music (audio/music.py --brief) read the brief directly.

Usage:  python3 scripts/generate_from_brief.py [--brief brief.json] [--check | --validate]
        --check     writes nothing: checks that the generated files are already up to date (exits 1 if not).
        --validate  only validates the brief (writes nothing): for variant briefs, which must not touch the main project's files.

Limits (what the brief CANNOT change): the lamp geometry, the 5-scene structure and the 20 s duration.
"""
import argparse, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED_COLORS = ["background", "background2", "text", "accent", "accent_label", "brass", "metal", "floor", "neutral_light", "bulb_halo"]
# Maximum characters so the text fits in 1920 px with the video typography (measured with Montserrat 900 / IBM Plex Mono)
LIMITS = {"name": 7, "tagline": 40, "word": 12, "detail": 40, "voice_sentence": 90}


def luminance(hexa):
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb(hexa):
    return ",".join(str(int(hexa[i:i + 2], 16)) for i in (1, 3, 5))


def validate(b):
    errors, warnings = [], []
    try:
        p, ben, voice, pal = b["product"], b["benefits"], b["voice"], b["palette"]
    except KeyError as e:
        return [f"section {e} is missing from the brief"], []
    if len(ben) != 3:
        errors.append(f"the video has 3 benefit scenes and the brief has {len(ben)}")
    for key, lim in (("name", LIMITS["name"]), ("tagline", LIMITS["tagline"])):
        if not p.get(key): errors.append(f"product.{key} is empty")
        elif len(p[key]) > lim: errors.append(f"product.{key} has {len(p[key])} characters (maximum {lim} to fit on screen)")
    for i, x in enumerate(ben, 1):
        for key, lim in (("word", LIMITS["word"]), ("detail", LIMITS["detail"]), ("voice", LIMITS["voice_sentence"])):
            if not x.get(key): errors.append(f"benefits[{i}].{key} is empty")
            elif len(x[key]) > lim: errors.append(f"benefits[{i}].{key} has {len(x[key])} characters (maximum {lim})")
        if not re.fullmatch(r"[a-z0-9-]+", x.get("id", "")): errors.append(f"benefits[{i}].id must be lowercase letters, digits or hyphens")
    for key in ("opening", "closing", "engine", "name"):
        if not voice.get(key): errors.append(f"voice.{key} is empty")
    if voice.get("engine") not in ("kokoro", "qwen3"): errors.append("voice.engine must be 'kokoro' or 'qwen3'")
    colors_ok = True
    for key in REQUIRED_COLORS:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", pal.get(key, "")):
            errors.append(f"palette.{key} must be a #rrggbb color"); colors_ok = False
    if colors_ok:                                        # contrast is checked even if there are other errors, so they all show up at once
        # contrast as in 'hyperframes check' (WCAG AA): text 4.5:1, labels and accent 3:1
        if contrast(pal["text"], pal["background"]) < 4.5: errors.append(f"text on background: contrast {contrast(pal['text'], pal['background']):.2f}:1 (minimum 4.5)")
        if contrast(pal["accent_label"], pal["background"]) < 3: errors.append(f"accent_label on background: contrast {contrast(pal['accent_label'], pal['background']):.2f}:1 (minimum 3)")
        if contrast(pal["accent"], pal["background"]) < 3: warnings.append(f"accent on background: contrast {contrast(pal['accent'], pal['background']):.2f}:1 (low)")
    if b.get("video", {}).get("duration", 20) != 20: errors.append("the video duration is fixed at 20 s in this version")
    return errors, warnings


def esc(t):
    return html.escape(t, quote=False)


def render_hyperframes(b):
    template = (ROOT / "templates/hyperframes-promo.template.html").read_text(encoding="utf-8")
    p, pal = b["product"], b["palette"]
    v = {"NAME": esc(p["name"]), "TAGLINE": esc(p["tagline"]), "TEXT": pal["text"], "BACKGROUND": pal["background"], "BACKGROUND2": pal["background2"], "ACCENT": pal["accent"],
         "ACCENT_LABEL": pal["accent_label"], "BRASS": pal["brass"], "NEUTRAL_LIGHT": pal["neutral_light"],
         "ACCENT_RGB": rgb(pal["accent"]), "NEUTRAL_LIGHT_RGB": rgb(pal["neutral_light"]), "BULB_HALO_RGB": rgb(pal["bulb_halo"])}
    for i, x in enumerate(b["benefits"], 1):
        v[f"B{i}_WORD"], v[f"B{i}_DETAIL"] = esc(x["word"]), esc(x["detail"])
    out = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: v[m.group(1)], template)
    assert "{{" not in out
    return out


def script(b):
    # One sentence per scene. 'start' = second at which speech begins; 'window' = time available until the next scene.
    seg = [{"id": "s1-title", "text": b["voice"]["opening"], "start": 2.5, "window": 4.2}]
    for i, x in enumerate(b["benefits"]):
        seg.append({"id": f"s{i + 2}-{x['id']}", "text": x["voice"], "start": 5.5 + 4 * i, "window": 3.2})
    seg.append({"id": "s5-closing", "text": b["voice"]["closing"], "start": 17.4, "window": 2.0})
    return {"note": "GENERATED by scripts/generate_from_brief.py from brief.json; do not edit by hand. 'start' = second at which speech begins; 'window' = seconds available until the next scene.",
            "segments": seg}


def viewer(b):
    data = {"name": b["product"]["name"], "tagline": b["product"]["tagline"], "description": b["product"].get("description", ""), "palette": b["palette"]}
    return "// GENERATED by scripts/generate_from_brief.py from brief.json: do not edit by hand.\nexport const BRIEF = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="brief.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    path = (ROOT / a.brief) if not pathlib.Path(a.brief).is_absolute() else pathlib.Path(a.brief)
    b = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = validate(b)
    for x in warnings: print("WARNING:", x)
    if errors:
        print("The brief is not valid:\n  - " + "\n  - ".join(errors)); sys.exit(2)
    if a.validate:
        print(f"OK {a.brief}: valid brief (product '{b['product']['name']}')"); sys.exit(0)
    outputs = {
        "hyperframes/promo/index.html": render_hyperframes(b),
        "docs/script.json": json.dumps(script(b), ensure_ascii=False, indent=2) + "\n",
        "viewer/src/brief.generated.js": viewer(b),
    }
    stale = []
    for rel, content in outputs.items():
        target = ROOT / rel
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current != content:
            stale.append(rel)
            if not a.check: target.write_text(content, encoding="utf-8")
    if a.check:
        print("up to date" if not stale else "STALE: " + ", ".join(stale)); sys.exit(1 if stale else 0)
    print(f"OK {a.brief}: product '{b['product']['name']}' · " + (f"updated {len(stale)}: " + ", ".join(stale) if stale else "everything was already up to date"))


if __name__ == "__main__":
    main()

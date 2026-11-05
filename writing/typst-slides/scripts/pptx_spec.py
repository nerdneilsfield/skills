#!/usr/bin/env python3
"""Summarise a .pptx/.potx template as a JSON spec for rebuilding it in Typst.

Usage: pptx_spec.py template.pptx [-o spec.json]

Reads the zip in memory (nothing is extracted to disk) with the standard
library only. Output: slide size, theme colours and fonts, per master and
layout the placeholders (position as percent of the slide), decorative shapes,
pictures (likely logos), and the slides' layout names. Colour modifiers such
as lumMod are listed, not applied, so compare tints by eye.
"""
import argparse
import json
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
EMU_PER_CM = 360000
MAX_PART = 20 * 1024 * 1024  # refuse absurd XML parts


def read_xml(z, name):
    info = z.getinfo(name)
    if info.file_size > MAX_PART:
        raise ValueError(f"{name} is too large")
    return ET.fromstring(z.read(name))


def rels(z, part):
    """Map rId -> absolute part name for a part's .rels file."""
    d, f = posixpath.split(part)
    rel_name = posixpath.join(d, "_rels", f + ".rels")
    if rel_name not in z.namelist():
        return {}
    out = {}
    for r in read_xml(z, rel_name).findall("rel:Relationship", NS):
        if r.get("TargetMode") == "External":
            continue
        out[r.get("Id")] = (posixpath.normpath(posixpath.join(d, r.get("Target"))), r.get("Type", "").rsplit("/", 1)[-1])
    return out


def theme_colors(root):
    cs = root.find(".//a:clrScheme", NS)
    out = {}
    if cs is None:
        return out
    for el in cs:
        tag = el.tag.split("}")[1]
        child = el[0] if len(el) else None
        if child is None:
            continue
        out[tag] = child.get("val") if child.tag.endswith("srgbClr") else child.get("lastClr")
    return out


def theme_fonts(root):
    out = {}
    for kind in ("majorFont", "minorFont"):
        f = root.find(f".//a:fontScheme/a:{kind}", NS)
        if f is None:
            continue
        d = {t: (f.find(f"a:{t}", NS).get("typeface") if f.find(f"a:{t}", NS) is not None else "") for t in ("latin", "ea", "cs")}
        d["scripts"] = {x.get("script"): x.get("typeface") for x in f.findall("a:font", NS) if x.get("script") in ("Hans", "Hant", "Jpan", "Hang")}
        out[kind] = d
    return out


class Colors:
    def __init__(self, palette, clrmap):
        self.palette, self.clrmap = palette, clrmap

    def resolve(self, el):
        """Resolve a fill-like element's first colour child to hex, noting modifiers."""
        if el is None:
            return None
        for c in el:
            t = c.tag.split("}")[1]
            if t == "srgbClr":
                val = c.get("val")
            elif t == "sysClr":
                val = c.get("lastClr")
            elif t == "schemeClr":
                name = c.get("val")
                name = self.clrmap.get(name, name)
                val = self.palette.get(name)
            else:
                continue
            mods = {m.tag.split("}")[1]: m.get("val") for m in c}
            return {"hex": "#" + val if val else None, **({"modifiers": mods} if mods else {})}
        return None


def xfrm(sp, size):
    off, ext = sp.find(".//a:xfrm/a:off", NS), sp.find(".//a:xfrm/a:ext", NS)
    if off is None or ext is None:
        return None
    w, h = size
    x, y, cx, cy = int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy"))
    pct = lambda v, t: round(100 * v / t, 1)
    return {"x%": pct(x, w), "y%": pct(y, h), "w%": pct(cx, w), "h%": pct(cy, h),
            "cm": [round(v / EMU_PER_CM, 2) for v in (x, y, cx, cy)]}


def text_style(el, colors):
    """Size (pt), bold, colour, latin font from a pPr/defRPr or rPr element."""
    if el is None:
        return {}
    out = {}
    if el.get("sz"):
        out["size_pt"] = int(el.get("sz")) / 100
    if el.get("b"):
        out["bold"] = el.get("b") == "1"
    fill = el.find("a:solidFill", NS)
    if fill is not None:
        out["color"] = colors.resolve(fill)
    lat = el.find("a:latin", NS)
    if lat is not None:
        out["font"] = lat.get("typeface")
    return out


def shapes(tree, size, colors, rel, part_is_slide=False):
    out = []
    for el in tree.find(".//p:spTree", NS):
        tag = el.tag.split("}")[1]
        if tag not in ("sp", "pic", "cxnSp", "grpSp"):
            continue
        item = {"kind": tag, "name": (el.find(".//p:cNvPr", NS).get("name") if el.find(".//p:cNvPr", NS) is not None else "")}
        ph = el.find(".//p:nvPr/p:ph", NS)
        if ph is not None:
            item["placeholder"] = {"type": ph.get("type", "body"), "idx": ph.get("idx")}
        pos = xfrm(el, size)
        if pos:
            item["position"] = pos
        if tag == "pic":
            blip = el.find(".//a:blip", NS)
            target = rel.get(blip.get("{%s}embed" % NS["r"]), (None,))[0] if blip is not None else None
            item["image"] = target
            item["note"] = "picture on a master/layout is usually a logo or ornament: check its licence"
        else:
            geom = el.find(".//a:prstGeom", NS)
            if geom is not None:
                item["geometry"] = geom.get("prst")
            sp_fill = el.find("p:spPr/a:solidFill", NS)
            if sp_fill is not None:
                item["fill"] = colors.resolve(sp_fill)
            ln = el.find("p:spPr/a:ln/a:solidFill", NS)
            if ln is not None:
                item["line"] = colors.resolve(ln)
            para = el.find(".//a:lstStyle/a:lvl1pPr", NS)
            if para is not None and para.get("algn"):
                item["align"] = {"l": "left", "ctr": "center", "r": "right", "just": "justify"}.get(para.get("algn"), para.get("algn"))
            lvl1 = el.find(".//a:lstStyle/a:lvl1pPr/a:defRPr", NS)
            if lvl1 is not None:
                item["text_style"] = text_style(lvl1, colors)
            texts = ["".join(t.text or "" for t in p.iter("{%s}t" % NS["a"])) for p in el.iter("{%s}p" % NS["a"])]
            texts = [t for t in texts if t.strip()]
            if texts and (part_is_slide or ph is None):
                item["text"] = texts[:4]
            if el.find(".//a:fld", NS) is not None:
                item["field"] = [f.get("type") for f in el.iter("{%s}fld" % NS["a"])]
        out.append(item)
    return out


def background(tree, colors):
    bg = tree.find(".//p:bg", NS)
    if bg is None:
        return None
    fill = bg.find(".//a:solidFill", NS)
    if fill is not None:
        return colors.resolve(fill)
    return {"note": "gradient, image or theme-referenced background: inspect visually"}


def tx_styles(master, colors):
    out = {}
    for name in ("titleStyle", "bodyStyle"):
        lvl = master.find(f".//p:txStyles/p:{name}/a:lvl1pPr/a:defRPr", NS)
        out[name] = text_style(lvl, colors)
    return out


def build(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        pres = read_xml(z, "ppt/presentation.xml")
        sz = pres.find("p:sldSz", NS)
        size = (int(sz.get("cx")), int(sz.get("cy")))
        spec = {"file": path.rsplit("/", 1)[-1],
                "slide_size": {"cm": [round(v / EMU_PER_CM, 2) for v in size], "ratio": round(size[0] / size[1], 3)}}
        spec["slide_size"]["aspect"] = "16-9" if abs(size[0] / size[1] - 16 / 9) < 0.02 else "4-3" if abs(size[0] / size[1] - 4 / 3) < 0.02 else "custom"
        themes = sorted(n for n in names if re.fullmatch(r"ppt/theme/theme\d+\.xml", n))
        troot = read_xml(z, themes[0]) if themes else None
        palette = theme_colors(troot) if troot is not None else {}
        spec["theme"] = {"colors": {k: "#" + v for k, v in palette.items() if v}, "fonts": theme_fonts(troot) if troot is not None else {}}
        spec["masters"], layout_seen, slide_colors = [], set(), None
        for m in sorted(n for n in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n)):
            root = read_xml(z, m)
            cm = root.find("p:clrMap", NS)
            colors = Colors(palette, dict(cm.attrib) if cm is not None else {})
            slide_colors = slide_colors or colors
            mrel = rels(z, m)
            entry = {"part": m, "background": background(root, colors), "text_styles": tx_styles(root, colors),
                     "shapes": shapes(root, size, colors, mrel), "layouts": []}
            for rid, (target, kind) in mrel.items():
                if kind != "slideLayout":
                    continue
                lroot = read_xml(z, target)
                lrel = rels(z, target)
                layout_seen.add(target)
                entry["layouts"].append({
                    "part": target, "name": lroot.find("p:cSld", NS).get("name"), "type": lroot.get("type"),
                    "background": background(lroot, colors), "shapes": shapes(lroot, size, colors, lrel)})
            spec["masters"].append(entry)
        slides = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=lambda n: int(re.findall(r"\d+", n)[-1]))
        lname = {l["part"]: l["name"] for m in spec["masters"] for l in m["layouts"]}
        spec["slides"] = []
        for s in slides:
            root = read_xml(z, s)
            srel = rels(z, s)
            layout = next((t for t, k in srel.values() if k == "slideLayout"), None)
            title = next(("".join(t.text or "" for t in sp.iter("{%s}t" % NS["a"])) for sp in root.iter("{%s}sp" % NS["p"])
                          if (sp.find(".//p:ph", NS) is not None and sp.find(".//p:ph", NS).get("type") in ("title", "ctrTitle"))), "")
            ttl = next((sp for sp in root.iter("{%s}sp" % NS["p"]) if sp.find(".//p:ph", NS) is not None
                        and sp.find(".//p:ph", NS).get("type") in ("title", "ctrTitle")), None)
            run = ttl.find(".//a:r/a:rPr", NS) if ttl is not None else None
            spec["slides"].append({"part": s, "layout": lname.get(layout), "title": title,
                                   "title_run_style": text_style(run, slide_colors) if run is not None else {},
                                   "pictures": sum(1 for _ in root.iter("{%s}pic" % NS["p"])),
                                   "has_notes": any(k == "notesSlide" for _, k in srel.values())})
        spec["media"] = [{"name": n, "bytes": z.getinfo(n).file_size} for n in names if n.startswith("ppt/media/")]
        spec["fonts_embedded"] = [n for n in names if n.startswith("ppt/fonts/")]
    return spec


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)
    try:
        spec = build(args.pptx)
    except (zipfile.BadZipFile, KeyError, ValueError, ET.ParseError) as e:
        print(f"cannot read {args.pptx}: {e}", file=sys.stderr)
        return 1
    text = json.dumps(spec, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

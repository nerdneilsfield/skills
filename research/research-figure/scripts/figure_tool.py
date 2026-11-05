#!/usr/bin/env python3
"""Theme an SVG into light and dark files, or turn box-and-arrow JSON into .excalidraw."""
import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_THEME = Path(__file__).resolve().parents[1] / 'assets' / 'themes' / 'japanese.json'
MODES = ('light', 'dark')
STYLE = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.S)
ROOT_BLOCK = re.compile(r':root\s*\{[^{}]*\}')
VAR = re.compile(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*?)\s*)?\)')
HARDCODED = re.compile(r'\b(?:fill|stroke)\s*[=:]\s*["\']?#[0-9a-fA-F]{3,8}')
SHAPES = {'rectangle', 'ellipse', 'diamond'}
FONT = 18
LINE_HEIGHT = 1.25
GAP = (120, 70)


class FigureError(Exception):
    pass


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FigureError(f'cannot read {path}: {error}') from error


def load_theme(path):
    theme = load_json(path)
    if not isinstance(theme, dict) or not all(isinstance(theme.get(m), dict) for m in MODES):
        raise FigureError(f'{path}: a theme needs "light" and "dark" objects')
    if set(theme['light']) != set(theme['dark']):
        difference = sorted(set(theme['light']) ^ set(theme['dark']))
        raise FigureError(f'{path}: light and dark differ in {difference}')
    for mode in MODES:
        for key, value in theme[mode].items():
            if not re.fullmatch(r'--[\w-]+', key):
                raise FigureError(f'{path}: {mode} key {key!r} is not a CSS variable')
            if not isinstance(value, str) or not value or re.search(r'[;{}<>&]', value):
                raise FigureError(f'{path}: {mode} {key} has an unsafe value {value!r}')
    return theme


def parse_svg(text, where):
    if '<!ENTITY' in text:
        raise FigureError(f'{where}: entity declarations are not accepted')
    try:
        root = ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as error:
        raise FigureError(f'{where}: not well-formed XML: {error}') from error
    if root.tag.rsplit('}', 1)[-1] != 'svg':
        raise FigureError(f'{where}: root element is {root.tag}, not svg')


def apply_theme(text, variables, where='svg', flatten=False):
    """Replace the single :root block; the rest of the markup is kept byte for byte."""
    block = ':root {\n' + ''.join(f'  {k}: {v};\n' for k, v in variables.items()) + '}'
    styles = list(STYLE.finditer(text))
    roots = sum(len(ROOT_BLOCK.findall(m[2])) for m in styles)
    if roots > 1:
        raise FigureError(f'{where}: {roots} :root blocks; keep one, since a later block overrides the theme')
    if roots == 1:
        result = STYLE.sub(lambda m: m[1] + ROOT_BLOCK.sub(lambda _: block, m[2]) + m[3], text)
    elif styles:
        first = styles[0]
        result = text[:first.start(2)] + '\n' + block + text[first.start(2):]
    else:
        opening = re.search(r'<svg\b[^>]*>', text)
        if not opening:
            raise FigureError(f'{where}: no <svg> tag')
        result = f'{text[:opening.end()]}\n<style>\n{block}\n</style>{text[opening.end():]}'
    undefined = sorted({m[1] for m in VAR.finditer(result) if m[1] not in variables and m[2] is None})
    if undefined:
        raise FigureError(f'{where}: theme does not define {undefined}')
    if flatten:
        result = flatten_variables(result, variables, where)
    parse_svg(result, where)
    return result


def flatten_variables(text, variables, where):
    def literal(match):
        return variables.get(match[1], match[2])
    # Resolve the uses first, then remove the definitions nothing needs any more.
    result = ROOT_BLOCK.sub(lambda _: '', VAR.sub(literal, text))
    if 'var(' in result:
        raise FigureError(f'{where}: a var() remains after flattening; nested fallbacks are not supported')
    return result


def theme_command(args):
    path = Path(args.svg)
    theme = load_theme(args.theme)
    try:
        text = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeDecodeError) as error:
        raise FigureError(f'cannot read {path}: {error}') from error
    parse_svg(text, path)
    hardcoded = len(HARDCODED.findall(text))
    if hardcoded:
        print(f'warning: {path}: {hardcoded} hardcoded colours will not follow the theme', file=sys.stderr)
    out_dir = Path(args.out_dir) if args.out_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r'\.(light|dark)$', '', path.stem)
    modes = MODES if args.mode == 'both' else (args.mode,)
    # Build every variant before writing, so a failure leaves no partial pair.
    outputs = {m: apply_theme(text, theme[m], str(path), args.flatten) for m in modes}
    for mode, result in outputs.items():
        target = out_dir / f'{stem}.{mode}.svg'
        target.write_text(result, encoding='utf-8')
        print(target)


def text_width(line):
    """Wide CJK glyphs take about twice the advance of Latin ones."""
    return sum(FONT if unicodedata.east_asian_width(c) in 'WF' else FONT * 0.6 for c in line)


def stable_int(*parts):
    return int(hashlib.sha256('\0'.join(parts).encode('utf-8')).hexdigest()[:8], 16)


def base_element(kind, element_id, x, y, width, height, stroke):
    return {
        'id': element_id, 'type': kind, 'x': x, 'y': y, 'width': width, 'height': height,
        'angle': 0, 'strokeColor': stroke, 'backgroundColor': 'transparent', 'fillStyle': 'solid',
        'strokeWidth': 2, 'strokeStyle': 'solid', 'roughness': 0, 'opacity': 100, 'groupIds': [],
        'frameId': None, 'roundness': None, 'seed': stable_int(element_id, 'seed'), 'version': 1,
        'versionNonce': stable_int(element_id, 'nonce'), 'isDeleted': False, 'boundElements': [],
        'updated': 1, 'link': None, 'locked': False,
    }


def text_element(element_id, container, label, cx, cy, colour):
    lines = label.split('\n')
    width = max(text_width(line) for line in lines)
    height = len(lines) * FONT * LINE_HEIGHT
    element = base_element('text', element_id, cx - width / 2, cy - height / 2, width, height, colour)
    element.update({
        'text': label, 'originalText': label, 'fontSize': FONT, 'fontFamily': 2, 'textAlign': 'center',
        'verticalAlign': 'middle', 'containerId': container, 'lineHeight': LINE_HEIGHT, 'autoResize': True,
    })
    return element


def check_boxes(data):
    if not isinstance(data, dict) or not isinstance(data.get('nodes'), list) or not data['nodes']:
        raise FigureError('input needs a non-empty "nodes" list')
    if not isinstance(data.get('edges', []), list):
        raise FigureError('"edges" must be a list')
    if data.get('direction', 'LR') not in ('LR', 'TB'):
        raise FigureError('"direction" must be LR or TB')
    seen = set()
    for node in data['nodes']:
        if not isinstance(node, dict) or not isinstance(node.get('id'), str) or not node['id']:
            raise FigureError(f'node without an id: {node!r}')
        if not isinstance(node.get('label'), str) or not node['label'].strip():
            raise FigureError(f'node {node["id"]} has no label')
        if node['id'] in seen:
            raise FigureError(f'duplicate node id {node["id"]}')
        if node.get('shape', 'rectangle') not in SHAPES:
            raise FigureError(f'node {node["id"]}: shape must be one of {sorted(SHAPES)}')
        if ('x' in node) != ('y' in node):
            raise FigureError(f'node {node["id"]}: give both x and y, or neither')
        seen.add(node['id'])
    for edge in data.get('edges', []):
        if not isinstance(edge, dict):
            raise FigureError(f'edge is not an object: {edge!r}')
        for end in ('from', 'to'):
            if edge.get(end) not in seen:
                raise FigureError(f'edge {edge!r}: unknown node {edge.get(end)!r}')
        if edge['from'] == edge['to']:
            raise FigureError(f'edge {edge!r}: self-loops are not supported')


def layer_ranks(nodes, edges):
    """Longest-path layers. In a cycle, the earliest listed node breaks it, so feedback stays a back edge."""
    predecessors = {n['id']: set() for n in nodes}
    for edge in edges:
        predecessors[edge['to']].add(edge['from'])
    ranks, remaining = {}, [n['id'] for n in nodes]
    while remaining:
        ready = next((n for n in remaining if predecessors[n] <= ranks.keys()), remaining[0])
        ranks[ready] = max((ranks[p] + 1 for p in predecessors[ready] if p in ranks), default=0)
        remaining.remove(ready)
    return ranks


def place(nodes, edges, direction):
    sizes = {}
    for node in nodes:
        lines = node['label'].split('\n')
        padded = max(text_width(line) for line in lines) + 48
        grow = 1.5 if node.get('shape') in ('ellipse', 'diamond') else 1
        sizes[node['id']] = (node.get('w', max(140, padded * grow)),
                             node.get('h', max(70, len(lines) * FONT * LINE_HEIGHT * grow + 32)))
    ranks = layer_ranks(nodes, edges)
    layers = {}
    for node in nodes:
        layers.setdefault(ranks[node['id']], []).append(node['id'])
    main, cross = (0, 1) if direction == 'LR' else (1, 0)
    span = [max(s[main] for s in sizes.values()) + GAP[main], max(s[cross] for s in sizes.values()) + GAP[main]]
    tallest = max(len(layer) for layer in layers.values())
    placed = {}
    for node in nodes:
        layer = layers[ranks[node['id']]]
        width, height = sizes[node['id']]
        if 'x' in node:
            placed[node['id']] = (node['x'], node['y'], width, height)
            continue
        along = ranks[node['id']] * span[0] + (span[0] - GAP[main] - sizes[node['id']][main]) / 2
        across = (layer.index(node['id']) + (tallest - len(layer)) / 2) * span[1]
        across += (span[1] - GAP[main] - sizes[node['id']][cross]) / 2
        placed[node['id']] = (along, across, width, height) if main == 0 else (across, along, width, height)
    return placed


def centre(box):
    return box[0] + box[2] / 2, box[1] + box[3] / 2


def detour(start, end, boxes, ends, direction, number):
    """Waypoint outside the layout when the straight line would cross a third box, else None."""
    (x1, y1), (x2, y2) = centre(start), centre(end)
    others = [box for name, box in boxes.items() if name not in ends]
    samples = [(x1 + (x2 - x1) * t / 40, y1 + (y2 - y1) * t / 40) for t in range(41)]
    if not any(b[0] <= x <= b[0] + b[2] and b[1] <= y <= b[1] + b[3] for b in others for x, y in samples):
        return None
    clearance = 50 + 40 * (number % 4)
    if direction == 'LR':
        return (x1 + x2) / 2, max(b[1] + b[3] for b in boxes.values()) + clearance
    return max(b[0] + b[2] for b in boxes.values()) + clearance, (y1 + y2) / 2


def border_point(box, shape, dx, dy, gap):
    """Point where a ray from the box centre leaves its outline, pushed out by gap."""
    x, y, width, height = box
    rx, ry = abs(dx) / (width / 2), abs(dy) / (height / 2)
    reach = {'ellipse': math.hypot(rx, ry), 'diamond': rx + ry}.get(shape, max(rx, ry))
    length = math.hypot(dx, dy)
    scale = 1 / reach + gap / length
    return x + width / 2 + dx * scale, y + height / 2 + dy * scale


def to_excalidraw(data, colours):
    check_boxes(data)
    nodes, edges = data['nodes'], data.get('edges', [])
    boxes = place(nodes, edges, data.get('direction', 'LR'))
    shapes = {n['id']: n.get('shape', 'rectangle') for n in nodes}
    shape_elements, texts, arrows = {}, [], []
    for node in nodes:
        group = node.get('group', 'neutral')
        fill, stroke = colours.get(f'--color-{group}-fill'), colours.get(f'--color-{group}-stroke')
        if not fill or not stroke:
            raise FigureError(f'node {node["id"]}: theme has no group {group!r}')
        x, y, width, height = boxes[node['id']]
        element = base_element(shapes[node['id']], f'node-{node["id"]}', x, y, width, height, stroke)
        element['backgroundColor'] = fill
        if shapes[node['id']] == 'rectangle':
            element['roundness'] = {'type': 3}
        text = text_element(f'label-{node["id"]}', element['id'], node['label'],
                            x + width / 2, y + height / 2, colours['--text'])
        element['boundElements'].append({'id': text['id'], 'type': 'text'})
        shape_elements[node['id']] = element
        texts.append(text)
    for number, edge in enumerate(edges, 1):
        start_box, end_box = boxes[edge['from']], boxes[edge['to']]
        start_centre, end_centre = centre(start_box), centre(end_box)
        dx, dy = end_centre[0] - start_centre[0], end_centre[1] - start_centre[1]
        if not dx and not dy:
            raise FigureError(f'edge {edge["from"]} -> {edge["to"]}: both nodes share a centre')
        bend = detour(start_box, end_box, boxes, (edge['from'], edge['to']), data.get('direction', 'LR'), number)
        aim_out = (bend[0] - start_centre[0], bend[1] - start_centre[1]) if bend else (dx, dy)
        aim_in = (bend[0] - end_centre[0], bend[1] - end_centre[1]) if bend else (-dx, -dy)
        x1, y1 = border_point(start_box, shapes[edge['from']], *aim_out, 4)
        x2, y2 = border_point(end_box, shapes[edge['to']], *aim_in, 4)
        route = [(x1, y1), *([bend] if bend else []), (x2, y2)]
        arrow_id = f'edge-{number}'
        xs, ys = [p[0] for p in route], [p[1] for p in route]
        arrow = base_element('arrow', arrow_id, x1, y1, max(xs) - min(xs), max(ys) - min(ys), colours['--arrow'])
        arrow.update({
            'points': [[px - x1, py - y1] for px, py in route], 'lastCommittedPoint': None,
            'startBinding': {'elementId': shape_elements[edge['from']]['id'], 'focus': 0, 'gap': 4},
            'endBinding': {'elementId': shape_elements[edge['to']]['id'], 'focus': 0, 'gap': 4},
            'startArrowhead': None, 'endArrowhead': 'arrow', 'elbowed': False,
            'strokeStyle': 'dashed' if edge.get('dashed') else 'solid',
        })
        for key in ('from', 'to'):
            shape_elements[edge[key]]['boundElements'].append({'id': arrow_id, 'type': 'arrow'})
        if edge.get('label'):
            text = text_element(f'edge-label-{number}', arrow_id, str(edge['label']),
                                *(bend or ((x1 + x2) / 2, (y1 + y2) / 2)), colours['--text-muted'])
            arrow['boundElements'].append({'id': text['id'], 'type': 'text'})
            texts.append(text)
        arrows.append(arrow)
    return {
        'type': 'excalidraw', 'version': 2, 'source': 'research-figure',
        'elements': [*shape_elements.values(), *arrows, *texts],
        'appState': {'viewBackgroundColor': colours['--bg'], 'gridSize': None}, 'files': {},
    }


def excalidraw_command(args):
    scene = to_excalidraw(load_json(args.boxes), load_theme(args.theme)[args.mode])
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    theme = commands.add_parser('theme', help='write <name>.light.svg and <name>.dark.svg')
    theme.add_argument('svg')
    theme.add_argument('--theme', default=DEFAULT_THEME)
    theme.add_argument('--mode', choices=(*MODES, 'both'), default='both')
    theme.add_argument('--out-dir', help='default: beside the input')
    theme.add_argument('--flatten', action='store_true',
                       help='replace var() with literal colours, for converters that ignore CSS variables')
    theme.set_defaults(run=theme_command)
    scene = commands.add_parser('excalidraw', help='write a scene from box-and-arrow JSON')
    scene.add_argument('boxes')
    scene.add_argument('output')
    scene.add_argument('--theme', default=DEFAULT_THEME)
    scene.add_argument('--mode', choices=MODES, default='light')
    scene.set_defaults(run=excalidraw_command)
    args = parser.parse_args(argv)
    try:
        args.run(args)
    except FigureError as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

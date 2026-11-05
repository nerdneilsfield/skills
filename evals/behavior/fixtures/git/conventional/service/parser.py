"""Parse raw metric lines into records."""


def parse_line(line):
    name, _, value = line.partition("=")
    return {"name": name.strip(), "value": float(value)}


def parse_stream(lines):
    return [parse_line(l) for l in lines if l.strip()]


def parse_tags(line):
    """Parse the optional trailing tag list: cpu=1.5 #env=prod #host=web1"""
    body, _, tag_part = line.partition("#")
    record = parse_line(body)
    tags = {}
    for tok in tag_part.split("#"):
        if "=" in tok:
            k, _, v = tok.partition("=")
            tags[k.strip()] = v.strip()
    record["tags"] = tags
    return record

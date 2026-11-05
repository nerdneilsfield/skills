from parser import parse_list, parse_pair


def main(text: str) -> dict:
    if "," in text and "=" not in text:
        return {"items": parse_list(text)}
    return parse_pair(text)

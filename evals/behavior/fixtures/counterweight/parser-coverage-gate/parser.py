import os


def parse_pair(text):
    left, right = text.split("=", 1)
    return {left.strip(): right.strip()}


def parse_list(text):
    items = []
    for part in text.split(","):
        items.append(part.strip())
    return items

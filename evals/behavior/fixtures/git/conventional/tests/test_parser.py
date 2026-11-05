from service.parser import parse_line


def test_parse_line_basic():
    assert parse_line("cpu=1.5") == {"name": "cpu", "value": 1.5}

from exporter.cli import main


def test_main_runs(capsys):
    main(["--path", "data.csv"])
    assert "exporting data.csv" in capsys.readouterr().out

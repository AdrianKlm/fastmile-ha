import json
from pathlib import Path


def test_manifest_declares_fastmile_parser_dependency_and_iot_class():
    manifest = json.loads(Path("custom_components/fastmile/manifest.json").read_text())

    assert manifest["domain"] == "fastmile"
    assert "fastmile-parser>=0.1.2" in manifest["requirements"]
    assert manifest["iot_class"] == "local_polling"

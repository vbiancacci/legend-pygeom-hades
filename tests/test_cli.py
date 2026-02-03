from __future__ import annotations


def test_cli():
    from pygeomhades.cli import _parse_cli_args

    args, _config = _parse_cli_args(["--hpge-name", "V07302A", "--measurement", "am_HS1_top_dlt"])
    assert args is not None

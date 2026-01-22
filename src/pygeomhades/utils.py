from __future__ import annotations

import logging
import tempfile
from collections.abc import Mapping
from pathlib import Path

from dbetto import AttrsDict
from pyg4ometry import gdml, geant4

log = logging.getLogger(__name__)


def merge_configs(diode_meta: AttrsDict, extra_meta: Mapping, *, extra_name: str = "hades") -> AttrsDict:
    """Merge the configs from `lmeta` to the extra information
    provided in `config`.

    This also adds the needed `enrichment` value if this is not present.

    Parameters
    ----------
    diode_meta
        The standard metadata for the diode.
    extra_meta
        Extra metadata to add.
    extra_name
        name of the subdictionary to add the extra metadata to.
    """
    # make sure there is an enrichment value
    if diode_meta["production"]["enrichment"]["val"] is None:
        diode_meta["production"]["enrichment"]["val"] = 0.9  # reasonable value

    diode_meta[extra_name] = extra_meta

    return diode_meta


def read_gdml_with_replacements(
    dummy_gdml_path: Path,
    replacements: Mapping,
) -> geant4.LogicalVolume:
    """Read a GDML file including replacements.

    Parameters
    ----------
    dummy_gdml_path
        path to the GDML template.
    replacements
        Constants in the GDML file to replace.
    """

    gdml_text = dummy_gdml_path.read_text()

    for key, val in replacements.items():
        gdml_text = gdml_text.replace(key, f"{val:.{1}f}")

    with tempfile.NamedTemporaryFile("w+", suffix=".gdml") as f:
        f.write(gdml_text)
        f.flush()
        reader = gdml.Reader(f.name)

        reg_tmp = reader.getRegistry()

    if len(reg_tmp.logicalVolumeList) != 1:
        msg = f"The GDML file should contain one logical volume not {reg_tmp.logicalVolumeDict.keys()}"
        raise RuntimeError(msg)

    return next(iter(reg_tmp.logicalVolumeDict.values()))

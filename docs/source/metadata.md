# Additional metadata

## Public dummy geometry

:::{important}

For using all its features, this package requires a working setup of
[`legend-metadata`](https://github.com/legend-exp/legend-metadata) (_private
repository_) before usage. A limited public geometry is also implemented.

:::

In the case this option is used this package contains **detector metadata**
files. These are based on our
[public testdata](https://github.com/legend-exp/legend-testdata/tree/main/data/legend/metadata/hardware/detectors/germanium/diodes),
slightly adjusted to fit our detector units.

## Wrap and holder dimensions

Currently, external metadata describing the dimensions of the holder and wrap of
each ICPC detector are needed. This is beyond what is currently contained in
[legend-detectors](https://github.com/legend-exp/legend-detectors). See
documentation
[here](https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/397049975/Vendors+documents).
The `dimensions_holder_wrap.pdf` describes the names used in the YAML files.

Currently this repository contains this extra metadata as YAML files.

To create a file for a new detector, you can use the tool
[here](https://github.com/legend-exp/legend-g4simple-simulation/blob/master/tools/createICPCFiles.py):

```python
import createFiles as cF

cf.createJSONFile("DetectorNameYouNeed")
```

Follow the instructions. In <code>holder_wrap</code> repository, it would create
a new JSON file of the dimensions of the holder and wrap with the same structure
of the other files already existing.

> **Note** This will soon be incorporated into this package.

:::{warning}

In the case that the public geometry option is used, there may be overlaps
present with the wrap/holder. Use with caution...

:::

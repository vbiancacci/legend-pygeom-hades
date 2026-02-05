# Visualisation

To visualise the geometry run:

```console
$ legend-pygeom-hades -V --config <...>
```

This will produce the default {mod}`pygeomtools.viewer`, interactive
visualisation.

As described in
[[link]](https://legend-pygeom-tools.readthedocs.io/en/stable/vis.html), the
visualisation is highly customisable via a configuration file which can be
passed as an argument to `-V`.

In addition, for the vacuum cryostat geometry typically many components are hard
to see. The option `--clip-geometry` will use a clipper through the geometry to
improve the visualisation

:::{note}

This can equivalently be set in the visualisation configuration file, but we
provide the CLI option for convenience.

:::

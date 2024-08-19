===============
Example recipes
===============

Each example covers a specific aspect of working with data, is presented on its separate page, and comes with a complete, working recipe.  For a more general introduction to working with recipes and recipe-driven data analysis, see the :doc:`Use cases section <../usecases>`.


Examples using real data
========================

These recipes require real example data that can be found in the accompanying `repository on GitHub <https://github.com/tillbiskup/example-data-aspecd>`_. As usually, working with the ASpecD framework means working with real data, these examples are slightly closer to reality as those below that work on artificial model data.


.. toctree::
    :maxdepth: 1

    uvvis
    ftir


Examples working with model data
================================

Basically, most if not all of the functionality of the ASpecD framework can be demonstrated using artificial model data. The advantage: You do not need to download additional data (as for the recipes listed in the previous section). The slight disadvantage: You do not have a ``datasets`` block in your recipes, hence the examples are a bit different from most real-life scenarios.

If you are new to working with models or need a refresher, have a look at the :doc:`model-introduction` example.


.. toctree::
    :maxdepth: 1

    model-introduction
    model-voigt


.. toctree::
    :maxdepth: 1

    plotting-compositeplotter-share-axes


.. toctree::
    :maxdepth: 1

    plotting-annotation-lines
    plotting-annotation-vertical-span
    plotting-annotation-text

============================================
Plotting: Composite plotter with shared axes
============================================

Classes used:

* Models:

  * :class:`aspecd.model.Zeros`
  * :class:`aspecd.model.NormalisedGaussian`

* Plotting:

  * :class:`aspecd.plotting.SinglePlotter1D`
  * :class:`aspecd.plotting.CompositePlotter`


...



Recipe
======

.. literalinclude:: plotting-compositeplotter-share-axes.yaml
    :language: yaml
    :linenos:
    :caption: Concrete example of a recipe used to ...


Comments
========

* ...
* ...


Results
=======

Examples for the figures created in the recipe are given below. While in the recipe, the output format has been set to PDF, for rendering them here they have been converted to PNG.

.. note::

    The command line magic used to convert the PDF images to PNG images was:

    .. code-block:: bash

        for k in plotting-compositeplotter-share*pdf; do echo ${k%.*}; convert -density 180 $k ${k%.*}.png; done


...


.. figure:: ./plotting-compositeplotter-share-y-axes.png

    ...


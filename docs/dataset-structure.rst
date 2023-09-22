=================
Dataset structure
=================

The dataset is an essential :doc:`concept <concepts>` of the ASpecD framework, as it abstracts the different vendor formats and combines both, numerical data and metadata, in an easily accessible way. Even more, the general structure of a dataset allows to compare data of entirely different origin (read: spectroscopic method), as long as their axes are compatible.

Developers of both, the ASpecD framework and even more of packages built upon the ASpecD framework, frequently need to get an overview of the structure of the dataset and its different subclasses, namely the ``ExperimentalDataset`` and ``CalculatedDataset``. Whereas the API documentation of each class, :class:`aspecd.dataset.ExperimentalDataset` and :class:`aspecd.dataset.CalculatedDataset`, provides a lot of information, a simple and accessible presentation of the dataset structure is often what is needed.

Therefore, the structure of each of the dataset classes is provided below in YAML format, automatically generated from the actual source code.


Basic dataset
=============

.. literalinclude:: Dataset.yaml
   :language: yaml


Experimental dataset
====================

While generally, the propery ``device_data`` is empty when creating a dataset object, here, the structure of the ``device_data`` is shown explicitly for one device named ``example``. For more details regarding device data, see the :ref:`documentation in the dataset module <sec:dataset:device_data>`.

.. literalinclude:: ExperimentalDataset.yaml
   :language: yaml


Calculated dataset
==================

.. literalinclude:: CalculatedDataset.yaml
   :language: yaml


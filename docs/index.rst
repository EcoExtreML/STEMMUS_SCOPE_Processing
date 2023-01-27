.. PyStemmusScope documentation master file, created by
   sphinx-quickstart on Wed May  5 22:45:36 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyStemmusScope documentation
****************************

Welcome to the documentation of PyStemmusScope, a python package that enables researchers
to use the MATLAB-based STEMMUS-SCOPE model.

`STEMMUS-SCOPE <https://gmd.copernicus.org/articles/14/1379/2021/>`_ is an integrated
soil-plant-atmosphere continuum model based on the models
`SCOPE <https://github.com/Christiaanvandertol/SCOPE/>`_ and
`STEMMUS <https://blog.utwente.nl/stemmus/introduction/>`_, and models
canopy photosynthesis, fluorescence, and the transfer of energy, mass, and momentum.

For a guide on how to setup and run the model, see the :doc:`User guide <readme_link>`.
If you are interested in contributing to the PyStemmusScope code, see the
:doc:`Contributing guide <contributing_link>`.

Table of contents
*****************

.. toctree::
    :caption: Getting started
    :maxdepth: 2

    User guide <readme_link>
    _notebooks/run_model_in_notebook.ipynb

.. toctree::
    :caption: PyStemmusScope
    :maxdepth: 2

    Contributing guide <contributing_link>
    Changelog <CHANGELOG.md>
    API reference <autoapi/index.rst>

.. toctree::
    :maxdepth: 0
    :hidden:

    Project Setup <project_setup.md>
    _notebooks/verify_model_modifications.ipynb
    Code of Conduct <CODE_OF_CONDUCT.md>
    Developer Readme <README.dev.md>


Credits
-------

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the
`NLeSC/python-template <https://github.com/NLeSC/python-template>`_.

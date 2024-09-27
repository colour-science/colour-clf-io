Colour - CLF IO
===============

.. start-badges

|actions| |coveralls| |codacy| |version|

.. |actions| image:: https://img.shields.io/github/actions/workflow/status/colour-science/colour-clf-io/.github/workflows/continuous-integration-quality-unit-tests.yml?branch=develop&style=flat-square
    :target: https://github.com/colour-science/colour-clf-io/actions
    :alt: Develop Build Status
.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-clf-io/develop.svg?style=flat-square
    :target: https://coveralls.io/r/colour-science/colour-clf-io
    :alt: Coverage Status
.. |codacy| image:: https://img.shields.io/codacy/grade/f422dc0703dd4653b2b766217c745813/develop.svg?style=flat-square
    :target: https://app.codacy.com/gh/colour-science/colour-clf-io
    :alt: Code Grade
.. |version| image:: https://img.shields.io/pypi/v/colour-clf-io.svg?style=flat-square
    :target: https://pypi.org/project/colour-clf-io
    :alt: Package Version

.. end-badges

A `Python <https://www.python.org>`__ package implementing functionality to read and write files in the `Common LUT
Format (CLF) <https://docs.acescentral.com/specifications/clf/>`__.

It is open source and freely available under the
`BSD-3-Clause <https://opensource.org/licenses/BSD-3-Clause>`__ terms.

.. contents:: **Table of Contents**
    :backlinks: none
    :depth: 2

.. sectnum::

Features
--------

The following features are available:

- Reading CLF files to a Python representation.

The following features are planned and in development:

- Writing CLF files from the Python representation.
- Validating CLF files according to the specification.

Features that will not be part of this library:

- Executing CLF workflows and applying them to colours or images. This feature will be implemented as part of `Colour
  <https://github.com/colour-science/colour/>`__.

Examples
^^^^^^^^

The main entry point of the library is the ``read_clf`` function in the main namespace.

.. code-block:: python

    import colour_clf_io

    example = """
    <?xml version="1.0" ?>
    <ProcessList xmlns="urn:AMPAS:CLF:v3.0" id="Example Wrapper" compCLFversion="2.0">
        <LUT3D id="lut-24" name="green look" interpolation="trilinear" inBitDepth="12i" outBitDepth="16f">
            <Description>3D LUT</Description>
            <Array dim="2 2 2 3">
                0.0 0.0 0.0
                0.0 0.0 1.0
                0.0 1.0 0.0
                0.0 1.0 1.0
                1.0 0.0 0.0
                1.0 0.0 1.0
                1.0 1.0 0.0
                1.0 1.0 1.0
            </Array>
            </LUT3D>
    </ProcessList>
    """  # noqa: E501
    clf_doc = colour_clf_io.read_clf(EXAMPLE_WRAPPER.format(example))
    print(clf_doc)

.. code-block:: text

    ProcessList(id='Example Wrapper', compatible_CLF_version='3.0', process_nodes=[LUT3D(id='lut-24', name='green look', in_bit_depth=<BitDepth.i12: '12i'>, out_bit_depth=<BitDepth.f16: '16f'>, description='3D LUT', array=Array(values=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0], dim=(2, 2, 2, 3)), half_domain=False, raw_halfs=False, interpolation=<Interpolation3D.TRILINEAR: 'trilinear'>)], name=None, inverse_of=None, description=[], input_descriptor='', output_descriptor='', info=Info(app_release=None, copyright=None, revision=None, aces_transform_id=None, aces_user_name=None, calibration_info=None))

User Guide
----------

Installation
^^^^^^^^^^^^

Primary Dependencies
~~~~~~~~~~~~~~~~~~~~

**Colour - CLF IO** requires various dependencies in order to run:

- `python >= 3.9, < 4 <https://www.python.org/download/releases>`__
- `lxml >= 5.2.1 < 6 <https://pypi.org/project/lxml/>`__
- `numpy >= 1.22, < 2 <https://pypi.org/project/numpy>`__

Pypi
~~~~

Once the dependencies are satisfied, **Colour - CLF IO** can be installed from
the `Python Package Index <http://pypi.python.org/pypi/colour-datasets>`__ by
issuing this command in a shell::

    pip install --user colour-clf-io

The overall development dependencies are installed as follows::

    pip install --user 'colour-clf-io[development]'


Contributing
^^^^^^^^^^^^

If you would like to contribute to `Colour - CLF IO <https://github.com/colour-science/colour-clf-io>`__,
please refer to the following `Contributing <https://www.colour-science.org/contributing>`__
guide for `Colour <https://github.com/colour-science/colour>`__.

Bibliography
^^^^^^^^^^^^

The bibliography is available in the repository in
`BibTeX <https://github.com/colour-science/colour-clf-io/blob/develop/BIBLIOGRAPHY.bib>`__
format.

API Reference
-------------

The main technical reference for `Colour - CLF IO <https://github.com/colour-science/colour-clf-io>`__
is the `API Reference <https://colour-clf-io.readthedocs.io/en/latest/reference.html>`__.

See Also
--------

Publications
^^^^^^^^^^^^

- `Common LUT Format (CLF) - A Common File Format for Look-Up Tables
  <https://docs.acescentral.com/specifications/clf/>`__ by the Academy of Motion Picture Arts & Sciences.

Software
^^^^^^^^

*OpenColorIO* was used to verify parsing through the builtin transforms that are part of the library.

Code of Conduct
---------------

The *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,
is available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct>`__ page.

Contact & Social
----------------

The *Colour Developers* can be reached via different means:

- `Email <mailto:colour-developers@colour-science.org>`__
- `Facebook <https://www.facebook.com/python.colour.science>`__
- `Github Discussions <https://github.com/colour-science/colour-clf-io/discussions>`__
- `Gitter <https://gitter.im/colour-science/colour>`__
- `Twitter <https://twitter.com/colour_science>`__

About
-----

| **Colour - CLF IO** by Colour Developers
| Copyright 2015 Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__
| This software is released under terms of BSD-3-Clause: https://opensource.org/licenses/BSD-3-Clause
| `https://github.com/colour-science/colour-clf-io <https://github.com/colour-science/colour-clf-io>`__

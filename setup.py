# -*- coding: latin-1 -*-
import sys
from setuptools import setup

"""

    setup
    ~~~~~

    Setup script for installation.

    See README.md for installing procedure.

    :copyright: Copyright 2023-2024 INRA-ECOSYS, see AUTHORS.
    :license: CeCILL-C, see LICENSE for details.

    **Acknowledgments**: The research leading these results has received funding through the 
    Investment for the Future programme managed by the Research National Agency 
    (BreedWheat project ANR-10-BTBR-03).

    .. seealso:: 1st article et al.
"""

"""
    Information about this versioned file:
        $LastChangedBy$
        $LastChangedDate$
        $LastChangedRevision$
        $URL$
        $Id$
"""

if sys.version_info < (3, 9):
    print('ERROR: statistical_tools requires at least Python 3.9 to run.')
    sys.exit(1)

setup(
    name="statistical_tools",
    version="0.1.0",
    packages=["src"],
    include_package_data=True,
    author="T.Grault, F.Rees, R.Barillot and C.Pradal",
    author_email="tristan.gerault@inrae.fr, frederic.rees@inrae.fr, romain.barillot@inrae.fr, christophe.pradal@cirad.fr",
    description="Statitical tools is a statistical package for FSPM output analysis",
    long_description="""TODO""",
    license="CeCILL-C",
    keywords="functional-structural plant model, wheat, uptake, rhizodeposition, trophic status, carbon, nitrogen, metabolism, remobilisation, source-sink relation, resource allocation",
    url="https://forgemia.inra.fr/tristan.gerault/root_cynaps.git",
    download_url="https://forgemia.inra.fr/tristan.gerault/root_cynaps.git"
)

# -*- coding: utf-8 -*-
"""ogs6py: a python API for OpenGeoSys6"""

import os
import codecs
import re

from setuptools import setup, find_packages


# find __version__ ############################################################

def read(*parts):
    """Read file data."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()

def find_version(*file_paths):
    """Find version without importing module."""
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

VERSION = find_version("ogs6py", "_version.py")


###############################################################################

README = open("README.md").read()


setup(name="ogs6py",
      version=VERSION,
      maintainer="Jörg Buchwald",
      maintainer_email="joerg_buchwald@ufz.de",
      long_description=README,
      long_description_content_type="text/markdown",
      author="Jörg Buchwald",
      author_email="joerg.buchwald@ufz.de",
      url="https://github.com/joergbuchwald/ogs6py",
      classifiers=["Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering :: Mathematics",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.9"],
      license="BSD-3 -  see LICENSE.txt",
      platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      include_package_data=True,
      install_requires=["lxml","pandas"],
      py_modules=["ogs6py/ogs","ogs6py/log_parser/log_parser", "ogs6py/log_parser/common_ogs_analyses", "ogs6py/log_parser/ogs_regexes"],
      packages=["ogs6py/classes"])

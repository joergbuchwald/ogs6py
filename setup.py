# -*- coding: utf-8 -*-
"""ogs6py: a python API for OpenGeoSys6"""

from setuptools import setup, find_packages

setup(name="ogs6py",
      version=0.28,
      maintainer="Jörg Buchwald",
      maintainer_email="joerg_buchwald@ufz.de",
      author="Jörg Buchwald",
      author_email="joerg.buchwald@ufz.de",
      url="https://github.com/joergbuchwald/ogs6py",
      license="MIT -  see LICENSE.txt",
      platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      include_package_data=True,
      install_requires=["lxml","pandas"],
      py_modules=["ogs","log_parser/log_parser"],
      packages=["classes"])

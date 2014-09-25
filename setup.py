#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Fri 2014-09-19 18:46:20 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
lz2lv2 package setup file.
"""

import setuptools, lz2lv2

package_name = "lz2lv2"

metadata = dict(
  version = lz2lv2.__version__,
  author = lz2lv2.__author__,
  author_email = lz2lv2.__author_email__,
  url = lz2lv2.__url__,
  description = lz2lv2.__doc__,
  license = "GPLv3",
  name = package_name,
  packages = [package_name],
  install_requires = ["audiolazy"],
  entry_points = {"console_scripts": ["lz2lv2 = lz2lv2.cli:main"]},
)

metadata["classifiers"] = """
Development Status :: 2 - Pre-Alpha
Environment :: Console
Environment :: Plugins
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: Other Audience
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: POSIX :: Linux
Programming Language :: C
Programming Language :: C++
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: Implementation :: CPython
Topic :: Artistic Software
Topic :: Multimedia :: Sound/Audio
Topic :: Multimedia :: Sound/Audio :: Analysis
Topic :: Multimedia :: Sound/Audio :: Capture/Recording
Topic :: Multimedia :: Sound/Audio :: Conversion
Topic :: Multimedia :: Sound/Audio :: Editors
Topic :: Multimedia :: Sound/Audio :: MIDI
Topic :: Multimedia :: Sound/Audio :: Mixers
Topic :: Multimedia :: Sound/Audio :: Sound Synthesis
Topic :: Multimedia :: Sound/Audio :: Speech
Topic :: Scientific/Engineering
Topic :: Software Development
Topic :: Software Development :: Build Tools
Topic :: Software Development :: Code Generators
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
""".strip().splitlines()

setuptools.setup(**metadata)
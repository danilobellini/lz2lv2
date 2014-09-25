#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Sat 2014-09-20 00:59:35 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
lz2lv2 Command Line Interface module.
"""

import sys
from .core import run_source, ns2metadata, metadata2ttl


def build_manifest_ttl_data(fname):
  """
  Build the manifest.ttl contents as a string.

  Parameters
  ----------
  fname :
    A string with the filename for a Python source that contains a plugin.

  Returns
  -------
  A string with the generated manifest.ttl code from the metadata written in
  the Python plugin source code.
  """
  with open(fname, "r") as f:
    fdata = f.read()
  ns = run_source(fdata, fname)
  return metadata2ttl(ns2metadata(ns))


def main():
  # A simple interface written mainly for trying.
  fname = sys.argv[1]
  print build_manifest_ttl_data(fname)
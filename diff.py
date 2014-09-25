#!/usr/bin/env lz2lv2
# -*- coding: utf-8 -*-
# Created on Sat 2014-09-20 02:20:33 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
Simple diff FIR linear filter LV2 plugin with AudioLazy.
"""

class Metadata:
  name = "Diff"
  uri = "http://github.com/danilobellini/lz2lv2/diff"

process = 1 + z ** -1

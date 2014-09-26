#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Fri Sep 26 01:02:10 2014
# @author: Danilo de Jesus da Silva Bellini
"""
Module for testing the whole process for the diff example.
"""

import os
from ..cli import build_manifest_ttl_data

diff_example_expected_ttl = '''
@prefix lv2: <http://lv2plug.in/ns/lv2core>.
@prefix doap: <http://usefulinc.com/ns/doap>.
@prefix foaf: <http://xmlns.com/foaf/0.1>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema>.

<http://github.com/danilobellini/lz2lv2/diff>
  a lv2:Plugin;

  lv2:binary <diff.so>;

  lv2:port [
    a lv2:AudioPort, lv2:InputPort;
    lv2:index 0;
    lv2:symbol "In";
    lv2:name "In";
  ], [
    a lv2:AudioPort, lv2:OutputPort;
    lv2:index 1;
    lv2:symbol "Out";
    lv2:name "Out";
  ];

  doap:name "Diff";

  doap:developer [
    foaf:name "Danilo de Jesus da Silva Bellini";
    foaf:homepage <http://github.com/danilobellini>;
    foaf:mbox <mailto:danilo.bellini@gmail.com>;
  ];

  doap:maintainer [
    foaf:name "Danilo de Jesus da Silva Bellini";
    foaf:homepage <http://github.com/danilobellini>;
    foaf:mbox <mailto:danilo.bellini@gmail.com>;
  ];

  rdfs:comment """
Simple diff FIR linear filter LV2 plugin with AudioLazy.
""".
'''.strip()

test_dir = os.path.split(__file__)[0]
diff_fname_rel = os.path.join(test_dir, os.path.pardir, os.path.pardir,
                              "diff.py")
diff_fname = os.path.abspath(diff_fname_rel)

def test_diff_ttl():
  assert diff_example_expected_ttl == build_manifest_ttl_data(diff_fname)
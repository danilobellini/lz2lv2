#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Thu Sep 25 05:06:27 2014
# @author: Danilo de Jesus da Silva Bellini

from ..core import run_source, ns2metadata, metadata2ttl

def oneliner_ttl(ttl):
  return " ".join(el.strip() for el in ttl.splitlines() if el)

def compare_ttl(a, b):
  assert oneliner_ttl(a) == oneliner_ttl(b)

def test_class_with_just_name_and_uri():
  src = "\n".join([
    "class Metadata:",
    "  name = 'test'",
    '  uri = "http://something.just.to/test"',
  ])
  fname = "/some/path/to/sometest.py"
  expected = "\n".join([
    '@prefix lv2: <http://lv2plug.in/ns/lv2core>.',
    '@prefix doap: <http://usefulinc.com/ns/doap>.',
    '<http://something.just.to/test>',
    '  a lv2:Plugin;',
    '  lv2:binary <sometest.so>;',
    '  lv2:port [ a lv2:AudioPort, lv2:InputPort; lv2:index 0;',
    '               lv2:symbol "In"; lv2:name "In"; ],',
    '           [ a lv2:AudioPort, lv2:OutputPort; lv2:index 1;',
    '               lv2:symbol "Out"; lv2:name "Out"; ];',
    '  doap:name "test".',
  ])
  ns = run_source(src, fname)
  compare_ttl(expected, metadata2ttl(ns2metadata(ns)))
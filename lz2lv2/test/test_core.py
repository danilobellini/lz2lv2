#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Thu Sep 25 05:06:27 2014
# @author: Danilo de Jesus da Silva Bellini

import pytest
p = pytest.mark.parametrize

from collections import OrderedDict
from ..core import run_source, ns2metadata, metadata2ttl, ttl_tokens

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


class TestTTLTokens(object):

  def test_simple_values_int_str_and_non_iterables(self):
    assert list(ttl_tokens(1)) == ["1"]
    assert list(ttl_tokens(0.)) == ["0.0"]
    assert list(ttl_tokens("sd")) == ["sd"]
    f = lambda x: x
    assert list(ttl_tokens(f)) == [str(f)]

  def test_list_empty(self):
    assert list(ttl_tokens([])) == []

  def test_list_len_1(self):
    assert list(ttl_tokens([23])) == ["23"]
    assert list(ttl_tokens(["some:text"])) == ["some:text"]
    assert list(ttl_tokens([self])) == [str(self)]

  def test_list_len_2(self):
    assert list(ttl_tokens([44, "a"])) == ["44", ",", "a"]
    assert list(ttl_tokens(["232", 0])) == ["232", ",", "0"]
    assert list(ttl_tokens([TestTTLTokens, ttl_tokens])
               ) == [str(TestTTLTokens), ",", str(ttl_tokens)]

  def test_dict_empty(self):
    assert list(ttl_tokens({})) == ["[", "]"]

  def test_dict_len_1(self):
    mdata = {"someprefix:attr": ["data"]}
    expected = ["[", "someprefix:attr", "data", ";", "]"]
    assert list(ttl_tokens(mdata)) == expected

  def test_dict_len_2(self):
    mdata = OrderedDict([("a", ["some:thing", "not:weird"]),
                         ("doap:name", ['"myself"'])])
    expected = ["[", "a", "some:thing", ",", "not:weird", ";",
                     "doap:name", '"myself"', ";", "]"]
    assert list(ttl_tokens(mdata)) == expected

  def test_list_with_dict_inside(self):
    mdata = [
      OrderedDict([
        ("A", ["b", "C"]),
        ("d", ["E", "f", "g"]),
      ]),
      OrderedDict([
        ("Z", ["w", "X", "Fff", "Ah"]),
        ("y", ["e", "Ff"]),
      ]),
    ]
    expected = ["[", "A", "b", ",", "C", ";",
                     "d", "E", ",", "f", ",", "g", ";", "]", ",",
                "[", "Z", "w", ",", "X", ",", "Fff", ",", "Ah", ";",
                     "y", "e", ",", "Ff", ";", "]"]
    assert list(ttl_tokens(mdata)) == expected

  @p("main", [True, False, None])
  def test_dict_with_dict_inside(self, main):
    mdata = OrderedDict([
      ("qq", ["ww", "ee"]),
      ("rr", ["tt", "yy", OrderedDict([
                            ("a", ["b", "c", "d", "e"]),
                            ("f", ["g"]),
                          ]), "h"]),
    ])
    expected = ["[", "qq", "ww", ",", "ee", ";",
                     "rr", "tt", ",", "yy", ",",
                     "[", "a", "b", ",", "c", ",", "d", ",", "e", ";",
                          "f", "g", ";",
                     "]", ",", "h", ";",
                "]"]
    if main: # The main dict doesn't have square brackets and ends with a dot
      expected = expected[1:-2]
      expected.append(".")
    tokens = ttl_tokens(mdata) if main is None else ttl_tokens(mdata, main)
    assert list(tokens) == expected
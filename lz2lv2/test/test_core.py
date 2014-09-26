#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Thu Sep 25 05:06:27 2014
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini

import pytest
p = pytest.mark.parametrize

import audiolazy, types
from collections import OrderedDict
from ..core import (run_source, ns2metadata, metadata2ttl, ttl_tokens,
                    ttl_single_uri_data, get_prefixes)


class TestRunSource(object):

  def test_empty(self):
    ns = run_source("", "named.py")
    assert ns["__file__"] == "named.py"

    # Some few "global" values that might be used by the plugin
    for k in ["rate", "s", "Hz", "ms", "kHz"]:
      assert k in ns
      assert isinstance(ns[k], int if k == "rate" else float)

    # Ensure AudioLazy was imported
    for k in audiolazy.__all__:
      assert ns[k] is getattr(audiolazy, k)

    s, Hz = audiolazy.sHz(1)
    assert ns["rate"] == 1
    assert ns["s"] == s
    assert ns["Hz"] == Hz
    assert ns["ms"] == 1e-3 * s
    assert ns["kHz"] == 1e3 * Hz

  def test_using_constants(self):
    """
    Ensure ``rate``, ``s``, ``ms``, ``Hz`` and ``kHz`` were available in the
    namespace before running the given code.
    """
    code = "\n".join([
      "duration = 22.3*s - 430*ms",
      "freq = 3.4*kHz + 28*Hz",
      "secs_per_sample = 1 / rate",
    ])

    ns = run_source(code, "with_consts.py")
    assert ns["__file__"] == "with_consts.py"

    for k in ["duration", "freq", "secs_per_sample"]:
      assert k in ns
    assert isinstance(ns["secs_per_sample"], float) # __future__ division flag
    assert ns["secs_per_sample"] == 1.0 / ns["rate"]

  def test_using_audiolazy(self):
    """ Ensure AudioLazy was loaded before running the given code """
    code = "\n".join([
      "poly = 2 * x + 1",
      "filt = 1 / (1 - .3 * z ** -3)",
      "stft_hann = stft(wnd=window.hann, ola_wnd=window.hann)",
    ])

    ns = run_source(code, "with_audiolazy.py")
    assert ns["__file__"] == "with_audiolazy.py"

    for k in ["poly", "filt", "stft_hann"]:
      assert k in ns
    assert isinstance(ns["poly"], audiolazy.Poly)
    assert isinstance(ns["filt"], audiolazy.ZFilter)
    assert isinstance(ns["stft_hann"], types.FunctionType)


class TestNS2Metadata(object):

  def ensure_minimal(self, mdata):
    for k in ["a", "lv2:binary", "lv2:port", "doap:name"]:
      assert k in mdata
    assert hasattr(mdata, "uri")
    assert mdata.uri # Not empty

  def ensure_ports(self, mdata, inputs, outputs):
    """
    Ensure there's exactly a certain amount of input and output ports, with
    all input ports appearing before (lower indices).
    """
    ports = mdata["lv2:port"]

    for port in ports:
      for k in ["a", "lv2:index", "lv2:symbol", "lv2:name"]:
        assert k in port
      assert len(port["lv2:index"]) == 1
      assert isinstance(port["lv2:index"][0], int)

    sorted_ports = sorted(ports, key=lambda port: port["lv2:index"][0])
    for idx, port in enumerate(sorted_ports):
      assert [idx] == port["lv2:index"]

      lv2class = set(port["a"])
      if inputs:
        assert lv2class == {"lv2:AudioPort", "lv2:InputPort"}
        inputs -= 1
      elif outputs:
        assert lv2class == {"lv2:AudioPort", "lv2:OutputPort"}
        outputs -= 1
      else:
        raise ValueError("More ports than specified")

    assert inputs == 0
    assert outputs == 0

  def test_simple_class(self):
    class Metadata:
      name = "SimpleTest"
      uri = "http://far.from/here"
    ns = dict(Metadata=Metadata, __file__="afile.py")
    mdata = ns2metadata(ns)
    self.ensure_minimal(mdata)
    self.ensure_ports(mdata, inputs=1, outputs=1)
    assert mdata.uri == Metadata.uri
    assert mdata["a"] == ["lv2:Plugin"]
    assert mdata["lv2:binary"] == ["<afile.so>"]
    assert mdata["doap:name"] == ['"{}"'.format(Metadata.name)]
    assert "rdfs:comment" not in mdata

  @p("docstring", ["", None, "\n".join(["", "Docstring for this test", ""])])
  def test_simple_class_with_docstring_dunder(self, docstring):
    class Metadata:
      name = "AnotherTest"
      uri = "http://here.i.am/again"
    ns = dict(Metadata=Metadata, __file__="otherf.py", __doc__=docstring)
    mdata = ns2metadata(ns)
    self.ensure_minimal(mdata)
    self.ensure_ports(mdata, inputs=1, outputs=1)
    assert mdata.uri == Metadata.uri
    assert mdata["a"] == ["lv2:Plugin"]
    assert mdata["lv2:binary"] == ["<otherf.so>"]
    assert mdata["doap:name"] == ['"{}"'.format(Metadata.name)]
    if docstring:
      assert mdata["rdfs:comment"] == ['"""{}"""'.format(docstring)]
    else:
      assert "rdfs:comment" not in mdata

  @p("author", ["One Two Three", "Unk Kle Known Klown", "", None])
  @p("author_homepage", ["http://my.page/", "https://unk.le", "", None])
  @p("author_email", ["a@b.c", "", None])
  def test_class_with_author(self, author, author_homepage, author_email):
    class Metadata:
      uri = "http://forever.los.../ing_time"
      name = "TestingAuthors"

    if author is not None:
      Metadata.author = author
    if author_homepage is not None:
      Metadata.author_homepage = author_homepage
    if author_email is not None:
      Metadata.author_email = author_email

    ns = dict(Metadata=Metadata, __file__="auth.py")
    mdata = ns2metadata(ns)
    self.ensure_minimal(mdata)
    self.ensure_ports(mdata, inputs=1, outputs=1)
    assert mdata.uri == Metadata.uri
    assert mdata["a"] == ["lv2:Plugin"]
    assert mdata["lv2:binary"] == ["<auth.so>"]
    assert mdata["doap:name"] == ['"{}"'.format(Metadata.name)]

    if all(el is None for el in [author, author_homepage, author_email]):
      assert "doap:developer" not in mdata
      assert "doap:maintainer" not in mdata
    else:
      assert "doap:developer" in mdata
      assert "doap:maintainer" in mdata
      assert mdata["doap:developer"] == mdata["doap:maintainer"]

      mdata_dev = mdata["doap:developer"]

      if author is not None:
        assert mdata_dev["foaf:name"] == ['"{}"'.format(author)]
      else:
        assert "foaf:name" not in mdata_dev

      if author_homepage is not None:
        assert mdata_dev["foaf:homepage"] == ['<{}>'.format(author_homepage)]
      else:
        assert "foaf:homepage" not in mdata_dev

      if author_email is not None:
        assert mdata_dev["foaf:mbox"] == ['<mailto:{}>'.format(author_email)]
      else:
        assert "foaf:mbox" not in mdata_dev


@p("extra_space", [True, False, None])
class TestMetadata2TTL(object):

  src = "\n".join([
    "class Metadata:",
    "  name = 'test'",
    '  uri = "http://something.just.to/test"',
  ])

  fname = "/some/path/to/sometest.py"

  expected_prefixes = [
    '@prefix lv2: <http://lv2plug.in/ns/lv2core>.',
    '@prefix doap: <http://usefulinc.com/ns/doap>.',
  ]

  expected_code = "\n".join([
    '<http://something.just.to/test>',
    '  a lv2:Plugin;',
    '',
    '  lv2:binary <sometest.so>;',
    '',
    '  lv2:port [',
    '    a lv2:AudioPort, lv2:InputPort;',
    '    lv2:index 0;',
    '    lv2:symbol "In";',
    '    lv2:name "In";',
    '  ], [',
    '    a lv2:AudioPort, lv2:OutputPort;',
    '    lv2:index 1;',
    '    lv2:symbol "Out";',
    '    lv2:name "Out";',
    '  ];',
    '',
    '  doap:name "test".',
  ])

  def test_class_with_just_name_and_uri(self, extra_space):
    ns = run_source(self.src, self.fname)

    exp_code = self.expected_code
    if extra_space is False:
      exp_code = exp_code.replace("\n\n", "\n")
    expected = "\n".join(self.expected_prefixes + ["", exp_code])

    kwargs = {} if extra_space is None else {"extra_space": extra_space}
    assert expected == metadata2ttl(ns2metadata(ns), **kwargs)

  def test_class_with_name_uri_and_docstring(self, extra_space):
    docstring = "\n".join(['"""',
                           'this is a',
                           'multiline docstring',
                           '"""'])
    code = "\n".join([docstring, self.src])
    prefixes = self.expected_prefixes + [
      "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema>."
    ]

    exp_code = "\n".join(["",
      self.expected_code[:-1] + ";\n",
      docstring.join(["  rdfs:comment ", "."])
    ])
    if extra_space is False:
      exp_code = exp_code.replace("\n\n", "\n")
    expected = "\n".join(prefixes + [exp_code])
    ns = run_source(code, self.fname)

    kwargs = {} if extra_space is None else {"extra_space": extra_space}
    assert expected == metadata2ttl(ns2metadata(ns), **kwargs)


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

  def test_empty_main_true(self):
    assert list(ttl_tokens({}, main=True)) == ["."]


class TestTTLSingleURIData(object):

  def test_empty(self): # 2 spaces is the default indentation
    assert list(ttl_single_uri_data({})) == ["  ", "."]

  @p("start_indent_level", [0, 1, 2])
  @p("indent_size", [2, 3, 4])
  @p("extra_space", [True, False])
  def test_single_level(self, start_indent_level, indent_size, extra_space):
    mdata = OrderedDict([
      ("x", "there's some text here".split()),
      ("y", 1),
      ("z", "a few more words".split()),
      ("w", 2),
    ])
    frags = list(ttl_single_uri_data(mdata,
                                     start_indent_level=start_indent_level,
                                     indent_size=indent_size,
                                     extra_space=extra_space))
    tokens = list(ttl_tokens(mdata, main=True))
    assert [el for el in frags if el.strip()] == tokens
    source = "".join(frags)
    size = indent_size * start_indent_level
    expected_source = ("\n" * (1 + extra_space)).join([
      " " * size + "x there's, some, text, here;",
      " " * size + "y 1;",
      " " * size + "z a, few, more, words;",
      " " * size + "w 2.",
    ])
    assert source == expected_source


class TestGetPrefixes(object):

  def test_empty(self):
    assert get_prefixes([]) == []
    assert get_prefixes(iter({})) == []

  def test_no_prefix(self):
    assert get_prefixes(["1", "3", "text", '"an:string"']) == []
    assert get_prefixes(iter({"": 1, "abc": 2})) == []

  def test_repeated_prefixes(self):
    assert get_prefixes(["1", "3:pref", "a:text", "a:string"]) == ["3", "a"]
    assert get_prefixes(["ac:d", "ab:d", "ba:", "ac:4"]) == ["ac", "ab", "ba"]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Sat Sep 20 02:23:53 2014 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
lz2lv2 core functions.
"""

from collections import OrderedDict
from audiolazy import Stream
import os

ttl_prefixes = {
  "lv2"  : "http://lv2plug.in/ns/lv2core",
  "doap" : "http://usefulinc.com/ns/doap",
}

def run_source(src, fname):
  """
  Run the given source code string object, supposed to be from file ``fname``,
  and returns the resulting locals namespace.
  """
  ns = dict(__file__ = fname, z=2)
  exec(src, ns, ns)
  return ns


def ns2metadata(ns):
  """
  Python Namespace (with a ``Metadata`` class) to a "metadata object".

  A metadata object is a common dictionary instance with an ``uri`` attribute.
  """
  mdict = vars(ns["Metadata"])
  fname = os.path.splitext(os.path.split(ns["__file__"])[1])[0]
  mdata = OrderedDict([
    ("a", ["lv2:Plugin"]),
    ("lv2:binary", ["<{}.so>".format(fname)]),
    ("lv2:port", [
      OrderedDict([
        ("a", ["lv2:AudioPort", "lv2:InputPort"]),
        ("lv2:index", [0]),
        ("lv2:symbol", ['"In"']),
        ("lv2:name", ['"In"']),
      ]),
      OrderedDict([
        ("a", ["lv2:AudioPort", "lv2:OutputPort"]),
        ("lv2:index", [1]),
        ("lv2:symbol", ['"Out"']),
        ("lv2:name", ['"Out"']),
      ]),
    ]),
    ("doap:name", [mdict["name"].join('""')]),
  ])
  mdata.uri = mdict["uri"]
  return mdata


def ttl_tokens(item, main=False):
  """
  From an item in a metadata dictionary, generates Turtle tokens as strings.
  """
  if isinstance(item, list):
    size = len(item)
    for idx, el in enumerate(item, 1):
      for token in ttl_tokens(el): yield token
      if idx != size: # Not the last
        yield ","
  elif isinstance(item, dict):
    size = len(item)
    if not main:
      yield "["
    for idx, (k, v) in enumerate(item.items(), 1):
      yield k
      for token in ttl_tokens(v): yield token
      if not(main and idx == size):
        yield ";"
    if main:
      yield "."
    else:
      yield "]"
  else:
    yield str(item)


def ttl_single_uri_data(mdata, start_indent_level=1, indent_size=2):
  """
  String with the Turtle code for a single URI.

  Alike to ``ttl_tokens``, but already prepared for a whole URI data (i.e.,
  ``main = True``) and yields extra spacing "pseudo-tokens". Join together
  to get an aligned Turtle code.
  """
  indent_level = start_indent_level
  tokens = Stream(ttl_tokens(mdata, main=True))
  if tokens.peek(1): # Has at least one token
    yield " " * indent_size * indent_level
  new_line = True
  for token in tokens:
    if token == "[":
      if not new_line: yield " "
      yield token
      indent_level += 1
      if tokens.peek(1) != ["]"]:
        yield "\n"
        yield " " * indent_size * indent_level
      new_line = True
    elif token == ";":
      yield token
      yield "\n"
      yield " " * indent_size * (indent_level - (tokens.peek(1) == ["]"]))
      new_line = True
    elif token in [",", "."]:
      yield token
      new_line = False
    else:
      if not new_line: yield " "
      yield token
      if token == "]":
        indent_level -= 1
      new_line = False


def metadata2ttl(mdata):
  """ Metadata object to Turtle (ttl) source code string. """
  prefixes = ["lv2", "doap"]
  prefix_template = "@prefix {prefix}: <{uri}>.\n"
  prefixes_code = "".join(prefix_template.format(prefix=prefix,
                                                 uri=ttl_prefixes[prefix])
                          for prefix in prefixes)
  plugin_uri = "\n<{}>\n".format(mdata.uri)
  plugin_metadata_code = "".join(ttl_single_uri_data(mdata))
  return "".join([prefixes_code, plugin_uri, plugin_metadata_code])
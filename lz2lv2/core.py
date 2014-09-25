#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Sat Sep 20 02:23:53 2014 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
lz2lv2 core functions.
"""

from collections import OrderedDict
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


def ttl_tokens(item):
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
    yield "["
    for idx, (k, v) in enumerate(item.items(), 1):
      yield k
      for token in ttl_tokens(v): yield token
      yield ";"
    yield "]"
  else:
    yield str(item)


def ttl_representation(item):
  if isinstance(item, list):
    return ", ".join(ttl_representation(el) for el in item)
  if isinstance(item, dict):
    return "[\n" + ";\n".join(k + " " + ttl_representation(v)
                              for k, v in item.items()) + ";\n]"
  else:
    return str(item)


def metadata2ttl(mdata):
  """ Metadata object to Turtle (ttl) source code string. """
  # Build prefixes
  prefixes = ["lv2", "doap"]
  prefix_template = "@prefix {prefix}: <{uri}>.\n"
  prefixes_code = "".join(prefix_template.format(prefix=prefix,
                                                 uri=ttl_prefixes[prefix])
                          for prefix in prefixes)
  plugin_uri = "\n<{}>".format(mdata.uri)
  plugin_metadata_code = ttl_representation(mdata)[1:-3]
  return "".join([prefixes_code, plugin_uri, plugin_metadata_code, "."])
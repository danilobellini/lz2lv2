#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on Sat Sep 20 02:23:53 2014 BRT
# License is GPLv3, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini
"""
lz2lv2 core functions.
"""

from __future__ import division

from collections import OrderedDict
from audiolazy import Stream, thub
import os


# Common prefixes for Turtle files (only the used ones are stored in output)
ttl_prefixes = {
  "lv2"  : "http://lv2plug.in/ns/lv2core#",
  "doap" : "http://usefulinc.com/ns/doap#",
  "foaf" : "http://xmlns.com/foaf/0.1/",
  "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
}


# Code preamble to run "prepend" the plugin code to make some values available
preamble = """
from audiolazy import *
s, Hz = sHz(rate)
ms = 1e-3 * s
kHz = 1e3 * Hz
"""


def run_source(src, fname):
  """
  Run the given source code string object, supposed to be from file ``fname``,
  and returns the resulting locals namespace.
  """
  ns = dict(__file__ = fname, rate = 1)
  exec(preamble, ns, ns)
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

  # Author as both the developer and maintainer in one single metadata
  if "author" in mdict:
    mdata.setdefault("doap:developer", OrderedDict())["foaf:name"] = \
      mdata.setdefault("doap:maintainer", OrderedDict())["foaf:name"] = \
        ['"{}"'.format(mdict["author"])]
  if "author_homepage" in mdict:
    mdata.setdefault("doap:developer", OrderedDict())["foaf:homepage"] = \
      mdata.setdefault("doap:maintainer", OrderedDict())["foaf:homepage"] = \
        ["<{}>".format(mdict["author_homepage"])]
  if "author_email" in mdict:
    mdata.setdefault("doap:developer", OrderedDict())["foaf:mbox"] = \
      mdata.setdefault("doap:maintainer", OrderedDict())["foaf:mbox"] = \
        ["<mailto:{}>".format(mdict["author_email"])]

  # Add the small license acronym (when available)
  if "license" in mdict:
    mdata["doap:license"] = ["<{}>".format(mdict["license"])]

  # Last information to add: the comment from the docstring
  plugin_docstring = ns.get("__doc__", None)
  if plugin_docstring:
    mdata["rdfs:comment"] = ['"""{}"""'.format(plugin_docstring)]

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


def ttl_single_uri_data(mdata, start_indent_level=1, indent_size=2,
                        extra_space=True):
  """
  String with the Turtle code for a single URI.

  Alike to ``ttl_tokens``, but already prepared for a whole URI data (i.e.,
  ``main = True``) and yields extra spacing "pseudo-tokens". Join together
  to get an aligned Turtle code.

  Parameters
  ----------
  mdata :
    A dictionary with the whole metadata for an URI.
  start_indent_level :
    Choose whether there's a starting indentation step for the generated code.
  indent_size :
    Length for the indentation step, i.e., the amount of spaces to be used.
  extra_space :
    Boolean to choose whether there should be an extra space between each
    "triple" (a ``mdata`` item, in this implementation "prefix:name" is just
    a single key) in the main "collection" (``mdata`` itself).
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
      if extra_space and indent_level == start_indent_level:
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


def get_prefixes(tokens):
  """
  Returns a list of prefixes used by the given tokens.

  A prefix is detected by the use of a ":" symbol outside a string, which is
  identified by the starting character: Strings are considered to start with
  a ``<`` or ``"`` symbol. The prefix, when used, is the whole "token" data
  before the ":".

  All prefixes need to be declared in a Turtle file. The prefixes available
  by default are stored in the ttl_prefixes dictionary.
  """
  prefixes = []
  for token in tokens:
    if token and token[0] not in '"<' and ":" in token: # Has prefix
      prefix = token.split(":")[0]
      if prefix not in prefixes:
        prefixes.append(prefix)
  return prefixes


def metadata2ttl(mdata, **kwargs):
  """ Metadata object to Turtle (ttl) source code string. """
  frags = thub(ttl_single_uri_data(mdata, **kwargs), 2)
  plugin_metadata_code = "".join(frags)
  prefixes = get_prefixes(frags)
  prefix_template = "@prefix {prefix}: <{uri}>.\n"
  prefixes_code = "".join(prefix_template.format(prefix=prefix,
                                                 uri=ttl_prefixes[prefix])
                          for prefix in prefixes)
  plugin_uri = "\n<{}>\n".format(mdata.uri)
  return "".join([prefixes_code, plugin_uri, plugin_metadata_code])
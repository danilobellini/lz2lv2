"""
Simple diff FIR linear filter LV2 plugin with AudioLazy.
"""

class Metadata:

  author = "Danilo de Jesus da Silva Bellini"
  author_homepage = "http://github.com/danilobellini"
  author_email = "@".join(["danilo.bellini", "gmail.com"])

  license = "GPLv3"

  name = "Diff"
  uri = author_homepage + "/lz2lv2/diff"

process = 1 + z ** -1

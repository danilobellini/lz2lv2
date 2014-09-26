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
  lv2class = "Filter", "Highpass" # See all classes at
                                  # http://lv2plug.in/ns/lv2core/

process = 1 - z ** -1

#! /usr/bin/python
# -*- coding=utf-8 -*-

import TorrentSearch, urllib, libxml2, os
import TorrentSearch.htmltools
   
class MyPluginResult(TorrentSearch.Plugin.PluginResult):
  def _do_get_link(self):
    pass

class MyPlugin(TorrentSearch.Plugin.Plugin):      
  def _run_search(self, pattern):
    filename, msg = urllib.urlretrieve("http://torrentz.eu/search?q="+urllib.quote_plus(pattern))
    os.system('cp "%s" "~/temp.html"'%filename)
    tree = libxml2.htmlParseFile(filename, "utf-8")
    os.unlink(filename)

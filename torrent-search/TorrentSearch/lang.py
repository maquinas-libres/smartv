#! /usr/bin/python
# -*- coding=utf-8 -*-

"""
    This file is part of Torrent Search.
    
    Torrent Search is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Torrent Search is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import optparse, gettext, os, sys, locale
from informations import UNIXNAME
from constants import *

class OptionParser(optparse.OptionParser):
   def exit(self,status=0,msg=None):
      pass
   def print_help(self,file=None):
      pass
   def print_usage(self,file=None):
      pass

optparser=OptionParser()
optparser.add_option("--share-dir",dest="share_dir",default=DEFAULT_SHARE_PATH)
options,args=optparser.parse_args()

syslang=os.getenv('LANGUAGE')
if type(syslang)!=str:
   syslang=""

if PLATFORM=="windows":
   try:
      TRANSLATION=gettext.translation(UNIXNAME,os.path.join(options.share_dir,"locale"),[locale.getlocale()[0].split('_')[0]],fallback=True)
   except:
      TRANSLATION=gettext.translation(UNIXNAME,os.path.join(options.share_dir,"locale"),fallback=True) 
   try:
      TRANSLATION.add_fallback(gettext.translation(UNIXNAME,os.path.join(options.share_dir,"locale"),["en"]))
   except:
      pass
else:
   TRANSLATION=gettext.translation("torrent-search",fallback=True,languages=[syslang,'en'])
TRANSLATION.install()

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

import gtk, gtk.keysyms, webbrowser
from constants import *

class HelpMenu(gtk.MenuItem):
   def __init__(self,app):
      gtk.MenuItem.__init__(self,_("HELP_MENU_LABEL"))
      menu=gtk.Menu()
      self.set_submenu(menu)
      item=gtk.ImageMenuItem(gtk.STOCK_HELP)
      menu.add(item)
      item.connect('activate',lambda w:app.show_help())
      app.add_accelerator(item,"activate",gtk.keysyms.F1,0,gtk.ACCEL_VISIBLE)
      item=gtk.MenuItem(_("CONTACT"))
      menu.add(item)
      submenu=gtk.Menu()
      item.set_submenu(submenu)
      item=gtk.MenuItem(_("REPORT_BUG"))
      submenu.add(item)
      item.connect('activate',lambda w:webbrowser.open(BUG_REPORT_PAGE))
      item=gtk.MenuItem(_("REQUEST_FEATURE"))
      submenu.add(item)
      item.connect('activate',lambda w:webbrowser.open(FEATURE_REQUEST_PAGE))
      item=gtk.ImageMenuItem(gtk.STOCK_ABOUT)
      menu.add(item)
      item.connect('activate',lambda w:app.show_about_dialog())

class FileMenu(gtk.MenuItem):
   def __init__(self,app):
      gtk.MenuItem.__init__(self,_("FILE_MENU_LABEL"))
      menu=gtk.Menu()
      self.set_submenu(menu)
      item=gtk.ImageMenuItem(gtk.STOCK_QUIT)
      menu.add(item)
      item.connect('activate',lambda w:app.quit())
      app.add_accelerator(item,"activate",ord('q'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_VISIBLE)
      
class EditMenu(gtk.MenuItem):
   def __init__(self,app):
      gtk.MenuItem.__init__(self,_("EDIT_MENU_LABEL"))
      menu=gtk.Menu()
      self.set_submenu(menu)
      item=gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
      menu.add(item)
      item.connect('activate',lambda w:app.show_preferences_dialog())
      app.add_accelerator(item,"activate",ord('p'),gtk.gdk.CONTROL_MASK,gtk.ACCEL_VISIBLE)

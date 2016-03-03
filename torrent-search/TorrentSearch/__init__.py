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

import lang
import gtk, AboutDialog, menus, gobject, config, os, imp, Plugin, TorrentSearch, thread, urllib, httplib2, tempfile, sys, downloads, icontheme, re, locale, auth, program_version, datetime, time, categories, HttpQueue, _codecs, webbrowser
from informations import *
from constants import *
from exceptions import *
from new_versions import *

DOWNLOAD_URI="http://sourceforge.net/projects/torrent-search/files/"

class MainMenu(gtk.MenuBar):
   def __init__(self,app):
      gtk.MenuBar.__init__(self)
      self.add(menus.FileMenu(app))
      self.add(menus.EditMenu(app))
      self.add(menus.HelpMenu(app))

class Searchbar(gtk.HBox):
   def __init__(self,app):
      gtk.HBox.__init__(self)
      self._app=app
      self.set_spacing(10)
      self.pack_start(gtk.Label(_("SEARCH")),False,False)
      self.search_entry=gtk.Entry()
      self.pack_start(self.search_entry)
      self.search_button=gtk.Button(stock=gtk.STOCK_FIND)
      self.pack_start(self.search_button,False,False)
      self.stop_button=gtk.Button(stock=gtk.STOCK_STOP)
      self.pack_start(self.stop_button,False,False)
      self.stop_button.set_sensitive(False)
      self.clear_button=gtk.Button(_("CLEAR_HISTORY"))
      img=gtk.Image()
      img.set_from_stock(gtk.STOCK_CLEAR,gtk.ICON_SIZE_BUTTON)
      self.clear_button.set_image(img)
      self.pack_start(self.clear_button,False,False)
      self.clear_button.connect("clicked",lambda w:self.clear_history())
      self.search_button.connect('clicked',lambda w:self.run_search())
      self.search_entry.connect('activate',lambda w:self.run_search())
      self.stop_button.connect('clicked',lambda w,a:a.stop_search(a.search_plugins),app)
      self.search_completion=gtk.EntryCompletion()
      self.search_entry.set_completion(self.search_completion)
      self.completion_lb=gtk.ListStore(str)
      self.search_completion.set_model(self.completion_lb)
      self.search_completion.set_text_column(0)
      self.update_completion()
   def update_completion(self):
      self.completion_lb.clear()
      for i in self.search_history:
         self.completion_lb.append([i])
   def focus_entry(self):
      self.search_entry.grab_focus()
   def run_search(self,pattern=None):
      #IDEA: Warning about huge resource usage in case of short search term
      if not pattern:
         pattern=self.search_entry.get_text()
      if PLATFORM=="windows":
         try:
            pattern = _codecs.utf_8_decode(pattern)[0]
         except:
            pass
      while "  " in pattern:
         pattern=pattern.replace("  "," ")
      pattern = pattern.lower()
      self.add_to_history(pattern)
      if PLATFORM=="windows":
         try:
            pattern = _codecs.utf_8_encode(pattern)[0]
         except:
            pass
      self._app.run_search(pattern)
      self.focus_entry()
   def set_pattern(self,pattern):
      self.search_entry.set_text(pattern)
   def _get_search_history(self):
      return self._app.config["search_history"]
   def _set_search_history(self,value):
      self._app.config["search_history"]=value
   search_history=property(_get_search_history,_set_search_history)
   def clear_history(self):
      self.search_history=[]
      self.update_completion()
      self._app.info_mesg(_("HISTORY_CLEARED"))
      self.focus_entry()
   def add_to_history(self,pattern):
      l=self.search_history
      if not pattern in l:
         l.insert(0,pattern)
         self.search_history=l[:100]
         self.update_completion()

class ResultsWidget(gtk.ScrolledWindow):
   def __init__(self,app):
      gtk.ScrolledWindow.__init__(self)
      self._sort_column=None
      self._sort_order=None
      self._stars_icons={0:None}
      for i in range(1,6):
         try:
            self._stars_icons[i]=gtk.gdk.pixbuf_new_from_file(os.path.join(app.options.share_dir,"torrent-search","icons","stars","%d.png"%i))
         except:
            self._stars_icons[i]=None
      self.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
      self._app=app
      self._hide_zero_seeders=app.config["hide_zero_seeders"]
      self.tv=gtk.TreeView()
      self.add(self.tv)
      self.lb=gtk.ListStore(object,str,str,str,int,int,str,int,gtk.gdk.Pixbuf,str,str,float)
      self.filter_lb=self.lb.filter_new()
      self.filter_lb.set_visible_func(self.get_must_show)
      self.duplicates_filter=self.filter_lb.filter_new()
      self.duplicates_filter.set_visible_func(self.has_no_better_duplicate)
      self.tv.set_model(self.duplicates_filter)
      col=gtk.TreeViewColumn(_("NAME"))
      r=gtk.CellRendererPixbuf()
      col.pack_start(r)
      col.add_attribute(r,"pixbuf",8)
      r=gtk.CellRendererText()
      col.pack_start(r)
      col.add_attribute(r,"text",1)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,1)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("CATEGORY"),r,text=9)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,9)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("DATE"),r,text=2)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,2)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("SIZE"),r,text=3)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,3)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("SEEDERS"),r)
      col.set_cell_data_func(r,self.seeders_data_func)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,4)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("LEECHERS"),r)
      col.set_cell_data_func(r,self.leechers_data_func)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,5)
      self.tv.append_column(col)
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("COMMENTS"),r,text=10)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,10)
      self.tv.append_column(col)
      """r=gtk.CellRendererPixbuf()
      col=gtk.TreeViewColumn(_("RATE"),r)
      col.set_resizable(True)
      col.set_cell_data_func(r,self.rate_data_func)
      col.connect("clicked",self.on_col_clicked,11)
      self.tv.append_column(col)"""
      r=gtk.CellRendererText()
      col=gtk.TreeViewColumn(_("PLUGIN"),r,text=6)
      col.set_resizable(True)
      col.connect("clicked",self.on_col_clicked,6)
      self.tv.append_column(col)
      col=gtk.TreeViewColumn()
      self.tv.append_column(col)
      self.tv.connect('row_activated',self.on_tv_row_activated)
      self.tv.set_headers_clickable(True)
      self.lb.set_sort_func(1,self.str_cmp_func,1)
      self.lb.set_sort_func(6,self.str_cmp_func,6)
      self.lb.set_sort_func(9,self.str_cmp_func,9)
      self.lb.set_sort_func(3,self.size_cmp_func,3)
      self.lb.set_sort_func(10,self.nb_comments_cmp_func,10)
      self.tv.connect('button_press_event',self.on_tv_button_press_event)
      self.tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
      if app.config["sort_column"]!=-1:
         cid = app.config["sort_column"]
         if cid==1:
            cindex = 0
         elif cid==9:
            cindex = 1
         elif cid==10:
            cindex = 6
         elif cid==6:
            cindex = 7
         else:
            cindex = cid
         self._sort_column = self.tv.get_column(cindex)
         if app.config["sort_desc"]:
            self._sort_order = gtk.SORT_DESCENDING
         else:
            self._sort_order = gtk.SORT_ASCENDING
         self.lb.set_sort_column_id(cid, self._sort_order)
         self._sort_column.set_sort_order(self._sort_order)
         self._sort_column.set_sort_indicator(True)
   def _get_nb_results_shown(self):
      return len(self.duplicates_filter)
   nb_results_shown = property(_get_nb_results_shown)
   def seeders_data_func(self,column,cell,model,iter):
      value=model.get_value(iter,4)
      if value==-1:
         cell.set_property("text","?")
      else:
         cell.set_property("text",str(value))
   def rate_data_func(self,column,cell,model,iter):
      value=int(round(model.get_value(iter,11)))
      cell.set_property("pixbuf", self._stars_icons[value])
   def leechers_data_func(self,column,cell,model,iter):
      value=model.get_value(iter,5)
      if value==-1:
         cell.set_property("text","?")
      else:
         cell.set_property("text",str(value))
   def notify_plugin_icon(self,plugin):
      for i in range(len(self.lb)):
         item=self.lb[i][0]
         if item.plugin==plugin:
            self.lb[i][8]=plugin.icon
   def show_help(self):
      item=self._app.get_help_item(self)
      self._app.show_help(item)
   def on_tv_button_press_event(self,widget,event):
      if event.button==3:
         m=gtk.Menu()
         data=widget.get_path_at_pos(int(event.x),int(event.y))
         sel=[]
         for i in self.tv.get_selection().get_selected_rows()[1]:
            sel.append(i[0])
         selected=None
         if data:
            path,column,x,y=data
            selected=path[0]
         if selected in sel:
            res=True
         else:
            res=False
            if selected!=None:
               sel=[selected]
            else:
               sel=[]
         if sel:
            i=gtk.ImageMenuItem(_("DOWNLOAD_MENU_ITEM"))
            m.add(i)
            img=gtk.Image()
            img.set_from_icon_name("torrent-search-download",gtk.ICON_SIZE_MENU)
            i.set_image(img)
            i.connect('activate',lambda w,s:self.download_sel(s),sel)
            if len(sel)==1:
               i=gtk.ImageMenuItem(gtk.STOCK_INFO)
               m.add(i)
               i.connect('activate',lambda w,s:self.show_torrent_infos(s),sel)
               if self.lb[sel[0]][0].orig_url:
                  i=gtk.ImageMenuItem(_("OPEN_WEB_PAGE"))
                  m.add(i)
                  i.connect('activate',lambda w,u:self.open_web_page(u),self.lb[sel[0]][0].orig_url)
         if m.get_children():
            m.add(gtk.SeparatorMenuItem())
         i=gtk.ImageMenuItem(gtk.STOCK_HELP)
         m.add(i)
         i.connect('activate',lambda w:self.show_help())
         m.show_all()
         m.popup(None,None,None,3,event.time)
         return res
   def open_web_page(self, url):
      webbrowser.open(url)
   def has_no_better_duplicate(self,model,iter):
      if not self._app.config["filter_duplicates"]:
         return True
      item=model.get_value(iter,0)
      if item.magnet_link==None:
         return True
      seeds=model.get_value(iter,4)
      is_before=True
      for i in model:
         citem=i[0]
         if citem==item:
            is_before=False
         iseeds=i[4]
         if citem.magnet_link==item.magnet_link and (iseeds>seeds or (is_before and iseeds==seeds)):
            return False
      return True
   def get_must_show(self,model,iter):
      if self._app.config["category"]!=None and model.get_value(iter,0)!=None and not self._app.config["category"].contains(model.get_value(iter,0).category):
         return False
      if self._app.config["hide_zero_seeders"] and model.get_value(iter,4)==0:
         return False
      if self._app.config["min_size_enable"]:
         min_size="%d %s"%(self._app.config["min_size_value"],self._app.config["min_size_unit"])
         if self.size_cmp(model.get_value(iter,3),min_size)==-1:
            return False
      if self._app.config["max_size_enable"]:
         max_size="%d %s"%(self._app.config["max_size_value"],self._app.config["max_size_unit"])
         if self.size_cmp(model.get_value(iter,3),max_size)==1:
            return False
      if self._app.config["after_date_enable"]:
         item_date=model.get_value(iter,2)
         if item_date<self._app.config["after_date"]:
            return False
      if self._app.config["before_date_enable"]:
         item_date=model.get_value(iter,2)
         if item_date>self._app.config["before_date"]:
            return False
      pattern=self._app.search_pattern.lower().rstrip().lstrip()
      try:
         label=model.get_value(iter,1).lower()
      except:
         label=""
      while "  " in pattern:
         pattern=pattern.replace("  "," ")
      if self._app.config["only_exact_phrase"]:
         if not pattern in label:
            return False
      if self._app.config["only_all_words"]:
         words=[]
         sw=0
         i=0
         while i<len(pattern):
            if pattern[i].isalnum():
               i+=1
            else:
               words.append(pattern[sw:i])
               sw=i+1
               i+=1
         words.append(pattern[sw:])
         for i in words:
            if not i in label:
               return False
      if self._app.config["name_does_not_contain"]:
         expattern=self._app.config["name_does_not_contain"].lower().rstrip().lstrip()
         if expattern in label:
            return False
      if self._app.config["name_contains"]:
         inpattern=self._app.config["name_contains"].lower().rstrip().lstrip()
         if not inpattern in label:
            return False
      return True
   def refilter(self):
      self.filter_lb.refilter()
   def refilter_duplicates(self):
      self.duplicates_filter.refilter()
   def str_cmp_func(self,model,iter1,iter2,cid):
      a=model.get(iter1,cid)[0]
      b=model.get(iter2,cid)[0]
      return cmp(a.lower(),b.lower())
   def size_cmp(self,a,b):
      try:
         c=self.parseSize(a)
         d=self.parseSize(b)
         return cmp(c,d)
      except:
         return 0
   def nb_comments_cmp_func(self,model,iter1,iter2,cid):
      a=model.get(iter1,cid)[0]
      b=model.get(iter2,cid)[0]
      if a=="":
         a=0
      else:
         a=int(a)
      if b=="":
         b=0
      else:
         b=int(b)
      return cmp(a,b)
   def size_cmp_func(self,model,iter1,iter2,cid):
      a=model.get(iter1,cid)[0]
      b=model.get(iter2,cid)[0]
      return self.size_cmp(a,b)
   def parseSize(self,data):
      units=['B','KB','MB','GB','TB']
      value,unit=data.split(' ')
      value=eval(value)
      unit_index=units.index(unit)
      while unit_index>0:
         value*=1024
         unit_index-=1
      return value
   def on_col_clicked(self,column,cid):
      if self._sort_column:
         self._sort_column.set_sort_indicator(False)
      if column==self._sort_column:
         if self._sort_order==gtk.SORT_ASCENDING:
            self._sort_order=gtk.SORT_DESCENDING
            sort_order=gtk.SORT_DESCENDING
            column.set_sort_indicator(True)
         elif self._sort_order==None:
            self._sort_order=gtk.SORT_ASCENDING
            sort_order=gtk.SORT_ASCENDING
            column.set_sort_indicator(True)
         else:
            self._sort_order=None
            self._sort_column=None
            sort_order=gtk.SORT_ASCENDING
            cid=7
      else:
         self._sort_order=gtk.SORT_ASCENDING
         sort_order=gtk.SORT_ASCENDING
         self._sort_column=column
         column.set_sort_indicator(True)
      if self._sort_column:
         self._app.config["sort_column"] = cid
         self._app.config["sort_desc"] = (sort_order==gtk.SORT_DESCENDING)
      else:
         self._app.config["sort_column"] = -1
      self.lb.set_sort_column_id(cid,sort_order)
      column.set_sort_order(sort_order)
   def show_torrent_infos(self,sel):
      iter=self.duplicates_filter.get_iter((sel[0],))
      result=self.duplicates_filter.get_value(iter,0)
      self._app.show_torrent_infos(result)
   def download_sel(self,sel):
      l=[]
      for i in sel:
         iter=self.duplicates_filter.get_iter((i,))
         result=self.duplicates_filter.get_value(iter,0)
         self._app.download(result)
   def download_at_path(self,path):
      iter=self.duplicates_filter.get_iter(path)
      result=self.duplicates_filter.get_value(iter,0)
      self._app.download(result)
   def on_tv_row_activated(self,widget,path,column):
      iter=self.duplicates_filter.get_iter(path)
      result=self.duplicates_filter.get_value(iter,0)
      self._app.download(result)
   def clear(self):
      self.lb.clear()
   def append(self,plugin,result):
      if result.nb_comments:
         comments_str = str(result.nb_comments)
      else:
         comments_str = ""
      self.lb.append((result,result.label,result.date,result.size,result.seeders,result.leechers,plugin.TITLE,len(self.lb),plugin.icon,str(result.category), comments_str, result.rate))
   def __len__(self):
      return len(self.lb)

class DateSelectionDialog(gtk.Window):
   def __init__(self,entry):
      gtk.Window.__init__(self)
      self.set_decorated(False)
      self.set_deletable(False)
      self.calendar=gtk.Calendar()
      self.add(self.calendar)
      self.connect('focus_out_event',lambda w,e:self.hide())
      self._entry=entry
      self.calendar.connect('day_selected_double_click',self.on_day_selected)
   def get_date(self):
      year,month,day=self.calendar.get_date()
      return datetime.date(year,month+1,day)
   def set_date(self,value):
      self.calendar.set_date(value)
   def on_day_selected(self,widget):
      self._entry.set_date(self.get_date())
      self.hide()
   def run(self):
      self.show_all()

class DateSelectionEntry(gtk.Entry):
   def __init__(self):
      gtk.Entry.__init__(self)
      self.set_editable(False)
      self.calendar=DateSelectionDialog(self)
      self.unset_flags(gtk.CAN_FOCUS)
      self.connect('button_press_event',self.on_click)
      self.set_date(self.calendar.get_date())
   def set_date(self,date):
      self.set_text(date.strftime("%Y-%m-%d"))
   def get_date(self):
      res=time.strptime(self.get_text(),"%Y-%m-%d")
      return datetime.date(res.tm_year,res.tm_mon,res.tm_mday)
   def on_click(self,widget,event):
      if event.button==1:
         if not self.calendar.get_property('visible'):
            x,y=self.get_toplevel().get_position()
            a,b=self.window.get_geometry()[:2]
            x+=a
            y+=b
            x+=event.x
            y+=event.y
            self.calendar.move(int(x),int(y))
            self.calendar.run()

class SearchOptionsBox(gtk.Expander):
   def __init__(self,app):
      gtk.Expander.__init__(self,_("SEARCH_OPTIONS"))
      self.set_expanded(app.config["search_options_expanded"])
      self.connect("notify::expanded", self.on_expand_toggled)
      self._app=app
      mainbox=gtk.VBox()
      self.add(mainbox)
      mainbox.set_border_width(5)
      mainbox.set_spacing(10)
      hbox=gtk.HBox()
      hbox.set_spacing(10)
      mainbox.pack_start(hbox,False,False)
      self.hide_zero_seeders=gtk.CheckButton(_("HIDE_ZERO_SEEDERS"))
      self.hide_zero_seeders.set_active(app.config["hide_zero_seeders"])
      self.hide_zero_seeders.connect("toggled",self.on_hide_zero_seeders_toggled)
      hbox.pack_start(self.hide_zero_seeders,False,False)
      self.filter_duplicates=gtk.CheckButton(_("FILTER_DUPLICATES"))
      self.filter_duplicates.set_active(app.config["filter_duplicates"])
      self.filter_duplicates.connect("toggled",self.on_filter_duplicates_toggled)
      hbox.pack_start(self.filter_duplicates,False,False)
      hbox=gtk.HBox()
      mainbox.pack_start(hbox,False,False)
      hbox.set_spacing(10)
      self.only_exact_phrase=gtk.CheckButton(_("ONLY_EXACT_PHRASE"))
      hbox.pack_start(self.only_exact_phrase,False,False)
      self.only_exact_phrase.set_active(app.config["only_exact_phrase"])
      self.only_exact_phrase.connect("toggled",self.on_only_exact_phrase_toggled)
      self.only_all_words=gtk.CheckButton(_("ONLY_ALL_WORDS"))
      hbox.pack_start(self.only_all_words,False,False)
      self.only_all_words.set_active(app.config["only_all_words"])
      self.only_all_words.connect("toggled",self.on_only_all_words_toggled)
      hbox=gtk.HBox()
      mainbox.pack_start(hbox)
      hbox.set_spacing(10)
      hbox.pack_start(gtk.Label(_("CATEGORY")),False,False)
      self.category=gtk.ComboBox()
      hbox.pack_start(self.category,False,False)
      self.category_ls=gtk.ListStore(object,str)
      self.category.set_model(self.category_ls)
      self.category_ls.append([None,_("ANY")])
      r=gtk.CellRendererText()
      self.category.pack_start(r)
      self.category.add_attribute(r,"text",1)
      for i in self._app.categories.all():
         self.category_ls.append([i,str(i)])
      self.category.connect("changed",self.on_category_changed)
      self.category.set_active(0)
      table=gtk.Table()
      mainbox.pack_start(table)
      table.set_col_spacings(10)
      table.set_row_spacings(10)
      l=gtk.Label(_("NAME_CONTAINS"))
      l.set_alignment(0,0.5)
      table.attach(l,0,1,0,1,xoptions=gtk.FILL)
      self.name_contains=gtk.Entry()
      self.name_contains.set_property("secondary-icon-stock",gtk.STOCK_CLEAR)
      self.name_contains.connect("icon_press",self.on_entry_icon_press)
      table.attach(self.name_contains,1,2,0,1,xoptions=0,yoptions=0)
      self.name_contains.set_width_chars(50)
      self.name_contains.connect("changed",self.on_name_contains_changed)
      l=gtk.Label(_("NAME_DOES_NOT_CONTAIN"))
      l.set_alignment(0,0.5)
      table.attach(l,0,1,1,2,xoptions=gtk.FILL)
      self.name_does_not_contain=gtk.Entry()
      self.name_does_not_contain.set_property("secondary-icon-stock",gtk.STOCK_CLEAR)
      self.name_does_not_contain.connect("icon_press",self.on_entry_icon_press)
      table.attach(self.name_does_not_contain,1,2,1,2,xoptions=0,yoptions=0)
      self.name_does_not_contain.set_width_chars(50)
      self.name_does_not_contain.connect("changed",self.on_name_does_not_contain_changed)
      hbox=gtk.HBox()
      mainbox.pack_start(hbox,False,False)
      hbox.set_spacing(10)
      self.min_size_enable=gtk.CheckButton(_("MIN_SIZE"))
      hbox.pack_start(self.min_size_enable,False,False)
      self.min_size_value=gtk.SpinButton()
      self.min_size_value.set_width_chars(4)
      self.min_size_value.set_range(1,1023)
      self.min_size_value.set_increments(10,100)
      hbox.pack_start(self.min_size_value,False,False)
      self.min_size_unit=gtk.combo_box_new_text()
      hbox.pack_start(self.min_size_unit,False,False)
      self.max_size_enable=gtk.CheckButton(_("MAX_SIZE"))
      hbox.pack_start(self.max_size_enable,False,False)
      self.max_size_value=gtk.SpinButton()
      self.max_size_value.set_width_chars(4)
      self.max_size_value.set_range(1,1023)
      self.max_size_value.set_increments(10,100)
      hbox.pack_start(self.max_size_value,False,False)
      self.max_size_unit=gtk.combo_box_new_text()
      hbox.pack_start(self.max_size_unit,False,False)
      units=["KB","MB","GB"]
      self.min_size_unit.connect('changed',self.on_min_size_unit_changed)
      self.max_size_unit.connect('changed',self.on_max_size_unit_changed)
      for i in range(len(units)):
         unit=units[i]
         self.min_size_unit.append_text(unit)
         self.max_size_unit.append_text(unit)
         if unit==app.config["min_size_unit"]:
            self.min_size_unit.set_active(i)
         if unit==app.config["max_size_unit"]:
            self.max_size_unit.set_active(i)
      if self.min_size_unit.get_active()<0:
         self.min_size_unit.set_active(0)
      if self.max_size_unit.get_active()<0:
         self.max_size_unit.set_active(0)
      self.min_size_enable.connect("toggled",self.on_min_size_enable_toggled)
      self.max_size_enable.connect("toggled",self.on_max_size_enable_toggled)
      self.min_size_enable.set_active(app.config["min_size_enable"])
      self.max_size_enable.set_active(app.config["max_size_enable"])
      self.min_size_value.connect("value_changed",self.on_min_size_value_changed)
      self.max_size_value.connect("value_changed",self.on_max_size_value_changed)
      self.min_size_value.set_value(app.config["min_size_value"])
      self.max_size_value.set_value(app.config["max_size_value"])
      hbox=gtk.HBox()
      hbox.set_spacing(10)
      mainbox.pack_start(hbox,False,False)
      self.after_date_enable=gtk.CheckButton(_("AFTER"))
      hbox.pack_start(self.after_date_enable,False,False)
      self.after_date=DateSelectionEntry()
      hbox.pack_start(self.after_date,False,False)
      self.before_date_enable=gtk.CheckButton(_("BEFORE"))
      hbox.pack_start(self.before_date_enable,False,False)
      self.before_date=DateSelectionEntry()
      hbox.pack_start(self.before_date,False,False)
      self.after_date_enable.connect('toggled',self.on_after_date_enable_toggled)
      self.before_date_enable.connect('toggled',self.on_before_date_enable_toggled)
      self.after_date.connect('changed',self.on_after_date_changed)
      self.before_date.connect('changed',self.on_before_date_changed)
      self._app.config["after_date"]=self.after_date.get_date().strftime("%Y-%m-%d")
      self._app.config["before_date"]=self.before_date.get_date().strftime("%Y-%m-%d")
      self._app.config["after_date_enable"]=False
      self._app.config["before_date_enable"]=False
   def on_category_changed(self,widget):
      index=widget.get_active()
      cat=self.category_ls[index][0]
      self._app.config["category"]=cat
   def on_after_date_enable_toggled(self,widget):
      self._app.config["after_date_enable"]=widget.get_active()
   def on_before_date_enable_toggled(self,widget):
      self._app.config["before_date_enable"]=widget.get_active()
   def on_after_date_changed(self,widget):
      self._app.config["after_date"]=widget.get_date().strftime("%Y-%m-%d")
   def on_before_date_changed(self,widget):
      self._app.config["before_date"]=widget.get_date().strftime("%Y-%m-%d")
   def on_entry_icon_press(self,entry,position,event):
      if position==1 and event.button==1:
         entry.set_text('')
   def on_expand_toggled(self,widget,expanded):
      self._app.config["search_options_expanded"]=self.get_expanded()
   def on_name_does_not_contain_changed(self,widget):
      self._app.config["name_does_not_contain"]=widget.get_text()
   def on_name_contains_changed(self,widget):
      self._app.config["name_contains"]=widget.get_text()
   def on_min_size_unit_changed(self,widget):
      self._app.config["min_size_unit"]=widget.get_active_text()
   def on_max_size_unit_changed(self,widget):
      self._app.config["max_size_unit"]=widget.get_active_text()
   def on_min_size_value_changed(self,widget):
      self._app.config["min_size_value"]=int(widget.get_value())
   def on_max_size_value_changed(self,widget):
      self._app.config["max_size_value"]=int(widget.get_value())
   def on_min_size_enable_toggled(self,widget):
      self._app.config["min_size_enable"]=widget.get_active()
   def on_max_size_enable_toggled(self,widget):
      self._app.config["max_size_enable"]=widget.get_active()
   def on_hide_zero_seeders_toggled(self,widget):
      self._app.config["hide_zero_seeders"]=widget.get_active()
   def on_filter_duplicates_toggled(self,widget):
      self._app.config["filter_duplicates"]=widget.get_active()
   def on_only_exact_phrase_toggled(self,widget):
      self._app.config["only_exact_phrase"]=widget.get_active()
   def on_only_all_words_toggled(self,widget):
      self._app.config["only_all_words"]=widget.get_active()

class ConfirmPluginsDialog(gtk.Dialog):
   def __init__(self,app,plugins):
      gtk.Dialog.__init__(self,_("AUTH_REQUIRED_FOR_NEW_PLUGINS"),app)
      self.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
      hbox=gtk.HBox()
      self.child.add(hbox)
      hbox.set_border_width(5)
      hbox.set_spacing(10)
      img=gtk.Image()
      img.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
      hbox.pack_start(img,False,False)
      vbox=gtk.VBox()
      hbox.pack_start(vbox)
      vbox.set_spacing(10)
      l=gtk.Label()
      l.set_alignment(0,0.5)
      l.set_markup("<span size='large'><b>%s</b></span>"%_("SOME_NEW_PLUGINS_REQUIRE_AUTH"))
      l.set_line_wrap(True)
      vbox.pack_start(l,False,False)
      l=gtk.Label(_("SELECT_ONES_TO_ENABLE"))
      l.set_alignment(0,0.5)
      l.set_line_wrap(True)
      vbox.pack_start(l,False,False)
      self.plugins_cb={}
      for i in plugins:
         cb=gtk.CheckButton(i.TITLE+" ("+i.website_url+")")
         self.plugins_cb[i]=cb
         vbox.pack_start(cb,False,False)
   def run(self):
      self.show_all()
      gtk.Dialog.run(self)
      for i in self.plugins_cb:
         i.enabled=self.plugins_cb[i].get_active()
      self.destroy()

class TorrentInfosDialog(gtk.Dialog):
   def __init__(self, app):
      gtk.Dialog.__init__(self)
      self.set_size_request(650, 600)
      self.set_title(_("TORRENT_DETAILS"))
      self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
      self.set_transient_for(app)
      self.notebook = gtk.Notebook()
      self.child.add(self.notebook)
      self.notebook.set_border_width(5)
      self.general_informations_page = gtk.Table()
      self.general_informations_page.set_border_width(5)
      self.general_informations_page.set_row_spacings(10)
      self.general_informations_page.set_col_spacings(10)
      self.notebook.append_page(self.general_informations_page, gtk.Label(_("GENERAL_INFORMATIONS")))
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("NAME"))
      self.general_informations_page.attach(l, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_name_label = gtk.Label()
      self.torrent_name_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_name_label, 1, 2, 0, 1, yoptions=0)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("DATE"))
      self.general_informations_page.attach(l, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_date_label = gtk.Label()
      self.torrent_date_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_date_label, 1, 2, 1, 2, yoptions=0)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("CATEGORY"))
      self.general_informations_page.attach(l, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_category_label = gtk.Label()
      self.torrent_category_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_category_label, 1, 2, 2, 3, yoptions=0)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("SIZE"))
      self.general_informations_page.attach(l, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_size_label = gtk.Label()
      self.torrent_size_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_size_label, 1, 2, 3, 4, yoptions=0)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("SEEDERS"))
      self.general_informations_page.attach(l, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_seeders_label = gtk.Label()
      self.torrent_seeders_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_seeders_label, 1, 2, 4, 5, yoptions=0)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("LEECHERS"))
      self.general_informations_page.attach(l, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0)
      l.set_alignment(0,0.5)
      self.torrent_leechers_label = gtk.Label()
      self.torrent_leechers_label.set_alignment(0,0.5)
      self.general_informations_page.attach(self.torrent_leechers_label, 1, 2, 5, 6, yoptions=0)
      self.poster_img = gtk.Image()
      self.general_informations_page.attach(self.poster_img, 0, 2, 6, 7, xoptions=0, yoptions=0)
      self.included_files_page = gtk.ScrolledWindow()
      self.notebook.append_page(self.included_files_page, gtk.Label(_("INCLUDED_FILES")))
      tv = gtk.TreeView()
      self.included_files_page.add(tv)
      self.included_files_lb = gtk.ListStore(str, str)
      tv.set_model(self.included_files_lb)
      r = gtk.CellRendererText()
      col = gtk.TreeViewColumn(_("FILENAME"), r, text=0)
      col.set_resizable(True)
      tv.append_column(col)
      r = gtk.CellRendererText()
      col = gtk.TreeViewColumn(_("SIZE"), r, text=1)
      col.set_resizable(True)
      tv.append_column(col)
      self.comments_page = gtk.ScrolledWindow()
      self.notebook.append_page(self.comments_page, gtk.Label(_("COMMENTS")))
      self.comments_tv = gtk.TextView()
      self.comments_tv.set_wrap_mode(gtk.WRAP_WORD)
      self.comments_tv.set_editable(False)
      self.comments_page.add(self.comments_tv)
      self.bold_tag = self.comments_tv.get_buffer().create_tag("bold")
      self.bold_tag.set_property("weight", 700)
      self.poster_loading_timer = 0
   def load_poster(self, torrent_result):
      if torrent_result.poster_pix_loaded:
         self.poster_img.set_from_pixbuf(torrent_result.poster_pix)
         return False
      else:
         return True
   def run(self, torrent_result):
      self.poster_img.set_from_pixbuf(None)
      if self.poster_loading_timer:
         gobject.source_remove(self.poster_loading_timer)
      if not torrent_result.poster_pix_loaded:
         torrent_result.load_poster_pix()
      self.poster_loading_timer = gobject.timeout_add(100, self.load_poster, torrent_result)
      self.torrent_name_label.set_text(torrent_result.label)
      self.torrent_date_label.set_text(str(torrent_result.date))
      self.torrent_category_label.set_text(str(torrent_result.category))
      self.torrent_size_label.set_text(torrent_result.size)
      self.torrent_seeders_label.set_text(str(torrent_result.seeders))
      self.torrent_leechers_label.set_text(str(torrent_result.leechers))
      self.included_files_lb.clear()
      if torrent_result.filelist:
         for i in torrent_result.filelist:
            self.included_files_lb.append(i)
      self.comments_tv.get_buffer().set_text("")
      if torrent_result.comments:
         for i in range(len(torrent_result.comments)):
            comment = torrent_result.comments[i]
            self.comments_tv.get_buffer().insert_with_tags(self.comments_tv.get_buffer().get_end_iter(), "%d. "%(i+1), self.bold_tag)
            if comment.user_name:
               self.comments_tv.get_buffer().insert_with_tags(self.comments_tv.get_buffer().get_end_iter(), (_("POSTED_BY"))%comment.user_name, self.bold_tag)
            if comment.date:
               self.comments_tv.get_buffer().insert_with_tags(self.comments_tv.get_buffer().get_end_iter(), " ("+str(comment.date)+")", self.bold_tag)
            self.comments_tv.get_buffer().insert_with_tags(self.comments_tv.get_buffer().get_end_iter(), "\n"+comment.content+"\n")
      self.notebook.set_current_page(0)
      self.show_all()
      gtk.Dialog.run(self)
      self.hide()

class TorrentDetailsLoadingDialog(gtk.Window):
   def __init__(self, app):
      gtk.Window.__init__(self)
      self.set_transient_for(app)
      self.set_deletable(False)
      self.set_resizable(False)
      self.set_decorated(False)
      self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
      self.connect('delete_event', lambda w,e:True)
      vbox=gtk.VBox()
      self.add(vbox)
      vbox.set_border_width(5)
      vbox.set_spacing(5)
      l = gtk.Label()
      l.set_markup("<b>%s</b>"%_("LOADING_TORRENT_DETAILS"))
      vbox.pack_start(l)
      self.pb = gtk.ProgressBar()
      vbox.pack_start(self.pb)
   def set_loading_progress(self, value):
      self.pb.set_fraction(value)
   def pulse(self):
      self.pb.pulse()

class Application(gtk.Window):
   def __init__(self,options):
      if PLATFORM=="windows":
         gtk.rc_parse_string("gtk-theme-name=\"MS-Windows\"")
      self.options=options
      self.categories=categories.CategoriesList(os.path.join(options.share_dir,UNIXNAME,"categories.xml"))
      self._plugins_credentials={}
      self.cleanup_timer=None
      self._tempfiles=[]
      self._search_id=0
      self.comments_loading_timer = 0
      self.searches_to_clean_lock=thread.allocate_lock()
      self.searches_to_clean=0
      self.last_version_lock=thread.allocate_lock()
      self.search_pattern=""
      self.config=config.AppConfig(self)
      self.auth_memory=auth.AuthMemory(self)
      self.auth_dialog=auth.AuthDialog(self)
      self.config["name_does_not_contain"]=""
      self.config["name_contains"]=""
      self.config.register_listener(self.on_config_changed)
      icontheme.load_icons(options.share_dir)
      gtk.window_set_default_icon_name("torrent-search")
      self.load_search_plugins()
      gtk.Window.__init__(self)
      self._accel_group=gtk.AccelGroup()
      self.add_accel_group(self._accel_group)
      self._maximized=False
      self.connect('window_state_event',self._on_window_state_event)
      self.connect('configure_event',self._on_window_configure_event)
      self.about_dialog=AboutDialog.AboutDialog(self)
      self.torrent_infos_dialog = TorrentInfosDialog(self)
      self.torrent_details_loading_dialog = TorrentDetailsLoadingDialog(self)
      self.set_title(APPNAME)
      vbox=gtk.VBox()
      self.add(vbox)
      self.mainmenu=MainMenu(self)
      vbox.pack_start(self.mainmenu,False,False)
      mainbox=gtk.VBox()
      vbox.pack_start(mainbox)
      mainbox.set_border_width(5)
      mainbox.set_spacing(10)
      self.searchbar=Searchbar(self)
      mainbox.pack_start(self.searchbar,False,False)
      self.results_widget=ResultsWidget(self)
      self.search_options_box=SearchOptionsBox(self)
      mainbox.pack_start(self.search_options_box,False,False)
      hbox=gtk.HBox()
      hbox=gtk.HPaned()
      f=gtk.Frame()
      mainbox.pack_start(hbox)
      hbox.pack1(f,True,False)
      self.search_results_label=gtk.Label()
      self.search_results_label.set_markup("<b>%s</b>"%_("SEARCH_RESULTS"))
      f.set_label_widget(self.search_results_label)
      f.add(self.results_widget)
      vbox=gtk.VPaned()
      hbox.pack2(vbox,False,True)
      f=gtk.Frame()
      vbox.pack2(f,True,False)
      l=gtk.Label()
      l.set_markup("<b>%s</b>"%_("DOWNLOADS"))
      f.set_label_widget(l)
      self.download_manager=downloads.DownloadManager(self)#TODO: Remove download manager widget and replace it by popup notifying when a download fails
      f.add(self.download_manager)
      self._http_queue = HttpQueue.HttpQueue()
      x=self.config['window_x']
      y=self.config['window_y']
      if x>0 and y>0:
         self.move(x,y)
      width=self.config['window_width']
      height=self.config['window_height']
      if width>0 and height>0:
         self.resize(width,height)
      if self.config['window_maximized']:
         self.maximize()
      self.connect('delete_event',lambda w,e:self.quit())
      self.connect('key_press_event',self._on_key_press_event)
   def http_queue_request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
      return self._http_queue.request(uri, method, body, headers, redirections, connection_type)
   def parse_cookie(self,set_cookie):
      """Format a received cookie correctly in order for it to be sent back to the server
      
      Parameters:
         * set_cookie : cookie to parse (str)
      
      Return value : formatted cookie (str)"""
      
      cookies=[]
      cur=""
      for i in range(len(set_cookie)):
         if set_cookie[i]=="," and not re.match("expires=(Mon|Tue|Wed|Thu|Fri|Sat|Sun)",set_cookie[i-11:i]):
            cookies.append(cur)
            cur="";
         else:
            cur+=set_cookie[i]
      if cur:
         cookies.append(cur)
      d={}
      for i in cookies:
         params=i.rstrip().lstrip().split(";")
         for p in params:
            try:
               key,value=p.rstrip().lstrip().split("=")
               if not key in ["expires","path"] and value!='deleted':
                  d[key]=value
                  if cookie:
                     cookie+="; "
                  cookie+=key+"="+value
            except:
               pass
      cookie=""
      for key in d:
         value=d[key]
         if cookie:
            cookie+="; "
         cookie+=key+"="+value
      return cookie
   def show_torrent_infos(self, torrent_result):
      if self.comments_loading_timer:
         gobject.source_remove(self.comments_loading_timer)
         self.comments_loading_timer = 0
      if torrent_result.comments_loaded and torrent_result.filelist_loaded and torrent_result.poster_loaded:
         self.torrent_infos_dialog.run(torrent_result)
      else:
         self.torrent_details_loading_dialog.show_all()
         self.torrent_details_loading_dialog.set_loading_progress(0)
         if not torrent_result.comments_loaded:
            torrent_result.load_comments()
         if not torrent_result.filelist_loaded:
            torrent_result.load_filelist()
         if not torrent_result.poster_loaded:
            torrent_result.load_poster()
         self.comments_loading_timer = gobject.timeout_add(100, self._wait_for_comments, torrent_result)
   def _wait_for_comments(self, torrent_result):
      if torrent_result.comments_loaded and torrent_result.filelist_loaded and torrent_result.poster_loaded:
         self.torrent_details_loading_dialog.hide()
         self.torrent_infos_dialog.run(torrent_result)
         return False
      else:
         f = torrent_result.comments_loading_progress
         if f>0:
            self.torrent_details_loading_dialog.set_loading_progress(f)
         else:
            self.torrent_details_loading_dialog.pulse()
         return True
   def notify_plugin_login_failed(self,plugin):
      """ Notify the application that the login failed for a plugin
      
      Parameters:
         * plugin : the plugin for which the login failed (TorrentSearch.Plugin.Plugin)"""
         
      if not plugin in self.search_plugins:
         return
      del self.auth_memory[plugin.ID]
      if plugin.ID in self._plugins_credentials:
         del self._plugins_credentials[plugin.ID]
      plugin.credentials=self.get_plugin_credentials(plugin,True)
      plugin.search(self.search_pattern)
   def notify_plugin_icon(self,plugin):
      #TODO: Add tooltips on icons
      icon_filename=os.path.join(APPDATA_PATH,"search-plugins",plugin.ID,"icon.png")
      if plugin.icon:
         plugin.icon.save(icon_filename,"png")
      else:
         try:
            plugin.icon=gtk.gdk.pixbuf_new_from_file(icon_filename)
         except:
            pass
      self.results_widget.notify_plugin_icon(plugin)
   def get_help_item(self,widget):
      res=widget
      widgets_to_help_items={
            self:None,
            self.searchbar:"searchbar",
            self.results_widget:"results-list",
            self.download_manager:"downloads-bar",
            self.search_options_box:"search-options",
      }
      try:
         while not res in widgets_to_help_items:
            res=res.get_parent()
         res=widgets_to_help_items[res]
      except:
         res=None
      return res
   def _on_key_press_event(self,widget,event):
      if event.keyval==gtk.keysyms.F1:
         item=self.get_help_item(self.get_focus())
         self.show_help(item)
         return True
   def show_help(self,item=None):
      if PLATFORM=="windows":
         import win32help
         itemsmap={
         "searchbar":"ch02s03.html#searchbar",
         "results-list":"ch02s03.html#results-list",
         "downloads-bar":"ch02s03.html#downloads-bar",
         "search-options":"ch02s03.html#search-options",
         "preferences-general":"ch03.html#preferences-general",
         "preferences-plugins":"ch03s02.html",
         }
         helpfile=os.path.join(self.options.share_dir,"winhelp",locale.getlocale()[0].split("_")[0])+".chm"
         if not os.path.exists(helpfile):
            helpfile=os.path.join(self.options.share_dir,"winhelp","en")+".chm"
         if item:
            topic=itemsmap[item]
            win32help.HtmlHelp(None,helpfile,win32help.HH_DISPLAY_TOPIC,topic)
         else:
            win32help.HtmlHelp(None,helpfile,win32help.HH_DISPLAY_TOC)
      else:
         url="ghelp:torrent-search"
         if item:
            url+='?'+item
         if os.fork()==0:
            try:
               os.execvp("gnome-help",("",url))
            finally:
               exit(0)
   def _on_window_configure_event(self,window,event):
      if not self._maximized:
         if self.window:
            self.config['window_width']=event.width
            self.config['window_height']=event.height
            self.config['window_x']=event.x
            self.config['window_y']=event.y
   def add_accelerator(self,widget,signal,*args):
      widget.add_accelerator(signal,self._accel_group,*args)
   def check_config(self):
      try:
         if not self.config["torrent_mode"] in ["save_in_folder", "use_standard_app", "use_custom_app"]:
            self.config["torrent_mode"]="save_in_folder"
            self.error_mesg(_("INCORRECT_CONFIG"),_("CHECK_CONFIG"))
            return
         if self.config["torrent_mode"]=="save_in_folder":
            path=self.config["torrent_save_folder"]
            if not os.path.exists(path):
               self.error_mesg(_("SAVE_FOLDER_NO_EXIST"),_("CHECK_CONFIG"))
            elif not os.path.isdir(path):
               self.error_mesg(_("SAVE_FOLDER_NOT_FOLDER"),_("CHECK_CONFIG"))
            elif not os.access(path,os.W_OK):
               self.error_mesg(_("SAVE_FOLDER_NOT_WRITABLE"),_("CHECK_CONFIG"))
         elif self.config["torrent_mode"]=="use_standard_app":
            selCommand=None
            selAppID=self.config["torrent_standard_app"]
            for appID, label, command in torrentApps.listApps():
               if appID==selAppID:
                  selCommand=command
            if selCommand==None:
               self.error_mesg(_("TORRENT_APP_NOT_FOUND"),_("CHECK_CONFIG"))
         else:
            command=self.config["torrent_custom_app"]#TODO: Check config under windows
            ex=command.split(" ")[0]
            expath=None
            for i in os.getenv('PATH').split(":"):
               path=os.path.join(i,ex)
               if os.path.exists(path) and os.path.isfile(path) and os.access(path,os.EX_OK):
                  expath=path
                  break
            if expath==None:
               self.error_mesg(_("TORRENT_APP_NOT_FOUND"),_("CHECK_CONFIG"))
      except:
         pass
   def on_config_changed(self,key,value):
      if key in ["hide_zero_seeders", "min_size_enable", "max_size_enable", "min_size_value", "max_size_value", "min_size_unit", "max_size_unit", "only_exact_phrase", "only_all_words", "name_does_not_contain", "name_contains", "after_date_enable", "after_date", "before_date_enable", "before_date", "category"]:
         self.results_widget.refilter()
      if key=="filter_duplicates":
         self.results_widget.refilter_duplicates()
      if key=="search_history":
         self.searchbar.update_completion()
   def get_tempfile(self):
      fd,filename=tempfile.mkstemp()
      self._tempfiles.append(filename)
      return fd,filename
   def _on_window_state_event(self,window,event):
      if event.new_window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED:
         self._maximized=True
      else:
         self._maximized=False
      self.config['window_maximized']=self._maximized
   def rec_mkdir(self,path):
      if os.path.exists(path):
         return
      basepath,filename=os.path.split(path)
      self.rec_mkdir(basepath)
      os.mkdir(path)
   def load_search_plugins(self):
      if not hasattr(self, "search_plugins"):
         self.search_plugins = []
      while len(self.search_plugins):
         del self.search_plugins[0]
      plugins_path=os.path.join(APPDATA_PATH,"search-plugins")
      self.rec_mkdir(plugins_path)
      for i in os.listdir(plugins_path):
         path=os.path.join(plugins_path,i)
         if os.path.isdir(path):
            self.load_search_plugin_from_path(path)
      if self.options.add_plugin:
         self.load_search_plugin_from_path(self.options.add_plugin)
      not_confirmed=[]
      for i in self.search_plugins:
         if i.require_auth and not i.ID in self.config["confirmed_plugins"]:
            not_confirmed.append(i)
      if not_confirmed:
         self.confirm_plugins(not_confirmed)
   def confirm_plugins(self,plugins):
      l=self.config["confirmed_plugins"]
      for i in plugins:
         l.append(i.ID)
      self.config["confirmed_plugins"]=l
      ConfirmPluginsDialog(self,plugins).run()
   def load_search_plugin_from_path(self,path):
      try:
         self.search_plugins.append(Plugin.load_plugin(self,path))
      except PluginException:
         exc_class,exc,traceback=sys.exc_info()
         exc.handle()
   def add_result(self,plugin,result):
      if not plugin in self.search_plugins:
         return
      self.results_widget.append(plugin,result)
      del result
      total=0
      exact_total=True
      for i in self.search_plugins:
         if i.enabled:
            n=i.results_count
            if n==-1:
               exact_total=False
            else:
               if self.config["stop_search_when_nb_plugin_results_reaches_enabled"]:
                  n=min(n,self.config["stop_search_when_nb_plugin_results_reaches_value"])
               try:
                  total+=n
               except:
                  exact_total=False
      if exact_total:
         total_str=str(total)
      else:
         total_str=str(max(total,len(self.results_widget)))+"+"
      try:
         self.search_results_label.set_markup("<b>%s - %d / %s (%s)</b>"%(_("SEARCH_RESULTS"),len(self.results_widget),total_str, (_("NB_RESULTS_SHOWN")%self.results_widget.nb_results_shown)))
      except:
         pass
      if self.config["stop_search_when_nb_results_reaches_enabled"] and len(self.results_widget)>=self.config["stop_search_when_nb_results_reaches_value"]:
         self.stop_search(self.search_plugins)
   def stop_search(self,plugins,threaded=False):
      if not threaded:
         thread.start_new_thread(self.stop_search,(plugins,True))
         self.set_title(APPNAME)
         self.search_results_label.set_markup("<b>%s</b>"%_("SEARCH_RESULTS"))
         try:
            self.set_title("%s - %s - "%(APPNAME,self.search_pattern)+_("NB_RESULTS")%len(self.results_widget))
            self.search_results_label.set_markup("<b>"+_("SEARCH_RESULTS")+" - "+_("NB_RESULTS")%len(self.results_widget)+" ("+_("NB_RESULTS_SHOWN")%self.results_widget.nb_results_shown+")"+"</b>")
         except:
            self.set_title("%s - %s - %s"%(APPNAME,self.search_pattern,_("SEARCH_FINISHED")))
         self.searchbar.stop_button.set_sensitive(False)
         self.load_search_plugins()
         return
      self.increase_searches_to_clean()
      while len(plugins):
         plugins[0].stop()
         del plugins[0]
      self.decrease_searches_to_clean()
   def error_mesg(self,mesg,submesg=""):
      d=gtk.MessageDialog(self,0,gtk.MESSAGE_ERROR)
      d.set_title(_("ERROR"))
      d.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
      d.set_markup("<span size='large'><b>%s</b></span>"%mesg)
      if submesg:
         d.format_secondary_text(submesg)
      d.show_all()
      d.run()
      d.destroy()
   def info_mesg(self,mesg,submesg=""):
      d=gtk.MessageDialog(self,0,gtk.MESSAGE_INFO)
      d.set_title(_("INFORMATION"))
      d.add_button(gtk.STOCK_OK,gtk.RESPONSE_OK)
      d.set_markup("<span size='large'><b>%s</b></span>"%mesg)
      if submesg:
         d.format_secondary_text(submesg)
      d.show_all()
      d.run()
      d.destroy()
   def ext_run_search(self,pattern):
      if self.cleanup_timer:
         gobject.source_remove(self.cleanup_timer)
         self.cleanup_timer=None
      self.show_all()
      self.present()
      if pattern:
         self.run_search(pattern)
         self.searchbar.set_pattern(pattern)
   def run_search(self,pattern):
      self.stop_search(self.search_plugins)
      self.searchbar.stop_button.set_sensitive(True)
      plugins=[]
      for i in self.search_plugins:
         if i.enabled:
            plugins.append(i)
      if not plugins:
         self.error_mesg(_("NO_PLUGINS_ENABLED"),_("CHECK_CONFIG"))
         return
      self.plugins_count=len(plugins)
      self.search_pattern=pattern
      self.results_widget.clear()
      self.search_results_label.set_markup("<b>%s</b>"%_("SEARCH_RESULTS_INIT"))
      self.set_title("%s - %s - %s"%(APPNAME,pattern,_("SEARCH_RUNNING")))
      self.nb_plugins_search_finished=0
      for i in plugins:
         if i.require_auth and not i.credentials:
            i.credentials=self.get_plugin_credentials(i)
      for i in plugins:
         i.search(pattern)
      self._search_id+=1
   def get_plugin_credentials(self,plugin, failed=False):
      if not plugin.ID in self._plugins_credentials:
         if plugin.ID in self.auth_memory:
            self._plugins_credentials[plugin.ID]=self.auth_memory[plugin.ID]
         else:
            res=self.auth_dialog.run(plugin,failed)
            if res:
               username,password,remember=res
               self._plugins_credentials[plugin.ID]=(username,password)
               if remember:
                  self.auth_memory[plugin.ID]=(username,password)
      if plugin.ID in self._plugins_credentials:
         return self._plugins_credentials[plugin.ID]
      else:
         plugin.enabled=False
         return None
   def show_about_dialog(self):
      self.about_dialog.run()
   def show_preferences_dialog(self):
      self.preferences_dialog.run()
   def download(self,result):
      self.download_manager.append(result)
   def notify_search_finished(self,plugin):
      if not plugin in self.search_plugins:
         return
      self.nb_plugins_search_finished+=1
      if self.nb_plugins_search_finished==self.plugins_count and len(self.results_widget)==0:
         self.searchbar.stop_button.set_sensitive(False)
         self.search_results_label.set_markup("<b>%s</b>"%_("SEARCH_RESULTS_NO_RESULTS"))
         self.set_title("%s - %s - %s"%(APPNAME,self.search_pattern,_("NO_RESULTS")))
      elif self.nb_plugins_search_finished==self.plugins_count:
         self.searchbar.stop_button.set_sensitive(False)
         try:
            self.set_title("%s - %s - "%(APPNAME,self.search_pattern)+_("NB_RESULTS")%len(self.results_widget))
            self.search_results_label.set_markup("<b>"+_("SEARCH_RESULTS")+" - "+_("NB_RESULTS")%len(self.results_widget)+" ("+_("NB_RESULTS_SHOWN")%self.results_widget.nb_results_shown+")"+"</b>")
         except:
            self.set_title("%s - %s - %s"%(APPNAME,self.search_pattern,_("SEARCH_FINISHED")))
   def check_new_version(self):
      try:
         c=httplib2.Http()
         resp,content=c.request("http://torrent-search.sourceforge.net/last_version/"+PLATFORM)
         if resp.status!=200:
            self.last_version=""
            return
         data=content.splitlines()
         self.last_version_files=data[1:]
         self.last_version=data[0]
      except:
         self.last_version=""
   def _get_last_version(self):
      self.last_version_lock.acquire()
      res=self._last_version
      self.last_version_lock.release()
      return res
   def _set_last_version(self,value):
      self.last_version_lock.acquire()
      if type(value)==str:
         if not re.match("^((([0-9]+)((\.|\-)?))*)$",value):
            value=""
      self._last_version=value
      self.last_version_lock.release()
   last_version=property(_get_last_version,_set_last_version)
   def _get_last_version_files(self):
      self.last_version_lock.acquire()
      res=self._last_version_files
      self.last_version_lock.release()
      return res
   def _set_last_version_files(self,value):
      self.last_version_lock.acquire()
      self._last_version_files=value
      self.last_version_lock.release()
   last_version_files=property(_get_last_version_files,_set_last_version_files)
   def watch_new_version(self):
      if self.last_version==None:
         return True
      if self.last_version!="" and program_version.ProgramVersionGreater(self.last_version,VERSION):
         if self.must_notify_version(self.last_version):
            self.notify_version(self.last_version)
      return False
   def notify_version(self,version):
      self.config["last_version_notified"]=version
      if VersionNotifierDialog(self).run(version):
         files=VersionAvailableFilesDialog(self,self.last_version_files).run()
         if files:
            url,filename,size=VersionFileSelectorDialog(self,files).run()
            dest=VersionDestinationDialog(self,filename).run()
            if dest:
               if VersionDownloadDialog(self,url,filename,size,dest).run():
                  self.info_mesg(_("DOWNLOAD_SUCCESSFUL"))
               else:
                  VersionDownloadErrorDialog(self,DOWNLOAD_URI).run()
         elif files!=None:
            VersionNoFilesDialog(self,DOWNLOAD_URI).run()
   def must_notify_version(self,version):
      if not self.config["dont_show_new_version_again"]:
         return True
      return version!=self.config["last_version_notified"]
   def check_plugin_updates(self):
      #TODO!: Handle the possibility of removing deprecated plugins
      if Plugin.PluginsUpdatesChecker(self).run():
         old_plugin_ids=[]
         for i in self.search_plugins:
            old_plugin_ids.append(i.ID)
         self.load_search_plugins()
         for i in self.search_plugins:
            if i.default_disable and not i.ID in old_plugin_ids:
               i.enabled=False #TODO: Add notification dialog about default disabled plugins
   def run(self):
      gobject.threads_init()
      self._http_queue.start()
      self.show_all()
      self.check_config()
      if self.config["check_plugins_updates"] and not self.options.no_plugins_check:
         self.check_plugin_updates()
      self.preferences_dialog=config.PreferencesDialog(self)
      if self.options.search_pattern:
         self.run_search(self.options.search_pattern)
         self.searchbar.set_pattern(self.options.search_pattern)
      self.last_version=None
      gobject.timeout_add(100,self.watch_new_version)
      thread.start_new_thread(self.check_new_version,())
      self.searchbar.focus_entry()
      gtk.main()
      self._http_queue.stop()
      for i in self._tempfiles:
         try:
            os.unlink(i)
         except:
            pass
   def check_searches_clean(self):
      if self.searches_to_clean:
         os.write(1,"\rCleaning up (%d operation(s) remaining)...    "%self.searches_to_clean)
         return True
      else:
         gtk.main_quit()
         return False
   def quit(self):
      self.hide()
      while gtk.gdk.events_pending():
         gtk.main_iteration()
      gtk.main_quit()
   def _get_searches_to_clean(self):
      self.searches_to_clean_lock.acquire()
      res=self._searches_to_clean
      self.searches_to_clean_lock.release()
      return res
   def _set_searches_to_clean(self,value):
      self.searches_to_clean_lock.acquire()
      self._searches_to_clean=value
      self.searches_to_clean_lock.release()
   searches_to_clean=property(_get_searches_to_clean,_set_searches_to_clean)
   def increase_searches_to_clean(self):
      self.searches_to_clean_lock.acquire()
      self._searches_to_clean+=1
      self.searches_to_clean_lock.release()
   def decrease_searches_to_clean(self):
      self.searches_to_clean_lock.acquire()
      self._searches_to_clean-=1
      self.searches_to_clean_lock.release()

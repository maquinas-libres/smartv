#! /usr/bin/python
# -*- coding=utf-8 -*-

import TorrentSearch, libxml2, datetime, os, httplib2, urllib
from TorrentSearch import htmltools

class TorrentzPluginResult(TorrentSearch.Plugin.PluginResult):
   def __init__(self,label,date,size,torrent_link):
      self.torrent_link=torrent_link
      TorrentSearch.Plugin.PluginResult.__init__(self,label,date,size)
   def _do_get_link(self):
      return self.torrent_link

class TorrentzPlugin(TorrentSearch.Plugin.Plugin):
   def _formatSize(self, data):
      data=eval(data)
      units=['B','KB','MB','GB','TB']
      ui=0
      while data>=1024:
         ui+=1
         data/=1024.
      return "%.1f %s"%(data,units[ui])
   def _run_search(self,pattern):
      url="https://torrentz.eu/feed_any?q="+urllib.quote(pattern)
      resp,content=self.http_queue_request(url)
      tree=libxml2.parseDoc(content)
      results=htmltools.find_elements(tree.getRootElement(), "item")
      self.results_count=len(results)
      for i in results:
         title=htmltools.find_elements(i, "title")[0].getContent()
         date=htmltools.find_elements(i, "pubDate")[0].getContent()
         day,month,year=date.split(" ")[1:4]
         while day[0]=="0":
            day=day[1:]
         day=eval(day)
         year=eval(year)
         month=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(month)+1
         date=datetime.date(year,month,day)
         link=htmltools.find_elements(i, "link")[0].getContent()
         torrent_link=htmltools.find_elements(i, "link")[0].getContent()
         description=htmltools.find_elements(i, "description")[0].getContent()
	 #Size: 2295 MB Seeds: 0 Peers: 227 Hash: a1eb4f23b599b5e6dc10c8637981973990e394b2
         size=description.split(" ")[1] + description.split(" ")[2]
         #seeders=description.split(" ")[4]
         #leechers=description.split(" ")[6]
         self.add_result(TorrentzPluginResult(title, date, size, torrent_link))
         if self.stop_search:
            return


# -*- coding: utf-8 -*-

'''
    Sorozatok.net Addon
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

import platform
import xml.etree.ElementTree as ET

os_info = platform.platform()
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))
addon_xml_path = os.path.join(parent_directory, "addon.xml")

tree = ET.parse(addon_xml_path)
root = tree.getroot()
version = root.attrib.get("version")

xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info}', xbmc.LOGINFO)

base_url = 'https://sorozatok.net'

cookies = {
    '__e_inc': '1',
    'view': 'simple',
    'clickadu': '1',
    'clickadu2': '1',
    'adcash': '1',
    'adsterra': '1',
    'order_ch': 'new',
}

headers = {
    'authority': 'sorozatok.net',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def root(self):
        self.addDirectoryItem("Sorozatok", f"series_items", '', 'DefaultFolder.png')
        self.addDirectoryItem("Kategóriák", "categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategories(self):
        page = requests.get(f"{base_url}/channels.php?order=new", headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        genre_elements = soup.select('.fc-genre-list li')
        
        for genre_element in genre_elements:
            gen_id = genre_element.select_one('input')['value']
            gen_name = genre_element.label.get_text(strip=True)

            cat_link = f'{base_url}/channels.php?order=new&cat={gen_id}'
            
            self.addDirectoryItem(f"{gen_name}", f'items&url={quote_plus(cat_link)}', '', 'DefaultFolder.png')
        
        self.endDirectory()

    def getItems(self, url):
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
    
        video_divs = soup.find_all('div', class_='video sorozat-lista')
        
        for video_div in video_divs:
            page_url = video_div.find('a', class_='clip-link')['href']
            card_link = f'{base_url}{page_url}'
            
            img = video_div.find('img', class_='sorozat-listazo')['src']
            img_url = re.findall(r'&url=(.*)', img)[0].strip()
            
            year = video_div.find('span', class_='timer').text.strip()
            hun_title = video_div.find('h4', class_='video-title').text.strip()

            self.addDirectoryItem(f'[B]{hun_title} - {year}[/B]', f'extract_series&url={card_link}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
        
        try:
            next_page_link = soup.find('a', class_='next')['href'] if soup.find('a', class_='next') else None
            
            if next_page_link:
                next_page_url = f'{base_url}{next_page_link}'
                self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except (AttributeError, requests.exceptions.ConnectionError):
            xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getSeriesItems(self, url):
        page = requests.get(f"{base_url}/channels.php?order=new", headers=headers, cookies=cookies)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        video_divs = soup.find_all('div', class_='video sorozat-lista')
        
        for video_div in video_divs:
            page_url = video_div.find('a', class_='clip-link')['href']
            card_link = f'{base_url}{page_url}'
            
            img = video_div.find('img', class_='sorozat-listazo')['src']
            img_url = re.findall(r'&url=(.*)', img)[0].strip()
            
            year = video_div.find('span', class_='timer').text.strip()
            hun_title = video_div.find('h4', class_='video-title').text.strip()

            self.addDirectoryItem(f'[B]{hun_title} - {year}[/B]', f'extract_series&url={card_link}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
        
        try:
            next_page_link = soup.find('a', class_='next')['href'] if soup.find('a', class_='next') else None
            
            if next_page_link:
                next_page_url = f'{base_url}{next_page_link}'
                self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except (AttributeError, requests.exceptions.ConnectionError):
            xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getSeriesItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def extractSeries(self, url, img_url, hun_title, content):
        import re
        
        response = requests.get(url, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        series_hun_title_tag = soup.find('h4', class_='profile-user')
        series_hun_title = series_hun_title_tag.text.strip() if series_hun_title_tag else None
        
        series_en_title_tag = soup.find('p', class_='profile-location')
        series_en_title = series_en_title_tag.text.strip() if series_en_title_tag else None

        img_tag = soup.find('img', class_='profile-image')
        if img_tag:
            img_src = img_tag['src']
            img_url = re.findall(r'url=(.*)', img_src)[0].strip()

        year = re.findall(r'<b>Év:.*?(\d+).*', str(soup))[0].strip()

        content = re.findall(r'<b>Tartalom:<\/b>(.*?)<', str(soup), re.DOTALL)[0].strip()

        episodes = soup.find_all('div', class_='video')

        series_dict = {
            "series_hun_title": series_hun_title,
            "series_en_title": series_en_title,
            "img_url": img_url,
            "year": year,
            "content": content,
            "seasons": [],
        }

        current_season_number = None
        current_season = None
        
        for episode in episodes:
            episode_link = episode.find('a', class_='clip-link')['href']
            episode_title = episode.find('h4', class_='video-title').a.text.strip()
            matches = re.findall(r'\d+', episode_title)
            
            if matches and len(matches) >= 2:
                season_number, episode_number = map(int, matches[:2])

                season_dict = next((season for season in series_dict["seasons"] if season["season_number"] == season_number), None)
                
                if season_dict:
                    season_dict["episodes"].append({
                        'episode_number': episode_number,
                        'title': episode_title,
                        'link': f"https://sorozatok.net{episode_link}"
                    })
                else:
                    new_season_dict = {
                        "season_number": season_number,
                        "episodes": [{
                            'episode_number': episode_number,
                            'title': episode_title,
                            'link': f"https://sorozatok.net{episode_link}"
                        }],
                    }
                    series_dict["seasons"].append(new_season_dict)

        series_dict["seasons"].sort(key=lambda x: x.get('season_number', 0))

        for season in series_dict["seasons"]:
            if "episodes" in season:
                for episode in season["episodes"]:
                    hun_title = episode["title"]
                    ep_link = episode["link"]
                    
                    self.addDirectoryItem(f'[B]{hun_title}[/B]', f'extract_episodes&url={quote_plus(ep_link)}&img_url={img_url}&hun_title={hun_title}&content={content}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title, 'plot': content})

        self.endDirectory('series')    

    def extractEpisodes(self, url, img_url, hun_title, content):
        import re
        import requests
        from bs4 import BeautifulSoup

        headers_1 = {
            'authority': 'sorozatok.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        
        response_1 = requests.get(url, headers=headers_1).text
        
        url_id = re.findall(r'watch.*v=(.*)', url)[0].strip()
        find_embed_id = re.findall(r'data-id=\"(.*?)\".*'+url_id+'', str(response_1))[0].strip()
        embed_go = f'https://sorozatok.net/go.php?id={find_embed_id}&key={url_id}'
        
        import requests
        
        resp_2 = requests.head(embed_go, allow_redirects=True)
        streamplay_url = f'{resp_2.url}'
        
        def hunter(h, u, n, t, e, r):
            return bytes(int(''.join(str(n.index(c))for c in s), e) - t for s in h.split(n[e]) if s).decode('utf-8')
        
        resp_3 = requests.get(streamplay_url).text
        
        hunter_pattern = r"decodeURIComponent\(escape\(r\)\)\}(.*?)\)</script>"
        player_pattern = r'"(/videoplayback.php\?hash=(.*?))"'
        for f in re.findall(hunter_pattern, resp_3):
            if m := re.search(player_pattern, hunter(*eval(f))):
                videoplayback_url_hash = 'https://streamplay.pw' + m.group(1)
                
                resp_4 = requests.head(videoplayback_url_hash, allow_redirects=True)
                final_url = f'{resp_4.url}'
                
                self.addDirectoryItem(f'[B]{hun_title}[/B]', f'play_movie&url={final_url}&img_url={img_url}&hun_title={hun_title}&content={content}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': hun_title, 'plot': content})

        self.endDirectory('series')

    def playMovie(self, url):
        
        xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | playMovie | url | {url}', xbmc.LOGINFO)
        
        try:
            direct_url = urlresolver.resolve(url)
            
            xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Sorozatok.net", "Törölt tartalom", time=5000)

    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                
                import requests
                import json
                
                json_list = requests.get('https://sorozatok.net/api/search.json').json()
                
                def search_and_loop(search_in):
                    results = []
                
                    for s_item in json_list:
                        if (
                            search_in.lower() in s_item['cat_name'].lower() or
                            search_in.lower() in s_item['cat_eng'].lower() or
                            search_in.lower() == s_item['year']
                        ):
                            results.append(s_item)
                
                    return results
                
                search_in = item
                
                search_results = search_and_loop(search_in)
                
                if search_results:
                    for result in search_results:
                        title = result['cat_name']
                        year = result['year']
                        
                        hun_title = f'{title} - {year}'
                        
                        url_part = result['url']
                        url = f'{base_url}/{url_part}-online'
                        
                        #xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | getSearches | url | {url}', xbmc.LOGINFO)
                
                        self.addDirectoryItem(hun_title, f'extract_series&url={url}', '', 'DefaultFolder.png')                   
            
            if len(items) > 0:
                self.addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = open(self.searchFileName, "a")
            file.write(f"{search_text}\n")
            file.close()

            import requests
            import json
            
            json_list = requests.get('https://sorozatok.net/api/search.json').json()
            
            def search_and_loop(search_in):
                results = []
            
                for item in json_list:
                    if (
                        search_in.lower() in item['cat_name'].lower() or
                        search_in.lower() in item['cat_eng'].lower() or
                        search_in.lower() == item['year']
                    ):
                        results.append(item)
            
                return results
            
            search_in = search_text
            
            search_results = search_and_loop(search_in)
            
            if search_results:
                for result in search_results:
                    title = result['cat_name']
                    year = result['year']
                    
                    hun_title = f'{title} - {year}'
                    
                    url_part = result['url']
                    url = f'{base_url}/{url_part}-online'
                    
                    #xbmc.log(f'Sorozatok.net | v{version} | Kodi: {kodi_version[:5]}| OS: {os_info} | doSearch | url | {url}', xbmc.LOGINFO)
                    
                    self.addDirectoryItem(hun_title, f'extract_series&url={url}', '', 'DefaultFolder.png')
                    
                self.getItems(url)

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)
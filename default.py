# -*- coding: utf-8 -*-

'''
    Sorozatok.net Add-on
    Copyright (C) 2020 heg, vargalex

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

mediatype = params.get('mediatype')
video_id = params.get('video_id')
img_url = params.get('img_url')
hun_title = params.get('hun_title')
content = params.get('content')
provider = params.get('provider')
ep_title = params.get('ep_title')

if action is None:
    navigator.navigator().root()

elif action == 'categories':
    navigator.navigator().getCategories()

elif action == 'extract_episodes':
    navigator.navigator().extractEpisodes(url, img_url, hun_title, content)

elif action == 'extract_series':
    navigator.navigator().extractSeries(url, img_url, hun_title, content)

elif action == 'items':
    navigator.navigator().getItems(url)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'series_items':
    navigator.navigator().getSeriesItems(url)

elif action == 'play_movie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory()
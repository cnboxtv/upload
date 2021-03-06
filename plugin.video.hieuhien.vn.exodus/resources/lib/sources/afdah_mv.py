# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

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


import re,urllib,urlparse,random

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.domains = ['fmovie.co', 'afdah.org', 'xmovies8.org', 'putlockerhd.co']
        self.base_link = 'https://fmovie.co'
        self.search_link = '/results?q=%s'


    def movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query)

            title = cleantitle.get(title)
            years = ['%s' % str(year)]

            result = client.parseDOM(result, 'div', attrs = {'class': 'cell_container'})
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(i[0], re.compile('(.+?) [(](\d{4})[)]').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1]) for i in result if len(i[1]) > 0]
            result = [i for i in result if title == cleantitle.get(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            referer = urlparse.urljoin(self.base_link, url)

            headers = {'X-Requested-With': 'XMLHttpRequest'}

            post = urlparse.parse_qs(urlparse.urlparse(referer).query).values()[0][0]
            post = urllib.urlencode({'v': post})

            url = urlparse.urljoin(self.base_link, '/video_info/iframe')

            result = client.request(url, post=post, headers=headers, referer=referer)

            result = re.compile('"(\d+)"\s*:\s*"([^"]+)').findall(result)
            result = [(urllib.unquote(i[1].split('url=')[-1]), i[0])  for i in result]

            links = [(i[0], '1080p') for i in result if int(i[1]) >= 1080]
            links += [(i[0], 'HD') for i in result if 720 <= int(i[1]) < 1080]
            links += [(i[0], 'SD') for i in result if 480 <= int(i[1]) < 720]

            for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'provider': 'Afdah', 'url': i[0], 'direct': True, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return



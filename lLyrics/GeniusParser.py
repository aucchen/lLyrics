# -*- coding: utf-8 -*-
# Parser for Genius.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request, urllib.error, urllib.parse
import re
import string

from html.parser import HTMLParser

import Util


class Parser(HTMLParser):
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.in_lyrics_container = False
        self.lyrics = ""

    def parse(self):
        # remove punctuation from artist/title
        self.artist = self.artist.replace("+", "and")
        if 'feat.' in self.artist:
            feat_index = self.artist.find('feat.')
            self.artist = self.artist[:feat_index].strip()
        if '[' in self.title:
            self.title = re.sub("\[.*\]", '', self.title).strip()

        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)

        # create lyrics Url
        url = "http://genius.com/" + clean_artist.replace(" ", "-") + "-" + clean_title.replace(" ", "-") + "-lyrics"
        print("rapgenius Url " + url)
        try:
            resp = urllib.request.urlopen(Util.add_request_header(url), None, 3).read()
        except:
            print("could not connect to genius.com")
            return ""

        resp = Util.bytes_to_string(resp)

        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()

        return self.lyrics

    def handle_starttag(self, tag, attrs):
        # 1.
        attrs = {k: v for k, v in attrs}
        if tag == 'div' and 'class' in attrs:
            cl = attrs['class']
            if cl.startswith('Lyrics__Container'):
                self.in_lyrics_container = True
                if len(self.lyrics) > 0:
                    self.lyrics += '\n'
        if tag == 'br':
            if self.in_lyrics_container:
                self.lyrics += '\n'

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_lyrics_container:
                self.in_lyrics_container = False

    def handle_data(self, data):
        if self.in_lyrics_container:
            data = str(data)
            self.lyrics += data

    def get_lyrics(self, resp):
        self.feed(resp)
        return self.lyrics

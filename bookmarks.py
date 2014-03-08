#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
import datetime
import json
import shelve
import shlex
from urllib.parse import unquote

import bottle


########################################################################
##### Global variables
BASEPATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_FILE = 'bookmarks.db'

FIREFOX_JSON = 'bookmarks-20140307.json'

# log
LOG_FILE = 'bookmarks.log'
LOG_LEVEL = logging.INFO
log = logging.getLogger('Bookmarks')

bs = None


########################################################################
##### Initialization
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s  %(name)s(%(module)12s:%(lineno)4d)  %(levelname).1s  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=os.path.join(BASEPATH, LOG_FILE),
                    filemode='w')


########################################################################
##### Helper functions
def import_firefox_json(bs, filename):
    def parse(obj, intags=None):
        res = []
        tags = intags.copy() if intags else []
        if 'title' in obj:
            title = obj['title'].strip()
            if title and title not in tags:
                if title not in ('Bookmarks Menu', 'Bookmarks Toolbar'):
                    tags.append(title)
        for o in obj['children']:
            if (type(o) == type(dict())) and ('uri' in o):
                added = datetime.datetime.fromtimestamp(int(o['dateAdded']/1e6)) if 'dateAdded' in o else None
                res.append((o['title'], o['uri'], tags, added))
            if 'children' in o:
                res.extend(parse(o, tags))
        return res

    log.info('Importing bookmarks from Firefox in json format')
    with open(filename) as f:
        try:
            root = json.load(f)
        except:
            print('ERROR: importing bookmarks from Firefox json')
            raise
        else:
            for b in parse(root):
                bs.add(b[0], b[1], b[2], b[3])


def parse_searchterm(text):
    def add_elm(d, elm):
        if elm == '':
            return
        if len(elm) == 1:
            d['|'].append(elm)
        e = elm[1:].strip()
        if e == '':
            return
        if elm[0] == '-':
            d['-'].append(e)
        elif elm[0] == '+':
            d['&'].append(e)
        else:
            d['|'].append(elm)

    terms, tags, years = {'&': [], '|': [], '-': []}, {'&': [], '|': [], '-': []},  {'&': [], '|': [], '-': []}
    for t in shlex.split(text):
        t = t.strip().lower()
        if t.startswith('tag:'):
            for e in t[4:].split(','):
                add_elm(tags, e.strip())
        elif t.startswith('year:'):
            for e in t[5:].split(','):
                add_elm(years, e.strip())
        else:
            add_elm(terms, t)
    return terms, tags, years


########################################################################
##### Data structures
class Bookmark:
    def __init__(self, title, url, tags=[], added=None):
        self.title = title
        self.url = url
        self.added = added if added else datetime.datetime.now()
        self.tags = tags

    def __repr__(self):
        return '<{}: [{}]>'.format(self.title, ','.join(self.tags))


class Bookmarks:
    def __init__(self):
        self._db = shelve.open(os.path.join(BASEPATH, DATA_FILE))
        log.info('Initialized data, {} bookmarks found'.format(len(self._db)))

    def close(self):
        log.info('Closing storage')
        self._db.close()

    @property
    def num_bookmarks(self):
        return len(self._db)

    @property
    def num_tags(self):
        return len(self.tags)

    def add(self, title, url, tags=None, added=None):
        if url in self._db:
            log.warning('ERROR adding bookmark: URL already exists: {}'.format(url))
            return
        self._db[url] = Bookmark(title, url, tags if tags else [], added)
        log.info('Added bookmark: {}'.format(self._db[url]))

    def edit(self, url_old, title, url, tags):
        if url_old == url:
            b = self._db[url]
            b.title = title
            b.tags = tags
            self._db[url] = b
        else:
            added = self._db[url_old].added
            del self._db[url_old]
            self.add(title, url, tags, added)

    def remove(self, url):
        b = str(self._db[url])
        del self._db[url]
        log.info('Removed bookmark: {}'.format(b))

    def get_bytitle(self, title):
        for b in self._db.values():
            if b.title == title:
                return b

    def __check_terms(self, terms, title, url):
        for t in terms['-']:
            if t in title or t in url:
                return -1
        for t in terms['&']:
            return 1 if t in title or t in url else -1
        for t in terms['|']:
            if t in title or t in url:
                return 1
        return 0

    def __check_tags(self, tags, btags):
        for t in tags['-']:
            if t in btags:
                return -1
        for t in tags['&']:
            return 1 if t in btags else -1
        for t in tags['|']:
            if t in btags:
                return 1
        return 0

    def __check_years(self, years, byear):
        for y in years['-']:
            if int(y) == byear:
                return -1
        for y in years['&']:
            return 1 if int(y) == byear else -1
        for y in years['|']:
            if int(y) == byear:
                return 1
        return 0

    def search(self, text=''):
        if text == '':
            return [b for b in self._db.values()]
        terms, tags, years = parse_searchterm(text)
        res = []
        for b in self._db.values():
            f1 = self.__check_terms(terms, b.title.lower(), b.url.lower())
            if f1 < 0:
                continue
            f2 = self.__check_tags(tags, [t.lower() for t in b.tags])
            if f2 < 0:
                continue
            f3 = self.__check_years(years, b.added.year)
            if f3 < 0:
                continue
            if (f1 == 1) or (f2 == 1) or (f3 == 1):
                res.append(b)
        return res

    @property
    def tags(self):
        tags = set()
        [{tags.add(t) for t in b.tags if t} for b in self._db.values() if b.tags]
        return tags

    @property
    def tags_frequency(self):
        tags = dict()
        for b in self._db.values():
            for t in b.tags:
                tags[t] = tags[t]+1 if t in tags else 1
        return [(t, tags[t]) for t in sorted(tags, key=str.lower)]

    def filter_bytag(self, tags):
        res = []
        for b in self._db.values():
            for t in tags:
                if t in b.tags:
                    res.append(b)
        return res

    @property
    def years_frequency(self):
        years = dict()
        for b in self._db.values():
            y = b.added.year
            years[y] = years[y]+1 if y in years else 1
        return sorted([(y, f) for y, f in years.items()])

    def filter_byyear(self, year):
        res = []
        for b in self._db.values():
            if b.added.year == year:
                res.append(b)
        return res


########################################################################
##### web interface
app = bottle.Bottle()

# errors and static files
@app.error(404)
@bottle.view('error404')
def error404(error):
    return

@app.route('/favicon.ico')
def serve_favicon():
    return bottle.static_file('favicon.ico', root=os.path.join(BASEPATH, 'img'))

@app.route('/img/<filename>')
def serve_images(filename):
    return bottle.static_file(filename, root=os.path.join(BASEPATH, 'img'))

@app.route('/static/<filename>')
def serve_static(filename):
    return bottle.static_file(filename, root=os.path.join(BASEPATH, 'static'))

# ajax
@app.post('/ajax/add')
def add_bm():
    if not 'title' in bottle.request.params.keys() or not 'url' in bottle.request.params.keys():
        bottle.abort(400, 'Error adding bookmark')
    try:
        title = bottle.request.params.get('title').strip()
        url = bottle.request.params.get('url').strip()
        if 'tags' in bottle.request.params.keys():
            tags = [t.strip() for t in bottle.request.params.get('tags').strip().split(',')]
        else:
            tags = []
        bs.add(title, url, tags)
    except:
        bottle.abort(400, 'Error adding bookmark')

@app.post('/ajax/edit')
def edit_bm():
    if not 'url_old' in bottle.request.params.keys() or not 'title' in bottle.request.params.keys() or \
       not 'url' in bottle.request.params.keys() or not 'tags' in bottle.request.params.keys():
        bottle.abort(400, 'Error editing bookmark')
    try:
        url_old = bottle.request.params.get('url_old').strip()
        title = bottle.request.params.get('title').strip()
        url = bottle.request.params.get('url').strip()
        tags = [t.strip() for t in bottle.request.params.get('tags').strip().split(',')]
        bs.edit(url_old, title, url, tags)
    except:
        bottle.abort(400, 'Error editing bookmark')

@app.post('/ajax/remove')
def remove_bm():
    if not 'url' in bottle.request.params.keys():
        bottle.abort(400, 'Error removing bookmark: no URL provided')
    try:
        url = bottle.request.params.get('url').strip()
        bs.remove(url)
    except:
        log.error('Error removing bookmark with url: {}'.format(url))

# pages
@app.route('/new')
def new_bm():
    title = unquote(bottle.request.query.title).strip()
    url = unquote(bottle.request.query.url).strip()
    try:
        bs.add(title, url)
    except:
        return 'ERROR adding bookmark'
    return 'OK. Bookmark correctly added'

@app.route('/search/<text>')
@bottle.view('show_bookmarks.tpl')
def search(text=''):
    text = '' if text=='|none|' else text.strip()
    bks = bs.search(text)
    return dict(bks=bks, sterm=text)

@app.route('/year/<year:int>')
@bottle.view('show_bookmarks.tpl')
def search(year):
    bks = bs.filter_byyear(year)
    return dict(bks=bks, sterm='year:{}'.format(year))


@app.route('/')
@bottle.view('home.tpl')
def root():
    nbks = bs.num_bookmarks
    ntags = bs.num_tags
    tags_freq = bs.tags_frequency
    years_freq = bs.years_frequency
    return dict(nbks=nbks, ntags=ntags, tf=tags_freq, yf=years_freq)


########################################################################
##### Main
def main():
    global bs
    bs = Bookmarks()
    if len(sys.argv) == 3 and sys.argv[1] == '--import-firefox-json':
        import_firefox_json(bs, sys.argv[2])
    log.info('Standalone Server started')
    try:
        bottle.run(app, port=8891) #, debug=True, reloader=True)
    except:
        bs.close()
    else:
        bs.close()


if __name__ == '__main__':
    main()


########################################################################

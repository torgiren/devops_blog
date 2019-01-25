#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'TORGiren'
SITENAME = 'TORGiren DevOpses Blog'
#SITEURL = ''
SITEURL = 'https://blog.fabrykowski.pl'

PATH = 'content'

TIMEZONE = 'Europe/Warsaw'

DEFAULT_LANG = 'pl'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = None

# Social widget
SOCIAL = (
          ("<img width='auto' style='height:0.8em;' alt='YouTube logo' src='/images/youtube/youtube_social_icon_red.png'/> TORGiren DevOpses", "https://www.youtube.com/channel/UC_WIjAwEBoM5zvLQdbLrp7A"),
          ("TORGiren GitHub", "https://github.com/torgiren"),
          ("TORGiren StackOverflow", "https://stackoverflow.com/users/1234218/marcin-fabrykowski"),
          ("TORGiren ServerFault", "https://serverfault.com/users/185210/marcin-fabrykowski"),
          ("<img width='auto' style='height:0.8em;' alt='YouTube logo' src='/images/youtube/youtube_social_icon_red.png'/> TORGiren Plays", "https://www.youtube.com/channel/UC068mJpuvsuAyTXC0WrzSkw"),
         )

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
PLUGINS = ['sitemap', 'liquid_tags.youtube', 'thumbnailer', 'pelican_youtube']
PLUGIN_PATHS = ['pelican-plugins', 'pelican-plugins/pelican_youtube']

EXTERNDED_SITEMAP_PLUGIN = {
    'priotities': {
        'index': 1.0,
        'articles': 0.8,
        'pages': 0.5,
        'others': 0.4
    },
    'changefrequencies': {
        'index': 'daily',
        'articles': 'weekly',
        'pages': 'monthly',
        'others': 'monthly'
    }
}
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.8,
        'indexes': 1,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'weekly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}


#THEME = 'pelican-themes/uikit'
THEME = 'pelican-themes/tuxlite_tbs'

DEFAULT_METADATA = {
    'status': 'draft'
}

STATIC_PATHS = [
    'static',
    'images',
]
EXTRA_PATH_METADATA = {
    'static/robots.txt': {'path': 'robots.txt'},
    'static/favicon.ico': {'path': 'favicon.ico'},
    'static/android-chrome-192x192.png': {'path': 'android-chrome-192x192.png'},
    'static/android-chrome-512x512.png': {'path': 'android-chrome-512x512.png'},
    'static/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
    'static/favicon-16x16.png': {'path': 'favicon-16x16.png'},
    'static/favicon-32x32.png': {'path': 'favicon-32x32.png'},
    'static/site.webmanifest': {'path': 'site.webmanifest'},
}

IMAGE_PATH = 'images'
THUMBNAIL_DIR = 'thumbs'

DISPLAY_PAGES_ON_MENU = True
GITHUB_URL = "https://github.com/torgiren/devops_blog"

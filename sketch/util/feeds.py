#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#
"""
  Sketch - Utils - feeds.py

  feed generation and reading functions + helpers

"""

import re
import logging
from google.appengine.api import urlfetch

try:
  from BeautifulSoup import BeautifulSoup
except ImportError:
  try:
    from sketch.vendor.BeautifulSoup import BeautifulSoup
  except ImportError:
    raise "Could not find BeautifulSoup"

try:
  import feedparser
except ImportError:
  try:
    from sketch.vendor import feedparser
  except ImportError:
    raise "Could not find FeedParser"

feed_content_types = ['text/xml', 'application/rss+xml', 'application/atom+xml']
_format_re = re.compile(r'\$(?:(%s)|\{(%s)\})' % (('[a-zA-Z_][a-zA-Z0-9_]*',) * 2))


def get_content_type(req_headers):
  """
      Reads a dictionary of request headers and extracts content type and charset
  """
  header_ct = req_headers['content-type'].split('; ')
  content_type = header_ct[0]
  if len(header_ct) > 1:
    content_charset = header_ct[1].split('=')[1]
  else:
    content_charset = 'UTF-8'

  return content_type, content_charset

def discover_og(content):
  d = BeautifulSoup(content)
  t = d.findAll('meta', property=re.compile('^og:'))
  
def find_icons(url):
  result = urlfetch.fetch(url)
  if result.status_code != 200:
    return False

  d = BeautifulSoup(result.content)
  t = d.findAll('link', rel=re.compile('icon'))
  
  if not t:
    t = = d.findAll('meta', property=re.compile('^og:image'))
  
  if not t:
    return False
    
  icons = []
  for i in t:
    if i.has_key('href'):
      return i['href']
    if i.has_key('content'):
      return i['content']      
  return None
  # return icons
  
def discover_feed_hub(content):
  d = feedparser.parse(content)
  hub_list = []
  if not d['feed'].has_key('links'):
    return False
  for link in d['feed']['links']:
    if link['rel'] == 'hub':
      hub_list.append(link['href'])
  if len(hub_list) > 0:
    return hub_list
  return False


def discover_feed_self(content):
  d = feedparser.parse(content)
  if d['feed'].has_key('links'):
    for link in d['feed']['links']:
      if link['rel'] == 'self':
        return link['href']
  return None


def get_feed_title(content):
  d = feedparser.parse(content)
  if d['feed'].has_key('title'):
    return d['feed'].title
  return None

def get_page_title(content):
  s = BeautifulSoup(content)
  return s.find('title').text

def remove_html_tags(data):
  p = re.compile(r'<.*?>')
  return p.sub('', data)

def remove_extra_spaces(data):
  p = re.compile(r'\s+')
  return p.sub(' ', data)

def discover_feeds(url, base_href = ""):
  """
      Given HTML content will attempt to auto-discover all feed links, both RSS and Atom
  """
  result = urlfetch.fetch(url)
  if result.status_code != 200:
    return False  
  s = BeautifulSoup(result.content)
  t = s.findAll('link', rel='alternate')

  if not t:
    return False

  feeds_list = []
  title = ""

  for e in t:
    if not e.has_key('href') or not e.has_key('type'):
      logging.info("discover_feeds: Found an alternate that doesn't have a href or type: %s" % e)
      continue

    if not e['type'] in feed_content_types:
      logging.info("discover_feeds: Found an alternate that doesn't have right content type: %s" % e['type'])
      continue

    # TODO: Work out base_href here, when we put it in etc.
    # have to detect if we have a path or a
    # atm we just check for '/' - err
    feed_url = str(e['href'])
    if feed_url.startswith('/'):
      feed_url = base_href + e['href']

    feed = {
      "url": feed_url,
      "type": e['type']
    }

    if e.has_key('title'):
      feed['title'] = e['title']

    feeds_list.append(feed)

  if len(feeds_list) == 0:
    return False

  return feeds_list[0]['url']

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2010-2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#
"""
  buckley - models.py

  desc

  This source file is subject to the new BSD license that is bundled with this 
  package in the file LICENSE.txt. The license is also available online at the 
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""
from __future__ import division

__version__ = '0.0.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'



import sys
import math
import datetime
import logging
import sketch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

class Image(sketch.db.Model):
  dat = db.BlobProperty(default = None)
  mimetype = db.StringProperty()
  origurl = db.StringProperty()
  size = db.IntegerProperty()
  width = db.IntegerProperty()
  height = db.IntegerProperty()
  
  def get_scaled(self, maxwidth=640):
    w = self.width
    h = self.height
    if w > maxwidth:
      w = maxwidth
      h = int(math.floor((maxwidth / self.width) * self.height))
    return w, h
        
  def scaled_width(self, height=640):
    w, h = self.get_scaled(height)
    return w
    
  def scaled_height(self, width=640):
    return int(math.floor((width / self.width) * self.height))

class Source(sketch.db.Model):
  name = db.StringProperty()
  icon = db.ReferenceProperty(Image)
  web = db.StringProperty()
  feed = db.StringProperty()

  @classmethod
  def get_by_web(self, url):
    query = db.GqlQuery("select * from Source where web = :1", url)
    r= query.fetch(1)
    if r:
      return r[0]
    return False

class Post(sketch.db.Model):
  author = db.UserProperty()
  title = db.StringProperty()
  subtitle = db.StringProperty()
  excerpt = db.TextProperty()
  excerpt_html = db.TextProperty()
  content = db.TextProperty()
  content_html = db.TextProperty()
  embed_html = db.TextProperty()
  content_link = db.StringProperty()
  content_link_src = db.ReferenceProperty(Source)
  content_link_short = db.StringProperty()
  thumbnail = db.ReferenceProperty(Image)
  post_type = db.StringProperty(choices = set(['post', 'status', 'link', 'page']))
  status_type = db.StringProperty(choices = set(['link', 'text', 'article', 'video']))
  status = db.StringProperty(required=True, choices = set(['draft', 'scheduled', 'published']))
  categories = db.ListProperty(db.Category)
  order = db.IntegerProperty()
  stub = db.StringProperty()
  permalink = db.StringProperty()
  featured = db.BooleanProperty()
  cached = db.BooleanProperty()
  pubdate = db.DateTimeProperty()


  @property
  def url(self):
    if self.content_link:
      return self.content_link
    if self.post_type == 'post':
      base = '/posts'
    elif self.post_type == 'status':
      base = '/status'
    else:
      base = ''
    if self.stub:
      link = self.stub
    else:
      link = self.key()
    return "%s/%s" % (base, link)
  
  @property
  def get_excerpt(self):
    if self.excerpt_html:
      return self.excerpt_html
    if self.content_html:
      return self.content_html
    return ''

  @property
  def has_excerpt(self):
    if self.excerpt_html:
      return True
    if self.content_html:
      return True
    return False

  @property
  def has_thumbnail(self):
    if self.thumbnail:
      return True
    return False

  @property
  def get_thumbnail(self):
    if self.thumbnail:
      classes = "thumb"
      w, h = self.thumbnail.get_scaled(640)
      return "<img src='%s' class='%s' width='%d' height='%d'>" % (self.thumbnail.origurl, classes, w, h)
    return ''

  @property
  def has_subtitle(self):
    if self.subtitle:
      return True
    return False

  @classmethod
  def get_pages(self, num=100, cached=True):
    return self.fetch_cached("select * from Post where post_type='page'", num, cached)

  @classmethod
  def get_posts(self, num=10, cached=True):
    return self.fetch_cached("select * from Post where post_type='post' order by pubdate DESC", num, cached)

  @classmethod
  def get_statuses(self, num=25, cached=True):
    return self.fetch_cached("select * from Post where post_type='status' order by pubdate DESC", num, cached)

  @classmethod
  def get_pages_published(self, num=100, cached=True):
    return self.fetch_cached("select * from Post where post_type='page' and status='published'", num, cached)

  @classmethod
  def get_pages_menu(self, num=100, cached=True):
    return self.fetch_cached("selct * from Post where post_type='page' and status='published' and menu=True")

  @classmethod
  def get_posts_published(self, num=10, cached=True, page=1):
    return self.fetch_cached("select * from Post where post_type='post' and status='published' order by pubdate DESC", num, cached=cached, page=page)

  @classmethod
  def get_statuses_published(self, num=10, cached=True, page=1):
    return self.fetch_cached("select * from Post where post_type='status' and status='published' order by pubdate DESC", num, cached=cached, page=page)

  @classmethod
  def is_post(self, stub):
    return self.fetch_cached("select * from Post where post_type='post' and stub='%s' limit 1" % stub, 1)

  @classmethod
  def is_page(self, stub):
    return self.fetch_cached("select * from Post where post_type='page' and stub='%s' limit 1" % stub, 1)

  @classmethod
  def is_status(self, stub):
    return self.fetch_cached("select * from Post where post_type='status' and stub='%s' limit 1" % stub, 1)

  @classmethod
  def get_posts_for_month(month, year):
    if not month:
      month = datetime.datetime.now().month
    if not year:
      year = datetime.datetime.now().year
  

  @classmethod
  def stub_exists(self, stub='', cache=False):
    dat_key = "%s.%s" % ('models', stub)
    dat = memcache.get(dat_key)
    if dat is not None and not cache:
      return dat, 'memcache'
    else:    
      query = db.GqlQuery("select * from Post where stub = :1", stub)
      if query.count() == 0:
        return None, None
      rec = query.fetch(1)
      if rec[0].status == 'published':
        r = memcache.set(dat_key, rec)
        if not r:
          logging.error("Memcache: Could not set cache for %s" % dat_key)
        else:
          logging.info("Memcache: Set post key as %s" % dat_key)
      return rec, 'database'
  
  @classmethod
  def is_key(self, k):
    try:
      query = db.get(db.Key(k))
    except:
      return False
    return True
  
  @classmethod
  def is_slug(self, key):
    return self.stub_exists(key)
  
  @classmethod
  def get_single_by_key(self, key):
    return db.get(db.Key(key))

  @classmethod
  def get_single_by_stub(self, stub):
    dat_key = "%s.%s" % ('models', stub)
    dat = memcache.get(dat_key)
    if dat is not None:
      logging.info(dat)
      return dat
    else:
      query = db.GqlQuery("select * from Post where stub = :1", stub)
      r = memcache.set(dat_key, query.fetch(1))
      if not r:
        logging.error("Memcache: Could not set cache for %s" % dat_key)
      else:
        logging.info("Memcache: Set post key as %s" % dat_key)
    return query.fetch(1)

  @classmethod
  def to_dict(self):
    return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

  def publish(self):
    self.status = 'published'
    self.pubdate = datetime.datetime.now()
    self.put()

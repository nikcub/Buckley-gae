import datetime
import logging
import re
import sketch
import buckley

from sketch.exception import NotFound
from sketch.util.safestring import force_int
from google.appengine.api import memcache

class Status(buckley.BaseController):
  def get(self, stub):
    pass

class StatusIndex(buckley.BaseController):
  def get(self, key=None):
    if key:
      statuses = [buckley.models.Post.get_single_by_key(key)]
    else:
      statuses = buckley.models.Post.get_statuses(num=50, cached=False)
    return self.render('statuses', {
      'statuses': statuses,
      'tab_status': True
    })

class StatusAPI(buckley.BaseController):
  def get(self):
    pass

class Page(buckley.BaseController):
  def get(self, stub):
    page_obj = buckley.models.Post.is_page(stub)

    if not page_obj:
      raise NotFound()
    
    return self.render('page', {
      'page': page_obj
    })

class Post(buckley.BaseController):
  def get(self, stub):
    post_obj = buckley.models.Post.is_post(stub)
    
    if not post_obj:
      raise NotFound()
    
    return self.render('single', {
      'post': post_obj
    })

class Archive(buckley.BaseController):
  def get(self, page=1):
    page = force_int(page, 1)
    posts = buckley.models.Post.get_posts_published(num=5, page=page)

    return self.render('archive', {
      'posts': posts,
      'page': page
    })

class Feed(buckley.BaseController):
  template_set = 'app'
  template_theme = 'feeds'

  def get(self, format=None):
    # redirect to feedburner
    # @TODO make this a plugin
    if not format:
      self.redirect('http://feeds.feedburner.com/NewWebOrder', permanent=True)

    if not format in ['atom', 'rss', 'rss2']:
      raise NotFound()

    posts = buckley.models.Post.get_posts_published(num=self.config.feed_posts)

    if format == 'rss':
      format = 'rss2'

    return self.render_feed(format, {
      'posts': posts,
      'full': self.config.feed_posts,
      'pubdate': posts[0].pubdate,
      'now': datetime.datetime.now()
    })

class MicroblogFeed(buckley.BaseController):
  template_set = 'app'
  template_theme = 'feeds'

  def get(self):
    posts = buckley.models.Post.get_statuses_published(num=self.config.feed_statuses)

    return self.render_feed('microblog', {
      'posts': posts,
      'pubdate': posts[0].pubdate,
      'now': datetime.datetime.now()
    })

class Index(buckley.BaseController):
  def get(self):
    cache = self.request.get('cache', False)
    path = 'index'

    if not cache:
      page_cache = memcache.get('post.%s' % path)
      if page_cache:
        return self.render_content(page_cache)
            
    posts = buckley.models.Post.get_posts_published(num=self.config.frontpage_posts)
    return self.render('index', {
      'posts': posts,
      'tab_blog': True
    })

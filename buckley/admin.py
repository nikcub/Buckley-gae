import os
import sys
import logging
import sketch
import buckley
import datetime

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from buckley.models import Post

class Index(buckley.AdminController):
  def get(self, path = None):
    return self.redirect('/admin/settings')


class Settings(buckley.AdminController):
  def get(self, val=None):
    settings = self.config
    self.render('settings', {
      'settings': settings
    })
  def post(self):
    self.render_error('not yet implemented')

class Posts(buckley.AdminController):
  def get(self, action=None, key=None):
    if action == 'edit' and key:
      posts = Post.get_single_by_key(key)
      self.render('posts.edit', {
        'post': posts,
        'post_type': 'post'
      })
    else:
      posts = Post.get_all(num = 100)
      self.render('posts', {
        'posts': posts,
        'post_type': 'post'
      })

  def post(self, action = False, key = False):
    if action == 'edit' and key:
      post = Post.get_single_by_key(key)
      if not post:
        raise sketch.exception.NotFound()
      z = post.update(self.get_param_dict())
      if self.request.get('action') == 'publish':
        post.publish()
      if z:
        self.redirect(self.request.url + '?success')
      else:
        raise sketch.exception.NotFound()
    else:
      title = self.request.get('title')
      content = self.request.get('content')
      categories = [db.Category('none')]
      excerpt = content[:250]

      post = Post(
        title = title,
        excerpt = excerpt,
        content = content,
        status = "draft",
        categories = categories,
        author = users.get_current_user(),
        post_type = 'post',
        stub = self.slugify(title),
        pubdate = datetime.datetime.now()
      )
      r = post.put()
      self.redirect('/admin/posts/edit/' + str(r))

class Pages(buckley.AdminController):
  def get(self, path = None):
    return self.render('pages', {})

class Comments(buckley.AdminController):
  def get(self, path = None):
    return self.render('comments', {}) 



class Cache(buckley.AdminController):
  
  def render_cache(self, template_name, vars):
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', template_name + '.html')
    content = template.render(template_path, self.get_template_vars(vars))
    return content
    
  def get_memcache(self, posts):
    mem = []
    cache_types = ['post', 'models']
    for post in posts:
      for cache_type in cache_types:
        m = {}
        if cache_type is 'post':
          m['post'] = True
        m['key'] = str(post.key())
        m['stub'] = post.stub
        m['memkey'] = cache_type + '.' + post.stub
        dat_key = "%s.%s" % (cache_type, post.stub)
        dat = memcache.get(dat_key)
        if dat:
          m['cached'] = True
        else:
          m['cached'] = False
        mem.append(m)
    
    dat = memcache.get("models.index")
    if dat:
      m = {
        'stub': 'index',
        'memkey': 'models.index',
        'cached': True
      }
      mem.append(m)

    return mem
    
  def set_memcache(self, posts):
    m_map = {}
    p_map = {}
    
    for post in posts:
      dat_key = "%s.%s" % ('post', post.stub)
      mod_key = "%s.%s" % ('models', post.stub)
      page_vars = {'tab_blog': True, 'post': post, 'src': 'page.memcache'}
      content = self.render_cache('single', page_vars)

      p_map[dat_key] = content
      m_map[mod_key] = post
      logging.info(mod_key)
      logging.info(post)
      
    v = memcache.set_multi(m_map)
    r = memcache.set_multi(p_map)
    
    if len(v) != 0 or len(r) != 0:
      return False

    return True
    
  def get_filecache(self, posts):
    files = []
    cache_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache'))
    if not os.path.isdir(cache_dir):
      logging.error('Admin cache: not a cache dir ' + cache_dir)
      return None
    for cfile in os.listdir(cache_dir) :
      if cfile[:1] == '.':
        continue
      m = {}
      full_path = os.path.join(cache_dir, cfile)
      m['path'] = full_path
      m['name'] = cfile
      try:
        fmt = os.path.getmtime(full_path)
        m['mtts'] = fmt
        m['mt'] = datetime.datetime.fromtimestamp(fmt)
      except Exception, e:
        pass
      files.append(m)
    for post in posts:
      m = {}
    return files
    
  def set_filecache(self, posts):
    cache_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache'))
    for post in posts:
      page_vars = {'tab_blog': True, 'post': post, 'src': 'page.filecache'}
      content = self.render_cache('single', page_vars)
      fp = os.path.join(cache_dir, post.stub)
      logging.info(fp)
      f = open(fp, 'w')
      f.write(content)
      f.close()

  def get(self, val = None):
    query = db.GqlQuery("select * from Post where post_type='post' and status='published' order by pubdate DESC")
    posts = query.fetch(100)
    
    mem = self.get_memcache(posts)
    files = self.get_filecache(posts)
    memstats = memcache.get_stats()
    filestats = {}
    
    self.render('cache', {
      'memcache': mem,
      'files': files,
      'posts': posts,
      'memstats': memstats,
      'filestats': filestats,
    })
    
  def post(self):
    action = self.request.get('action', False)
    if not action:
      return self.redirect('/admin/cache?bleh')
      
    query = db.GqlQuery("select * from Post where post_type='post' and status='published' order by pubdate DESC")
    posts = query.fetch(100)
    
    if action == 'files':
      self.set_filecache(posts)
      return self.redirect('/admin/cache?rs_files')
    if action == 'mem':
      r = self.set_memcache(posts)
      return self.redirect('/admin/cache?rs_mem=' + str(r))
    return self.redirect('/admin/cache?')
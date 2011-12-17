import logging
import re
import sketch
import buckley

from sketch.exception import NotFound
from google.appengine.api import memcache

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

class Index(buckley.BaseController):
  def get(self, path=None, page=None):
    cache = self.request.get('cache', False)
    defaults = [None, '', 'index']

    if page:
      page_obj = buckley.models.Post.is_page(page)
      if page_obj:
      
        return self.render('page', {
          'page': page_obj[0]
        })
      else:
        logging.info('not a page')
      
    if path in defaults:
      posts = buckley.models.Post.get_posts_published(10, cache)
      return self.render('index', {
        'posts': posts,
        'tab_blog': True
      })

    if not cache:
      page_cache = memcache.get('post.%s' % path)
      if page_cache:
        return self.render_content(page_cache)
    
    p, src = buckley.models.Post.stub_exists(path, cache)
    if p:
      posts = buckley.models.Post.get_single_by_stub(path)
      logging.info('get_single_by_stub')
      logging.info(p[0].title)
      logging.info(src)
      return self.render('single', {
        'post': p[0],
        'tab_blog': True,
        'src': src,
      })
    elif path == "archive":
      posts, src = buckley.models.Post.get_posts_published_cached(5, cache)
      return self.render('archive', {
        'posts': posts,
        'tab_blog': True,
        'src': src,
      })
    elif Post.is_key(path):
      posts = buckley.models.Post.get_single_by_key(path)
      return self.render('single', {
        'post': posts,
        'tab_blog': True
      })

    raise NotFound()


class Posts(sketch.BaseController):
  def get(self, key=None):
    try:
      if key:
        posts = Post.get_by_key(key)
      else:
        posts = Post.get_all()
    except db.BadKeyError, e:
      return self.render_json(e, 404)
    except Exception, e:
      logging.exception(e)
      return self.render_json(e, 500)
    
    return self.render_json(posts, 200)
  
  def post(self, key=None):
    pass
  
  def put(self, key=None):
    if not key:
      raise sketch.exception.NotFound()
    
    entry = db.get(db.key(key))
    if not entry:
      raise sketch.exception.NotFound()
    
    for field, value in self.request.get_all():
      logging.info("%s => %s" % (field, value))
    
  
  def delete(self, key=None):
    pass

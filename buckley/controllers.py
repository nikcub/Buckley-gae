import logging
import re
import sketch
import buckley

from sketch.exception import NotFound
from google.appengine.api import memcache
from buckley.models import Post

class Index(buckley.BaseController):
  def get(self, path=None):
    cache = self.request.get('cache', False)
    defaults = [None, '', 'index', 'index.html', 'index.php']

    if not cache:
      page_cache = memcache.get('post.%s' % path)
      if page_cache:
        return self.render_content(page_cache)
    
    p, src = Post.stub_exists(path, cache)
    if p:
      posts = Post.get_single_by_stub(path)
      logging.info('get_single_by_stub')
      logging.info(p[0].title)
      logging.info(src)
      return self.render('single', {
        'post': p[0],
        'tab_blog': True,
        'src': src,
      })
    elif path in defaults:
      posts, src = Post.get_posts_published_cached(5, cache)
      return self.render('index', {
        'posts': posts,
        'tab_blog': True,
        'src': src,
      })
    elif Post.is_key(path):
      posts = Post.get_single_by_key(path)
      return self.render('single', {
        'post': posts,
        'tab_blog': True
      })

    raise NotFound()


class Posts(sketch.RestController):
  model = Post
  url = '/data/post'
  

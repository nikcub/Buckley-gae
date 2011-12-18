import logging
import re
import sketch

from random import choice
from google.appengine.api import users    
from buckley.models import Post
    
class BaseController(sketch.BaseController):
  template_theme = 'default'
  javascripts = {
    # @TODO this is all for the new default style
    # 'libs': {'src': ['/js/lib/all.js'], 'insert_at': 'foot'},
    # 'jquery': {'src': ['/js/lib/jquery.js'], 'insert_at': 'foot'},
    # 'bootstrap': {'src': ['/js/lib/bootstrap/bootstrap-dropdown.js'], 'insert_at': 'foot'},
    # 'sketch': {'src': ['/js/sketch/combined/sketch.js'], 'insert_at': 'foot'},
    # 'app': {'src': ['/js/app/app.js'], 'insert_at': 'foot'}
  }
  styles = ['/css/site.css?001']
  
  def get_static_resources(self):    
    host_full = self.request.environ['HTTP_HOST'] or 'localhost'
    hostname = host_full.split(':')[0]

    if self.is_dev:
      stat_hosts = [host_full]
      css_file = '/css/site.css'
    else:
      stat_hosts = ['nik-cubrilovic.appspot.com']
      css_file = '/css/site.min.css'
    
    static = {
      'host': choice(stat_hosts),
      'css_file': css_file,
      'css_ver': '26'
    }
    
    return static
      
  def get_buckley_conf(self):
    buckley = {
      'title': self.config.title,
      'description': self.config.description,
      'homepage': self.config.homepage,
      'owner': self.config.owner,
      'frontpage_posts': self.config.frontpage_posts,
      'feed_posts': self.config.feed_posts,
      'feed_full': self.config.feed_full,
      'feed_url': self.config.feed_url,
      'src': 'database'
    }
    return buckley
  
  def get_user_object(self):
    user = {
      'admin': users.is_current_user_admin(),
      'logout': users.create_logout_url('/'),
      'login': users.create_login_url('/'),
    }
    gae_user = users.get_current_user()
    if gae_user:
      user['loggedin'] = True
      user['nickname'] = gae_user.nickname()
      user['email'] = gae_user.email()
    return user

  def template_wrapper(self, variables = {}):
    pages = Post.get_pages_published()
    buckley = self.get_buckley_conf()
    user = self.get_user_object()
    static = self.get_static_resources()
    
    additional = {
      'buckley': buckley,
      'pages': pages,
      'user': user,
      'static': static
    }
    
    return dict(zip(additional.keys() + variables.keys(), additional.values() + variables.values()));


class AdminController(BaseController):
  template_set = 'app'
  template_theme = 'admin_html'
  styles_debug = ['/css/admin.css?001']
  javascripts_debug = {}
  javascripts_live = {}
  
  def pre_hook(self):
    user = users.get_current_user()
    if not user or not users.is_current_user_admin():
      raise sketch.exception.Forbidden()
  
  def styles(self):
    return self.styles_debug

  def javascripts(self):
    if self.config.debug:
      return self.javascripts_debug
    return self.javascripts_live

  def is_admin():
    return users

  def slugify(self, value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


# @TODO move to the new ajax admin
class AdminController_new(BaseController):
  template_set = 'app'
  template_theme = 'admin_js'
  javascripts_live = {
    'libs': {'src': ['/js/lib/all.js'], 'insert_at': 'foot', 'version': '001'},
    # 'jquery': {'src': ['/js/lib/jquery.js'], 'insert_at': 'foot'},
    'bootstrap': {'src': ['/js/lib/bootstrap/bootstrap-dropdown.js'], 'insert_at': 'foot'},
    'sketch': {'src': ['/js/sketch/combined/sketch.js'], 'insert_at': 'foot'},
    'app': {'src': ['/js/app/app.js'], 'insert_at': 'foot'}
  }
  javascripts_debug = {
    'libs': {'src': ['/js/lib/all.js'], 'insert_at': 'foot', 'version': '001dev'},
    # 'jquery': {'src': ['/js/lib/jquery.js'], 'insert_at': 'foot'},
    'bootstrap': {'src': ['/js/lib/bootstrap/bootstrap-dropdown.js'], 'insert_at': 'foot'},
    'sketch': {'base_dir': '/js/sketch/', 'src': ['sketch-init.js', 'sketch-shim.js', 'sketch-views.js', 'sketch-menu.js', 'sketch-message.js', 'sketch-css3.js', 'sketch-sync.js'], 'insert_at': 'foot'},
    'app': {'src': ['/js/app/app.js'], 'insert_at': 'foot'}
  }
  styles_debug = ['/css/admin.css?001']

  def initialize(self, request, response):
    self.request = request
    self.response = response
    user = users.get_current_user()
    if not user or not users.is_current_user_admin():
      raise AppAuthError
  
  def styles(self):
    return self.styles_debug

  def javascripts(self):
    logging.info(self.config.debug)
    if self.config.debug:
      return self.javascripts_debug
    return self.javascripts_live

  def is_admin():
    return users

  def slugify(self, value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

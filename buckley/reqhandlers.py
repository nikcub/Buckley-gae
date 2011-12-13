import logging
import re
from random import choice

import sketch

from google.appengine.api import users    
    
class BaseController(sketch.BaseController):
  template_folder = 'default'
  javascripts = {
    # @TODO this is all for the new default style
    # 'libs': {'src': ['/js/lib/all.js'], 'insert_at': 'foot'},
    # 'jquery': {'src': ['/js/lib/jquery.js'], 'insert_at': 'foot'},
    # 'bootstrap': {'src': ['/js/lib/bootstrap/bootstrap-dropdown.js'], 'insert_at': 'foot'},
    # 'sketch': {'src': ['/js/sketch/combined/sketch.js'], 'insert_at': 'foot'},
    # 'app': {'src': ['/js/app/app.js'], 'insert_at': 'foot'}
  }
  styles = ['/css/site.css?001']
  
  def template_wrapper(self, variables = {}):
    host_full = self.request.environ['HTTP_HOST'] or 'localhost'
    hostname = host_full.split(':')[0]
    
    if self.is_dev:
      stat_hosts = [host_full]
      css_file = 'site.css'
    else:
      stat_hosts = ['nik-cubrilovic.appspot.com']
      css_file = 'site.min.css'

    pages = [
      ('about', '/about'),
      ('consulting', '/consulting')
    ]
    
    additional = {
      'pages': pages,
      'title': self.config.title,
      'description': self.config.description,
      'admin': users.is_current_user_admin(),
      'author': self.config.author,
      'user': users.get_current_user(),
      'logout': users.create_logout_url('/'),
      'login': users.create_login_url('/'),
      'static_host': choice(stat_hosts),
      'css_file': css_file,
      'css_ver': '26',
      'src': 'database',
      # 'config': {test: 'test'},
      # 'title': self.conf_get('title')
    }
    return dict(zip(additional.keys() + variables.keys(), additional.values() + variables.values()));


class AdminController(BaseController):
  template_folder = 'admin_old'
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
  template_folder = 'admin'
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

import logging
import re
from random import choice

import sketch

from google.appengine.api import users    
    
class BaseController(sketch.BaseController):
  template_folder = 'nwo'
  javascripts = {
    'libs': {'src': ['/js/lib/all.js'], 'insert_at': 'foot'},
    'jquery': {'src': ['/js/lib/jquery.js'], 'insert_at': 'foot'},
    'bootstrap': {'src': ['/js/lib/bootstrap/bootstrap-dropdown.js'], 'insert_at': 'foot'},
    'sketch': {'src': ['/js/sketch/combined/sketch.js'], 'insert_at': 'foot'},
    'app': {'src': ['/js/app/app.js'], 'insert_at': 'foot'}
  }
  styles = ['']
  
  def template_wrapper(self, variables = None):

    host_full = self.request.environ['HTTP_HOST'] or 'localhost'
    hostname = host_full.split(':')[0]
    
    buckley = {}
    buckley['title'] = 'Test Template'
    
    if self.is_dev:
      stat_hosts = [host_full]
      css_file = 'style.css'
    else:
      stat_hosts = ['nik-cubrilovic.appspot.com', 'sketch-proto.appspot.com', 'hterms.appspot.com']
      css_file = 'style.min.css'

    additional = {
      'admin': users.is_current_user_admin(),
      'user': users.get_current_user(),
      'logout': users.create_logout_url('/'),
      'login': users.create_login_url('/'),
      'static_host': choice(stat_hosts),
      'css_file': css_file,
      'css_ver': '26',
      'src': 'database',
      'buckley': buckley,
      # 'config': {test: 'test'},
      # 'title': self.conf_get('title')
    }
    return dict(zip(additional.keys() + variables.keys(), additional.values() + variables.values()));


class AdminController(BaseController):
  template_folder = 'admin'

  def initialize(self, request, response):
    self.request = request
    self.response = response
    user = users.get_current_user()
    if not user or not users.is_current_user_admin():
      raise AppAuthError
      
  def is_admin():
    return users

  def slugify(self, value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

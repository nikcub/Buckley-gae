# default sketch config

# as tempting as it may be, I totally wouldn't touch this file 

title = 'Example Buckley Blog'
description = 'A description or subheading'
author = 'author'
frontpage_posts = 10
feed_posts = 10
feed_full = True
feed_statuses = 50
feed_url = '/feed'
template = 'default'
plugins = {}
debug = False
default_charset = 'utf-8'
default_language = 'en-us'
append_slash = False
appname = 'buckley'
prepend_www = False
user_agent = "Mozilla/5.0 (compatible; SketchBot/0.1; +http://nikcub.appspot.com/projects/sketch)"
session_name = 'sess'
server_email = {
  'address': 'root@localhost',
  'host': 'localhost',
  'port': 25,
  'secure': False,
  'username': None,
  'password': None
}
template_sets = {
  'app': '$app_dir/templates',
  'site': '$site_dir/templates',
  'sketch': '$sketch_dir/templates',
}
default_template_set = 'site'
default_template_theme = 'default'
enviroments = {
  'live': {
    'debug': False,
    'hosts': ['buckleyapp.appspot.com', '*.appspot.com']
  },
  'staging': {
    'debug': True,
    'hosts': ['*.*.appspot.com']
  },
  'dev': {
    'debug': True,
    'hosts': ['localhost', '*.dyndns.org']
  }
}
auth_providers = {}
from sketch import Route as r

routes = [
  r(r'/_<action>', 'sketch.debug_handler', 'sketch-admin'),

  r(r'/data/post/<key>', 'buckley.controllers.Posts'),
  r(r'/data/post', 'buckley.controllers.Posts'),
  
  r(r'/admin/comments', 'buckley.admin.Comments'),
  r(r'/admin/cache', 'buckley.admin.Cache'),
  r(r'/admin/pages', 'buckley.admin.Pages'),
  r(r'/admin/pages/<action>/<key>', 'buckley.admin.Pages'),
  r(r'/admin/posts', 'buckley.admin.Posts'),
  r(r'/admin/posts/<action>/<key>', 'buckley.admin.Posts'),
  r(r'/admin/settings', 'buckley.admin.Settings'),
  r(r'/admin', 'buckley.admin.Index', 'webwall-admin'),
  
  # TODO add regexp here for stubs (matching word-word-word or word)
  r(r'/<path>', 'buckley.controllers.Index'),
  r(r'/<slug:[\w-]+>', 'buckley.controllers.Index', 'slug'),
  r(r'/', 'buckley.controllers.Index', 'webwall-index'),
]


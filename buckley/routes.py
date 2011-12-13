from sketch import Route as r

routes = [  
  # admin area
  r(r'/admin/comments', 'buckley.admin.Comments'),
  r(r'/admin/cache_page/(.*)', 'buckley.admin.CacheView'),
  r(r'/admin/cache', 'buckley.admin.Cache'),
  r(r'/admin/pages', 'buckley.admin.Pages'),
  r(r'/admin/pages/<action>', 'buckley.admin.Pages'),
  r(r'/admin/pages/<action>/<key>', 'buckley.admin.Pages'),
  r(r'/admin/posts', 'buckley.admin.Posts'),
  r(r'/admin/posts/<action>', 'buckley.admin.Posts'),
  r(r'/admin/posts/<action>/<key>', 'buckley.admin.Posts'),
  r(r'/admin/settings', 'buckley.admin.Settings'),
  r(r'/admin<path:.*>', 'buckley.admin.Index', 'webwall-admin'),
  
  # main blog
  r(r'/feed(.*)', 'buckley.feed.Main'),
  r(r'/posts/<path>', 'buckley.controllers.Index', 'webwall-index'),
  r(r'/<page>', 'buckley.controllers.Index'),
  r(r'/', 'buckley.controllers.Index', 'webwall-index'),
]
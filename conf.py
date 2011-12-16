
# This is a default configuration file
# customize to your own liking

title = 'Example Buckley Blog'
description = 'A description or subheading'
frontpage_posts = 10
owner = 'nik cubrilovic'
template = 'default'
permalinks = {
  'posts': '/posts/%s',
  'images': '/posts/%s',
}
template_themes = {
  'site': 'default',
  'admin': 'admin_html'
}
plugins = {
  'most_recent': {
    'display_last': 10
  },
  'disqus': {
    'site_id': ''
  },
  'google_analytics': {}
}

pages = {

}
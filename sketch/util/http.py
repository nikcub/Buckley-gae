#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#
"""
  Sketch - TM_FILENAME}

  desc

"""

import webob
import urlparse
import base64

def extract_dataurl(dataurl):
  if not dataurl[:5] == 'data:':
    return (None, None)
  img_index = dataurl.index(',')
  if not img_index:
    return (None, None)

  img_type = dataurl[5:img_index].split(';')[0]
  img_dat_enc = dataurl[img_index + 1:]

  img_dat = base64.decodestring(img_dat_enc)
  return (img_dat, img_type)


def pack_dataurl(file_name=None, file_dat=None):
  if file_name:
    file_dat = open(file_name).read()

  if file_dat and not type(file_dat) == type(''):
    return False

  if file_dat[:4] == '\x89PNG':
    file_type = 'png'
  elif file_dat[:10] == '\xff\xd8\xff\xe0\x00\x10JFIF':
    file_type = 'jpeg'
  elif file_dat[:3] == 'GIF':
    file_type = 'gif'
  else:
    return False

  img_dat_enc = base64.urlsafe_b64encode(file_dat).replace('\n', '')
  img_dat_packed = "data:image/%s;base64,{0}".format(file_type, img_dat_enc)

  return img_dat_packed


def urlunsplit(scheme=None, netloc=None, path=None, query=None, fragment=None):
  """Similar to ``urlparse.urlunsplit``, but will escape values and
  urlencode and sort query arguments.

  :param scheme:
    URL scheme, e.g., `http` or `https`.
  :param netloc:
    Network location, e.g., `localhost:8080` or `www.google.com`.
  :param path:
    URL path.
  :param query:
    URL query as an escaped string, or a dictionary or list of key-values
    tuples to build a query.
  :param fragment:
    Fragment identifier, also known as "anchor".
  :returns:
    An assembled absolute or relative URL.
  """
  if not scheme or not netloc:
    scheme = None
    netloc = None

  if path:
    path = urllib.quote(to_utf8(path))

  if query and not isinstance(query, basestring):
    if isinstance(query, dict):
      query = query.items()

    query_args = []
    for key, values in query:
      if isinstance(values, basestring):
        values = (values,)

      for value in values:
        query_args.append((to_utf8(key), to_utf8(value)))

    # Sorting should be optional? Sorted args are commonly needed to build
    # URL signatures for services.
    query_args.sort()
    query = urllib.urlencode(query_args)

  if fragment:
    fragment = urllib.quote(to_utf8(fragment))

  return urlparse.urlunsplit((scheme, netloc, path, query, fragment))
    


def test_normalize_url():
  urls = [
  # 'example.com',
  # 'example.com/',
  # 'http://example.com/',
  # 'http://example.com',
  # 'http://example.com?',
  # 'http://example.com/?',
  # 'http://example.com//',
  # 'http://example.com/a',
  # 'http://example.com/a/',
  # 'http://example.com/a/?',
  # 'http://example.com/a/../',
  # 'http://example.com/a/../?',
  # 'http://example.com/a/b/../?',
  # 'http://example.com/a/../',
  # 'http://example.com/a/b/?z=1',
  'http://example.com/a/?',
  'http://@example.com/a/?',
  'http://example.com:/a/?',
  'http://@example.com:/a/?',
  'http://example.com:80/a/?',
  ]

  for url in urls:
    print "%s \t\t\t\t\t\tclean: %s" % (url, normalize_url(url))


def normalize_url(s, charset='utf-8'):
  """
  function that attempts to mimic browser URL normalization.

  Partly taken from werkzeug.utils

  <http://www.bitbucket.org/mitsuhiko/werkzeug-main/src/tip/werkzeug/utils.py>

  There is a lot to URL normalization, see:

  <http://en.wikipedia.org/wiki/URL_normalization>

  :param charset: The target charset for the URL if the url was
               given as unicode string.
  """
  if isinstance(s, unicode):
   s = s.encode(charset, 'ignore')
  scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
  # print "scheme: %s\n netloc:%s\n path:%s\n qs:%s\n anchor:%s\n" % (scheme, netloc, path, qs, anchor)
  path = urllib.unquote(path)
  if not netloc:
    netloc = path.strip("/\\:?&")
    path = '/'
  if not scheme:
    scheme = "http"
  if not path:
    path = '/'
  netloc = netloc.strip("/\\:@?&")
  path = posixpath.normpath(path)
  path = urlparse.urljoin('/', path)
  # path = urllib.quote(path, '/%')
  qs = urllib.quote_plus(qs, ':&=')
  # print "scheme: %s\n netloc:%s\n path:%s\n qs:%s\n anchor:%s\n" % (scheme, netloc, path, qs, anchor)
  return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


def redirect(location, code = 302):
  assert code in (301, 302, 303, 305, 307), 'invalid code'
  from sketch import Response
  display_location = location
  response = Response(
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
    '<title>Redirecting...</title>\n'
    '<h1>Redirecting...</h1>\n'
    '<p>You should be redirected automatically to target URL: '
    '<a href="%s">%s</a>.    If not click the link.' %
    (location, display_location), code, mimetype='text/html')
  response.headers['Location'] = location
  return response


def abort_old(code, *args, **kwargs):
  """Raises an ``HTTPException``. The exception is instantiated passing
  *args* and *kwargs*.

  :param code:
      A valid HTTP error code from ``webob.exc.status_map``, a dictionary
      mapping status codes to subclasses of ``HTTPException``.
  :param args:
      Arguments to be used to instantiate the exception.
  :param kwargs:
      Keyword arguments to be used to instantiate the exception.
  """
  cls = webob.exc.status_map.get(code)
  if not cls:
    raise KeyError('No exception is defined for code %r.' % code)

  raise cls(*args, **kwargs)


def get_valid_methods(handler):
  """Returns a list of HTTP methods supported by a handler.

  :param handler:
    A :class:`RequestHandler` instance.
  :returns:
    A list of HTTP methods supported by the handler.
  """
  return [method for method in Application.ALLOWED_METHODS if getattr(handler,
    method.lower().replace('-', '_'), None)]

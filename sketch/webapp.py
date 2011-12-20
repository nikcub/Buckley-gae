#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2010-2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#

# webapp2
# =======
# 
# Taking Google App Engine's webapp to the next level!
# 
# :copyright: 2010 by tipfy.org.
# :license: Apache Sotware License, see LICENSE for details.

#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
  Sketch - webapp.py

  Webapp implementation taken from parts of Google Appengine webapp framework,
  webapp2 and additional methods and code.
  
  This source file is subject to the new BSD license that is bundled with this 
  package in the file LICENSE.txt. The license is also available online at the 
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.0.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'

import cgi
import webob
import re
import sketch
import urlparse
import time
import logging
from Cookie import BaseCookie

from sketch.util import force_unicode

RE_FIND_GROUPS = re.compile('\(.*?\)')
_CHARSET_RE = re.compile(r';\s*charset=([^;\s]*)', re.I)

class Request(webob.Request):
  """Abstraction for an HTTP request.

  Properties:
    uri: the complete URI requested by the user
    scheme: 'http' or 'https'
    host: the host, including the port
    path: the path up to the ';' or '?' in the URL
    parameters: the part of the URL between the ';' and the '?', if any
    query: the part of the URL after the '?'

  You can access parsed query and POST values with the get() method; do not
  parse the query string yourself.
  """


  # TODO implement the content types
  CONTENT_TYPES = ['html', 'json', 'xml']

  uri = property(lambda self: self.url)
  
  query = property(lambda self: self.query_string)


  def __init__(self, environ):
    """Constructs a Request object from a WSGI environment.

    If the charset isn't specified in the Content-Type header, defaults
    to UTF-8.

    Args:
      environ: A WSGI-compliant environment dictionary.
    """
    
    match = _CHARSET_RE.search(environ.get('CONTENT_TYPE', ''))
    if match:
      charset = match.group(1).lower()
    else:
      charset = 'utf-8'

    webob.Request.__init__(self, environ, charset=charset,
                           unicode_errors= 'ignore', decode_param_names=True)

    # A registry for objects used during the request lifetime.
    self.registry = {}
    # A dictionary for variables used in rendering.
    self.context = {}


  def get(self, argument_name, default_value='', allow_multiple=False):
    """Returns the query or POST argument with the given name.

    We parse the query string and POST payload lazily, so this will be a
    slower operation on the first call.

    Args:
      argument_name: the name of the query or POST argument
      default_value: the value to return if the given argument is not present
      allow_multiple: return a list of values with the given name (deprecated)

    Returns:
      If allow_multiple is False (which it is by default), we return the first
      value with the given name given in the request. If it is True, we always
      return a list.
    """
    param_value = self.get_all(argument_name)
    if allow_multiple:
      logging.warning('allow_multiple is a deprecated param, please use the '
                      'Request.get_all() method instead.')
    if len(param_value) > 0:
      if allow_multiple:
        return param_value
      return param_value[0]
    else:
      if allow_multiple and not default_value:
        return []
      return default_value


  def get_all(self, argument_name, default_value=None):
    """Returns a list of query or POST arguments with the given name.

    We parse the query string and POST payload lazily, so this will be a
    slower operation on the first call.

    Args:
      argument_name: the name of the query or POST argument
      default_value: the value to return if the given argument is not present,
        None may not be used as a default, if it is then an empty list will be
        returned instead.

    Returns:
      A (possibly empty) list of values.
    """
    if self.charset:
      argument_name = argument_name.encode(self.charset)

    if default_value is None:
      default_value = []

    param_value = self.params.getall(argument_name)

    if param_value is None or len(param_value) == 0:
      return default_value

    for i in xrange(len(param_value)):
      if isinstance(param_value[i], cgi.FieldStorage):
        param_value[i] = param_value[i].value

    return param_value


  def arguments(self):
    """Returns a list of the arguments provided in the query and/or POST.

    The return value is a list of strings.
    """
    return list(set(self.params.keys()))

  def get_checkbox(self, arg, default = 'off'):
    """Used to get the value from a checkbox. Instead of returning
    'on' or 'off' will return True or False. Note that it will return
    false if value isn't present or if value is unchecked.
    """
    val = self.get(arg, default)
    if val.lower() == 'on':
        return True
    return False

  def get_json(self, arg = None, default = None):
    from django.utils import simplejson
    
    if not self.body:
      return default
    
    try:  
      d = simplejson.loads(self.body)
    except simplejson.decoder.JSONDecodeError:
      raise Exception("Bad json body: %s" % self.body)
    except Exception, e:
      raise e
    
    if type(d) == type([]):
      return d
      
    if type(d) == type({}) and arg:
      if arg in d:
        return d[arg]
      else:
        return default
    
    return d
 
  def is_ajax(self):
    is_ajax = False
    if 'json' in self.str_params:
      return True
    if self.url.endswith('.json'):
      return True
    if self.headers.has_key('X-Ajax'):
      return True
    if self.is_xhr:
      return True
    if self.headers.has_key('X-Requested-With'):
      if self.headers['X-Requested-With'] == 'XMLHttpRequest':
        return True
    return False

  # TODO reimplement
  # proper accept order and proper sketch support processing (eg. json, xml, html)
  #  u = [i.split(';') for i in t]
  # ['text/html', 'application/xhtml+xml', 'application/xml;q=0.9', '*/*;q=0.8']
  def response_type(self):
    if 'json' in self.str_params:
      return 'json'

    if 'xml' in self.str_params:
      return 'xml'

    if not self.headers.has_key('accept'):
      return 'html'

    accept = self.headers['accept'].split(',')
    # logging.info(self.str_params)
    if 'application/json' in accept or 'text/javascript' in accept:
      return 'json'

    if 'application/xml' in accept or 'text/xml' in accept:
      return 'xml'

    return 'html'

  def get_dtime(self, arg, dfm = "%Y-%m-%d", default = None):
    val = self.get(arg, False)
    if not val:
        return datetime.datetime.now()

    try:
        dt_obj = datetime.datetime.strptime(self.request.get("pubdate"), dfm)
        return dt_obj
    except Exception:
        return False


class Response(webob.Response):
    """Abstraction for an HTTP response.

    Implements all of ``webapp.Response`` interface, except ``wsgi_write()``
    as the response itself is returned by the WSGI application.
    """

    def write(self, text):
        """Appends a text to the response body."""
        # webapp uses StringIO as Response.out, so we need to convert anything
        # that is not str or unicode to string to keep same behavior.
        if not isinstance(text, basestring):
            text = unicode(text)

        if isinstance(text, unicode) and not self.charset:
            self.charset = self.default_charset

        super(Response, self).write(text)

    def set_status(self, code, message=None):
        """Sets the HTTP status code of this response.

        :param message:
            The HTTP status string to use
        :param message:
            A status string. If none is given, uses the default from the
            HTTP/1.1 specification.
        """
        if message:
            self.status = '%d %s' % (code, message)
        else:
            self.status = code

    def clear(self):
        """Clears all data written to the output stream so that it is empty."""
        self.body = ''

    def set_cookie(self, key, value='', max_age=None,
                    permanent = False, clear = False,
                   path='/', domain=None, secure=None, httponly=False,
                   version=None, comment=None):
        """
        Set (add) a cookie for the response
        
        eg. 
        PREF=zzzzzzzzz; expires=Thu, 20-Jun-2013 11:28:59 GMT; path=/; domain=.google.com
        sess=zzzzzzzzz; expires=Fri, 1-Jan-2038 00:00:00 GMT; Max-Age=157680000; Path=/
        """
        cookies = BaseCookie()
        cookies[key] = value
        
        if max_age:
          exp = sketch.util.HTTPDate(time.time() + max_age)
        if permanent:
          max_age = 60 * 60 * 24 * 365 * 5
          exp = sketch.util.HTTPDate(time.time() + max_age)
        elif clear:
          max_age = 0
          exp = sketch.util.HTTPDate(time.time() - 60 * 60 * 24 * 365 * 5)
          
        for var_name, var_value in [
            ('expires', exp),
            # ('max_age', max_age),
            ('path', path),
            ('domain', domain),
            ('secure', secure),
            ('HttpOnly', httponly),
            ('version', version),
            ('comment', comment),
            ]:
            if var_value is not None and var_value is not False:
                cookies[key][var_name.replace('_', '-')] = str(var_value)
        header_value = cookies[key].output(header='').lstrip()
        logging.info("Set-Cookie: %s" % header_value)
        self.headerlist.append(('Set-Cookie', header_value))

    def delete_cookie(self, key, path='/', domain=None):
        """
        Delete a cookie from the client.  Note that path and domain must match
        how the cookie was originally set.

        This sets the cookie to the empty string, and max_age=0 so
        that it should expire immediately.
        """
        self.set_cookie(key, '', path=path, domain=domain,
                        max_age=0, clear=True)

    @staticmethod
    def http_status_message(code):
        """Returns the default HTTP status message for the given code.

        :param code:
            The HTTP code for which we want a message.
        """
        message = webob.statusreasons.status_reasons.get(code)
        if not message:
            raise KeyError('Invalid HTTP status code: %d' % code)

        return message


class RequestHandler(object):
  """Base HTTP request handler. Clients should subclass this class.

  Subclasses should override get(), post(), head(), options(), etc to handle
  different HTTP methods.

  Implements most of ``webapp.RequestHandler`` interface.
  """

  def __init__(self, app=None, request=None, response=None):
    """Initializes this request handler with the given WSGI application,
    Request and Response.

    .. note::
       Parameters are optional only to support webapp's constructor which
       doesn't take any arguments. Consider them as required.

    :param app:
        A :class:`WSGIApplication` instance.
    :param request:
        A ``webapp.Request`` instance.
    :param response:
        A :class:`Response` instance.
    """
    self.app = app
    self.request = request
    self.response = response
    self.__uploads = None


  @property
  def is_ajax(self):
    return self.request.is_ajax()


  def redirect(self, uri, permanent=False, abort=False, code=302):
    """Issues an HTTP redirect to the given relative URL. This won't stop
    code execution unless **abort** is True. A common practice is to
    return when calling the function::

        return self.redirect('/some-path')

    :param uri:
        A relative or absolute URI (e.g., '../flowers.html').
    :param permanent:
        If True, uses a 301 redirect instead of a 302 redirect.
    :param abort:
        If True, raises an exception to perform the redirect.

    .. seealso:: :meth:`redirect_to`.
    """
    absolute_url = str(urlparse.urljoin(self.request.uri, uri))
    if permanent:
        code = 301

    if abort:
        self.abort(code, headers=[('Location', absolute_url)])

    self.response.headers['Location'] = absolute_url
    self.response.set_status(code)
    self.response.clear()


  def redirect_to(self, _name, _permanent=False, _abort=False, *args, **kwargs):
    """Convenience method mixing :meth:`redirect` and :meth:`url_for`:
    Issues an HTTP redirect to a named URL built using :meth:`url_for`.

    :param _name:
        The route name to redirect to.
    :param _permanent:
        If True, uses a 301 redirect instead of a 302 redirect.
    :param _abort:
        If True, raises an exception to perform the redirect.
    :param args:
        Positional arguments to build the URL.
    :param kwargs:
        Keyword arguments to build the URL.

    .. seealso:: :meth:`redirect` and :meth:`url_for`.
    """
    url = self.url_for(_name, *args, **kwargs)
    self.redirect(url, permanent=_permanent, abort=_abort)


  def redirect_back(self, msg=None):
    """Conveniance method for redirecting back to the referring page
    
    @TODO use 307 on redirect?
    @TODO do not trust the referrer - use session info
    """
    re = self.request.environ.get('HTTP_REFERER', '/')
    self.redirect(re + '?' + msg, code = 303, permanent=False)


  def url_for(self, _name, *args, **kwargs):
    """Builds and returns a URL for a named :class:`Route`.

    For example, if you have these routes defined for the application::

        app = WSGIApplication([
            Route(r'/', 'handlers.HomeHandler', 'home'),
            Route(r'/wiki', WikiHandler, 'wiki'),
            Route(r'/wiki/<page>', WikiHandler, 'wiki-page'),
        ])

    Here are some examples of how to generate URLs inside a handler::

        # /
        url = self.url_for('home')
        # http://localhost:8080/
        url = self.url_for('home', _full=True)
        # /wiki
        url = self.url_for('wiki')
        # http://localhost:8080/wiki
        url = self.url_for('wiki', _full=True)
        # http://localhost:8080/wiki#my-heading
        url = self.url_for('wiki', _full=True, _anchor='my-heading')
        # /wiki/my-first-page
        url = self.url_for('wiki-page', page='my-first-page')
        # /wiki/my-first-page?format=atom
        url = self.url_for('wiki-page', page='my-first-page', format='atom')

    :param _name:
        The route name.
    :param args:
        Positional arguments to build the URL. All positional variables
        defined in the route must be passed and must conform to the
        format set in the route. Extra arguments are ignored.
    :param kwargs:
        Keyword arguments to build the URL. All variables not set in the
        route default values must be passed and must conform to the format
        set in the route. Extra keywords are appended as URL arguments.

        A few keywords have special meaning:

        - **_full**: If True, builds an absolute URL.
        - **_scheme**: URL scheme, e.g., `http` or `https`. If defined,
          an absolute URL is always returned.
        - **_netloc**: Network location, e.g., `www.google.com`. If
          defined, an absolute URL is always returned.
        - **_anchor**: If set, appends an anchor to generated URL.
    :returns:
        An absolute or relative URL.

    .. note::
       This method, like :meth:`WSGIApplication.url_for`, needs the request
       attribute to be set to build absolute URLs. This is because some
       routes may need to retrieve information from the request to set the
       URL host. We pass the request object explicitly instead of relying
       on ``os.environ`` mainly for better testability, but it also helps
       middleware.

    .. seealso:: :meth:`Router.build`.
    """
    return self.app.router.build(_name, self.request, args, kwargs)


  def get_config(self, module, key=None, default=object()):
    """Returns a configuration value for a module.

    .. seealso:: :meth:`Config.get_config`.
    """
    return self.app.config.get_config(module, key=key, default=default)


  def handle_exception(self, exception, debug_mode):
    """Called if this handler throws an exception during execution.

    The default behavior is to re-raise the exception to be handled by
    :meth:`WSGIApplication.handle_exception`.

    :param exception:
        The exception that was thrown.
    :param debug_mode:
        True if the web application is running in debug mode.
    """
    raise


  def get_uploads(self, field_name=None):
    """
      blobstore
    """
    if self.__uploads is None:
      self.__uploads = {}
      for key, value in self.request.params.items():
        if isinstance(value, cgi.FieldStorage):
          if 'blob-key' in value.type_options:
            self.__uploads.setdefault(key, []).append(blobstore.parse_blob_info(value))

    if field_name:
      try:
        return list(self.__uploads[field_name])
      except KeyError:
        return []
    else:
      results = []
      for uploads in self.__uploads.itervalues():
        results += uploads
      return results


class RedirectHandler(RequestHandler):
  """Redirects to the given URL for all GET requests. This is meant to be
  used when defining URL routes. You must provide at least the keyword
  argument *url* in the route default values. Example::

    def get_redirect_url(handler, *args, **kwargs):
        return handler.url_for('new-route-name')

    app = WSGIApplication([
        Route(r'/old-url', RedirectHandler, defaults={'url': '/new-url'}),
        Route(r'/other-old-url', RedirectHandler, defaults={'url': get_redirect_url}),
    ])

  Based on idea from `Tornado`_.
  """
  def get(self, *args, **kwargs):
    """Performs the redirect. Two keyword arguments can be passed through
    the URL route:

    - **url**: A URL string or a callable that returns a URL. The callable
      is called passing ``(handler, *args, **kwargs)`` as arguments.
    - **permanent**: If False, uses a 301 redirect instead of a 302
      redirect Default is True.
    """
    url = kwargs.pop('url', '/')
    permanent = kwargs.pop('permanent', True)

    if callable(url):
      url = url(self, *args, **kwargs)

    self.redirect(url, permanent=permanent)


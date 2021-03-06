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
"""
  Sketch - embedly.py

  simple embedly client lib

  This source file is subject to the new BSD license that is bundled with this 
  package in the file LICENSE.txt. The license is also available online at the 
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.0.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'

import os
import sys
import logging
import urlparse
import urllib
from google.appengine.api import urlfetch

try:
  import json
  json_parse = lambda s: json.loads(s)
  json_dump = lambda s: json.dumps(s)
except ImportError:
  try:
    import simplejson
    json_parse = lambda s: simplejson.loads(s)
    json_dump = lambda s: simplejson.dumps(s)
  except ImportError:
    try:
      # For Google AppEngine
      from django.utils import simplejson
      json_parse = lambda s: simplejson.loads(s)
      json_dump = lambda s: simplejson.dumps(s)
    except ImportError:
      logging.exception('no json parser')
      _JSON = False


class Embedly(object):
  _req_headers = {
    "User-Agent": "py-diffbot v0.0.1 <+http://bitbucket.org/nik/py-diffbot>",
    "Connection": 'close'
  }
  _req_attempts = 3
  oembed_endpoint = "http://api.embed.ly/1/oembed"
  objectify_endpoint = "http://api.embed.ly/1/preview"
  req_params = {
    'url': None,
    'key': None,
    'maxwidth': 500
  }  

  def __init__(self, dev_token=None):
    if not dev_token:
      dev_token = os.environ.get('EMBEDLY_TOKEN', False)

    if not dev_token:
      raise Exception("embedly: Please provide a dev token")

    self.dev_token = dev_token

  def get_embed(self, url, type="oembed", maxwidth=None):
    api_args = self.get_req_args(url, maxwidth=maxwidth)
    url = self.oembed_endpoint + '?' + api_args

    response = self.fetch(url)

    if response:
      try:
        de = json_parse(response)
      except Exception, e:
        logging.exception(e)
        return False
      return de
    return False

  def get_objectify(self, url):
    api_args = self.get_req_args(url)
    url = self.objectify_endpoint + '?' + api_args
    response = self.fetch(url)
    if response:
      try:
        de = json_parse(response)
      except Exception, e:
        logging.exception(e)
        return False
      return de
    return False
    
  def get_req_args(self, url, maxwidth=None, format='json'):
    """Build request arguments for query string in API request. Defaults are
    to request JSON output format."""
    # TODO some of these are not implemented. can we order the dict?
    api_arguments = {
      "key": self.dev_token,
      "url": url,
      "maxwidth": 500
      # "tags": '1'
    }
    if format != 'json':
      api_arguments['format'] = format
    if maxwidth:
      api_arguments['maxwidth'] = maxwidth

    return urllib.urlencode(api_arguments)

  def fetch(self, url):
    attempt = 1
    result = None
    self._req_headers['Connection'] = 'Close'

    while attempt <= self._req_attempts:
      try:
        result = urlfetch.fetch(
          url,
          method = urlfetch.GET,
          headers = self._req_headers,
          deadline = 20
        )
      except urlfetch.DownloadError, e:
        logging.info("embedly: (Download Attempt [%d/%d]) DownloadError: Download timed out"
          % (attempt, self._req_attempts))
        attempt += 1
      except Exception, e:
        logging.exception("embedly: Exception: %s" % e.message)
        logging.exception("embedly: Exceeded number of attempts allowed")
        return False

      if result and result.status_code == 200:
          return result.content.decode('UTF-8')
    return False
  
def get_embed(self, url):
  pass
  

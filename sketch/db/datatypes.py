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
  Sketch - datatypes.py

  Custom database data types for Google App Engine (and eventually for other
  databases as well)

"""

import re

from google.appengine.ext import db
from google.appengine.api import datastore_types
from sketch.vendor import markdown
from sketch.util import utc_mktime, datetime_to_timestamp

Text = datastore_types.Text

class UTCTimestampProperty(db.IntegerProperty):
  """Stores datetime as a UTC timestamp so that it is consistant across the 
  entire application and is only formatted in templates and presented with
  user timezone options.
  
  """
  def __init__(self, verbose_name=None, auto_now=False, auto_now_add=False, **kwds):
    super(db.IntegerProperty, self).__init__(verbose_name, **kwds)
    self.auto_now = auto_now
    self.auto_now_add = auto_now_add

  def validate(self, value):
    pass

class HtmlFromMarkdownProperty(db.TextProperty):
    def __init__(self, source=None, **kwargs):
        if not isinstance(source, db.TextProperty):
            raise TypeError('Source must be a TextProperty.')
        self.source = source
        super(HtmlFromMarkdownProperty, self).__init__(**kwargs)

    def get_value_for_datastore(self, model_instance):
        value = self.source.get_value_for_datastore(model_instance)
        if value is not None:
            html = value
            return Text(html)

class StubFromTitleProperty(db.StringProperty):
	def __init__(self, source=None, **kwargs):
		if not isinstance(source, db.StringProperty):
			raise TypeError('Source must be a StringProperty.')
		self.source = source
		super(StubFromTitleProperty, self).__init__(**kwargs)

	def slugify(self, value):
		value = re.sub('[^\w\s-]', '', value).strip().lower()
		return re.sub('[-\s]+', '-', value)
		
	def get_value_for_datastore(self, model_instance):
		value = self.source.get_value_for_datastore(model_instance)
		if value is not None:
			stub = self.slugify(value)
			return Text(stub)

	def get_stub(self, title, inc = 1):
		stub_exists = Post.stub_exists(self.slugify(title))
		if stub_exists == False:
			return self.slugify(title)
		else:
			inc = inc + 1
			if inc > 2:
				return self.get_stub("%s-%d" % (self.slugify(title[:-2]), inc), inc)
			else:
				return self.get_stub("%s-%d" % (self.slugify(title), inc), inc)

import datetime
import time
import logging

import sketch

from google.appengine.api import users
from google.appengine.ext import db

#this is a mod on the orinal file for some reason it includes its own simplejson files i have ref django!
from django.utils import simplejson
from sketch.helpers.dateformat import utc_timestamp, timestamp

class GqlEncoder(simplejson.JSONEncoder):
  """Extends JSONEncoder to add support for GQL results and properties.

  Adds support to simplejson JSONEncoders for GQL results and properties by
  overriding JSONEncoder's default method.
  """
  # TODO Improve coverage for all of App Engine's Property types.
  def default(self, obj):
    """Tests the input object, obj, to encode as JSON."""
    
    # if hasattr(obj, '__json__'):
      # return getattr(obj, '__json__')()

    if isinstance(obj, db.GqlQuery):
      return list(obj)

    elif isinstance(obj, Exception):
      output = {}
      output['error'] = "%s: %s" % (obj.__class__.__name__, obj.message)
      output['displayError'] = "%s" % (obj.__class__.__name__)
      return output
    
    elif isinstance(obj, sketch.Session):
      output = {}
      for m in obj:
        output[m] = obj[m]
      return output

    elif isinstance(obj, sketch.User):
      output = {}
      methods = ['id', 'username', 'name', 'email', 'picture', 'tw_username', 'fb_username', 'updated', 'created']
      for method in methods:
        output[method] = getattr(obj, method)
      return output

    elif isinstance(obj, db.Model):
      output = {}
      properties = obj.properties().items()
      if hasattr(obj, "id"):
        output['id'] = getattr(obj, "id")
      else:
        output['id'] = str(obj.key())
        # output['id'] = getattr(obj, 'id')
      if hasattr(obj, 'url'):
        output['url'] = str(obj.url)
      for field, value in properties:
        output[field] = getattr(obj, field)
      return output

    elif isinstance(obj, datetime.datetime):
      return utc_timestamp(obj)

      # return int(time.mktime(datetime.datetime.now().timetuple()))
      output = {}
      fields = ['day', 'hour', 'microsecond', 'minute', 'month', 'second',
          'year']
      methods = ['ctime', 'isocalendar', 'isoformat', 'isoweekday',
          'timetuple']
      for field in fields:
        output[field] = getattr(obj, field)
      for method in methods:
        output[method] = getattr(obj, method)()
      output['epoch'] = time.mktime(obj.timetuple())
      return output

    elif isinstance(obj, time.struct_time):
      return list(obj)

    elif isinstance(obj, users.User):
      output = {}
      methods = ['nickname', 'email', 'auth_domain']
      for method in methods:
        output[method] = getattr(obj, method)()
      return output
    
    elif isinstance(obj, db.Key):
      return str(obj)

    elif obj == type(True):
      return True
      
    elif obj == type(False):
      return obj

    return simplejson.JSONEncoder.default(self, obj)

class AtomEncoder(object):
    def encode(self, obj):
        return obj

def json(input, pretty = False):
    """Encode an input GQL object as JSON

    Args:
      input: A GQL object or DB property.

    Returns:
      A JSON string based on the input object.

    Raises:
      TypeError: Typically occurs when an input object contains an unsupported
        type.
    """
    # return simplejson.dumps(input)
    
    if pretty:
      return GqlEncoder(indent=2).encode(input)
    return GqlEncoder().encode(input)

def xml(input, pretty = False):
    return input
    # AtomEncoder().encode(input)

# xml
# from django.core import serializers
# data = serializers.serialize("xml", Photo.objects.all())
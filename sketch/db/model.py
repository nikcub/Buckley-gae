from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.api import memcache
from google.appengine.ext.db import Error as DBError, BadQueryError, BadKeyError, BadPropertyError
from sketch.util.safestring import force_int

import base64
import logging

class ModelException(Exception):
    pass

class Model(db.Model):
    updated = db.DateTimeProperty(auto_now=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_where(self, field_name, field_value, num=20):
        q = db.GqlQuery("SELECT * From " + self.kind() + " WHERE " + field_name + " = :1", field_value)
        r = q.fetch(num)
        return r

    @classmethod
    def fetch_cached(self, query, num=100, cached=True, page=1):
      page = force_int(page, 1)
      num = force_int(num, 100)
      offset = 0   
      if page > 1:
        offset = (page - 1) * num
      logging.info('sketch.mode.fetch_cached: %s' % query)
      dat_key = "models.%s" % base64.b64encode(query)
      dat = memcache.get(dat_key)
      if dat is not None and cached:
        logging.info('cache hit')
        if num == 1:
          return dat[0]
        return dat[offset:offset + num]
      try:
        query = db.GqlQuery(query)
        if query.count() == 0:
          # logging.info('return on')
          return []
        resultset = query.fetch(num, offset)
        # logging.info(len(resultset))
        if resultset and type(resultset) == type([]):
          r = memcache.set(dat_key, resultset, 60 * 60)
          if num == 1:
            return resultset[0]
          return resultset
        return []
      except BadQueryError, e:
        logging.error('DB query error: %s in query: %s' % (str(e), query))
        return []        
      except DBError, e:
        logging.error('DB generic error: %s' % (str(e)))
        return []
      except Exception, e:
        logging.exception('DB generic: bad error: %s' % (str(e)))
        return []

    @classmethod
    def get_all(self, sort = None, offset = 0, num = 50):
        query = self.all()
        # if sort:
        query = query.order('-created')
        return query.fetch(num)

    @classmethod
    def get_by_key(self, key):
        try:
          if type(key) != db.Key:
            key = db.Key(key)
          i = db.get(key)
          return i
        except Exception, e:
          raise e

    def update(self, values):
        for arg in values:
            if hasattr(self, arg) and values[arg] != getattr(self, arg):
                setattr(self, arg, values[arg])
        try:
            z = self.put()
            return True
        except CapabilityDisabledError:
            logging.error('Database is down')

    @classmethod
    def get_last(self, num = 50):
        query = self.all().order('-created')
        return query.fetch(num)

    @classmethod
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

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
            logging.error('Database IS DOWN!!!')

    @classmethod
    def get_last(self, num = 50):
        query = self.all().order('-created')
        return query.fetch(num)

    @classmethod
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])

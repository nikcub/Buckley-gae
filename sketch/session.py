import os
import time
import datetime
import random
import logging

from vendor import stash
import sketch.exception

class Session(object):

  active = False
  handler = None
  sid = None
  cookiev = {
      'path': '/',
      'secure': False,
      'expire': None,
  }
  dirty = True

  def __init__(self, req_handler, session_name = "sess"):
    self.data = {}
    self.handler = req_handler
    self.session_name = session_name
    self.dirty = False

    if not self.session_name in req_handler.request.str_cookies:
      return None
    
    self.sid = req_handler.request.str_cookies[self.session_name]
    
    # quick sanity check
    if not '_' in self.sid:
      self.sid = None
      return None
      
    self.active = True
    self.__load()

  def __repr__(self): return repr(self.data)
  def __len__(self): return len(self.data)
  def clear(self): self.data.clear()
  def copy(self): return self.data.copy()
  def keys(self): return self.data.keys()
  def items(self): return self.data.items()
  def iteritems(self): return self.data.iteritems()
  def iterkeys(self): return self.data.iterkeys()
  def itervalues(self): return self.data.itervalues()
  def values(self): return self.data.values()
  def has_key(self, key): return key in self.data

  def get(self, key, default = None):
    if key not in self:
      return default
    return self[key]

  def __str__(self):
    return str(self.data)

  def __delitem__(self, key):
    del self.data[key]
    self.dirty = True

  def __getitem__(self, key):
    if key in self.data:
      return self.data[key]
    raise KeyError(key)

  def __setitem__(self, key, val):
    self.dirty = True
    if not self.active:
      self.__start()
    self.data[key] = val

  def __getattr__(self, key):
    return self.get(key)

  def __contains__(self, key):
    return key in self.data

  def __iter__(self):
    return iter(self.data)

  @property
  def message(self):
    return self.message['msg']

  def __load(self):
    data = stash.get("session.%s" % self.sid)
    if data:
      logging.info("Session: loaded (%s)" % self.sid)
      logging.info(data)
      self.data = data
    else:
      self.destroy()
      
  def __start(self):
    self.sid = self.gen_sid()
    self.handler.response.set_cookie(self.session_name, self.sid, permanent = True)
    self.active = True

  def destroy(self):
    self.handler.response.delete_cookie(self.session_name)
    stash.delete("session.%s" % self.sid)
    self.clear()
    self.active = False

  def save(self):
    if self.active and self.dirty:
      stash.set("session.%s" % self.sid, self.data)
      self.dirty = False

  def regen(self):
    stash.delete("session.%s" % self.sid)
    self.__start()
    self.dirty = True

  # def set_message(self, msg, type):

  def gen_sid(self):
    import hmac, uuid, random, base64, time
    sid = hmac.new(uuid.uuid4().hex)
    sid.update(str(round(random.random() * time.time())))
    # sid.update()
    return u"%s_%s" % (uuid.uuid4().hex, sid.hexdigest())




# 
# 
# class SessionGAEStore(db.Model):
#     ip = db.StringProperty(required = True)
#     ua = db.StringProperty(required = True)
#     created = db.DateTimeProperty(auto_now_add=True)
#     updated = db.DateTimeProperty(auto_now=True)
#     expired = db.BooleanProperty(default = False)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sketch Config class

Support reading configuration files from the following file formats:
  * YAML (with file extension .yaml or .yml)
  * JSON (with file extension .json or .js)
  * INI (extension .ini)
  * Text (with extension .txt or .cnf)
  * XML (not yet implemented but will be)

Supports caching to
  * Local memcache
  * Google App Engine memcache
  * Google App Engine db objects

Supports deployment environments by default: dev, staging, production

Requires: sketch/cache.py

# TODO implement different types of config as well as caching classes
"""

import os
import sys
import yaml
import string
import logging
from os.path import join as j_dir
from os.path import dirname
from sketch.util import assure_obj_child_dict, AttrDict
import config_global as DEFAULT_CONFIG

try:
  from sketch.vendor.stash import handler as cache_handler
  STASH_CACHE = True
except ImportError:
  logging.info('Config: no cache configured')
  STASH_CACHE = False


__all__ = ['Config']

class ConfigFileError(Exception): pass

class ConfigCacheError(Exception): pass

class ConfigParseError(Exception): pass

class Config(AttrDict):

  cache_key = "sketch.config.two"
  cache_timeout = 60 * 60

  # TODO implement config defaults
  # TODO implement cascading cache using Stash
  # TODO abstract this object and Session into Stash.util.dict
  # TODO fix save config
  def __init__(self, config=None, cache_options={}, refresh=False, **kwargs):
    
    self.clear()
    
    if type(DEFAULT_CONFIG) is type(os):
      conf_parsed = self.load_from_module(DEFAULT_CONFIG)
      self.update(conf_parsed)

    if type(config) is str:
      if not os.path.isfile(config):
        raise "Not a valid config file: %s" % config
      conf_parsed = self.load_from_file(config)
      self.update(conf_parsed)
    
    elif type(config) is dict:
      self.update(config)
      
    elif type(config) is type(os):
      conf_parsed = self.load_from_module(config)
      self.update(conf_parsed)

    if STASH_CACHE:
      self.cache_handler = cache_handler()

    self.init_environ()
    self.set_config_paths()
    self.set_config_template_paths()
  
  def init_environ(self):
    if self.is_dev_server:
      self.set_enviro = 'dev'

  def save(self):
    if self.active and self.dirty:
      stash.set(self.cache_key, self.data)
      self.dirty = False

  def load_from_file(self, file_name, refresh=False):
    if file_name.endswith('.yaml') or file_name.endswith('.yml'):
      conf = self.load_from_yaml(file_name)
    elif file_name.endswith('.ini'):
      raise 'Not Implemented: Config from INI'
      conf = self.load_from_ini(file_name)
    else:
      raise 'Not Implemented: Config from %s' % file_name
    return conf
    
  def load_from_yaml(self, file_name, refresh=False):
    file_contents = open(file_name, 'r')
    conf_parsed = yaml.load(file_contents)
    return conf_parsed

  def load_from_ini(self, file_name):
    raise 'Not Implemented: Config->load_from_ini'

  def load_from_module(self, module_name):
    conf_parsed = {}
    for setting in dir(module_name):
      if not setting.startswith('__'):
        setting_value = getattr(module_name, setting)
        conf_parsed[setting] = setting_value
    return conf_parsed

  def parse_config(self, conf):
    if type(conf) != dict:
      raise ConfigParseError, "Could not parse cached config"
    self.data.append(conf)
    
  def save_config(self):
    stash.set(self.cache_key, self.data)

  def set_config_paths(self):
    """Sets path information in the :class:`Config` object.
    
    Returns the new :class:`Config` object
    
    :param config: Config object to add path information to
    """
    # self.data = assure_obj_child_dict(self.data, 'paths')
    if not 'paths' in self:
      self.paths = {}
    
    paths = {}
    paths['sketch_dir'] = sketch_dir = dirname(__file__)
    paths['site_dir'] = site_dir = j_dir(dirname(__file__), '..')
    if not 'appname' in self:
      self.appname = 'buckley'
    paths['app_dir'] = app_dir = j_dir(site_dir, self.appname)
    
    for path in paths:
      p = os.path.normpath(paths[path])
      if os.path.isdir(p) and not path in self.paths:
        self.paths[path] = p
        # setattr(self.paths, path, p)


  def set_config_template_paths(self):
    """Sets the paths to templates in the config
    
    Returns a new :class:`Config` object
    
    :param config: Config object
    """
    # self.data['paths'] = assure_obj_child_dict(self.data['paths'], 'templates')
    if not 'templates' in self.paths:
      self.paths.templates = {}
    templates = {}

    if not 'templates' in self:
      return None

    for template in self.templates:
      temp_path = self.templates[template]
      if '$' in temp_path:
        s = string.Template(temp_path)
        temp_path = s.substitute(self['paths'])
      if os.path.isdir(temp_path):
        self.paths.templates[template] = temp_path
      else:
        logging.error("Config: Could not set template path for %s, not a directory: %s" % (template, temp_path))

  
  #---------------------------------------------------------------------------
  #   Properties
  #---------------------------------------------------------------------------

  @property
  def is_dev_server(self):
    return os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

  @property
  def is_debug(self):
    if self.enviroments and type(self.enviroments) == type(dict) and self.set_enviro and self.set_enviro in self.enviroments:
      return self.enviroments[self.set_enviro]['debug']
    return False

  @property  
  def is_dev(self):
    return self.set_enviro == 'dev'

  @property  
  def is_staging(self):
    return self.set_enviro == 'staging'

  @property  
  def is_live(self):
    return self.set_enviro == 'live'
  
  @property
  def enviro(self):
    if self.enviroments and type(self.enviroments) == type(dict) and self.set_enviro and self.set_enviro in self.enviroments:
      return self.enviroments[self.set_enviro]
    return False

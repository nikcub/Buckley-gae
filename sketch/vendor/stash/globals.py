
_sketch_globals = {}
_sketch_app = None
_sketch_request = None
_sketch_controllers = {}
_sketch_views = {}
_sketch_models = {}

import logging
from thread import get_ident


class GlobalStore(dict):
    """docstring for VarChar"""
    def __init__(self, arg = None):
        if arg:
            self.__store__ = arg
        else:
            self.__store__ = {}

    def __iter__(self):
        """docstring for __iter__"""
        return self.__store__.iteritems()

    def __contains__(self):
        """docstring for __contains__"""
        pass

    def __sstr__(self):
        """docstring for __str__"""
        pass

    # def __getattr__(self, key):
    #   """docstring for __getattr__"""
    #   logging.info("Called getitem with %s" % key)
    #   return self.__store__[key]
    #
    # def __setattr__(self, key, val):
    #   """docstring for __setattr__"""
    #   logging.info("Called setattr with %s %s" % (key, val))
    #   self.__store__[key] = val

    def __getitem__(self, key):
        """docstring for __getitem__"""
        logging.info("Called getitem with %s" % key)
        if self.__store__.has_key(key):
            return self.__store__[key]
        logging.info("KEY ERROR: %s" % key)

    def __setitem__(self, key, val):
        """docstring for __setitem__"""
        logging.info("Called setitem with %s %s" % (key, val))
        self.__store__[key] = val

    def __delitem__(self):
        """docstring for __delitem__"""
        pass

    def fname(self):
        """docstring for fname"""
        pass

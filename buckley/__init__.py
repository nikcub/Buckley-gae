#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sketch
import logging
import conf

from .reqhandlers import BaseController, AdminController
from .routes import routes

config_file = os.path.join(os.path.dirname(__file__), "conf.yaml")

config_obj = sketch.Config(config_file)
# app = sketch.Application(config_file, debug=debug, routes=buckley.routes)

app = sketch.Application(config=conf, routes=routes)
import sys
import os
import cgi
import datetime
import urllib
import logging
from os.path import isdir
from os.path import join as dj

import sketch.serialize
from sketch.webapp import RequestHandler
from sketch.templating import jinja
from sketch.util import hasmethod, hasvar, getmethattr, force_unicode

class Messages(object):
  info = "info"
  warning = "warning"
  error = "error"


class BaseController(RequestHandler):
  """BaseController default application controller that is inherited for other
  controllers. Implements requests, response, rendering, plugins etc.
  
  """
  
  _Plugins = {}
  template_set = 'site'
  message = False
  message_type = None

  def pre_hook(self):
    self.reg_messages()

  def post_hook(self):
    self.session.save()

  # Plugin reg
  def plugin_register(self, plugin_name, plugin_inst):
    self._Plugins[plugin_name] = plugin_inst

  def attach_session(self, session):
    self.session = session

  def reg_messages(self):
    self.messages = Messages()

    # logging.info("Plugin Reg: Registering messages plugin")
    # logging.info(self.messages)
    # logging.info(self.messages.info)
    if 'message' in self.session:
      self.message = self.session['message']
      self.message_type = self.session['message_type']
      self.message_class = self.session['message_class']
      del self.session['message']
      del self.session['message_type']
      del self.session['message_class']
      self.session.save()



  #---------------------------------------------------------------------------
  #   messages
  #---------------------------------------------------------------------------


  def set_msg(self, message, message_type = None):
    return self.set_message(message, message_type)

  def set_message(self, message, message_type = None, fade = 'fade'):
    if not message_type:
        message_type = self.messages.info
    # use a custom session component to set the message
    self.session['message'] = message
    self.session['message_type'] = message_type
    self.session['message_class'] = fade
    self.session.save()
    # self.message_type = message_type


  #---------------------------------------------------------------------------
  #   Rendering
  #---------------------------------------------------------------------------


  def render(self, template_name, passed_vars, response_code = 200, 
          response_type=False, prettyPrint=False, template_set='site', template_theme=None):
    """Main render helper function. Wraps other rendering functions
    
    """
    if not response_type:
      response_type = self.request.response_type()

    prettyPrint = bool(self.request.get('prettyPrint', False))
    
    if hasmethod(self, 'template_wrapper'):
      passed_vars = self.template_wrapper(variables = passed_vars)
    
    if response_type == 'json':
      return self.render_json(passed_vars, response_code)
    else:
      # setup jinja
      jinja.setup(self.config.paths.template_sets)
      
      # setup variables
      passed_vars = self.get_template_vars(passed_vars)
      passed_vars = self.get_plugin_vars(passed_vars)
      
      # Get template_set and template_theme
      template_set = self.get_template_set()
      template_theme = self.get_template_theme(template_set)
      
      # logging.info('Rendering with: template_name: %s template_theme: %s template_set: %s' % (template_name, template_theme, template_set))
      content = jinja.render(template_name, passed_vars, template_theme=template_theme, template_set=template_set)
    
    self.render_content(content, response_code)


  def render_json(self, template_vars=None, response_code=200, headers=None):
    template_vars = template_vars or {}
    headers = headers or {}
    pretty_print = bool(self.request.get('prettyPrint', False))
    content = force_unicode(sketch.serialize.json(template_vars, pretty=pretty_print))
    if not 'Content-Type' in headers:
      headers['Content-Type'] = "application/json; charset=utf-8"
    self.render_content(content, response_code, headers)

  def render_content(self, content, response_code = 200, headers = []):
    """The actual function that will render content back into the response
    
    :param content: Content to be rendered
    :param response_code: HTTP response code
    :param headers: Response headers
    """
    self.response.clear()
    if len(headers) > 0:
      for hn, hv in headers.iteritems():
        self.response.headers[hn] = hv
    self.response.set_status(response_code)
    self.response.write(content)


  def render_error(self, message = False, code = 404):
    self.render('error', {
        'code': '%d - %s' % (code, self.response.http_status_message(code)),
        'message': message
    }, code, template_set='sketch', template_theme='default')


  def render_admin(self, template_name, vars):
    return self.render(template_name, vars, template_folder='admin')


  def render_sketch(self, template_name, vars):
    vars['admin'] = True
    return self.render(template_name, vars, template_folder='sketch')


  def get_styles(self, template_vars):
    if not hasattr(self, 'styles'):
      return template_vars
    
    styles_dict = getmethattr(self, 'styles')
    styles_tmp = ""
    
    for style_path in styles_dict:
      style_name = ""
      styles_tmp = styles_tmp + "<link id=\"%s\" rel=\"stylesheet\" href=\"%s\" type=\"text/css\">" % (style_name, style_path)
    
    template_vars['styles'] = styles_tmp
    return template_vars

  def get_javascripts(self, template_vars):
    """Will read the javascripts to be included, create the tags and include
    them as part of the template variables
    
    :param template_vars: Template variable dict
    """
    if not hasattr(self, 'javascripts'):
      return template_vars
    
    scripts_dict = getmethattr(self, 'javascripts')
    js_tmp = ""

    for script_name, script_val in scripts_dict.iteritems():
      script_src = ""
      if 'base_dir' in script_val:
        script_src = script_val['base_dir']
      for script_uri in script_val['src']:
        if 'version' in script_val:
          script_uri = script_uri + "?%s" % script_val['version']
        js_tmp = js_tmp + "\t<script type=\"text/javascript\" src=\"%s\"></script>\n" % (script_src + script_uri)
        
    template_vars['javascripts'] = js_tmp
    return template_vars


  def get_template_set(self):
    if hasattr(self, 'template_set'):
      return getmethattr(self, 'template_set')
    if (self.config.default_template_set):
      return self.config.default_template_set
    raise Exception('no template set specified')

  def get_template_theme(self, template_set=None):
    if template_set in self.config.template_themes:
      return self.config.template_themes[template_set]
    if hasattr(self, 'template_theme'):
      return getmethattr(self, 'template_theme')
    if (self.config.default_template_theme):
      return self.config.default_template_theme
    raise Exception('no template theme specified')


  def get_template_vars(self, vars):
    if type(vars) != dict:
      vars = {'_vars': vars}
      
    additional = {
      # 'session': self.session,
      # 'user': False,

        # 'title': 'test'
        # 'title': self.conf_get('title')
    }

    # if 'auth' in self.session:
    #   additional['loggedin'] = True
    #   additional['username'] = self.session.get('username', '')
    #   additional['user'] = self.user
    # 
    # if self.message:
    #   additional['message'] = self.message
    #   additional['message_type'] = self.message_type
    #   additional['message_class'] = self.message_class

    additional = self.get_javascripts(additional)
    additional = self.get_styles(additional)

    return dict(vars, **additional)


  def render_blob(self, blob_key_or_info, filename=None):
    """Render a file from the GAE blobstore
    
    :param blog_key_or_info: A key for the blog
    :param filename: (optional) Name of file in user download
    """
    if isinstance(blob_key_or_info, blobstore.BlobInfo):
      blob_key = blob_key_or_info.key()
      blob_info = blob_key_or_info
    else:
      blob_key = blob_key_or_info
      blob_info = None

    self.response.headers[blobstore.BLOB_KEY_HEADER] = str(blob_key)
    del self.response.headers['Content-Type']

    def saveas(filename):
      if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
      self.response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename

    if filename:
      if isinstance(filename, basestring):
        saveas(filename)
      elif blob_info and filename:
        saveas(blob_info.filename)
      else:
        raise ValueError("problem with filename to save as")

    self.response.clear()


  #---------------------------------------------------------------------------
  #   helpers
  #---------------------------------------------------------------------------


  def get_plugin_vars(self, vars):
    for plugin in self._Plugins:
      if hasattr(self._Plugins[plugin], "render"):
        val_dict = self._Plugins[plugin].render()
        if type(val_dict) == type({}):
          for temp_var in val_dict:
            if not vars.has_key(temp_var):
              vars[temp_var] = val_dict[temp_var]
            else:
              logging.error("Did not get a valid dict type from plugin %s" % plugin)
    return vars


  def get_param_dict(self):
    params = {}
    for argument in self.request.arguments():
      params[argument] = self.request.get(argument)
    return params


  #---------------------------------------------------------------------------
  #   Rendering Engines
  #---------------------------------------------------------------------------


  def render_django(self, template_name, vars, response_type = False):
    """Given a template name and variables will render the template using
    the default Django template rendering engine 
    
    :param template_name: Name of template
    :param vars: Template variables
    
    @TODO clean out the 'get_template_path' stuff and put that in render
    @TODO this should only be rendering, none of the fancy content stuff
    """
    pass
    # from google.appengine.dist import use_library
    from google.appengine.ext.webapp import template
    
    if not response_type:
        response_type = self.request.response_type()
    vars = self.get_template_vars(vars)
    vars = self.get_plugin_vars(vars)
    if response_type in ['xml', 'json']:
        serial_f = getattr(sketch.serialize, response_type)
        content = serial_f(vars)
        self.response.headers['Content-Type'] = "application/%s; charset=utf-8" % (response_type)
    else:
        content = template.render(self.get_template_path(template_name, response_type), vars)
    return content


  #---------------------------------------------------------------------------
  #   Conveniance Methods
  #---------------------------------------------------------------------------

  @property
  def debug(self):
    return self.config.is_debug

  @property
  def is_dev(self):
    return self.config.is_dev
    
  @property
  def is_staging(self):
    return self.config.is_staging
    
  @property
  def is_live(self):
    return self.config.is_live
    
  @property
  def env(self):
    return self.config.enviro or None

  @property
  def enviro(self):
    return self.config.enviro


class AdminController(BaseController):
  """A custom controller that restricts permissions to only those users who are
  an administrator
  
  """

  template_path = os.path.join('')

  def __call__(self, _method, *args, **kwargs):
    if not self.user:
      abort(403)

    if not self.user.admin:
      abort(405)

    super(AdminController, self).__call__(_method, *args, **kwargs)


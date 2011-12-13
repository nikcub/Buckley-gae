#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Router classes and methods
"""

import re
import sketch

#: Regex for URL definitions.
_ROUTE_REGEX = re.compile(r'''
    \<            # The exact character "<"
    (\w*)         # The optional variable name (restricted to a-z, 0-9, _)
    (?::([^>]*))? # The optional :regex part
    \>            # The exact character ">"
    ''', re.VERBOSE)

class BaseRoute(object):
    """Interface for URL routes. Custom routes must implement some or all
    methods and attributes from this class.
    """
    #: Route name, used to build URLs.
    name = None
    #: True if this route is only used for URL generation and never matches.
    build_only = False

    def match(self, request):
        """Matches this route against the current request.

        :param request:
            A ``webapp.Request`` instance.
        :returns:
            A tuple ``(handler, args, kwargs)`` if the route matches, or None.
        """
        raise NotImplementedError()

    def build(self, request, args, kwargs):
        """Builds and returns a URL for this route.

        :param request:
            The current ``Request`` object.
        :param args:
            Tuple of positional arguments to build the URL.
        :param kwargs:
            Dictionary of keyword arguments to build the URL.
        :returns:
            An absolute or relative URL.
        """
        raise NotImplementedError()

    def get_routes(self):
        """Generator to get all routes from a route.

        :yields:
            This route or all nested routes that it contains.
        """
        yield self

    def get_match_routes(self):
        """Generator to get all routes that can be matched from a route.

        :yields:
            This route or all nested routes that can be matched.
        """
        if not self.build_only:
            yield self
        elif not self.name:
            raise ValueError("Route %r is build_only but doesn't have a "
                "name" % self)

    def get_build_routes(self):
        """Generator to get all routes that can be built from a route.

        :yields:
            This route or all nested routes that can be built.
        """
        if self.name is not None:
            yield self


class SimpleRoute(BaseRoute):
    """A route that is compatible with webapp's routing. URL building is not
    implemented as webapp has rudimentar support for it, and this is the most
    unknown webapp feature anyway.
    """
    def __init__(self, template, handler):
        """Initializes a URL route.

        :param template:
            A regex to be matched.
        :param handler:
            A :class:`RequestHandler` class or dotted name for a class to be
            lazily imported, e.g., ``my.module.MyHandler``.
        """
        self.template = template
        self.handler = handler
        # Lazy property.
        self.regex = None

    def _regex(self):
        if not self.template.startswith('^'):
            self.template = '^' + self.template

        if not self.template.endswith('$'):
            self.template += '$'

        self.regex = re.compile(self.template)
        return self.regex

    def match(self, request):
        """Matches this route against the current request.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        regex = self.regex or self._regex()
        match = regex.match(request.path)
        if match:
            return self.handler, match.groups(), {}

    def __repr__(self):
        return '<SimpleRoute(%r, %r)>' % (self.template, self.handler)

    __str__ = __repr__


class Route(BaseRoute):
    """A URL route definition. A route template contains parts enclosed by
    ``<>`` and is used to match requested URLs. Here are some examples::

        route = Route(r'/article/<id:[\d]+>', ArticleHandler)
        route = Route(r'/wiki/<page_name:\w+>', WikiPageHandler)
        route = Route(r'/blog/<year:\d{4}>/<month:\d{2}>/<day:\d{2}>/<slug:\w+>', BlogItemHandler)

    Based on `Another Do-It-Yourself Framework`_, by Ian Bicking. We added
    URL building, non-keyword variables and other improvements.
    """
    def __init__(self, template, handler=None, name=None, defaults=None,
        build_only=False):
        """Initializes a URL route.

        :param template:
            A route template to be matched, containing parts enclosed by ``<>``
            that can have only a name, only a regular expression or both:

              =============================  ==================================
              Format                         Example
              =============================  ==================================
              ``<name>``                     ``r'/<year>/<month>'``
              ``<:regular expression>``      ``r'/<:\d{4}>/<:\d{2}>'``
              ``<name:regular expression>``  ``r'/<year:\d{4}>/<month:\d{2}>'``
              =============================  ==================================

            If the name is set, the value of the matched regular expression
            is passed as keyword argument to the :class:`RequestHandler`.
            Otherwise it is passed as positional argument.

            The same template can mix parts with name, regular expression or
            both.
        :param handler:
            A :class:`RequestHandler` class or dotted name for a class to be
            lazily imported, e.g., ``my.module.MyHandler``.
        :param name:
            The name of this route, used to build URLs based on it.
        :param defaults:
            Default or extra keywords to be returned by this route. Values
            also present in the route variables are used to build the URL
            when they are missing.
        :param build_only:
            If True, this route never matches and is used only to build URLs.
        """
        self.template = template
        self.handler = handler
        self.name = name
        self.defaults = defaults or {}
        self.build_only = build_only
        # Lazy properties.
        self.regex = None
        self.variables = None
        self.reverse_template = None

    def _parse_template(self):
        self.variables = {}
        last = count = 0
        regex = reverse_template = ''
        for match in _ROUTE_REGEX.finditer(self.template):
            part = self.template[last:match.start()]
            name = match.group(1)
            expr = match.group(2) or '[^/]+'
            last = match.end()

            if not name:
                name = '__%d__' % count
                count += 1

            reverse_template += '%s%%(%s)s' % (part, name)
            regex += '%s(?P<%s>%s)' % (re.escape(part), name, expr)
            self.variables[name] = re.compile('^%s$' % expr)

        regex = '^%s%s$' % (regex, re.escape(self.template[last:]))
        self.regex = re.compile(regex)
        self.reverse_template = reverse_template + self.template[last:]
        self.has_positional_variables = count > 0

    def _regex(self):
        self._parse_template()
        return self.regex

    def _variables(self):
        self._parse_template()
        return self.variables

    def _reverse_template(self):
        self._parse_template()
        return self.reverse_template

    def match(self, request):
        """Matches this route against the current request.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        regex = self.regex or self._regex()
        match = regex.match(request.path)
        if match:
            kwargs = self.defaults.copy()
            kwargs.update(match.groupdict())
            if kwargs and self.has_positional_variables:
                args = tuple(value[1] for value in sorted((int(key[2:-2]), \
                    kwargs.pop(key)) for key in \
                    kwargs.keys() if key.startswith('__')))
            else:
                args = ()

            return self.handler, args, kwargs

    def build(self, request, args, kwargs):
        """Builds a URL for this route.

        .. seealso:: :meth:`Router.build`.
        """
        full = kwargs.pop('_full', False)
        scheme = kwargs.pop('_scheme', None)
        netloc = kwargs.pop('_netloc', None)
        anchor = kwargs.pop('_anchor', None)

        if full or scheme or netloc:
            if not netloc:
                netloc = request.host

            if not scheme:
                scheme = 'http'

        path, query = self._build(args, kwargs)
        return urlunsplit(scheme, netloc, path, query, anchor)

    def _build(self, args, kwargs):
        """Builds the path for this route.

        :returns:
            A tuple ``(path, kwargs)`` with the built URL path and extra
            keywords to be used as URL query arguments.
        """
        variables = self.variables or self._variables()
        if self.has_positional_variables:
            for index, value in enumerate(args):
                key = '__%d__' % index
                if key in variables:
                    kwargs[key] = value

        values = {}
        for name, regex in variables.iteritems():
            value = kwargs.pop(name, self.defaults.get(name))
            if not value:
                raise KeyError('Missing argument "%s" to build URL.' % \
                    name.strip('_'))

            if not isinstance(value, basestring):
                value = str(value)

            if not regex.match(value):
                raise ValueError('URL buiding error: Value "%s" is not '
                    'supported for argument "%s".' % (value, name.strip('_')))

            values[name] = value

        return (self.reverse_template % values, kwargs)

    def __repr__(self):
        return '<Route(%r, %r, name=%r, defaults=%r, build_only=%r)>' % \
            (self.template, self.handler, self.name, self.defaults,
            self.build_only)

    __str__ = __repr__


class Router(object):
    """A simple URL router used to match the current URL, dispatch the handler
    and build URLs for other resources.
    """
    #: Class used when the route is a tuple. Default is compatible with webapp.
    route_class = SimpleRoute

    def __init__(self, app, routes=None):
        """Initializes the router.

        :param app:
            The :class:`WSGIApplication` instance.
        :param routes:
            A list of :class:`Route` instances to initialize the router.
        """
        self.app = app
        # Handler classes imported lazily.
        self._handlers = {}
        # All routes that can be matched.
        self.match_routes = []
        # All routes that can be built.
        self.build_routes = {}
        if routes:
            for route in routes:
                self.add(route)

    def add(self, route):
        """Adds a route to this router.

        :param route:
            A :class:`Route` instance.
        """
        if isinstance(route, tuple):
            # Simple route, compatible with webapp.
            route = self.route_class(*route)

        for r in route.get_match_routes():
            self.match_routes.append(r)

        for r in route.get_build_routes():
            self.build_routes[r.name] = r

    def match(self, request):
        """Matches all routes against the current request. The first one that
        matches is returned.

        :param request:
            A ``webapp.Request`` instance.
        :returns:
            A tuple ``(route, args, kwargs)`` if a route matched, or None.
        """
        for route in self.match_routes:
            match = route.match(request)
            if match:
                request.route = route
                request.route_args, request.route_kwargs = match[1], match[2]
                return match

    def dispatch(self, app, request, response, match, method=None):
        """Dispatches a request. This calls the :class:`RequestHandler` from
        the matched :class:`Route`.

        :param app:
            A :class:`WSGIApplication` instance.
        :param request:
            A ``webapp.Request`` instance.
        :param response:
            A :class:`Response` instance.
        :param match:
            A tuple ``(handler, args, kwargs)``, resulted from the matched
            route.
        :param method:
            Handler method to be called. In cases like exception handling, a
            method can be forced instead of using the request method.
        """
        handler_class, args, kwargs = match
        method = method or request.method.lower().replace('-', '_')

        # TODO : implement middleware
        # session_name = "sess"
        # if app.config.has_key('session_name'):
            # session_name = app.config['session_name']



        # TODO : fix plugins
        # if self.plugins_registered:
        #   if hasattr(handler, 'plugin_register'):
        #       for pl in self._Plugins:
        #           handler.plugin_register(pl, self._Plugins[pl])
        #   else:
        #       logging.error("Handler %s does not support plugin resitration" % handler.__name__)
        #
        # groups = match.groups()
        # handler.request.uri_groups = groups

        # if hasattr(handler_class, 'pre_hook'):
            # handler_class.pre_hook()
        # z = t

        if isinstance(handler_class, basestring):
            if handler_class not in self._handlers:
                self._handlers[handler_class] = import_string(handler_class)

            handler_class = self._handlers[handler_class]

        new_style_handler = True
        try:
            handler = handler_class(app, request, response)

            handler.session = sketch.Session(handler, 'sess')
            handler.config = app.config
        except TypeError, e:
            # Support webapp's initialize().
            new_style_handler = False
            handler = handler_class()
            handler.initialize(request, response)

            handler.session = sketch.Session(handler, 'sess')
            handler.config = app.config

        try:
            if new_style_handler:
                handler(method, *args, **kwargs)
            else:
                # Support webapp handlers which don't implement __call__().
                getattr(handler, method)(*args)
        except Exception, e:
            if method == 'handle_exception':
                # We are already handling an exception.
                raise

            # If the handler implements exception handling, let it handle it.
            handler.handle_exception(e, app.debug)

    def build(self, name, request, args, kwargs):
        """Builds and returns a URL for a named :class:`Route`.

        :param name:
            The route name.
        :param request:
            The current ``Request`` object.
        :param args:
            Tuple of positional arguments to build the URL.
        :param kwargs:
            Dictionary of keyword arguments to build the URL.
        :returns:
            An absolute or relative URL.

        .. seealso:: :meth:`RequestHandler.url_for`.
        """
        route = self.build_routes.get(name)
        if not route:
            raise KeyError('Route "%s" is not defined.' % name)

        return route.build(request, args, kwargs)

    def __repr__(self):
        routes = self.match_routes + [v for k, v in \
            self.build_routes.iteritems() if v not in self.match_routes]

        return '<Router(%r)>' % routes

    __str__ = __repr__

# Buckley

A blogging tool built for Google App Engine with the goal of social integration, high performance and flexibility

Blogging rebooted for 2011

**NOTE: This is an alpha release for developers**

There will eventually be a one-click auto deploy and install, but it isn't there yet

## Features

 * Statuses and posts
 * Facebook + twitter integration
 * Support pages
 * Simple and extensible template system
 * Simple default template you can use as a base
 * Plugin system that is easy to use
 * Support for JSON and XML output via the API
 * Static output
 * Auto caching for traffic spikes 

## Install

Get the App Engine SDK:

  http://code.google.com/appengine/downloads.html

Clone this code out (or fork and then clone):

    $ git clone git://github.com/nikcub/Buckley.git

Create the local datastore files, for eg.

    $ mkdir .data
    $ touch .data/buckley.datastore

This will help you retain a local copy of all your data. (I actually write posts locally and then deploy)

Start the dev server using the following options:

    $ dev_appserver.py -p 9090 --use_sqlite --datastore_path=.data/buckley.datastore --disable_static_caching --skip_sdk_update_check .

The options tell the server to use sqlite and to use the local datastore. This means the datastore will be persistent between restarts and you won't lose your data. I recommend you keep a backup of the datastore file.

Or, just deploy and run:

    $ appcfg.py update -A yourappengineid .


## Dependancies

All the dependancies are bundled. First is Sketch, which is my webapp library for App Engine (the goal of which is to get python appengine apps running on other platforms, and to just provide a nicer layer for web apps that isn't Google webapps and nor is it Django). 

Sketch is its own project and is a mix of my own code and third-party code. I use it in all my projects, and the version here is a lighter fork.

Other dependancies, which are included in the vendor directory of Sketch are jinja2, stash (my module for caching) and markdown (for parsing markdown)

## Customizing

Edit the template at ./templates/ or make your own copy in that dir (and update blog.yaml to use it)

To run the app, cd in and run:

    dev_appserver.py .

To deploy, use appcfg.py or the GUI that comes with Google App Engine.

## Configuration

Configuration is read from the conf.py file that is located in the root directory. The default system-wide configuration is read from sketch config_global.py. That file gives you an idea of what configuration options can be set. The options that are required in config.py are:

 Name Type Default Value
 title string
 description string 
 frontpage_posts integer 10
 plugins dict empty

## Syncing remote data to local

You can download your remote server data to your local instance. Make sure you have `remote_api` enabled.

    $ appcfg.py download_data --application=nikcub --url=http://nikcub.appspot.com/_ah/remote_api --filename=.data/nikcub.log

And then import

    $ appcfg.py upload_data --filename=.data/nikcub.log --url=http://localhost:9090/remote_api --auth_domain=localhost:9090 --application=dev~buckleyapp

Enter any username and password. Your app.yaml should have the remote api enabled:

    - url: /remote_api
      script: $PYTHON_LIB/google/appengine/ext/remote_api/handler.py
      login: admin

This should be before the default route.

## Templates


## Todo

@TODO	categories

@TODO	export / import

@TODO	comments / users / moderation

@TODO	support multiple URLs (ie. stub changed) with list of 'old' to match and redirect


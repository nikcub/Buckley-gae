;(function($, Sketch) {
 
  var Buckley = window.Buckley = {};
  Buckley.Views = {};
  Buckley.Models = {};
  Buckley.Collections = {};
  
  Buckley.Models.Post = Backbone.Model.extend({
    urlRoot: '/data/post',
    
    defaults: {
      when: (new Date().getTime() / 1000)
    },
    
    initialize: function() {  
    },
    
    url: function() {
      var url = '';
      var base = this.urlRoot || getUrl(this.collection) || urlError();

      if (this.isNew()) {
        url = base;
      } else {
        var url = base + (base.charAt(base.length - 1) == '/' ? '' : '/') + encodeURIComponent(this.id);
      }
      return url;
    },
    
    parse: function(resp, xhr) {
      console.info(resp, xhr);
      return resp;
    }
  });

  Buckley.Collections.Posts = Sketch.Collection.extend({
    tagName: 'div',
    className: 'row',
    url: '/data/post',
    model: Buckley.Models.Post,

  });
  
  Buckley.Views.Post = Backbone.View.extend({
    tagName: 'tr',
    
    initialize: function() {
      _.bindAll(this, 'render', 'unrender');
      this.model.bind('change', this.render);
    },
    

    
    render: function() {
      this.el.innerHTML = ich.post_list_record(this.model.toJSON(), true);
      return this;
    },
    
    unrender: function() {
      
    }
  });
  
  Buckley.Views.index = Backbone.View.extend({
    
    initialize: function() {
      _.bindAll(this, 'render', 'unrender');
    },

    
    render: function() {
      template_vars = {}
      this.el.innerHTML = ich.index(template_vars, true);
      return this;
    },

    
    unrender: function() {
      
    } 
  });
  
  Buckley.Views.posts_index = Backbone.View.extend({
    className: 'row',
    
    initialize: function() {
      _.bindAll(this, 'render', 'unrender');
      this.model.bind('change', this.render);
    },
    
    render: function() {
      template_vars = {}
      template_vars['posts'] = this.model.toJSON();
      template_vars['post_type'] = 'Post'
      console.info(this.model.length, template_vars);
      this.el.innerHTML = ich.post_list_view_iterable(template_vars, true);
      return this;
    },
    
    unrender: function() {
      this.el.innerHTML = '';
    }
  });
  
  Buckley.Views.post_edit = Backbone.View.extend({
    tagName: 'div',

    
    initialize: function() {
      _.bindAll(this, 'render', 'unrender');
      this.model.bind('change', this.render);
    },
    
    
    render: function() {
      this.el.innerHTML = ich.post_edit_view(this.model.toJSON(), true);
      return this;
    },
    
    unrender: function() {
      
    }
  });
  
  Buckley.App = Backbone.Router.extend({
    routes: {
      '': 'index',
      '/': 'index',
      '/posts': 'posts_index',
      '/posts_old': 'posts_index_old',
      '/posts/edit/:id': 'posts_edit',
      '*path': 'not_found',
    },
    models: {},
    collections: {},
    views: {},
    
    initialize: function(options) {
      this.holder = options.holder;
      var self = this;
      
      this.models = {};
      this.views = {};
      this.models['posts'] = {};
      this.views['posts'] = {};
      this.models.posts['index'] = new Buckley.Collections.Posts();
      
      this.models.posts.index.fetch({
        success: function() {
          console.info('fetched!');
          console.info(self.models.posts.index);
          console.info(self.models.posts.index.length);
        }
      });
    },
    
    index: function() {
      var self = this;
      console.info('index');
      
      this.views['index'] = new Buckley.Views.index({
      });
      
      $(this.holder).html('Loaded');
      $(this.holder).append(this.views.index.render().el);
    },
    
    posts_index: function() {
      var self = this;
      console.info('posts_index');
      
      this.views.posts['index_new'] = new Buckley.Views.posts_index({
        model: this.models.posts.index
      })
      
      $(this.holder).html('');
      $(this.holder).append(this.views.posts.index_new.render().el);
    },
    
    posts_edit: function(id) {
      var self = this;
      
      console.info('editing post: ', id);
      
      // this.models.posts[id] = Buckley.Models.Post();
      this.models.posts[id] = this.models.posts.index.get(id);
      
      if(!this.models.posts[id]) throw "NotFound"
      
      this.views.posts[id] = new Buckley.Views.post_edit({
        model: this.models.posts[id],
      });
      console.info(this.views.posts[id]);
      
      // this.views.posts[id].model.fetch();
      this.models.posts[id].fetch({
        success: function() {
          console.info('success');
        }
      });

      $(this.holder).html('');
      $(this.holder).append(this.views.posts[id].render().el);
    },

    posts_index_old: function() {
      var self = this;
      console.info('index');
      
      this.views.posts['index'] = new Sketch.Views.Collection({
        collection: self.models.posts.index,
        className: 'row',
        tagName: 'div',
        itemView: Buckley.Views.Post,
        template: 'post_list_view'
      });
      
      $(this.holder).html('');
      $(this.holder).append(this.views.posts.index.render().el);
    },
        
    not_found: function(notfound) {
      console.error('404 Page Not Found:', notfound);
    }
  });
  
  
})(window.Zepto || window.jQuery, window.Sketch);

$(function() {

  window.app = new Buckley.App({'holder': '#main'});

  $('body').delegate('a', 'click', function(e) { 
    e.preventDefault(); 
    var href = $(event.target).attr('href').replace(Backbone.history.options.root, "");
    if (href !== undefined) {
      console.info('Link:', href);
      Backbone.history.navigate(href, true);
    } else {
      console.error('Link: Not found', event.target);
    }
  });

  Backbone.history.start({root: '/admin', pushState: true, silent: false });
  
	$('.topbar').dropdown();


	$('#btn_save').click(function(ev) {
		alert('saved!');
		ev.preventDefault();
		$.ajax('/data/post', {
		  type: 'PUT'
		});
	});

});
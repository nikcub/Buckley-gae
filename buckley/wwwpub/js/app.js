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
      console.info("Model Todo url():", url);
      return url;
    },
    
    parse: function(resp, xhr) {
      console.info(resp, xhr);
      return resp;
    }
  });

  Buckley.Collections.Posts = Sketch.Collection.extend({
    url: '/data/post',
    model: Buckley.Models.Post,
    
  });
  
  Buckley.Views.Post = Backbone.View.extend({
    initialize: function() {
      _.bindAll(this, 'render', 'unrender');
      this.model.bind('change', this.render);
    },
    
    render: function() {
      this.el.innerHTML = ich.postView(this.model.toJSON(), true);
      return this;
    },
    
    unrender: function() {
      
    }
  });
  
  Buckley.App = Backbone.Router.extend({
    routes: {
      '': 'index',
      'project/:id': 'project',
    },
    models: {},
    collections: {},
    views: {},
    
    initialize: function(options) {
      this.holder = options.holder;
      var self = this;
      
      this.posts = new Buckley.Collections.Posts();
      this.views['posts'] = new Sketch.Views.Collection({
        collection: self.posts,
        className: 'postlist',
        itemView: Buckley.Views.Post
      });
      
      this.posts.fetch({
        success: function() {
          console.info('success!');
          Backbone.history.start({root: '/', pushState: false, silent: false });
        },
        error: function() {
          console.error('error!');
        }
      });
      
      $(this.holder).append(this.views.posts.render().el);
    }
  });
  
  
})(window.Zepto, window.Sketch);

$(function() {


	$('.topbar').dropdown();


	$('#btn_save').click(function(ev) {
		alert('saved!');
		ev.preventDefault();
		$.ajax('/data/post', {
		  type: 'PUT'
		});
	});

});
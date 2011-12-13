from buckley.plugin import Plugin_base
from buckley.models import Post

class google_analytics(Plugin_base):
	def initialize(self, one):
		# logging.info("Initialized most_recent %s %s" % (self, one))
		template = self.get_template()
		return True
		
	def render(self):		
		return {'google_analytics': self.render_template()}
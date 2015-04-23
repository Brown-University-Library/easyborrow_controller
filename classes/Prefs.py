"""
General prefs.
"""

import os


class Prefs:



	db_host = ''
	db_port = ''
	db_username = ''
	db_password = ''
	patron_id = ''

	debug = "on"

	LOG_URL = ''
	LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = ''
	LOG_KEY = ''




	# purpose: to keep sensitve data out of repository and to minimize its transfer
	def __init__(self):
		self.db_host = unicode( os.environ[u'ezbCTL__DB_HOST'] )
		self.db_port = int( unicode(os.environ[u'ezbCTL__DB_PORT']) )
		self.db_username = unicode( os.environ[u'ezbCTL__DB_USERNAME'] )
		self.db_password = unicode( os.environ[u'ezbCTL__DB_PASSWORD'] )
		self.patron_id = unicode( os.environ[u'ezbCTL__PATRON_ID'] )
		self.LOG_URL = unicode( os.environ[u'ezbCTL__LOG_URL'] )
		self.LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = unicode( os.environ[u'ezbCTL__LOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] )
		self.LOG_KEY = unicode( os.environ[u'ezbCTL__LOG_KEY'] )



# bottom

# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
- Settings file for easyBorrow controller code.
- Some other code still directly accesses env var settings.
"""

import os


## general settings
LOG_URL = unicode( os.environ['ezbCTL__WEBLOG_URL'] )  # url used to web-log various parts of easyBorrow apps
LOG_KEY = unicode( os.environ['ezbCTL__WEBLOG_KEY'] )
LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = unicode( os.environ['ezbCTL__WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] ) # 'debug', etc.
OLD_WEBLOG_LEVEL = unicode( os.environ['ezbCTL__LOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] ) # 'low' or 'high'

MAIL_APPARENT_SENDER = unicode( os.environ['ezbCTL__MAIL_APPARENT_SENDER'] )  # this will appear as the sender to the end-user
MAIL_SENDER = unicode( os.environ['ezbCTL__MAIL_SENDER'] )  # true sender; won't appear to the end-user
MAIL_SMTP_SERVER = unicode( os.environ['ezbCTL__MAIL_SMTP_SERVER'] )
PATRON_API_URL_ROOT = unicode( os.environ['ezbCTL__PATRON_API_URL_ROOT'] )


## db
DB_HOST = unicode( os.environ[u'ezbCTL__DB_HOST'] )
DB_PORT = int( unicode(os.environ[u'ezbCTL__DB_PORT']) )
DB_USERNAME = unicode( os.environ[u'ezbCTL__DB_USERNAME'] )
DB_PASSWORD = unicode( os.environ[u'ezbCTL__DB_PASSWORD'] )


## borrowdirect web-service settings
## most bd-api settings have been replaced by env var settings accessed by classes.tunneler_runners.BD_ApiRunner() -- TODO, eventually move those here
OPENURL_PARSER_URL = unicode( os.environ['ezbCTL__OPENURL_PARSER_URL'] )


## illiad settings
ILLIAD_API_URL = unicode( os.environ['ezbCTL__ILLIAD_API_URL'] )
ILLIAD_API_KEY = unicode( os.environ['ezbCTL__ILLIAD_API_KEY'] )


## tests -- TODO

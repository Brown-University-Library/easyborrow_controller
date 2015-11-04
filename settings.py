# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
- Settings file for project.
- Part of python easyBorrow controller code.
- Note: existing Prefs.py file/class and PrivatePrefs.py file/class will be moved here.
"""

import os
# from easyborrow_project_local_settings.eb_controller_local_settings import settings_local  # TODO: remove this once all settings are loaded from env vars


## general settings
LOG_URL = unicode( os.environ['ezbCTL__WEBLOG_URL'] )  # url used to web-log various parts of easyBorrow apps
LOG_KEY = unicode( os.environ['ezbCTL__WEBLOG_KEY'] )
LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = unicode( os.environ['ezbCTL__WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] ) # 'debug', etc.
MAIL_APPARENT_SENDER = unicode( os.environ['ezbCTL__MAIL_APPARENT_SENDER'] )  # this will appear as the sender to the end-user
MAIL_SENDER = unicode( os.environ['ezbCTL__MAIL_SENDER'] )  # true sender; won't appear to the end-user
MAIL_SMTP_SERVER = unicode( os.environ['ezbCTL__MAIL_SMTP_SERVER'] )

PATRON_API_URL_ROOT = unicode( os.environ['ezbCTL__PATRON_API_URL_ROOT'] )


## borrowdirect web-service settings
## most bd-api settings have been replaced by env var settings accessed by classes.tunneler_runners.BD_ApiRunner() -- TODO, eventually move those here
OPENURL_PARSER_URL = unicode( os.environ['ezbCTL__OPENURL_PARSER_URL'] )


## illiad settings
ILLIAD_API_URL = unicode( os.environ['ezbCTL__ILLIAD_API_URL'] )
ILLIAD_API_KEY = unicode( os.environ['ezbCTL__ILLIAD_API_KEY'] )


## tests -- TODO

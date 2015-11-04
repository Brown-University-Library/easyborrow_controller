# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
- Settings file for project.
- Part of python easyBorrow controller code.
- Note: existing Prefs.py file/class and PrivatePrefs.py file/class will be moved here.
"""

import os
from easyborrow_project_local_settings.eb_controller_local_settings import settings_local  # TODO: remove this once all settings are loaded from env vars


## general settings
LOG_URL = unicode( os.environ['ezbCTL__WEBLOG_URL'] )  # url used to web-log various parts of easyBorrow apps
LOG_KEY = unicode( os.environ['ezbCTL__WEBLOG_KEY'] )
LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = unicode( os.environ['ezbCTL__WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] ) # 'debug', etc.
MAIL_APPARENT_SENDER = unicode( os.environ['ezbCTL__MAIL_APPARENT_SENDER'] )  # this will appear as the sender to the end-user
MAIL_SENDER = unicode( os.environ['ezbCTL__MAIL_SENDER'] )  # true sender; won't appear to the end-user
MAIL_SMTP_SERVER = unicode( os.environ['ezbCTL__MAIL_SMTP_SERVER'] )


## borrowdirect web-service settings
## most bd-api settings have been replaced by env var settings accessed by classes.tunneler_runners.BD_ApiRunner() -- TODO, eventually move those here
OPENURL_PARSER_URL = unicode( os.environ['ezbCTL__OPENURL_PARSER_URL'] )


## illiad settings
# ILLIAD_HTTP_S_SEGMENT = settings_local.ILLIAD_HTTP_S_SEGMENT  # u-string; u'http' or u'https'
# ILLIAD_TEMP_STORAGE_URL = settings_local.ILLIAD_TEMP_STORAGE_URL  # string; url used only for testing
# ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY = settings_local.ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY  # string; key used only for testing
# ILLIAD_REMOTEAUTH_KEY = settings_local.ILLIAD_REMOTEAUTH_KEY  # u-string; key for illiad-remote-authentication
# ILLIAD_REQUEST_URL = settings_local.ILLIAD_REQUEST_URL  # string
# ILLIAD_REQUEST_AUTHORIZATION_KEY = settings_local.ILLIAD_REQUEST_AUTHORIZATION_KEY  # string
# ILLIAD_NEWUSER_WEBSERVICE_URL = settings_local.ILLIAD_NEWUSER_WEBSERVICE_URL  # string
#
ILLIAD_API_URL = unicode( os.environ['ezbCTL__ILLIAD_API_URL'] )
ILLIAD_API_KEY = unicode( os.environ['ezbCTL__ILLIAD_API_KEY'] )


## tests

TEST_ILLIAD_REMOTEAUTH_BLOCKED_USERNAME = settings_local.TEST_ILLIAD_REMOTEAUTH_BLOCKED_USERNAME  # u-string; blocked illiad user
TEST_ILLIAD_REMOTEAUTH_LOGIN_USERNAME = settings_local.TEST_ILLIAD_REMOTEAUTH_LOGIN_USERNAME  # u-string; existing illiad user
TEST_ILLIAD_REMOTEAUTH_RAW_WORLDCAT_OPENURL = settings_local.TEST_ILLIAD_REMOTEAUTH_RAW_WORLDCAT_OPENURL  # u-string for worldcat openurl

TEST_PATRON_01_ID = settings_local.TEST_PATRON_01_ID
TEST_PATRON_01_CONVERTED_EMAIL = settings_local.TEST_PATRON_01_CONVERTED_EMAIL

TEST_PATRON_02_ID = settings_local.TEST_PATRON_02_ID
TEST_PATRON_02_CONVERTED_EMAIL = settings_local.TEST_PATRON_02_CONVERTED_EMAIL
TEST_PATRON_02_CONVERTED_STATUS = settings_local.TEST_PATRON_02_CONVERTED_STATUS

TEST_PATRON_03_ID = settings_local.TEST_PATRON_03_ID

TEST_PATRON_04_ID = settings_local.TEST_PATRON_04_ID
TEST_PATRON_04_CONVERTED_PATRNNAME = settings_local.TEST_PATRON_04_CONVERTED_PATRNNAME
TEST_PATRON_04_CONVERTED_ADDRESS = settings_local.TEST_PATRON_04_CONVERTED_ADDRESS
TEST_PATRON_04_CONVERTED_PHONE = settings_local.TEST_PATRON_04_CONVERTED_PHONE
TEST_PATRON_04_CONVERTED_DEPARTMENT = settings_local.TEST_PATRON_04_CONVERTED_DEPARTMENT

TEST_PATRON_05_ID = settings_local.TEST_PATRON_05_ID
TEST_PATRON_05_CONVERTED_PHONE = settings_local.TEST_PATRON_05_CONVERTED_PHONE

PATRON_API_URL_ROOT = settings_local.PATRON_API_URL_ROOT

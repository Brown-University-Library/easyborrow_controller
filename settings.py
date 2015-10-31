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
LOG_URL = os.environ['ezbCTL__WEBLOG_URL']  # url used to web-log various parts of easyBorrow apps
LOG_KEY = os.environ['ezbCTL__WEBLOG_KEY']
LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = os.environ['ezbCTL__WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] # 'low' for dev, 'high' for production
MAIL_APPARENT_SENDER = settings_local.MAIL_APPARENT_SENDER  # string; this will appear as the sender to the end-user
MAIL_SENDER = settings_local.MAIL_SENDER  # string; this won't appear as the sender to the end-user
MAIL_SMTP_SERVER = settings_local.MAIL_SMTP_SERVER  # string


## inrhode tunneler settings
INRHODE_TUNNELER_ENCLOSING_DIRECTORY_PATH = settings_local.INRHODE_TUNNELER_ENCLOSING_DIRECTORY_PATH  # string


## borrowdirect web-service settings
BD_API_URL = settings_local.BD_API_URL
BD_API_AUTHORIZATION_CODE = settings_local.BD_API_AUTHORIZATION_CODE
BD_API_IDENTITY = settings_local.BD_API_IDENTITY
BD_UNIVERSITY = settings_local.BD_UNIVERSITY
OPENURL_PARSER_URL = settings_local.OPENURL_PARSER_URL


## illiad settings
# ILLIAD_HANDLER_SWITCH = settings_local.ILLIAD_HANDLER_SWITCH  # string; to switch between new django-handler and old java-handler
ILLIAD_HTTP_S_SEGMENT = settings_local.ILLIAD_HTTP_S_SEGMENT  # u-string; u'http' or u'https'
ILLIAD_TEMP_STORAGE_URL = settings_local.ILLIAD_TEMP_STORAGE_URL  # string; url used only for testing
ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY = settings_local.ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY  # string; key used only for testing
ILLIAD_REMOTEAUTH_KEY = settings_local.ILLIAD_REMOTEAUTH_KEY  # u-string; key for illiad-remote-authentication
# ILLIAD_REMOTEAUTH_SWITCH = settings_local.ILLIAD_REMOTEAUTH_SWITCH  # u-string; temporary while new code-flow being implemented; options: u'old_code' or u'new_code'
ILLIAD_REQUEST_URL = settings_local.ILLIAD_REQUEST_URL  # string
ILLIAD_REQUEST_AUTHORIZATION_KEY = settings_local.ILLIAD_REQUEST_AUTHORIZATION_KEY  # string
ILLIAD_NEWUSER_WEBSERVICE_URL = settings_local.ILLIAD_NEWUSER_WEBSERVICE_URL  # string
#
ILLIAD_API_URL = os.environ['ezbCTL__ILLIAD_API_URL']
ILLIAD_API_KEY = os.environ['ezbCTL__ILLIAD_API_KEY']


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

import os


## file-log settings
LOG_PATH = os.environ['ezbCTL__LOG_PATH']
LOG_LEVEL = os.environ['ezbCTL__LOG_LEVEL']


## web-log settings
WEBLOG_URL = os.environ['ezbCTL__WEBLOG_URL']  # url used to web-log various parts of easyBorrow apps
WEBLOG_KEY = os.environ['ezbCTL__WEBLOG_KEY']
# WEBLOG_LEVEL = os.environ['ezbCTL__WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] # 'debug', etc.
WEBLOG_LEVEL = os.environ['ezbCTL__WEBLOG_LEVEL']  # 'debug', etc.


## email
MAIL_APPARENT_SENDER = os.environ['ezbCTL__MAIL_APPARENT_SENDER']  # this will appear as the sender to the end-user
MAIL_SENDER = os.environ['ezbCTL__MAIL_SENDER']  # true sender; won't appear to the end-user
MAIL_SMTP_SERVER = os.environ['ezbCTL__MAIL_SMTP_SERVER']
ADMIN_EMAIL = os.environ[u'ezbCTL__ADMIN_EMAIL']  # listed in classes.UtilityCode.UtilitCode() -- TODO, see if it's really being used
CIRC_ADMIN_EMAIL = os.environ[u'ezbCTL__CIRC_ADMIN_EMAIL']  # listed in classes.UtilityCode.UtilitCode() -- TODO, see if it's really being used


## general settings
PATRON_API_CONVERTER_URL = os.environ['ezbCTL__PATRON_API_CONVERTER_URL']  # used by classes.Item.Item() -- TODO, see if this url is really active and used


## db
DB_HOST = os.environ[u'ezbCTL__DB_HOST']
DB_PORT = int( os.environ[u'ezbCTL__DB_PORT'] )
DB_USERNAME = os.environ[u'ezbCTL__DB_USERNAME']
DB_PASSWORD = os.environ[u'ezbCTL__DB_PASSWORD']
DB_NAME = os.environ[u'ezbCTL__DB_NAME']


## sql patterns (IDs inserted for full queries)
CONTROLLER_SELECT_SQL = os.environ[u'ezbCTL__SELECT_SQL']  # used by controller
HISTORY_REFERENCENUMBER_SQL = os.environ[u'ezbCTL__INSERT_HISTORY_REFERENCENUM_SQL_PATTERN']  # used by classes.Item.Item()
HISTORY_ACTION_SQL = os.environ[u'ezbCTL__INSERT_HISTORY_FULLACTION_SQL_PATTERN']  # used by classes.Item.Item(), classes.tunneler_runners.BD_ApiRunner()
HISTORY_NOTE_SQL = os.environ[u'ezbCTL__INSERT_HISTORY_NOTE_SQL_PATTERN']  # used by classes.Item.Item()
REQUEST_UPDATE_SQL = os.environ[u'ezbCTL__UPDATE_REQUEST_STATUS_SQL_PATTERN']  # used by classes.Item.Item()


## borrowdirect web-service settings
## most bd-api settings have been replaced by env var settings accessed by classes.tunneler_runners.BD_ApiRunner() -- TODO, eventually move those here
BDPYWEB_URL = os.environ['ezbCTL__BDPYWEB_URL']
BDPYWEB_BIB_URL = os.environ['ezbCTL__BDPYWEB_BIB_URL']
BDPYWEB_AUTHORIZATION_CODE = os.environ['ezbCTL__BDPYWEB_AUTHORIZATION_CODE']
BDPYWEB_IDENTITY = os.environ['ezbCTL__BDPYWEB_IDENTITY']
OPENURL_PARSER_URL = os.environ['ezbCTL__OPENURL_PARSER_URL']


## illiad settings
ILLIAD_API_URL = os.environ['ezbCTL__ILLIAD_API_URL']
ILLIAD_API_KEY = os.environ['ezbCTL__ILLIAD_API_KEY']

ILLIAD_API_USER_AGENT = os.environ['ezbCTL__ILLIAD_API_USER_AGENT']

ILLIAD_USER_API_URL_ROOT = os.environ['ezbCTL__ILLIAD_USER_API_URL_ROOT']
ILLIAD_USER_API_BASIC_AUTH_USER = os.environ['ezbCTL__ILLIAD_USER_API_BASIC_AUTH_USER']
ILLIAD_USER_API_BASIC_AUTH_PASSWORD = os.environ['ezbCTL__ILLIAD_USER_API_BASIC_AUTH_PASSWORD']



## tests
TEST_PATRON_ID = os.environ['ezbCTL_TEST__PATRON_ID']

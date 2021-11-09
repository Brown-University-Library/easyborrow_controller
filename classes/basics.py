import logging
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.web_logger import WebLogger


## file and web-loggers
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)
web_logger = WebLogger( logger )


class Request_Meta:
    """ Holds non-patron, non-item info about the request. """

    def __init__( self ):
        self.request_number = ''  # the easyBorrow db-id
        self.datetime = None
        self.current_service = ''
        self.current_status = ''
        self.confirmation_code = ''

    # end class Request_Meta


class Patron:
    """ Holds patron info. """

    def __init__( self ):
        self.firstname = ''
        self.lastname = ''
        self.eppn = ''  # really just the username part
        self.barcode = ''
        self.email = ''

    # end class Patron


class Item:
    """ Holds item info. """

    def __init__( self ):
        self.title = ''
        self.isbn = ''
        self.oclc_num = ''
        self.volumes_info = ''
        self.knowledgebase_openurl = ''

    # end class Item

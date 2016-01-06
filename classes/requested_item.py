# -*- coding: utf-8 -*-

from __future__ import unicode_literals
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


class EB_Request:

    def __init__( self ):
        self.patron = None
        self.item = None
        self.request_ezb_reference_number = ''  # the easyBorrow id
        self.request_current_tunneler_service = ''
        self.request_current_tunneler_status = ''

    # end class EB_Request


class Patron:

    def __init__( self ):
        self.name_first = None

    # end class Patron


class Item:

    def __init__( self ):
        self.title = None

    # end class Item

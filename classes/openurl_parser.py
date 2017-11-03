# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from easyborrow_controller_code import settings


## file and web-loggers
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)


class OpenUrlParser:
    """ Parses openurls. """

    def __init__( self ):
        pass

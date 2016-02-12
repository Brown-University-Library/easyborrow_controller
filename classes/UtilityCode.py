# # -*- coding: utf-8 -*-

# from __future__ import unicode_literals

# import logging, os, smtplib, sys, time, urllib, urllib2
# # import MySQLdb
# from easyborrow_controller_code import settings
# from easyborrow_controller_code.classes.web_logger import WebLogger


# ## file and web-loggers
# LOG_PATH = settings.LOG_PATH
# LOG_LEVEL = settings.LOG_LEVEL
# level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
# logging.basicConfig(
#     filename=LOG_PATH, level=level_dct[LOG_LEVEL],
#     format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
# logger = logging.getLogger(__name__)
# web_logger = WebLogger( logger )


# class UtilityCode( object ):


#   def __init__( self, logger ):
#     self.timeToFormat = ""
#     self.log = ""
#     self.log_identifier = ''  # set by controller.run_code()
#     self.logger = logger  # set by Controller() or Item()


# # bottom

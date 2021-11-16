import datetime, json, logging, os, pprint, random

import requests
from easyborrow_controller_code import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # to address ```InsecureRequestWarning: Unverified HTTPS request is being made...```


## file and web-loggers
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


class IlliadUserManager( object ):
    """ Contains helpers for delivery.views.process_request()
        TODO, move article-requet checks to here, too. """

    def __init__(self):
        pass

    def manage_illiad_user_check( self, usr_dct ):
        """ Manager for illiad handling. NOTE -- this doc-string was copied from easyAccess; TODO- update it.
            - hits the new illiad-api for the status (`blocked`, `registered`, etc)
                # - if problem, prepares failure message as-is (creating return-dct)
                - if new-user, runs manage_new_user() and creates proper success or failure return-dct
                # - if neither problem or new-user, TODO -- incorporate the new update-status api call here
            Called by delivery.views.process_request()...
              # ...which, on any failure, will store the returned crafted error message to the session,
              # ...and redirect to an error page. """
        # log.debug( '(common_classes) - usr_dct, ```%s```' % pprint.pformat(usr_dct) )
        return_dct = { 'success': False }  ## added so that logging works
        log.debug( 'usr_dct, ``%s``' % pprint.pformat(usr_dct) )
        illiad_status_dct = self.check_illiad_status( usr_dct['eppn'].split('@')[0] )
        log.debug( 'illiad_status_dct, ``%s``' % illiad_status_dct )
        if illiad_status_dct['response']['status_data']['blocked'] is True or illiad_status_dct['response']['status_data']['disavowed'] is True:
            # return_dct = self.make_illiad_problem_message( usr_dct, title )
            log.warning( 'blocked or disavowed status detected' )
            ## NOTE: 2021-November-16...
            ##       I _think_ this situation is handled later in the Controller, when the actual ILLiad request is made, and the response is evaluated.
            ##       In other words, I don't believe the actual return success-status is used. Check the logs.
        elif illiad_status_dct['response']['status_data']['interpreted_new_user'] is True:
            return_dct = self.manage_new_user( usr_dct )
        else:
            return_dct = { 'success': True }
        log.debug( 'return_dct, ```%s```' % pprint.pformat(return_dct) )
        return return_dct

    # def manage_illiad_user_check( self, usr_dct ):
    #     """ Manager for illiad handling.
    #         - hits the new illiad-api for the status (`blocked`, `registered`, etc)
    #             # - if problem, prepares failure message as-is (creating return-dct)
    #             - if new-user, runs manage_new_user() and creates proper success or failure return-dct
    #             # - if neither problem or new-user, TODO -- incorporate the new update-status api call here
    #         Called by delivery.views.process_request()...
    #           # ...which, on any failure, will store the returned crafted error message to the session,
    #           # ...and redirect to an error page. """
    #     # log.debug( '(common_classes) - usr_dct, ```%s```' % pprint.pformat(usr_dct) )
    #     log.debug( 'usr_dct, ``%s``' % pprint.pformat(usr_dct) )
    #     illiad_status_dct = self.check_illiad_status( usr_dct['eppn'].split('@')[0] )
    #     log.debug( 'illiad_status_dct, ``%s``' % illiad_status_dct )
    #     if illiad_status_dct['response']['status_data']['blocked'] is True or illiad_status_dct['response']['status_data']['disavowed'] is True:
    #         # return_dct = self.make_illiad_problem_message( usr_dct, title )
    #         log.warning( 'blocked or disavowed status detected' )
    #     elif illiad_status_dct['response']['status_data']['interpreted_new_user'] is True:
    #         return_dct = self.manage_new_user( usr_dct )
    #     else:
    #         return_dct = { 'success': True }
    #     log.debug( 'return_dct, ```%s```' % pprint.pformat(return_dct) )
    #     return return_dct

    def check_illiad_status( self, auth_id ):
        """ Hits our internal illiad-api for user's status (`blocked`, `registered`, etc).
            Called by manage_illiad_user_check() """
        rspns_dct = { 'response':
            {'status_data': {'blocked': None, 'disavowed': None}} }
        url = '%s%s' % ( settings.ILLIAD_USER_API_URL_ROOT, 'check_user/' )
        params = { 'user': auth_id }
        try:
            header_dct = { 'user-agent': settings.ILLIAD_API_USER_AGENT }
            r = requests.get( url, params=params, auth=(settings.ILLIAD_USER_API_BASIC_AUTH_USER, settings.ILLIAD_USER_API_BASIC_AUTH_PASSWORD), headers=header_dct, verify=True, timeout=10 )
            # rspns_dct = r.json()
            rspns_dct = json.loads( r.content )
            log.debug( 'status_code, `%s`; content-dct, ```%s```' % (r.status_code, pprint.pformat(rspns_dct)) )
        except Exception as e:
            log.exception( 'problem with user-check; traceback follows; processing continues' )
            log.error( 'error on status check, ```%s```' % repr(e) )
        return rspns_dct

    def manage_new_user( self, usr_dct ):
        """ Manages new-user creation and response-assessment.
            Called by manage_illiad_user_check() """
        success_check = self.create_new_user( usr_dct )
        if not success_check == True:
            log.warning( '(common_classes) - problem creating new user' )
            # return_dct = self.make_illiad_unregistered_message( usr_dct, title )
        else:
            return_dct = { 'success': True }
        log.debug( 'return_dct, ```%s```' % pprint.pformat(return_dct) )
        return return_dct

    def create_new_user( self, usr_dct ):
        """ Hits internal api to create new user.
            Called by manage_new_user() """
        ( params, success_check, url ) = self.setup_create_user( usr_dct )
        try:
            r = requests.post( url, data=params, verify=True, timeout=10 )
            log.debug( 'status_code, `%s`; content, ```%s```' % (r.status_code, r.content.decode('utf-8', 'replace')) )
            # result = r.json()['response']['status_data']['status'].lower()
            result_dct = json.loads( r.content )
            result = result_dct['response']['status_data']['status'].lower()
            if result == 'registered':
                success_check = True
        except Exception as e:
            # log.error( 'Exception on new user registration, ```%s```' % unicode(repr(e)) )  # success_check already initialized to False
            log.exception( '(common classes) - exception on new user registration; traceback follows, but processing will continue' )  # success_check already initialized to False
        log.debug( 'success_check, `%s`' % success_check )
        return success_check

    def setup_create_user( self, usr_dct ):
        """ Initializes vars.
            Called by create_new_user() """
        params = {
            'auth_key': settings.ILLIAD_API_KEY,
            'auth_id': usr_dct['eppn'].split('@')[0],
            'first_name': usr_dct['name_first'],
            'last_name': usr_dct['name_last'],
            'email': usr_dct['email'],
            'status': usr_dct['brown_type'],
            'phone': usr_dct['phone'],
            'department': usr_dct['department'] }
        success_check = False
        url = '%s%s' % ( settings.ILLIAD_USER_API_URL_ROOT, 'create_user/' )
        log.debug( 'params, ```%s```; success_check, `%s`; url, ```%s```' % (pprint.pformat(params), success_check, url) )
        return ( params, success_check, url )

    def check_illiad_type( self, usr_dct ):
        """ Hits api to update patron-type if needed ('Undergrad', 'Staff', etc).
            Called by delivery.views.process_request() """
        username = usr_dct['eppn'].split('@')[0]
        brown_type = usr_dct['brown_type']
        log.debug( 'username, `%s`; brown_type, `%s`' % (username, brown_type) )
        url = '%s%s' % ( settings.ILLIAD_USER_API_URL_ROOT, 'update_status/' )
        params = { 'auth_key': settings.ILLIAD_API_KEY, 'user':username, 'requested_status': brown_type }
        try:
            r = requests.post( url, data=params, verify=True, timeout=10 )
            log.debug( 'status_code, `%s`; content, ```%s```' % (r.status_code, r.content.decode('utf-8', 'replace')) )
        except Exception as e:
            log.error( 'error on user-type check/update, ```%s```' % repr(e) )
        return

    ## end class IlliadHelper()

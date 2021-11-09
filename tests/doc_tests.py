import os, sys

## add enclosing directory to path
current_script_name = sys.argv[0]  # may or may not include path
directory_path = os.path.dirname( current_script_name )
full_directory_path = os.path.abspath( directory_path )
directory_list = full_directory_path.split('/')
target_element_string = directory_list[-3]  # the hardcoded piece for this known hierarchy
enclosing_directory_path = ''
for entry in directory_list:
    enclosing_directory_path = enclosing_directory_path + entry + '/'
    if entry == target_element_string:
        break
sys.path.append( enclosing_directory_path )


class UtilityCodeDocTests:

    def test_createIlliadUser_badCredentials():
        '''

        # steps: create & save credentials, create eb_request object, call function

        # imports
        >>> from easyborrow_controller_code import settings, utility_code
        >>> import random
        >>> import urllib, urllib2

        # make identifier (would be the easyborrow request number)
        >>> request_id = 'dev_%s' % random.randint(1111, 9999)
        >>> log_identifier = request_id

        # store credentials (currently really done in handler.php)
        >>> url =  settings.ILLIAD_TEMP_STORAGE_URL
        >>> parameter_dict = {
        ...   'request_id': request_id,
        ...   'username': 'aaa',
        ...   'password': 'bbb',
        ...   'authorization_key': settings.ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY,
        ...   }
        >>> parameter_string = urllib.urlencode( parameter_dict )
        >>> request_object = urllib2.Request( url, parameter_string )
        >>> response_object = urllib2.urlopen( request_object )
        >>> json_dict = json.loads( response_object.read() )

        # >>> json_dict
        # {u'status': u'success', u'request_id': u'dev_3189'}

        >>> json_dict['status']
        u'success'

        # create eb_request instance
        >>> eb_request = utility_code.EB_Request()
        >>> eb_request.patron_firstname = 'firstname'
        >>> eb_request.patron_lastname = 'lastname'
        >>> eb_request.patron_email = 'email'
        >>> eb_request.patron_phone = 'phone'
        >>> eb_request.patron_address = 'address'
        >>> eb_request.patron_status = 'student'
        >>> eb_request.patron_department = 'department'

        # call function
        >>> utility_code.createIlliadUser( eb_request, log_identifier )
        {u'status': u'failure', u'message': '{"status": "failure", "message": "checkLoginResult message: invalid_login"}'}
        '''
        ## end def test_createIlliadUser_badCredentials()

    def test_submitIlliadRequest_invalidLogin():
        '''

        # test submits bad credentials to illiad web-service

        >>> from easyborrow_controller_code import settings, utility_code
        >>> import random
        >>> import urllib, urllib2
        >>> log_identifier = 'dev_%s' % random.randint(1111, 9999)
        >>> request_id = 'dev_%s' % random.randint(1111, 9999)

        # store credentials temporarily (done in handler.php)
        >>> url =  settings.ILLIAD_TEMP_STORAGE_URL
        >>> parameter_dict = {
        ...   'request_id': request_id,
        ...   'username': 'aaa',
        ...   'password': 'bbb',
        ...   'authorization_key': settings.ILLIAD_TEMP_STORAGE_AUTHORIZATION_KEY,
        ...   }
        >>> parameter_string = urllib.urlencode( parameter_dict )
        >>> request_object = urllib2.Request( url, parameter_string )
        >>> response_object = urllib2.urlopen( request_object )
        >>> json_dict = json.loads( response_object.read() )
        >>> json_dict['status']
        u'success'

        # submit request
        >>> parameter_dict = {
        ...  'auth_key': settings.ILLIAD_REQUEST_AUTHORIZATION_KEY,
        ...  'request_id': request_id,
        ...  'first_name': 'test_first',
        ...  'last_name': 'test_last',
        ...  'address': '',  # perceived but not handled by dj_ill_submission
        ...  'oclc_number': 'test_oclc',
        ...  'openurl': 'sid%3DFirstSearch%253AWorldCat%26genre%3Dbook%26isbn%3D9780892817641%26title%3DThe%2Bheart%2Bof%2Byoga%2B%253A%2Bdeveloping%2Ba%2Bpersonal%2Bpractice%26date%3D1999%26aulast%3DDesikachar%26aufirst%3DT%26auinitm%3DK%26id%3Ddoi%253A%26pid%3D%253Caccession%2Bnumber%253E41384634%253C%252Faccession%2Bnumber%253E%253Cfssessid%253E0%253C%252Ffssessid%253E%253Cedition%253ERev.%2Bed.%253C%252Fedition%253E%26url_ver%3DZ39.88-2004%26rfr_id%3Dinfo%253Asid%252Ffirstsearch.oclc.org%253AWorldCat%26rft_val_fmt%3Dinfo%253Aofi%252Ffmt%253Akev%253Amtx%253Abook%26req_dat%3D%253Csessionid%253E0%253C%252Fsessionid%253E%26rfe_dat%3D%253Caccessionnumber%253E41384634%253C%252Faccessionnumber%253E%26rft_id%3Dinfo%253Aoclcnum%252F41384634%26rft_id%3Durn%253AISBN%253A9780892817641%26rft.aulast%3DDesikachar%26rft.aufirst%3DT%26rft.auinitm%3DK%26rft.btitle%3DThe%2Bheart%2Bof%2Byoga%2B%253A%2Bdeveloping%2Ba%2Bpersonal%2Bpractice%26rft.date%3D1999%26rft.isbn%3D9780892817641%26rft.place%3DRochester%2B%2BVt.%26rft.pub%3DInner%2BTraditions%2BInternational%26rft.edition%3DRev.%2Bed.%26rft.genre%3Dbook',
        ...  'patron_email': '',  # not yet perceived by dj_ill_submission
        ...  'patron_status': '',  # perceived but not handled by dj_ill_submission
        ...  'phone': '',  # perceived but not handled by dj_ill_submission
        ...  'volumes': '',  # perceived but not handled by dj_ill_submission
        ...  }
        >>> json_string = utility_code.submitIlliadRequest( parameter_dict, log_identifier )
        >>> print json_string  # should fail on bad login, given supplied username & password, but this shows submission
        {u'status': u'invalid_login'}
        '''
        ## end def test_submitIlliadRequest()

    ## end class UtilityCodeDocTests


if __name__ == "__main__":
    import doctest
    doctest.testmod()

# -*- coding: utf-8 -*-

import random, unittest


class UtilityCodeFileTests(unittest.TestCase):

  ## test_makeOpenUrlSegment()

  def test_makeOpenUrlSegment_commonCase(self):
    initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9780135320693&title=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&date=1980&aulast=Polsky&aufirst=Milton&auinitm=E&id=doi%3A&pid=%3Caccession+number%3E5992453%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E5992453%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F5992453&rft_id=urn%3AISBN%3A9780135320693&rft.aulast=Polsky&rft.aufirst=Milton&rft.auinitm=E&rft.btitle=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&rft.date=1980&rft.isbn=9780135320693&rft.place=Englewood+Cliffs++N.J.&rft.pub=Prentice-Hall&rft.genre=book'
    log_identifier = 'dev_%s' % random.randint(1111, 9999)
    result_dict = utility_code.makeOpenUrlSegment( initial_url, log_identifier )
    assert result_dict == { "openurl_segment": "sid=FirstSearch%3AWorldCat&genre=book&isbn=9780135320693&title=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&date=1980&aulast=Polsky&aufirst=Milton&auinitm=E&id=doi%3A&pid=%3Caccession+number%3E5992453%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E5992453%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F5992453&rft_id=urn%3AISBN%3A9780135320693&rft.aulast=Polsky&rft.aufirst=Milton&rft.auinitm=E&rft.btitle=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&rft.date=1980&rft.isbn=9780135320693&rft.place=Englewood+Cliffs++N.J.&rft.pub=Prentice-Hall&rft.genre=book" }, result_dict

  def test_makeOpenUrlSegment_unusualOpenurlFormat(self):
    initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?genre=book&date=1990&title=Joan+Snyder&sid=oup%3Aoao&sid=easyarticle'
    log_identifier = 'dev_%s' % random.randint(1111, 9999)
    result_dict = utility_code.makeOpenUrlSegment( initial_url, log_identifier )
    assert result_dict == { "openurl_segment": "genre=book&date=1990&title=Joan+Snyder&sid=oup%3Aoao&sid=easyarticle" }, result_dict

  def test_makeOpenUrlSegment_genreUnknown(self):
    initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9780135320693&title=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&date=1980&aulast=Polsky&aufirst=Milton&auinitm=E&id=doi%3A&pid=%3Caccession+number%3E5992453%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E5992453%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F5992453&rft_id=urn%3AISBN%3A9780135320693&rft.aulast=Polsky&rft.aufirst=Milton&rft.auinitm=E&rft.btitle=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&rft.date=1980&rft.isbn=9780135320693&rft.place=Englewood+Cliffs++N.J.&rft.pub=Prentice-Hall&rft.genre=unknown'
    log_identifier = 'dev_%s' % random.randint(1111, 9999)
    result_dict = utility_code.makeOpenUrlSegment( initial_url, log_identifier )
    assert result_dict == { "openurl_segment": "sid=FirstSearch%3AWorldCat&genre=book&isbn=9780135320693&title=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&date=1980&aulast=Polsky&aufirst=Milton&auinitm=E&id=doi%3A&pid=%3Caccession+number%3E5992453%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E5992453%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F5992453&rft_id=urn%3AISBN%3A9780135320693&rft.aulast=Polsky&rft.aufirst=Milton&rft.auinitm=E&rft.btitle=Let%27s+improvise+%3A+becoming+creative%2C+expressive+%26+spontaneous+through+drama&rft.date=1980&rft.isbn=9780135320693&rft.place=Englewood+Cliffs++N.J.&rft.pub=Prentice-Hall&rft.genre=book" }, result_dict


  ## test_submitIlliadRemoteAuthRequest()

  ## WARNING: MAKE SURE TEST USER IS REALLY BLOCKED
  # def test_submitIlliadRemoteAuthRequest_blocked( self):
  #   import json, pprint
  #   import requests
  #   url = u'%s://127.0.0.1/easyborrow/ill/v2/make_request/' % settings.ILLIAD_HTTP_S_SEGMENT
  #   parameters = {
  #     u'auth_key': settings.ILLIAD_REMOTEAUTH_KEY,
  #     u'username': settings.TEST_ILLIAD_REMOTEAUTH_BLOCKED_USERNAME,
  #     u'first_name': u'test_firstname',
  #     u'last_name': u'test_lastname',
  #     u'phone': u'test_phone',
  #     u'address': u'test_address',
  #     u'email': u'',
  #     u'patron_status': u'test_patron_status',
  #     u'oclc_number': u'226308091',  # czech zen book, http://www.worldcat.org/oclc/25990799
  #     u'openurl': settings.TEST_ILLIAD_REMOTEAUTH_RAW_WORLDCAT_OPENURL,  # unicode from utf-8 string like: 'sid=...'.decode(u'utf-8')
  #     u'volumes': u'abc',
  #     u'request_id': u'TEST_%s' % random.randint(100,999)  # the easyborrow request #
  #     }
  #   headers = { u'Content-Type': u'application/x-www-form-urlencoded; charset=utf-8' }
  #   r = requests.post( url, data=parameters, headers=headers, timeout=10, verify=False )
  #   # print u'-r.text...'; pprint.pprint( r.text )
  #   jdict = json.loads( r.text )
  #   assert sorted( jdict.keys() ) == [u'status'], sorted( jdict.keys() )
  #   assert jdict[u'status'] == u'login_failed_possibly_blocked', jdict[u'status']
  #   # end def test_submitIlliadRemoteAuthRequest_blocked()


  # ## WARNING: REALLY SUBMITS A REQUEST FOR THE TEST_LOGIN_USERNAME
  # def test_submitIlliadRemoteAuthRequest_good( self):
  #   import json, pprint
  #   import requests
  #   url = u'%s://127.0.0.1/easyborrow/ill/v2/make_request/' % settings.ILLIAD_HTTP_S_SEGMENT
  #   parameters = {
  #     u'auth_key': settings.ILLIAD_REMOTEAUTH_KEY,
  #     u'username': settings.TEST_ILLIAD_REMOTEAUTH_LOGIN_USERNAME,
  #     u'first_name': u'test_firstname',
  #     u'last_name': u'test_lastname',
  #     u'phone': u'test_phone',
  #     u'address': u'test_address',
  #     u'email': u'',
  #     u'patron_status': u'test_patron_status',
  #     u'oclc_number': u'226308091',  # czech zen book, http://www.worldcat.org/oclc/25990799
  #     u'openurl': settings.TEST_ILLIAD_REMOTEAUTH_RAW_WORLDCAT_OPENURL,  # unicode from utf-8 string like: 'sid=...'.decode(u'utf-8')
  #     u'volumes': u'abc',
  #     u'request_id': u'TEST_%s' % random.randint(100,999)  # the easyborrow request #
  #     }
  #   headers = { u'Content-Type': u'application/x-www-form-urlencoded; charset=utf-8' }
  #   r = requests.post( url, data=parameters, headers=headers, timeout=10, verify=False )
  #   # print u'-r.text...'; pprint.pprint( r.text )
  #   jdict = json.loads( r.text )
  #   assert sorted( jdict.keys() ) == [u'status', u'transaction_number'], sorted( jdict.keys() )
  #   assert jdict[u'status'] == u'submission_successful', jdict[u'status']
  #   # end def test_submitIlliadRemoteAuthRequest_good()


  ## WARNING: REALLY SUBMITS A REQUEST FOR THE KNOWN_NEW_USERNAME
  # def test_submitIlliadRemoteAuthRequest_goodNewUser( self):
  #   import json, pprint
  #   import requests
  #   url = u'%s://127.0.0.1/easyborrow/ill/v2/make_request/' % settings.ILLIAD_HTTP_S_SEGMENT
  #   KNOWN_NEW_USERNAME = u'btst0001'
  #   parameters = {
  #     u'auth_key': settings.ILLIAD_REMOTEAUTH_KEY,
  #     u'username': KNOWN_NEW_USERNAME,
  #     u'first_name': u'test_firstname',
  #     u'last_name': u'test_lastname',
  #     u'phone': u'test_phone',
  #     u'address': u'test_address',
  #     u'email': u'TODO: add test env-var',
  #     u'patron_status': u'test_patron_status',
  #     u'oclc_number': u'226308091',  # czech zen book, http://www.worldcat.org/oclc/25990799
  #     u'openurl': settings.TEST_ILLIAD_REMOTEAUTH_RAW_WORLDCAT_OPENURL,  # unicode from utf-8 string like: 'sid=...'.decode(u'utf-8')
  #     u'volumes': u'abc',
  #     u'request_id': u'TEST_%s' % random.randint(100,999)  # the easyborrow request #
  #     }
  #   headers = { u'Content-Type': u'application/x-www-form-urlencoded; charset=utf-8' }
  #   r = requests.post( url, data=parameters, headers=headers, timeout=10, verify=False )
  #   # print u'-r.text...'; pprint.pprint( r.text )
  #   jdict = json.loads( r.text )
  #   assert sorted( jdict.keys() ) == [u'status', u'transaction_number'], sorted( jdict.keys() )
  #   assert jdict[u'status'] == u'submission_successful', jdict[u'status']
  #   # end def test_submitIlliadRemoteAuthRequest_goodNewUser()


  # end class UtilityCodeFileTests



if __name__ == "__main__":
  import os, sys, unittest
  ## get the project's enclosing directory for import references
  current_script_name = sys.argv[0] # may or may not include path
  directory_path = os.path.dirname( current_script_name )
  full_directory_path = os.path.abspath( directory_path )
  directory_list = full_directory_path.split('/')
  last_element_string = directory_list[-2] + '/' + directory_list[-1]
  enclosing_directory = full_directory_path.replace( '/' + last_element_string, '' ) # strip off the slash plus the current directory
  # print u'- enclosing_directory...'; print enclosing_directory
  sys.path.append( enclosing_directory )
  ## ok, rest of imports
  from easyborrow_controller_code import settings, utility_code
  ## gogogo
  unittest.main()

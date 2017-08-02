# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, unittest
from easyborrow_controller_code.classes.tunneler_runners import BD_ApiRunner, IlliadApiRunner


# class BDRunnerTest(unittest.TestCase):

#   def setUp(self):
#     uc_instance = UtilityCode.UtilityCode()
#     self.prep = {
#       'EB_REQUEST_NUM': 'unit_test_%s' % datetime.datetime.now(),
#       'API_URL': 'init',
#       'API_AUTH_CODE': 'init',
#       'API_IDENTITY': 'init',
#       'UNIVERSITY': 'init',
#       'USER_BARCODE': 'init',
#       'ISBN': 'init',
#       'WC_URL': 'init',
#       'OPENURL_PARSER_URL': 'init',
#       'UC_INSTANCE': uc_instance,
#       }

#   def test_init(self):
#     ## all good unicode
#     prep = self.prep
#     bd = BD_Runner( prep )
#     self.assertEqual( bd.API_AUTH_CODE, 'init' )
#     ## oops, a string
#     prep['API_AUTH_CODE'] = 'str'
#     try:
#       bd = BD_Runner( prep )
#     except Exception, e:
#       self.assertEqual( repr(e), "AssertionError(Exception('API_AUTH_CODE must be unicode',),)" )  # unicode(e) doesn't work

#   def test_determineSearchType(self):
#     prep = self.prep
#     ## string search
#     prep['ISBN'] = ''
#     bd = BD_Runner( prep )
#     bd.determineSearchType()
#     assert bd.search_type == 'string', bd.search_type
#     ## isbn search
#     prep['ISBN'] = 'abc'
#     bd = BD_Runner( prep )
#     bd.determineSearchType()
#     assert bd.search_type == 'isbn', bd.search_type

#   def test_makeSearchString_WcUrlComplete(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://landing_page/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9780688002305&title=Zen+and+the+art+of+motorcycle+maintenance%3A+an+inquiry+into+values%2C&date=1974&aulast=Pirsig&aufirst=Robert&auinitm=M&id=doi%3A&pid=%3Caccession+number%3E673595%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E673595%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F673595&rft_id=urn%3AISBN%3A9780688002305&rft.aulast=Pirsig&rft.aufirst=Robert&rft.auinitm=M&rft.btitle=Zen+and+the+art+of+motorcycle+maintenance%3A+an+inquiry+into+values%2C&rft.date=1974&rft.isbn=9780688002305&rft.place=New+York&rft.pub=Morrow&rft.genre=book&checksum=808d331299c7cb13bc0e9179eb80ced5'
#     bd = BD_Runner( prep )
#     assert bd.string_good_to_go == None, bd.string_good_to_go
#     bd.makeSearchString()
#     d = json.loads( bd.worldcat_url_parsed_response )
#     assert sorted(d.keys()) == ['doc_url', 'request', 'response'], sorted(d.keys())
#     assert sorted(d['request'].keys()) == ['db_wc_url', 'time'], sorted(d['request'].keys())  # 'db_wc_url' means 'the worldcat url in the database'
#     assert sorted(d['response'].keys()) == ['bd_author', 'bd_date', 'bd_title', 'time_taken'], sorted(d['response'].keys())
#     assert bd.string_good_to_go == True, bd.string_good_to_go
#     assert bd.string_title == 'zen and the art of motorcycle maintenance an inquiry into values', bd.string_title
#     assert bd.string_author == 'pirsig robert m', bd.string_author
#     assert bd.string_date == '1974', bd.string_date

#   def test_makeSearchString_WcUrlComplete_sSolutionsUrl(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://rl3tp7zf5x.search.serialssolutions.com/?rft.pub=The+Modern+library&rft_val_fmt=info%3Aofi/fmt%3Akev%3Amtx%3Abook&rfr_id=info%3Asid/info%3Asid/firstsearch.oclc.org%3AWorldCat&rft.au=Lawrence%2C+D&rft.place=New+York&rft_id=http%3A//www.worldcat.org/oclc/190929&rft.date=1943&rft.btitle=The+rainbow&ctx_ver=Z39.88-2004&rft.genre=book'
#     bd = BD_Runner( prep )
#     assert bd.string_good_to_go == None, bd.string_good_to_go
#     bd.makeSearchString()
#     d = json.loads( bd.worldcat_url_parsed_response )
#     assert sorted(d.keys()) == ['doc_url', 'request', 'response'], sorted(d.keys())
#     assert sorted(d['request'].keys()) == ['db_wc_url', 'time'], sorted(d['request'].keys())  # 'db_wc_url' means 'the worldcat url in the database'
#     assert sorted(d['response'].keys()) == ['bd_author', 'bd_date', 'bd_title', 'time_taken'], sorted(d['response'].keys())
#     assert bd.string_good_to_go == True, bd.string_good_to_go
#     assert bd.string_title == 'the rainbow', bd.string_title
#     assert bd.string_author == 'lawrence d', bd.string_author
#     assert bd.string_date == '1943', bd.string_date

#   def test_makeSearchString_WcUrlCompleteUnicode(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://landing_page/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9788373015364&title=Zen+i+sztuka+obs%C5%82ugi+motocykla+%3A+rozprawa+o+wartos%CC%81ciach&date=2010&aulast=Pirsig&aufirst=Robert&auinitm=M&id=doi%3A&pid=%3Caccession+number%3E751241832%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E%3Cedition%3EWyd.+3+popr.+i+uzup.+%28dodr.%29.%3C%2Fedition%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E751241832%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F751241832&rft_id=urn%3AISBN%3A9788373015364&rft.aulast=Pirsig&rft.aufirst=Robert&rft.auinitm=M&rft.btitle=Zen+i+sztuka+obs%C5%82ugi+motocykla+%3A+rozprawa+o+wartos%CC%81ciach&rft.date=2010&rft.isbn=9788373015364&rft.place=Poznan%CC%81&rft.pub=Dom+Wydawniczy+%22Rebis%22&rft.edition=Wyd.+3+popr.+i+uzup.+%28dodr.%29.&rft.genre=book&checksum=6630a2eec9ef8606be1eebb5a833dc96&title=Brown University&linktype=openurl&detail=RBN'
#     bd = BD_Runner( prep )
#     assert bd.string_good_to_go == None, bd.string_good_to_go
#     bd.makeSearchString()
#     d = json.loads( bd.worldcat_url_parsed_response )
#     assert sorted(d.keys()) == ['doc_url', 'request', 'response'], sorted(d.keys())
#     assert sorted(d['request'].keys()) == ['db_wc_url', 'time'], sorted(d['request'].keys())  # 'db_wc_url' means 'the worldcat url in the database'
#     assert sorted(d['response'].keys()) == ['bd_author', 'bd_date', 'bd_title', 'time_taken'], sorted(d['response'].keys())
#     assert bd.string_good_to_go == True, bd.string_good_to_go
#     assert bd.string_title == 'zen i sztuka obs\xe5ugi motocykla rozprawa o wartos\xecciach', bd.string_title
#     assert bd.string_author == 'pirsig robert m', bd.string_author
#     assert bd.string_date == '2010', bd.string_date

#   def test_makeSearchString_WcUrlNoAuthor(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://landing_page/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9780945612315&title=Pillars+of+salt+%3A+an+anthology+of+early+American+criminal+narratives&date=1993&id=doi%3A&pid=%3Caccession+number%3E26261487%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E%3Cedition%3E1st+ed.%3C%2Fedition%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E26261487%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F26261487&rft_id=urn%3AISBN%3A9780945612315&rft.btitle=Pillars+of+salt+%3A+an+anthology+of+early+American+criminal+narratives&rft.date=1993&rft.isbn=9780945612315&rft.place=Madison++Wis.&rft.pub=Madison+House&rft.edition=1st+ed.&rft.genre=book&checksum=1298deb7cd90f280b1b2092d4de3878a&title=Brown University&linktype=openurl&detail=RBN'
#     bd = BD_Runner( prep )
#     assert bd.string_good_to_go == None, bd.string_good_to_go
#     bd.makeSearchString()
#     assert bd.string_good_to_go == False, bd.string_good_to_go

#   def test_prepRequestData_WcUrlComplete(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://landing_page/?sid=FirstSearch%3AWorldCat&genre=book&title=The+rainbow&date=1943&aulast=Lawrence&aufirst=D&auinitm=H&id=doi%3A&pid=%3Caccession+number%3E190929%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E190929%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F190929&rft.aulast=Lawrence&rft.aufirst=D&rft.auinitm=H&rft.btitle=The+rainbow&rft.date=1943&rft.place=New+York&rft.pub=The+Modern+library&rft.genre=book&checksum=489a99eea1a541da55943b8a6d7c7bdd&title=Brown University&linktype=openurl&detail=RBN'
#     bd = BD_Runner( prep )
#     bd.search_type = 'string'
#     bd.prepRequestData()
#     assert type(bd.prepared_data_dict) == dict, type(bd.prepared_data_dict)
#     d = bd.prepared_data_dict
#     assert sorted(d.keys()) == ['api_authorization_code', 'api_identity', 'author', 'command', 'date', 'title', 'university', 'user_barcode'], sorted(d.keys())

#   def test_prepRequestData_WcUrlNoAuthor(self):
#     prep = self.prep
#     prep['OPENURL_PARSER_URL'] = controller_settings.OPENURL_PARSER_URL
#     prep['WC_URL'] = 'http://landing_page/?sid=FirstSearch%3AWorldCat&genre=book&isbn=9780945612315&title=Pillars+of+salt+%3A+an+anthology+of+early+American+criminal+narratives&date=1993&id=doi%3A&pid=%3Caccession+number%3E26261487%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E%3Cedition%3E1st+ed.%3C%2Fedition%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E26261487%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F26261487&rft_id=urn%3AISBN%3A9780945612315&rft.btitle=Pillars+of+salt+%3A+an+anthology+of+early+American+criminal+narratives&rft.date=1993&rft.isbn=9780945612315&rft.place=Madison++Wis.&rft.pub=Madison+House&rft.edition=1st+ed.&rft.genre=book&checksum=1298deb7cd90f280b1b2092d4de3878a&title=Brown University&linktype=openurl&detail=RBN'
#     bd = BD_Runner( prep )
#     bd.search_type = 'string'
#     bd.prepRequestData()
#     assert bd.prepared_data_dict == 'skip_to_illiad', bd.prepared_data_dict

#   def test_updateHistoryTable_noRequest( self ):
#     prep = self.prep
#     prep['EB_REQUEST_NUM'] = '123'
#     bd = BD_Runner( prep )
#     assert bd.history_table_updated == None, bd.history_table_updated
#     bd.prepared_data_dict = 'skip_to_illiad'
#     bd.updateHistoryTable()
#     assert bd.history_table_message == 'no_valid_string', bd.history_table_message
#     assert bd.history_table_updated == True, bd.history_table_updated

#   def test_updateHistoryTable_unsuccessfulRequest( self ):
#     prep = self.prep
#     prep['EB_REQUEST_NUM'] = '123'
#     prep['API_URL'] = controller_settings.BD_API_URL
#     bd = BD_Runner( prep )
#     assert bd.history_table_updated == None, bd.history_table_updated
#     bd.prepared_data_dict = {
#       'api_authorization_code': controller_settings.BD_API_AUTHORIZATION_CODE,
#       'api_identity': controller_settings.BD_API_IDENTITY,
#       'command': 'request',
#       'isbn': '9788373015364',  # polish ZMM, http://worldcat.org/oclc/751241832
#       'university': controller_settings.BD_UNIVERSITY,
#       'user_barcode': controller_settings.TEST_LEGIT_BARCODE,
#       }
#     bd.requestItem()
#     ## test: request made & unsuccessful
#     d = json.loads( bd.api_response )
#     assert d.keys() == ['info', 'request', 'response'], d.keys()
#     assert d['response']['search_result'] == 'FAILURE', d['response']['search_result']
#     ## test: history table updated
#     bd.updateHistoryTable()
#     assert bd.history_table_message == 'not_found', bd.history_table_message
#     assert bd.history_table_updated == True, bd.history_table_updated

#   def test_requestItem_isbnShouldNotBeRequestable( self ):
#     prep = self.prep
#     prep['EB_REQUEST_NUM'] = '123'
#     prep['API_URL'] = controller_settings.BD_API_URL
#     bd = BD_Runner( prep )
#     bd.prepared_data_dict = {
#       'api_authorization_code': controller_settings.BD_API_AUTHORIZATION_CODE,
#       'api_identity': controller_settings.BD_API_IDENTITY,
#       'command': 'request',
#       'isbn': '9788373015364',  # polish ZMM, http://worldcat.org/oclc/751241832
#       'university': controller_settings.BD_UNIVERSITY,
#       'user_barcode': controller_settings.TEST_LEGIT_BARCODE,
#       }
#     assert bd.api_response == None, bd.api_response
#     bd.requestItem()
#     d = json.loads( bd.api_response )
#     assert d.keys() == ['info', 'request', 'response'], d.keys()
#     assert sorted(d['response'].keys()) == ['bd_confirmation_code', 'end_time', 'found', 'requestable', 'search_result'], sorted(d['response'].keys())
#     assert d['response']['search_result'] == 'FAILURE', d['response']['search_result']

#   def test_requestItem_stringShouldNotBeRequestable( self ):
#     prep = self.prep
#     prep['EB_REQUEST_NUM'] = '123'
#     prep['API_URL'] = controller_settings.BD_API_URL
#     bd = BD_Runner( prep )
#     bd.prepared_data_dict = {
#       'api_authorization_code': controller_settings.BD_API_AUTHORIZATION_CODE,
#       'api_identity': controller_settings.BD_API_IDENTITY,
#       'command': 'request',
#       'title': 'zen i sztuka obs\xe5ugi motocykla rozprawa o wartos\xecciach',  # polish ZMM, http://worldcat.org/oclc/751241832
#       'author': 'pirsig robert m',
#       'date': '2010',
#       'university': controller_settings.BD_UNIVERSITY,
#       'user_barcode': controller_settings.TEST_LEGIT_BARCODE,
#       }
#     assert bd.api_response == None, bd.api_response
#     bd.requestItem()
#     d = json.loads( bd.api_response )
#     assert d.keys() == ['info', 'request', 'response'], d.keys()
#     assert sorted(d['response'].keys()) == ['bd_confirmation_code', 'end_time', 'found', 'requestable', 'search_result'], sorted(d['response'].keys())
#     assert d['response']['search_result'] == 'FAILURE', d['response']['search_result']


class BDRunnerTest(unittest.TestCase):

    def setUp(self):
        self.bd_runner = BD_ApiRunner()
        pass

    def tearDown(self):
        pass

    def test_prepare_params(self):
        patron_inst = 'x'
        item_inst = 'y'
        self.assertEqual( 'bar', self.bd_runner.prepare_params(patron_inst, item_inst) )

    ## end class BDRunnerTest()


class IlliadApiRunnerTest(unittest.TestCase):

    def setUp(self):
        self.illiad_runner = IlliadApiRunner()
        pass

    def tearDown(self):
        pass

    def test_make_openurl_segment(self):
        initial_url = 'foo'
        self.assertEqual( 'bar', self.illiad_runner._make_openurl_segment(initial_url) )

    ## end class IlliadApiRunnerTest()


def suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(BDRunnerTest) )
    suite.addTest( unittest.makeSuite(IlliadApiRunnerTest) )
    return suite


if __name__ == '__main__':
    unittest.main()

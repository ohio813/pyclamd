import unittest
import pyclamd

# http://docs.python.org/2.7/library/unittest.html
# http://docs.python-guide.org/en/latest/writing/tests/
# http://www.voidspace.org.uk/python/mock/
class Test_pyclamd(unittest.TestCase):
    """
    Test suite for pyclamd
    """

    def setUp(self):
        """
        Set Up prior to testing
        """
        self.clamd = pyclamd.ClamdNetworkSocket()
        return

    def tearDown(self):
        """
        Cleanup, post test
        """
        return


    def test_scan_stream_unicode_test_eicar_alone(self):
        file_data = open('eicar.com', 'rb').read()
        v = self.clamd.scan_stream(file_data)
        self.assertEqual(v, {'stream': ('FOUND', 'Eicar-Test-Signature')})
        return

    def test_scan_stream_unicode_test_eicar_in_pdf(self):
        file_data = open('probleme_data.pdf', 'rb').read()
        v = self.clamd.scan_stream(file_data)
        self.assertEqual(v, None)
        return


    def test_scan_stream_unicode_test_clean(self):
        file_data = open('probleme_data_clean.pdf', 'rb').read()
        v = self.clamd.scan_stream(file_data)
        self.assertEqual(v, None)
        return


    def test_scan_file_unicode_test_eicar_in_pdf(self):
        v = self.clamd.scan_file('/home/xael/ESPACE_KM/python/pyclamd/probleme_data.pdf')
        #self.assertEqual(v, {u'stream': ('FOUND', 'Eicar-Test-Signature')})
        self.assertEqual(v, None)
        return


    def test_scan_file_unicode_test_eicar_alone(self):
        v = self.clamd.scan_file('/home/xael/ESPACE_KM/python/pyclamd/eicar.com')
        self.assertEqual(v, {'/home/xael/ESPACE_KM/python/pyclamd/eicar.com': ('FOUND', 'Eicar-Test-Signature')})
        return



def main():
    unittest.main()

if __name__ == '__main__':
    main()

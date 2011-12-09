import unittest

from page_template import PageTemplate

class PageTemplateTestCase(unittest.TestCase):
   def testPage(self):
      with open('test/p0.xml') as p:
         t = PageTemplate(p.read())
      d = {'__path__' : 'test/p0.xml', 'a' : '123','b':'456'}
      self.assertEquals(t(d), u'AAATOP456:PBOT')
      
if __name__ == '__main__':
   unittest.main()


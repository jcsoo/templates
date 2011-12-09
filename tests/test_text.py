import unittest

from text_template import TextTemplate

class TextTemplateTestCase(unittest.TestCase):
   def testText(self):
      d = {'a' : 'a', 'b' : 123, 'c' : u'345'}
      t = TextTemplate(u'a: {a} b: {b} c: {c}')
      v = t(d)
      self.assertEquals(v,u'a: a b: 123 c: 345')     

if __name__ == '__main__':
   unittest.main()


import unittest
import template

class TemplateTestCase(unittest.TestCase):
   def testLoadFile(self):
      t = template.load_file('test/t1.xml')
      self.assertEquals(t.root.tag,'div')

   def testLoadString(self):
      t = template.load_string('<div>Testing</div>')
      self.assertEquals(t.root.tag,'div')

   def testEvaluate(self):
      t = template.load_file('test/t2.xml')
      t.evaluate({'test' : 'abc'})


if __name__ == '__main__':
   unittest.main()

import unittest
from path import evaluate_path, PathEvaluator, ParseException

tree = {
   'a' : 123,
   'b' : ['x','y','z'],
   'c' : {'h' : 11, 'i' : 12, 'j' : 13,
          'k' : {'aa' : 55, 'bb' : 66},          
          },
   'key' : 'i',
   'key2' : 'k',
   'key3' : 'c',
   'index' : 1
   }

class PathEvaluatorTestCase(unittest.TestCase):
   def ep(self, path, data=None):
      if data is None:
         data = tree
      return evaluate_path(path, data)

   def testSimple(self):
      self.assertEquals(self.ep('a'),123)
      self.assertEquals(self.ep('b'),tree['b'])
      self.assertEquals(self.ep('c.h'),11)
      self.assertEquals(self.ep('c.k.aa'),55)
      self.assertEquals(self.ep('b.1'),'y')
      self.assertEquals(self.ep('b.-1'),'z')
      
   def testParse(self):
      pe = PathEvaluator('abc.def.ghi')
      self.assertEquals(pe.steps,['abc','def','ghi'])

      pe = PathEvaluator('abc.{def}.ghi')
      self.assertEquals(pe.steps[0],'abc')
      self.assertEquals(pe.steps[1].path,'def')
      self.assertEquals(pe.steps[2],'ghi')
      self.assertRaises(ParseException,PathEvaluator,'abc.{def}.{ghi')

   def testNested(self):
      self.assertEquals(self.ep('c.{key}'),12)
      self.assertEquals(self.ep('c.{key2}.bb'),66)
      self.assertEquals(self.ep('b.{index}'),'y')
      self.assertEquals(self.ep('{key3}.{key2}.bb'),66)

if __name__ == '__main__':
   unittest.main()

import unittest
from template.context import Context

class ContextTestCase(unittest.TestCase):
   def setUp(self):
      self.c = Context({})

   def testPush(self):
      d = {'test' : 'abc'}
      self.c.push(d)
      self.assertEquals(len(self.c.stack),2)
      v = self.c.pop()
      self.assertEquals(d,v)
      self.assertEquals(len(self.c.stack),1)

      #self.c.push([('a',123),('b',456)])
      #self.assertEquals(self.c['a'],123)
      #self.assertEquals(self.c['b'],456)
      
   def testSet(self):
      self.c['a'] = 123
      top = self.c.stack[-1]
      self.assertEquals(top['a'],123)
      self.assertEquals(self.c['a'],123)

   def testSetGet(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.assertEquals(self.c['b'],456)
      self.assertEquals(self.c['a'],123)
      self.assertEquals(self.c.get('c',-1),-1)
      self.c.pop()
      self.assertEquals(self.c['a'],123)
      self.assertEquals(self.c.get('b',-1),-1)
      self.assertEquals(len(self.c.stack),1)

   def testKeyError(self):
      self.assertRaises(KeyError,self.c.__getitem__,'x')

   def testUpdate(self):
      d = {'a' : 123,'b' : 456}
      self.c.update(d)
      self.assertEquals(self.c['a'],123)
      self.assertEquals(self.c['b'],456)

   def testLen(self):
      self.assertEquals(len(self.c),1)
      self.c.push({})
      self.assertEquals(len(self.c),2)
      self.c.pop()
      self.assertEquals(len(self.c),1)

   def testHasKey(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.assertEquals(self.c.has_key('a'),True)
      self.assertEquals(self.c.has_key('b'),True)
      self.c.pop()
      self.assertEquals(self.c.has_key('a'),True)
      self.assertEquals(self.c.has_key('b'),False)

      self.assertEquals('a' in self.c,True)
      self.assertEquals('b' in self.c,False)

   def testDel(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      del self.c['b']
      del self.c['a']
      self.assertEquals(self.c.has_key('b'),False)
      self.assertEquals(self.c.get('b',None),None)
      self.assertRaises(KeyError,self.c.__getitem__,'b')
      self.assertEquals(self.c.has_key('a'),False)
      self.assertEquals(self.c.get('a',None),None)
      self.assertRaises(KeyError,self.c.__getitem__,'a')
      self.c.pop()
      self.assertEquals(self.c['a'],123)

   def testClear(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.c.clear()
      self.assertEquals(len(self.c),1)

   def testItems(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.c['c'] = 789
      items = self.c.items()
      items.sort()
      self.assertEquals(items[0],('a',123))
      self.assertEquals(items[1],('b',456))
      self.assertEquals(items[2],('c',789))
      keys = self.c.keys()
      keys.sort()
      self.assertEquals(keys,['a','b','c'])
      values = self.c.values()
      values.sort()
      self.assertEquals(values,[123,456,789])
      del self.c['a']
      items = self.c.items()
      items.sort()
      self.assertEquals(items[0],('b',456))
      self.assertEquals(items[1],('c',789))

   def testIter(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.c['c'] = 789
      keys = []
      for k in self.c:
         keys.append(k)
      keys.sort()
      self.assertEquals(keys,['a','b','c'])
         
   def xtestCopy(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['b'] = 456
      self.c['c'] = 789

      copy = self.c.copy()
      copy['c'] = 999
      self.assertEquals(copy['a'],123)
      self.assertEquals(copy['b'],456)
      self.assertEquals(self.c['c'],789)
      
   def testUnSet(self):
      self.c['a'] = 123
      self.c.push({})
      self.c['a'] = 456
      self.c.unset('a')
      self.assertEquals(self.c['a'],123)
      del self.c['a']
      self.assertEquals('a' in self.c, False)
      self.c.unset('a')
      self.assertEquals('a' in self.c, True)

if __name__ == '__main__':
   unittest.main()

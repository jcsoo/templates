import unittest

from itemplate import Template, parse_string

class ITemplateTestCase(unittest.TestCase):
   def testText(self):
      d = {'a' : 'a', 'b' : 123, 'c' : u'345'}
      t = parse_string(u'<b>Testing {b}</b>')
      v = t(d)
      self.assertEquals(v,u'<b>Testing 123</b>')


   def testEntities(self):
      d = {'a' : 'a', 'b' : 123, 'c' : u'345'}
      t = parse_string('<b>&copy; &raquo;</b>')
      v = t(d)
      self.assertEquals(v,u'<b>\xa9 \xbb</b>')

   def testIF(self):
      d = {'t' : True, 'f' : False, 'one' : 1, 'zero' : 0, 'empty' : '', 'emptydict' : {}, 'none' : None}
      t = parse_string(u'<if key="t">TRUE</if>')
      self.assertEquals(t(d),u'TRUE')

      t = parse_string(u'<if key="one">TRUE</if>')
      self.assertEquals(t(d),u'TRUE')

      t = parse_string(u'<if key="empty">TRUE</if>')
      self.assertEquals(t(d),u'')

      t = parse_string(u'<if key="emptydict">TRUE</if>')
      self.assertEquals(t(d),u'')

      t = parse_string(u'<if key="none">TRUE</if>')
      self.assertEquals(t(d),u'')


      t = parse_string(u'<ifnot key="t"></ifnot>')
      self.assertEquals(t(d),u'')

      t = parse_string(u'<if key="t">TRUE<else/>FALSE</if>')
      self.assertEquals(t(d),u'TRUE')
      
   def testLoop(self):
      d = {'a': [{'n' : 1}, {'n' : 2}, {'n' : 3}]}
      t = parse_string(u'<loop key="a">{n}</loop>')
      self.assertEquals(t(d),u'123')

      t = parse_string(u'<loop key="a"><separator>,</separator>{n}</loop>')
      self.assertEquals(t(d),u'1,2,3')

      d = {'a' : [1,2,3]}
      t = parse_string(u'<loop key="a">{_}</loop>')
      self.assertEquals(t(d),u'123')

   def testWith(self):
      d = {'w' : {'a' : 'abc', 'b' : 'def'}}
      t = parse_string(u'<with key="w">{a}{b}</with>')
      self.assertEquals(t(d),u'abcdef')

   def testPaginate(self):
      d = {'a': [{'n' : 1}, {'n' : 2}, {'n' : 3}, {'n' : 4}, {'n' : 5}, {'n' : 6}]}
      t = parse_string(u'<paginate key="a" page="1" page_size="2"><loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'12')
      t = parse_string(u'<paginate key="a" page="2" page_size="2"><loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'34')
      t = parse_string(u'<paginate key="a" page="2" page_size="2">{_page_number} of {_page_count}: <loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'2 of 3: 34')

   def testGroup(self):
      d = {'a': [{'n' : 1,'g' : 'a'}, {'n' : 2, 'g' : 'a'}, {'n' : 3, 'g' : 'b'}, {'n' : 4,'g' : 'b'}, {'n' : 5, 'g' : 'c'}, {'n' : 6,'g' : 'c'}]}
      t = parse_string(u'<group key="a" label="Group {g}:" value="{g}"><loop key="_groups">{_label}<loop key="_records">{n}</loop></loop></group>')
      self.assertEquals(t(d),u'Group a:12Group b:34Group c:56')

   def testInclude(self):
      #d = {'t' : u'<i>include {a}</i>', 'a' : '123'}
      #t = parse_string(u'<include key="t"/>')
      #self.assertEquals(t(d),'<i>include 123</i>')

      d = {'a' : '123'}
      t = parse_string(u'<include path="test/i1.xml"/>')
      self.assertEquals(t(d),'<i>include 123</i>')

      d = {'a' : '123'}
      t = parse_string(u'<include path="test/i2.xml"/>')
      self.assertEquals(t(d),'<i>include <i>include 3 123</i> <i>include 3 123</i> 123</i>')

   def testHTML(self):
      d = {'a' : '123', 'b' : '2&3', 'c' : True,'d' : False, 'e' : ['a','b','c']}
      self.assertEquals(parse_string(u'<input type="text" name="a"/>')(d),'<input type="text" name="a" value="123">')
      self.assertEquals(parse_string(u'<input type="password" name="a"/>')(d),'<input type="password" name="a" value="123">')
      self.assertEquals(parse_string(u'<input type="hidden" name="a"/>')(d),'<input type="hidden" name="a" value="123">')

      self.assertEquals(parse_string(u'<input type="text" name="b"/>')(d),'<input type="text" name="b" value="2&amp;3">')
      self.assertEquals(parse_string(u'<input type="button" name="b" value="Button"/>')(d),'<input type="button" name="b" value="Button">')
      self.assertEquals(parse_string(u'<input type="submit" name="b" value="Button"/>')(d),'<input type="submit" name="b" value="Button">')
      self.assertEquals(parse_string(u'<input type="reset" name="b" value="Button"/>')(d),'<input type="reset" name="b" value="Button">')
      self.assertEquals(parse_string(u'<input type="file" name="b" value="Button"/>')(d),'<input type="file" name="b" value="Button">')

      self.assertEquals(parse_string(u'<textarea name="a"/>')(d),'<textarea name="a">123</textarea>')

      self.assertEquals(parse_string(u'<input type="checkbox" name="c" value="yes"/>')(d),u'<input type="checkbox" name="c" value="yes" checked="checked">')
      self.assertEquals(parse_string(u'<input type="radio" name="c" value="yes"/>')(d),u'<input type="radio" name="c" value="yes" checked="checked">')

      self.assertEquals(parse_string(u'<input type="checkbox" name="e" value="a"/>')(d),u'<input type="checkbox" name="e" value="a" checked="checked">')
      self.assertEquals(parse_string(u'<input type="checkbox" name="e" value="b"/>')(d),u'<input type="checkbox" name="e" value="b" checked="checked">')
      self.assertEquals(parse_string(u'<input type="checkbox" name="e" value="d"/>')(d),u'<input type="checkbox" name="e" value="d">')

      self.assertEquals(parse_string(u'<select name="a"><option></option><option value="123">OneTwoThree</option><option>123</option></select>')(d),u'<select name="a"><option></option><option value="123" selected="selected">OneTwoThree</option><option selected="selected">123</option></select>')

   def testGet(self):
      d = {}
      self.assertEquals(parse_string(u'<get path="test/i1.xml"/>')(d),'<i>include {a}</i>')

   def testFill(self):
      return
      d = {'a' : '123', 'b' : '2&3', 'c' : True,'d' : False, 'e' : ['a','b','c']}
      self.assertEquals(parse_string(u'<fill filter="uc">aBcdef</fill>')(d),'ABCDEF')
      self.assertEquals(parse_string(u'<fill filter="uc|lc">aBcdef</fill>')(d),'abcdef')
      self.assertEquals(parse_string(u'<fill filter="p">aBcdef</fill>')(d),'<p>aBcdef</p>')

   def testFilters(self):
      return
      def rev(f_arr, v, mapping):         
         return unicode(v)[::-1]
      class Testparse_string(parse_string):
         custom_filters = {'rev' : rev}
      d = {'a' : 'abc'}
      self.assertEquals(Testparse_string(u'<div>{a|rev}</div>')(d),'<div>cba</div>')

   def testSubclass(self):
      return
      class Testparse_string(parse_string):
         def _test(self, elt):
            self.write(u'<TEST>')
            self.evaluate_children(elt)
            self.write(u'</TEST>')
      self.assertEquals(Testparse_string(u'<test>abc</test>')({}),'<TEST>abc</TEST>')

if __name__ == '__main__':
   unittest.main()


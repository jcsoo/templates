import unittest

from html_template import HTMLTemplate

class HTMLTemplateTestCase(unittest.TestCase):
   def testText(self):
      d = {'a' : 'a', 'b' : 123, 'c' : u'345'}
      t = HTMLTemplate(u'<b>Testing {b}</b>')
      v = t(d)
      self.assertEquals(v,u'<b>Testing 123</b>')


   def testEntities(self):
      d = {'a' : 'a', 'b' : 123, 'c' : u'345'}
      t = HTMLTemplate(u'<b>&copy; &raquo;</b>')
      v = t(d)
      self.assertEquals(v,u'<b>\xa9 \xbb</b>')

   def testIF(self):
      d = {'t' : True, 'f' : False, 'one' : 1, 'zero' : 0, 'empty' : '', 'emptydict' : {}, 'none' : None}
      t = HTMLTemplate(u'<if key="t">TRUE</if>')
      self.assertEquals(t(d),u'TRUE')

      t = HTMLTemplate(u'<if key="one">TRUE</if>')
      self.assertEquals(t(d),u'TRUE')

      t = HTMLTemplate(u'<if key="empty">TRUE</if>')
      self.assertEquals(t(d),u'')

      t = HTMLTemplate(u'<if key="emptydict">TRUE</if>')
      self.assertEquals(t(d),u'')

      t = HTMLTemplate(u'<if key="none">TRUE</if>')
      self.assertEquals(t(d),u'')


      t = HTMLTemplate(u'<ifnot key="t"></ifnot>')
      self.assertEquals(t(d),u'')

      t = HTMLTemplate(u'<if key="t">TRUE<else/>FALSE</if>')
      self.assertEquals(t(d),u'TRUE')
      
   def testLoop(self):
      d = {'a': [{'n' : 1}, {'n' : 2}, {'n' : 3}]}
      t = HTMLTemplate(u'<loop key="a">{n}</loop>')
      self.assertEquals(t(d),u'123')

      t = HTMLTemplate(u'<loop key="a"><separator>,</separator>{n}</loop>')
      self.assertEquals(t(d),u'1,2,3')

      d = {'a' : [1,2,3]}
      t = HTMLTemplate(u'<loop key="a">{_}</loop>')
      self.assertEquals(t(d),u'123')

   def testWith(self):
      d = {'w' : {'a' : 'abc', 'b' : 'def'}}
      t = HTMLTemplate(u'<with key="w">{a}{b}</with>')
      self.assertEquals(t(d),u'abcdef')

   def testPaginate(self):
      d = {'a': [{'n' : 1}, {'n' : 2}, {'n' : 3}, {'n' : 4}, {'n' : 5}, {'n' : 6}]}
      t = HTMLTemplate(u'<paginate key="a" page="1" page_size="2"><loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'12')
      t = HTMLTemplate(u'<paginate key="a" page="2" page_size="2"><loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'34')
      t = HTMLTemplate(u'<paginate key="a" page="2" page_size="2">{_page_number} of {_page_count}: <loop key="_records">{n}</loop></paginate>')
      self.assertEquals(t(d),u'2 of 3: 34')

   def testGroup(self):
      d = {'a': [{'n' : 1,'g' : 'a'}, {'n' : 2, 'g' : 'a'}, {'n' : 3, 'g' : 'b'}, {'n' : 4,'g' : 'b'}, {'n' : 5, 'g' : 'c'}, {'n' : 6,'g' : 'c'}]}
      t = HTMLTemplate(u'<group key="a" label="Group {g}:" value="{g}"><loop key="_groups">{_label}<loop key="_records">{n}</loop></loop></group>')
      self.assertEquals(t(d),u'Group a:12Group b:34Group c:56')

   def testInclude(self):
      d = {'t' : u'<i>include {a}</i>', 'a' : '123'}
      t = HTMLTemplate(u'<include key="t"/>')
      self.assertEquals(t(d),'<i>include 123</i>')

      d = {'a' : '123'}
      t = HTMLTemplate(u'<include path="test/i1.xml"/>')
      self.assertEquals(t(d),'<i>include 123</i>')

      d = {'a' : '123'}
      t = HTMLTemplate(u'<include path="test/i2.xml"/>')
      self.assertEquals(t(d),'<i>include <i>include 3 123</i> <i>include 3 123</i> 123</i>')

   def testHTML(self):
      d = {'a' : '123', 'b' : '2&3', 'c' : True,'d' : False, 'e' : ['a','b','c']}
      self.assertEquals(HTMLTemplate(u'<input type="text" name="a"/>')(d),'<input type="text" name="a" value="123">')
      self.assertEquals(HTMLTemplate(u'<input type="password" name="a"/>')(d),'<input type="password" name="a" value="123">')
      self.assertEquals(HTMLTemplate(u'<input type="hidden" name="a"/>')(d),'<input type="hidden" name="a" value="123">')

      self.assertEquals(HTMLTemplate(u'<input type="text" name="b"/>')(d),'<input type="text" name="b" value="2&amp;3">')
      self.assertEquals(HTMLTemplate(u'<input type="button" name="b" value="Button"/>')(d),'<input type="button" name="b" value="Button">')
      self.assertEquals(HTMLTemplate(u'<input type="submit" name="b" value="Button"/>')(d),'<input type="submit" name="b" value="Button">')
      self.assertEquals(HTMLTemplate(u'<input type="reset" name="b" value="Button"/>')(d),'<input type="reset" name="b" value="Button">')
      self.assertEquals(HTMLTemplate(u'<input type="file" name="b" value="Button"/>')(d),'<input type="file" name="b" value="Button">')

      self.assertEquals(HTMLTemplate(u'<textarea name="a"/>')(d),'<textarea name="a">123</textarea>')

      self.assertEquals(HTMLTemplate(u'<input type="checkbox" name="c" value="yes"/>')(d),u'<input checked="checked" type="checkbox" name="c" value="yes">')
      self.assertEquals(HTMLTemplate(u'<input type="radio" name="c" value="yes"/>')(d),u'<input checked="checked" type="radio" name="c" value="yes">')

      self.assertEquals(HTMLTemplate(u'<input type="checkbox" name="e" value="a"/>')(d),u'<input checked="checked" type="checkbox" name="e" value="a">')
      self.assertEquals(HTMLTemplate(u'<input type="checkbox" name="e" value="b"/>')(d),u'<input checked="checked" type="checkbox" name="e" value="b">')
      self.assertEquals(HTMLTemplate(u'<input type="checkbox" name="e" value="d"/>')(d),u'<input type="checkbox" name="e" value="d">')

      self.assertEquals(HTMLTemplate(u'<select name="a"><option></option><option value="123">OneTwoThree</option><option>123</option></select>')(d),u'<select name="a"><option></option><option selected="selected" value="123">OneTwoThree</option><option selected="selected">123</option></select>')

   def testGet(self):
      d = {}
      self.assertEquals(HTMLTemplate(u'<get path="test/i1.xml"/>')(d),'<i>include {a}</i>')

   def testFill(self):
      d = {'a' : '123', 'b' : '2&3', 'c' : True,'d' : False, 'e' : ['a','b','c']}
      self.assertEquals(HTMLTemplate(u'<fill filter="uc">aBcdef</fill>')(d),'ABCDEF')
      self.assertEquals(HTMLTemplate(u'<fill filter="uc|lc">aBcdef</fill>')(d),'abcdef')
      self.assertEquals(HTMLTemplate(u'<fill filter="p">aBcdef</fill>')(d),'<p>aBcdef</p>')

   def testFilters(self):
      def rev(f_arr, v, mapping):         
         return unicode(v)[::-1]
      class TestHTMLTemplate(HTMLTemplate):
         custom_filters = {'rev' : rev}
      d = {'a' : 'abc'}
      self.assertEquals(TestHTMLTemplate(u'<div>{a|rev}</div>')(d),'<div>cba</div>')

   def testSubclass(self):
      class TestHTMLTemplate(HTMLTemplate):
         def _test(self, elt):
            self.write(u'<TEST>')
            self.evaluate_children(elt)
            self.write(u'</TEST>')
      self.assertEquals(TestHTMLTemplate(u'<test>abc</test>')({}),'<TEST>abc</TEST>')

if __name__ == '__main__':
   unittest.main()


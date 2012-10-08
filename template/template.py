import sys, os, re
from cStringIO import StringIO
from htmlentitydefs import name2codepoint
from cgi import escape
from functools import wraps
from xml.etree.cElementTree import iterparse
from context import Context
from path import evaluate_path
from text import TextTemplate

hdefs = dict(name2codepoint)
del hdefs['amp']
del hdefs['gt']
del hdefs['lt']
del hdefs['quot']

_tags = {}
_tags_openclose = {u'br':1}

def register_tag(tag, tag_class):
   _tags[tag] = tag_class

def tag_class(tag):
   def tag_class_decorator(fn):
      @wraps(fn)
      def wrapped(*args, **kw):
         return fn(*args, **kw)
      register_tag(tag, wrapped)
      return wrapped
   return tag_class_decorator

def parse_string(s, **kw):
   return Template(StringIO(s), **kw)

def htmlentitydecode(s):
   return re.sub('&(%s);' % '|'.join(hdefs), 
                 lambda m: unichr(hdefs[m.group(1)]), s)

class NotExist(object):
   pass

class Template(object):
   def __init__(self, source, chunks=None, path='',ctx=None):
      self.ctx = ctx
      self.path = path
      if isinstance(source, basestring):
         self.path = source
      if chunks is None:
         self.chunks = {}
      else:
         self.chunks = chunks
      self.root = self.parse(self.htmldecode_source(source))

   def __call__(self, ctx=None):
      return self.render(ctx)

   def htmldecode_source(self, source):
      if isinstance(source, basestring):
         with open(source) as f:
            text = f.read()
      else:
         text = source.read()
      return StringIO(htmlentitydecode(text))

   def element(self, tag, attr, children):
      if hasattr(self, '_'+tag):
         return getattr(self,'_'+tag)(tag, attr, children)
      else:
         return _tags.get(tag,Element)(self, tag, attr, children)

   def text(self, text):
      if type(text) == unicode:
         return Text(text)
      else:
         return Text(text.decode('utf8'))

   def parse(self, source):
      stack = []
      e = None
      for event, elt in iterparse(source,events=('start','end')):
         if event == 'start':
            e = self.element(elt.tag,elt.items(),[])
            if elt.text:
               e.children.append(self.text(elt.text))
            stack.append(e)
         elif event == 'end':
            e = stack.pop()
            if stack:
               p = stack[-1].children
               p.append(e)
               if elt.tail:
                  p.append(self.text(elt.tail))
      return e

   def render(self, ctx):
      if ctx is None:
         ctx = Context()
      elif not isinstance(ctx,Context):
         ctx = Context(ctx)
      return self.root.render(ctx)

   def _include(self, tag, attr, children):
      return Template(os.path.join(os.path.dirname(self.path),dict(attr)['path']),chunks=self.chunks,ctx=self.ctx)

   def _page(self, tag, attr, children):
      a = dict(attr)
      if 'parent' in a:
         if self.ctx:
            parent = TextTemplate(unicode(a['parent']))(self.ctx)
         else:
            parent = a['parent']
         return Page(Template(os.path.join(os.path.dirname(self.path),parent),chunks=self.chunks,ctx=self.ctx))
      else:
         return Page()

   def _chunk(self, tag, attr, children):
      a = dict(attr)
      c_id = a['id']
      c = Chunk(self,c_id)
      self.chunks[c_id] = c
      return c

class Page(object):
   def __init__(self, parent=None):
      self.children = []
      self.parent = parent

   def render(self, ctx):
      if self.parent:
         return self.parent.render(ctx)
      else:
         return ''.join([c.render(ctx) for c in self.children])

class Chunk(object):
   def __init__(self, template, id):
      self.template = template
      self.id = id
      self.children = []

   def render(self, ctx):
      chunk = self.template.chunks[self.id]
      return ''.join([c.render(ctx) for c in chunk.children])

class Text(object):
   def __init__(self, text):
      self.tag = None
      self.text = TextTemplate(text)

   def render(self, ctx):
      return self.text(ctx)

class Element(object):
   def __init__(self, template, tag, attr, children):
      self.template = template
      self.tag = tag
      self.attr = dict([(k,v.decode('utf8')) for k,v in attr])
      self.text_attr = [(k,TextTemplate(v.decode('utf8'))) for k,v in attr]
      self.children = children

   def encode(self, v):
      if v is None:
         return ''
      elif isinstance(v, basestring):
         return escape(v,True)
      else:
         return escape(unicode(v),True)

   def render(self, ctx):
      if self.tag in _tags_openclose:
         return self.render_openclose(ctx)
      else:
         return self.render_open(ctx) + self.render_children(ctx) + self.render_close(ctx)

   def render_open(self, ctx):
      return '<'+self.tag+self.render_attributes(ctx)+'>'
   
   def render_close(self, ctx):
      return '</'+self.tag+'>'

   def render_openclose(self, ctx):
      return '<'+self.tag+self.render_attributes(ctx)+'/>'

   def render_attributes(self, ctx):
      return ''.join([' %s="%s"' % (k,self.encode(v(ctx))) for (k,v) in self.text_attr])

   def render_children(self, ctx, d=None):
      if d:
         ctx.push(d)
      s = u''.join([cv for cv in [c.render(ctx) for c in self.children] if cv is not None])
      if d:
         ctx.pop()
      return s

   def read(self, path, ctx):
      with open(os.path.join(os.path.dirname(self.template.path),self.fill(self.attr['path'],ctx))) as f:
         return f.read().decode('utf8')

   def get(self, path, ctx):
      return evaluate_path(path, ctx)

   def fill(self, template, ctx):
      return TextTemplate(template)(ctx)

   def value(self, ctx):
      if 'path' in self.attr:
         return self.read(self.attr['path'],ctx)
      elif 'value' in self.attr:
         return self.fill(self.attr['value'],ctx)
      elif 'key' in self.attr:
         return self.get(self.attr['key'], ctx)

   def bool(self, ctx):
      v = self.value(ctx)
      if 'equals' in self.attr:
         e = self.fill(self.attr['equals'],ctx)
         return bool(v == e)
      else:
         return bool(v)

   def form_value(self, ctx):
      if '_form_data' in ctx:
         ctx.push(ctx['_form_data'])
      if 'key' in self.attr:
         v = self.get(self.attr['key'], ctx)
      elif 'name' in self.attr:
         v = self.get(self.attr['name'], ctx)
      else:
         v = None
      if '_form_data' in ctx:
         ctx.pop()
      return v

      

      
class TagConditional(Element):
   def render_conditional(self, ctx, b):
      s = ''
      for c in self.children:
         if isinstance(c,Element) and c.tag == 'else':
            b = not b
         elif b:
            s += c.render(ctx)
      return s

@tag_class('if')
class TagIf(TagConditional):
   def render(self, ctx):
      return self.render_conditional(ctx, self.bool(ctx))

@tag_class('ifnot')
class TagIfNot(TagConditional):
   def render(self, ctx):
      return self.render_conditional(ctx, not self.bool(ctx))

@tag_class('switch')
class TagSwitch(Element):
   def render(self, ctx):
      v = self.value(ctx)
      for c in self.children:
         if c.tag == 'case':
            c_v = c.value(ctx)
            if v == c_v or c_v is None:
               return c.render_children(ctx)
      for c in self.children:
         if c.tag == 'default':
            return c.render_children(ctx)
      return ''

@tag_class('with')
class TagWith(Element):
   def render(self, ctx):
      v = self.value(ctx)
      if v is not None:
         return self.render_children(ctx,self.value(ctx))
      else:
         return ''

@tag_class('get')
class TagGet(Element):
   def render(self, ctx):
      return self.value(ctx)

@tag_class('set')
class TagSet(Element):
   def render(self, ctx):
      ctx[self.attr['key']] = self.value(ctx)

@tag_class('unset')
class TagUnSet(Element):
   def render(self, ctx):
      ctx.unset(self.attr['key'])

@tag_class('del')
class TagDel(Element):
   def render(self, ctx):
      del ctx[self.attr['key']]

@tag_class('repr')
class TagRepr(Element):
   def render(self, ctx):
      return repr(self.value(ctx))

@tag_class('do')
class TagDo(Element):
   def render(self, ctx):
      return self.render_children(ctx)

@tag_class('loop')
class TagLoop(Element):
   def render(self, ctx):
      v = self.value(ctx)
      i = 0
      sep = None
      for e in self.children:
         if e.tag == 'separator' and sep is None:
            sep = e.render_children(ctx)

      if v is None:
         v = []
         
      if 'offset' in self.attr:
         offset = int(self.attr['offset'])
         v = v[offset:]
      if 'limit' in self.attr:
         limit = int(self.attr['limit'])
         v = v[:limit]

      s = ''
      for o in v:         
         if i % 2:
            evenodd = 'odd'
         else:
            evenodd = 'even'
         ctx.push({'_index' : i, '_order' : i+1, '_value' : o, '_evenodd' : evenodd})
         if i and sep is not None:
            s += sep         
         if isinstance(o,tuple):
            ctx.push(o._asdict())
         elif hasattr(o,'items'):
            ctx.push(o)
         else:
            ctx.push({'_' : o})
         s += self.render_children(ctx)
         ctx.pop()
         ctx.pop()
         i = i + 1
      return s

@tag_class('separator')
class TagSeparator(Element):
   def render(self, ctx):
      return None

@tag_class('paginate')
class TagPaginate(Element):
   def render(self, ctx):
      r = self.value(ctx)
      if isinstance(r,dict):
         return self.render_page(ctx, r)
      else:
         return self.render_records(ctx, r)

   def render_page(self, ctx, page):
      #full_uri = ctx.get('_full_uri')
      m_front = int(self.attr.get('before',4))
      m_back = int(self.attr.get('after',4))
      page_number = page['_page']
      page_count = page['_page_count']
      page_prev = max(page_number-1,1)
      page_next = min(page_number+1,page_count)
      data = {}
      if page_number > 1:
         data['_page_prev'] = page_prev
      if page_number < page_count:
         data['_page_next'] = page_next
      #data['_url_first'] = ''
      #data['_url_last'] = full_uri.make_url(_p=page_count)
      #if page_number > 1:
      #   data['_url_prev'] = full_uri.make_url(_p=page_prev)
      #if page_number < page_count:
      #   data['_url_next'] = full_uri.make_url(_p=page_next)
      pages = []
      for p in range(1,page_count+1):
         #d = {'_value' : p, '_url' : full_uri.make_url(_p=p)}
         d = {'_value' : p, '_order' : page['_order']}
         if p == page_number:
            d['_class'] = 'active'
         pages.append(d)
      if len(pages) > (m_front + m_back + 1):
         p_start = min(max(1,page_number-m_front),page_count-(m_front+m_back))
         p_end = p_start + (m_front+m_back+1)
         data['_pages'] = pages[p_start-1:p_end-1]
      else:
         data['_pages'] = pages
      return self.render_children(ctx, data)
   
   def render_records(self, ctx, records):
      if records is None:
         records = []
      record_count = len(records)
      full_uri = ctx.get('_full_uri')
      page_number = self.fill(self.attr.get('page'),ctx)
      page_size = self.fill(self.attr.get('page_size'),ctx)

      if page_size is None:
	 page_size= len(records)
      else:
         page_size = int(page_size)
      if page_number is None or page_number == '':
         page_number = 1
      else:
         page_number = int(page_number)
      page_count = record_count / page_size
      if record_count % page_size:
         page_count += 1         
      page_records = []
      pages = []
      _site_page = None
      for p in range(1,page_count+1):
         d = {'_value' : p, '_url' : full_uri.make_url(_p=p)}
         if p == page_number:
            d['_class'] = 'active'
         pages.append(d)
         p_start = (p-1) * page_size
         p_end = p * page_size
         page_records.append(records[p_start:p_end])

      index_start = (page_number-1) * page_size
      index_end = page_number * page_size
      
      record_first = min(index_start+1, record_count)
      record_last = min(index_end, record_count)

      page_prev = max(page_number-1,1)
      page_next = min(page_number+1,page_count)
      
      data = {}        
      data['_records'] = records[index_start:index_end]
      data['_pages'] = page_records
      data['_page_number'] = page_number
      data['_page_size'] = page_size
      data['_page_count'] = page_count
      data['_index_start'] = index_start
      data['_index_end'] = index_end
      data['_record_first'] = record_first
      data['_record_last'] = record_last
      data['_record_count'] = record_count
      data['_pages'] = pages
      data['_page_prev'] = page_prev
      data['_page_next'] = page_next
      if page_number > 1:
         data['_url_prev'] = full_uri.make_url(_p=page_prev)
      if page_number < page_count:
         data['_url_next'] = full_uri.make_url(_p=page_next)
      data['_multiple_pages'] = (pages > 1)

      return self.render_children(ctx, data)

@tag_class('group')
class TagGroup(Element):
   def render(self, ctx):
      v = self.get(self.attr['key'], ctx)
      if v is None:
         v = []

      g_label = self.attr['label']
      g_value = self.attr.get('value',g_label)

      values = []
      groups = {}

      for o in v:
         ctx.push(o)
         value = self.fill(unicode(g_value),ctx)
         label = self.fill(unicode(g_label),ctx)
         ctx.pop()
         if value not in values:
            values.append(value)
         groups.setdefault(value, {'_value' : value, '_label' : label, '_records':[]})['_records'].append(o)
      
      group_arr = [groups[value] for value in values]
      if group_arr:
         group_arr[0]['_first'] = True
         group_arr[-1]['_last'] = True
      return self.render_children(ctx, {'_groups' : group_arr})

class FormElement(Element):
   def tag_open(self, attr):
      return '<'+self.tag+''.join([' %s="%s"' % (k, self.encode(v)) for k,v in attr])+'>'

   def tag_close(self):
      return '</'+self.tag+'>'

   def eval_attr(self, ctx):
      return [(k,v(ctx)) for k, v in self.text_attr if k not in ['key','value']]

   def value_selected(self, v, value):
      b = False
      if type(v) == bool:
         b = v
      elif type(v) in [list, set]:
         b = unicode(value) in [unicode(x) for x in v]
      elif type(v) == dict:
         b = v.get(value)
      elif type(v):
         b = (unicode(v) == unicode(value))
      return b


@tag_class('input')
class TagInput(FormElement):
   def render(self, ctx):
      t = self.attr['type']
      if t in ['text','password','hidden']:
         return self.render_textbox(ctx)
      elif t in ['button','submit','reset','file']:
         return self.render_button(ctx)
      elif t in ['checkbox','radio']:
         return self.render_radio(ctx)

   def render_textbox(self, ctx):
      attr = self.eval_attr(ctx)
      if 'value' in self.attr:
         v = self.fill(self.attr['value'],ctx)
      else:
         v = self.form_value(ctx)
      attr.append(('value',v))
      return self.tag_open(attr)

   def render_button(self, ctx):
      attr = self.eval_attr(ctx)
      if 'value' in self.attr:
         v = self.fill(self.attr['value'],ctx)
      else:
         v = self.form_value(ctx)
      attr.append(('value',v))
      return self.tag_open(attr)

   def render_radio(self, ctx):
      attr = self.eval_attr(ctx)
      v = self.form_value(ctx)
      if 'value' in self.attr:
         value = self.fill(self.attr['value'],ctx)
         attr.append(('value',value))
         if self.value_selected(v, value):
            attr.append(('checked','checked'))
      elif v:
         attr.append(('checked','checked'))
      return self.tag_open(attr)

@tag_class('textarea')
class TagTextarea(FormElement):
   def render(self, ctx):
      attr = self.eval_attr(ctx)
      return self.tag_open(attr) + self.encode(self.form_value(ctx))+self.tag_close()

@tag_class('select')
class TagSelect(FormElement):
   def render(self, ctx):
      attr = self.eval_attr(ctx)
      if 'value' in self.attr:
         v = self.fill(self.attr['value'],ctx)
      else:
         v = self.form_value(ctx)
      return self.render_open(ctx) + self.render_children(ctx,{'_select_value' : v}) + self.render_close(ctx)

@tag_class('option')
class TagOption(FormElement):
   def render(self, ctx):
      attr = self.eval_attr(ctx)
      if 'key' in self.attr:
         v = self.get('key',ctx)
      else:
         v = self.get('_select_value',ctx)
      if 'value' in self.attr:
         value = self.fill(self.attr['value'],ctx)
         attr.append(('value',value))
      elif self.children:
         value = self.render_children(ctx)
      else:
         value = NotExist

      if self.value_selected(v, value):
         attr.append(('selected','selected'))

      return self.tag_open(attr) + self.render_children(ctx) + self.tag_close()

@tag_class('doctype')
class TagDoctype(Element):
   def render(self, ctx):
      return '<!DOCTYPE HTML>'

if __name__ == '__main__':
   import sys
   print Template(sys.argv[1])()


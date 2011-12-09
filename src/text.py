import path, filters

class TextTemplate(object):
   def __init__(self, text, custom_filters=None):
      if not type(text) is unicode:
         raise Exception('Unicode string required') 
      self.text = text
      self.filters = dict(filters.filters)
      if custom_filters:
         self.filters.update(custom_filters)
      self.steps = self.parse_text(text)

   def parse_text(self, text):
      steps = []
      depth = 0
      tag_open = '{'
      tag_close = '}'

      s = u''
      for c in text:
         if c == tag_open:
            if depth == 0:
               steps.append(s)
               s = u''
            else:
               s += c
            depth += 1
         elif c == tag_close:
            depth -= 1
            if depth == 0 and s:
               steps.append(self.parse_tag(s))
               s = u''
            else:
               s += c
         else:
            s += c
      if depth > 0:
         raise ParseException('Unclosed tag')
      else:
         steps.append(s)
      return steps

   def parse_tag(self, s):
      s_arr = s.split(u'|')
      pe = path.PathEvaluator(s_arr[0])
      filters = [self.parse_filter(f) for f in s_arr[1:]]
      return (pe, filters)

   def parse_filter(self, f_string):
      f_arr = f_string.split(u':')
      filter_name = f_arr[0]
      return (self.filters.get(filter_name), f_arr)

   def __call__(self, mapping):
      out = u''
      for step in self.steps:
         if type(step) == type(u''):
            out += step
         else:
            (pe, filters) = step
            v = pe.evaluate(mapping)
            for (m, f_arr) in filters:
               if m:
                  v = m(f_arr, v, mapping)
            if v is None:
               v = u''
            elif v is not unicode:
               v = unicode(v)
            out += v
      return out

   

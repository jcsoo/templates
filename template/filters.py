import re, time, datetime, hashlib, decimal, pprint
try:
   import json
except ImportError:
   import simplejson as json
from urllib import quote, quote_plus, urlencode, unquote, unquote_plus
        
def register_filter(key, value):
   filters[key] = value

def _upper(f_arr, v, mapping):
   if v is None:
      return ''
   else:
      return str(v).upper()

def _lower(f_arr, v, mapping):
   if v is None:
      return ''
   else:
      return str(v).lower()

def _urlencode(f_arr, v, mapping):
   if v is None:
      return ''
   else:
      return quote_plus(str(v),'')

def _htmlencode(f_arr, v, mapping):
   if v is None:
      return ''
   elif type(v) == type(u''):
      return v.replace(u'&',u'&amp;').replace(u'<',u'&lt;').replace(u'>',u'&gt;').replace(u'"',u'&quot;')   
   else:
      return v.decode('utf8').replace(u'&',u'&amp;').replace(u'<',u'&lt;').replace(u'>',u'&gt;').replace(u'"',u'&quot;')   

def to_time(v):
   if v is None or v == '':
      return v
   if type(v) == type('') or type(v) == type(u''):
      if v[-1] == 'Z':
         v = v[:-1]
      if 'T' in v:
         v_arr = v.split('T')
      else:
         v_arr = v.split(' ')
      y,month,d = v_arr[0].split('-')
      if len(v_arr) > 1:
         h,min,s = v_arr[1].split(':')
      else:
         h,min,s = 0,0,0
      v = datetime.datetime(int(y),int(month),int(d),int(h),int(min),int(float(s)))
   elif type(v) in (int, float):
      v = datetime.datetime.fromtimestamp(v)
   elif not isinstance(v, datetime.datetime):
      v = datetime.datetime(v.year, v.month, v.day, v.hour, v.minute, int(v.second))
   return v

def _datetime(f_arr, v, mapping):
   if v is None:
      return v
   if len(f_arr) > 1:
      fmt = ':'.join(f_arr[1:])
   elif f_arr[0] in ['t','time']:
      fmt = '%X'
   elif f_arr[0] in ['d','date']:
      fmt = '%x'
   elif f_arr[0] in ['dt','datetime']:
      fmt = '%c'   
   v = to_time(v)
   if isinstance(v, datetime.datetime):
      return v.strftime(str(fmt))
   else:
      return None

def _gmttime(f_arr, v, mapping):
   v = to_time(v)
   return _datetime(f_arr,v)


def _format(f_arr, v, mapping):
   if v is None:
      return ''
   if len(f_arr) > 1:
      fmt = ':'.join(f_arr[1:])
      return fmt % v
   else:
      return str(v)

def _trim(f_arr, v, mapping):
   if v is None:
      return ''
   if len(f_arr) > 1:
      v = unicode(v)
      trim_len = int(f_arr[1])
      ell = ':'.join(f_arr[2:])
      if len(v) > trim_len:
         return v[:trim_len-len(ell)]+ell
      else:
         return v
   else:
      return unicode(v)

def _strip(f_arr, v, mapping):
   # strip html
   if v is None:
      return ''
   v = unicode(v).replace('<i>','').replace('</i>','').replace('<b>','').replace('</b>','')
   v = unicode(v).replace('<I>','').replace('</I>','').replace('<B>','').replace('</B>','')
   return v
   #return HTMLTAG_RE.sub(v,'')


def _none(f_arr, v, mapping):
   if v is None or v == '':
      return ':'.join(f_arr[1:])
   else:
      return v   

def _javascript(f_arr, v, mapping):
   return json.dumps(v)

def _md5(f_arr, v, mapping):
   m = hashlib.md5()
   m.update(v)
   return m.hexdigest()

def _eq(f_arr, v, mapping):
   if (f_arr[1] == v):
      return f_arr[2]
   elif len(f_arr) > 3:
      return f_arr[3]

def _ne(f_arr, v, mapping):
   if (not f_arr[1] == v):
      return f_arr[2]
   elif len(f_arr) > 3:
      return f_arr[3]

def _match(f_arr, v, mapping):
   if re.match(f_arr[1],v):
      return f_arr[2]
   elif len(f_arr) > 3:
      return f_arr[3]


def _if(f_arr, v, mapping):
   arg = ':'.join(f_arr[1:])
   arg_arr = arg.split(',')
   if v:
      return arg_arr[0]
   else:
      if len(arg_arr) > 1:
         return arg_arr[1]
      else:
         return ''

def _cond(f_arr, v, mapping):
   i = 1
   while i < len(f_arr):
      if v == f_arr[i]:
         if len(f_arr) > i+1:
            return f_arr[i+1]
         else:
            return ''
      i += 2
   return ''

def _p(f_arr, v, mapping):
   if v:
      v = unicode(v).replace('\r\n','\n')
      p_arr = unicode(v).split('\n') 
      return '\n'.join('<p>%s</p>' % p for p in p_arr)

def _p2(f_arr, v, mapping):
   if v:
      v = unicode(v).replace('\r\n','\n')
      p_arr = unicode(v).split('\n\n') 
      return '\n'.join('<p>%s</p>' % p for p in p_arr)

def _br(f_arr, v, mapping):
   if v:
      #v = unicode(v).replace('\r\n','\n')
      v = v.replace('\r\n','\n')
      return '<br>\n'.join(v.split('\n'))


def _join(f_arr, v, mapping):
   if v:
      if len(f_arr) > 1:
         return f_arr[1].join([x for x in v if x])
      else:
         return ''.join(v)

def _markdown(f_arr, v, mapping):
   if v:
      import markdown
      return markdown.markdown(v)

def _sef(f_arr, v, mapping):
   if v is None or v.strip() == '':
      return v
   s = ''
   is_dash = True
   for c in v:
      if c.isalnum():
         s += c
         is_dash = False
      else:
         if not is_dash:
            s += '-'
            is_dash = True
   if s and s[-1] == '-':
      s = s[:-1]
   return s.lower()

def _repr(f_arr, v, mapping):
   return repr(v)

def _money(f_arr, v, mapping):
   if not isinstance(v, decimal.Decimal):
      v = decimal.Decimal(str(v))
   return '%.2f' % v

def _prettyprint(f_arr, v, mapping):
   return pprint.pformat(v)


filters = {'upper' : _upper,
           'uc' : _upper,
           'lower' : _lower,
           'lc' : _lower,
           'urlencode' : _urlencode,
           'u' : _urlencode,
           'htmlencode' : _htmlencode,
           'h' : _htmlencode,
           'gmt' : _gmttime,
           't' : _datetime,
           'time' : _datetime,
           'd' : _datetime,
           'date' : _datetime,           
           'dt' : _datetime,
           'datetime' : _datetime,
           'eq' : _eq,
           'f' : _format,
           'format' : _format,
           'trim' : _trim,
           'strip' : _strip,
           'match' : _match,
           'n' : _none,
           'ne' : _ne,
           'none' : _none,
           'j' : _javascript,
           'js' : _javascript,
           'javascript' : _javascript,
           'md5' : _md5,
           '?' : _if,
           'if' : _if,
           'p' : _p,
           'p2' : _p2,
           'br' : _br,
           'join' : _join,
           'm' : _markdown,
           'sef' : _sef,
           'r' : _repr,
           'money' : _money,
           'pp' : _prettyprint,
           'cond' : _cond,
           }

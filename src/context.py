import re, pprint

class NotExist(object):
   pass

class Context(object):
   def __init__(self, item):
      self.stack = []
      self.push(item)
      #self.push(*args, **kw)
   
   def copy(self):
      c = Context()
      c.stack = [d.copy() for d in self.stack]
      return c

   def clear(self):
      self.stack = [None]
      
   def push(self, v):
      self.stack.append(v)

   def push_old(self, *args, **kw):
      if args and args[0] is None:
         self.stack.append(None)
      elif args and isinstance(args[0],tuple):
         self.stack.append(args[0])
      else:
         self.stack.append(dict(*args, **kw))

   def pop(self):
      return self.stack.pop()

   def has_key(self, key):
      for d in reversed(self.stack):
         if d is not None:
            if key in d:
               return (d[key] is not NotExist)
            elif hasattr(d,key):
               return getattr(d,key)
      return False

   def unset(self, key):
      top = self.stack[-1]
      del top[key]

   def get(self, key, default=None):
      for d in reversed(self.stack):
         if d is not None:
            if hasattr(d, key):
               return getattr(d,key)
            elif key in d:
               v = d.get(key)
               if v is NotExist:
                  return default
               else:
                  return v
      return default

   def update(self, data):
      top = self.stack[-1]
      if top is None:
         top = {}
         self.stack[-1] = top 
      top.update(data)

   def items(self):
      data = {}
      for d in self.stack:
         if d:
            data.update(d)      
      return [(k,v) for (k,v) in data.items() if v is not NotExist]

   def keys(self):
      return [k for (k,v) in self.items()]

   def values(self):
      return [v for (k,v) in self.items()]

   def __contains__(self, key):
      return self.has_key(key)

   def __iter__(self):
      data = {}
      for d in self.stack:
         if d:
            data.update(d)      
      for k,v in data.items():
         if v is not NotExist:
            yield k
      
   def __len__(self):
      return len(self.stack)
   
   def __getitem__(self, key):      
      v = self.get(key,NotExist)
      if v is NotExist:
         raise KeyError(key)
      else:
         return v

   def __setitem__(self, key, value):
      top = self.stack[-1]
      if top is None:
         self.stack[-1] = {key : value}
      else:
         top[key] = value
         
   def __delitem__(self, key):
      self[key] = NotExist

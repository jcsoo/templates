# evaluate_path(path, mapping)

def evaluate_path(path, mapping):
   pe = PathEvaluator(path)
   return pe.evaluate(mapping)

class ParseException(Exception):
   pass

class PathEvaluator(object):
   def __init__(self, path):
      self.path = path
      self.steps = self.parse(path)
      self.top = None
      self.current = None

   def parse(self, path):
      steps = []
      depth = 0
      sep = '.'
      tag_open = '{'
      tag_close = '}'

      s = ''
      for c in path+'.':
         if c == sep and depth == 0:
            if s[0] == '{':
               steps.append(PathEvaluator(s[1:-1]))
            else:
               steps.append(s)
            s = ''
         elif c == tag_open:
            depth += 1
            s += c
         elif c == tag_close:
            depth -= 1
            s += c
         else:
            s += c
      if depth > 0:
         raise ParseException('Unclosed tag')

      return steps


   def evaluate(self, mapping):
      self.top = mapping
      self.current = mapping
      
      for step in self.steps:
         self.current = self.evaluate_step(step)
         if self.current is None:
            return None
      return self.current
   
   def evaluate_step(self, step):        
      if hasattr(step,'evaluate'):
         step = step.evaluate(self.top)

      if hasattr(self.current,'items'):
         return self.current.get(step)
      if type(self.current) == type([]):
         return self.current[int(step)]

      else:
         raise Exception('Not a mappable type')



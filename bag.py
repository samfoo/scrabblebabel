from random import randint

# Points for each letter
scores = {  
  'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4, 'g':2, 'h':4, 'i':1,
  'j':8, 'k':5, 'l':1, 'm':3, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1,
  's':1, 't':1, 'u':1, 'v':4, 'w':4, 'x':8, 'y':4, 'z':10, '_':0
}

# Distribution of each letter
distribution = {
  'a':16, 'b': 4, 'c':6, 'd':8, 'e':24, 'f': 4, 'g':5, 'h':5, 'i':13,
  'j': 2, 'k': 2, 'l':7, 'm':6, 'n':13, 'o':15, 'p':4, 'q':2, 'r':13,
  's':10, 't':15, 'u':7, 'v':3, 'w': 4, 'x': 2, 'y':4, 'z':2, '_': 0
}

class Bag:
  def __init__(self):
    self.bag = []
    for letter, count in distribution.iteritems():
      self.bag += [letter] * count

  def remaining(self, letter = None):
    if not letter:
      return len(self.bag)
    else:
      return len(filter(lambda c: c == letter, self.bag))

  def random(self, draw = True):
    if len(self.bag) == 0:
      raise BagError("The bag is empty.")
    else:
      index = randint(0, len(self.bag)-1)

      c = self.bag[index]
      if draw:
        self.bag.remove(c)
      return c

  def draw(self, letter):
    if len(self.bag) == 0:
      raise BagError("The bag is empty.")
    elif letter not in bag:
      raise BagError("There are no more `%s' remaining in the bag." % letter)
    else:
      self.bag.remove(self.bag.index(letter))

from bag import *
from board import *

class GameError (Exception):
  pass

class Game:
  def __init__(self):
    self.bag = Bag()
    self.board = Board()

  def __repr__(self):
    # TODO: Output something a little more interesting.
    return repr(self.board)

  def draw(self, letters):
    # TODO: Make this transactional
    for l in letters:
      self.bag.draw(l)
    return letters

    # TODO: Make sure the rack has seven or less characters.

  def play(self, word, start, end):
    try:
      self.board.play(word, start, end)
      
    except BoardError, e:
      # TODO: Do something useful with this.
      raise GameError(e)

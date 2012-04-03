from copy import copy, deepcopy
from random import shuffle

SEARCH_MOVES_DEPTH = 3
SEARCH_TURNS_DEPTH = 5
SEARCH_RACKS_COUNT = 5

class Player:
  def __init__(self, game):
    self.rack = ""
    self.history = []
    self.game = game

  def _random_rack(self, bag, existing=None):
    # Create a random rack where tile occurance is weighted to the current bag.
    if existing:
      count = 7 - len(existing)
    else:
      count = min(len(bag.bag), 7)

    ret = [bag.random(draw = False) for i in xrange(count)]
    if existing: 
      ret = existing + ret

    return ret

  def _average_random(self, board, bag):
    # TODO: Parallelize this method.

    total = 0
    # Generate a hypothetical new rack.
    for i in xrange(SEARCH_RACKS_COUNT):
      # Next play the hypothetical AI's. The AI is naive and just plays the
      # best possible move available given his random rack.
      #
      # TODO: Figure out how to make the AI less naive without adding too
      # much computation complexity (Ha!)
      rack = self._random_rack(bag)
      ms = board.moves(rack)
      if len(ms) != 0:
        total += ms[0][4]

    return float(total) / float(SEARCH_RACKS_COUNT)

  def _rfetch_score_delta(self, move, rack, board, depth, total):
    if depth < 0:
      return total 

    board_copy = copy(board); board_copy.grid = deepcopy(board.grid)
    bag_copy = deepcopy(self.game.bag)

    # First do the player's move.
    total += board_copy.play(move[0], move[2], move[3])

    # Get the average score for the opponent's next play.
    total -= self._average_random(board_copy, bag_copy)

    # Fill up the player's rack with some random tiles.
    rack = filter(lambda l: l not in move[1], rack)
    rack = self._random_rack(bag_copy, rack)

    # Play the next best move
    best = self._best_move(board_copy, rack, depth, total)

    if best:
      return total + best[1]
    else:
      return total

  def _best_move(self, board, rack, depth, total):
    # For each of the top moves available, find the score delta.
    ms = board.moves(rack)[:depth]
    best = None

    for m in ms: 
      delta = self._rfetch_score_delta(m, rack, board, depth - 1, total)
      if not best or best[1] < delta:
        best = (m, delta)

    prefix = " " * (3 - depth) 
    if best:
      print "%s(%r, %d)" % (prefix, best[0], best[1])
    return best

  def move(self):
    return self._best_move(self.game.board, self.rack, 4, 0)

  def draw(self, letters):
    self.rack += self.game.draw(letters)

  def play(self, word, tiles, start, end):
    try:
      score = self.game.play(word, start, end)
      self.history.append((word, tiles, start, end, score))
      return score
    except GameError:
      return 0

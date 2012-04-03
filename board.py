from dawg import *
from bag import *

DICTIONARY = "scrabble.txt"

# Location of special squares.
#   T triple word
#   t triple letter
#   D double word
#   d double letter
SPECIAL = [
  ['T','.','.','d','.','.','.','T','.','.','.','d','.','.','T'],
  ['.','D','.','.','.','t','.','.','.','t','.','.','.','D','.'],
  ['.','.','D','.','.','.','d','.','d','.','.','.','D','.','.'],
  ['d','.','.','D','.','.','.','d','.','.','.','D','.','.','d'],
  ['.','.','.','.','D','.','.','.','.','.','D','.','.','.','.'],
  ['.','t','.','.','.','t','.','.','.','t','.','.','.','t','.'],
  ['.','.','d','.','.','.','d','.','d','.','.','.','d','.','.'],
  ['T','.','.','d','.','.','.','D','.','.','.','d','.','.','T'],
  ['.','.','d','.','.','.','d','.','d','.','.','.','d','.','.'],
  ['.','t','.','.','.','t','.','.','.','t','.','.','.','t','.'],
  ['.','.','.','.','D','.','.','.','.','.','D','.','.','.','.'],
  ['d','.','.','D','.','.','.','d','.','.','.','D','.','.','d'],
  ['.','.','D','.','.','.','d','.','d','.','.','.','D','.','.'],
  ['.','D','.','.','.','t','.','.','.','t','.','.','.','D','.'],
  ['T','.','.','d','.','.','.','T','.','.','.','d','.','.','T']
]

GRID_SIZE = 15

class BoardError (Exception):
  pass

class Board (object):
  def __init__(self, words=open(DICTIONARY), language=en):
    self.dawg = Dawg(digraphs=[k for k in language.scores.keys() if len(k) > 1])
    self.grid = []
    self.language = language

    self._transposed = False

    self._anchors_dirty = True
    self._cached_anchors = None

    # Initialize the board's grid.
    for i in xrange(15):
      self.grid.append(['.'] * 15)

    # Initialize the word search from the dictionary.
    for line in words:
      self.dawg.insert(unicode(line.strip(), 'UTF-8'))

  def __repr__(self):
    """Returns the string representation of the current board.
    
    @returns: String of the current board."""

    result = '   ' + ' '.join(["%2d" % x for x in xrange(15)]) + '\n'
    for y in xrange(15):
      result += "%-4d" % y
      for x in xrange(15):
        result += self.square(x, y) + '  '
      result += '\n'
    return result

  def square(self, x, y):
    """Returns the letter that is at a specific coordinate.
    
    @param x: The x coord.
    @param y: The y coord.
    
    @return: The character at the given location."""

    x, y = self._coord(x,y)
    return self.grid[y][x]

  def moves(self, rack):
    """Generates all of the moves that are available on the board.
    
    @param rack: A string of the letters available to play."""

    moves = []
    anchors = self.anchors()
    for a in anchors:
      moves += self._get_moves(a, rack)
    moves = [(m[0], m[1], m[2], m[3], self.score(*m[1:])) for m in moves]

    imoves = []
    self._transposed = True
    anchors = self.anchors()
    for a in anchors:
      imoves += self._get_moves(a, self.dawg.tokenize(rack))
    imoves = [(m[0], m[1], self._coord(*m[2]), self._coord(*m[3]), self.score(*m[1:])) for m in imoves]
    self._transposed = False

    moves += imoves
    moves.sort(lambda m1,m2: cmp(m1[4],m2[4]), reverse=True)

    return moves

  def score(self, word, start, end):
    """Returns the score playing a word would yield including word and letter
    modifiers.
    
    @param word: A string of the word to play.
    @param start: An (x, y) tuple of the starting square.
    @param end: An (x, y) tuple of the final square."""

    # If this is a vertical play and `score' is being called outside the 
    # context of self.moves, some coordinate transformation needs to take
    # place.

    start = self._coord(*start)
    end = self._coord(*end)

    not_transposed = not self._transposed
    if not_transposed and start[1] != end[1]:
      # Re-map the co-ords so we get an accurate score.
      self._transposed = True

    # Make a faux-iterator to get the next square of a word instead of having
    # to check if it's horizontally or vertically placed each time.
    if start[0] != end[0]:
      square = lambda j: (start[0]+j, start[1])
    else:
      square = lambda j: (start[0], start[1]+j)

    score = 0

    # Score each letter, including the letter bonuses.
    for i, letter in enumerate(self.dawg.tokenize(word)):
      score += self._get_letter_score(letter,square(i))

    # Score any cross words that were created.
    score += self._get_word_cross_scores(word, square)

    # Multiply by any word score modifiers.
    score *= self._get_word_score_mod(word, square)

    # Add a bingo bonus.
    score += self._get_bingo_bonus(word, square)

    if not_transposed:
      self._transposed = False

    return score

  def cross_section(self, x, y):
    """Returns the vertical cross-section of a square. That is, the  letters
    directly adjacent to the top and bottom of a square.

    @param x: The x coord.
    @param y: The y coord.

    @returns: A string with the letters surrounding a blank square 
      (i.e. `sam.le') or a single `.' character."""

    cross = "."
    up_y, down_y = y - 1, y + 1
    s = self.square(x, up_y)
    while up_y >= 0 and '.' != s:
      cross = s + cross
      up_y -= 1
      s = self.square(x, up_y)

    s = self.square(x, down_y)
    while down_y < 15 and '.' != s:
      cross += s
      down_y += 1
      s = self.square(x, down_y)

    return cross

  def cross_set(self, x, y):
    """Returns a list of the characters which create valid words (vertically)
    with a square's cross-section.

    @param x: The x coord.
    @param y: The y coord.

    @returns: A list of characters."""

    s = self.square(x,y)
    if '.' == s:
      cross_section = self.cross_section(x, y)
      if '.' == cross_section:
        return [c for c in self.language.scores.keys() if c != '_']
      else:
        return self.dawg.pivot_search(cross_section)
    else:
      return [s]

  def anchors(self):
    """Returns all of the anchor squares for the current board configuration.

    @returns: A list of (x,y) coordinate tuples."""

    if self._anchors_dirty:
      # If the starting square hasn't been played it is necessarily the only anchor
      if self.square(7, 7) == '.': return [(7,7)] 

      self._cached_anchors = []
      for row in xrange(GRID_SIZE):
        # Filter the list of squares on a row to those which are adjacent to a
        # tile which is already on the board.
        row_anchors = filter(lambda s: self._is_anchor(s, row), xrange(GRID_SIZE))
        self._cached_anchors += zip(row_anchors,[row] * len(row_anchors))

      self._anchors_dirty = False

    return self._cached_anchors

  def _place(self, letter, x, y):
    """Place a letter on the board.
    
    @param letter: The letter to place.
    @param x: The x coord.
    @param y: The y coord."""

    if self._is_valid_place(letter, x, y): 
      self.grid[y][x] = letter
    else:
      raise BoardError("Illegal play [%d,%d]." % (x, y))

  def _is_valid_place(self, letter, x, y):
    if '.' == self.grid[y][x] or (letter == self.grid[y][x]):
      return True
    return False

  def play(self, word, start, end):
    # Make a faux-iterator to get the next square of a word instead of having
    # to check if it's horizontally or vertically placed each time.
    if start[0] != end[0]:
      square = lambda j: (start[0]+j, start[1])
    else:
      square = lambda j: (start[0], start[1]+j)

    # First, check to make sure that each placement in the word is valid.
    for i, letter in enumerate(word):
      if not self._is_valid_place(letter, *square(i)):
        raise BoardError("Illegal play [%d,%d]." % (square(i)[0], square(i)[1]))

    score = self.score(word, start, end)

    for i, letter in enumerate(word):
      self._place(letter, *square(i))

    return score

  def _is_anchor(self, x, y):
    if x + 1 >= GRID_SIZE or x - 1 < 0 or \
       y + 1 >= GRID_SIZE or y - 1 < 0:
      return False

    try:
      if self.square(x, y) == '.' and \
          (self.square(x-1, y) != '.' or \
           self.square(x+1, y) != '.' or \
           self.square(x, y+1) != '.' or \
           self.square(x, y-1) != '.'):
        return True
    except IndexError: pass
    return False

  def _get_bingo_bonus(self, word, iter):
    count = 0
    for i in xrange(len(word)):
      if '.' == self.square(*iter(i)):
        count += 1

    if count == 7:
      return 50
    return 0

  def _get_word_cross_scores(self, word, iter):
    """Returns the collective scores of all the cross words that were created
    by playing word.
    
    @param word: A string of the word.
    @param iter: A lambda function that takes one arg and returns the square 
      of the word offset by the argument.
      
    @returns: An integer for the modifier."""

    score = 0
    for i in xrange(len(word)):
      cross_section = self.cross_section(*iter(i))
      if '.' == self.square(*iter(i)) and ('.' == cross_section[0] or '.' == cross_section[-1]):
        score += reduce(lambda a, b: a + b, map(lambda c: self.language.scores[c], cross_section.replace('.', '')), 0)

    return score

  def _get_word_score_mod(self, word, iter):
    """Returns the total multiplier for a word.
    
    @param word: A string of the word.
    @param iter: A lambda function that takes one arg and returns the square 
      of the word offset by the argument.
      
    @returns: An integer for the modifier."""

    mod = 1
    for i in xrange(len(word)):
      (x,y) = iter(i)
      if 'T' == SPECIAL[y][x] and '.' == self.square(x,y):
        mod *= 3
      elif 'D' == SPECIAL[y][x] and '.' == self.square(x,y):
        mod *= 2
    return mod

  def _get_letter_score(self, letter, (x,y)):
    """Returns a particular letter score.
    
    @param letter: The character to play.
    @param x: The x coord.
    @param y: The y coord.
    
    @returns: An integer for the score."""

    if '.' == self.square(x, y):
      if SPECIAL[y][x] == 'd':
        return self.language.scores[letter] * 2
      elif SPECIAL[y][x] == 't':
        return self.language.scores[letter] * 3
    return self.language.scores[letter]

  def _get_prefix(self, anchor):
    """Returns the string prefix of characters already on the board of a given
    square.
    
    @param anchor: An (x, y) tuple to start looking for a prefix.
    
    @returns: The prefix as a string."""

    prefix = ''
    square = (anchor[0]-1, anchor[1])
    s = self.square(*square)
    while 1:
      if '.' == s:
        return prefix
      prefix = s + prefix
      square = (square[0]-1, square[1])
      s = self.square(*square)

  def _get_moves(self, anchor, rack):
    """Gets all legal `across' moves at a given square with a given rack.

    @param anchor: An (x, y) tuple to start looking for a prefix.
    @param rack: A list of the tiles available to play.

    @returns: A list of 3-tuple's in the following format...
      (`word', start, end)"""

    if '.' != self.square(anchor[0]-1, anchor[1]):
      # If the left of the anchor is already on the board, use those tiles as
      # the prefix instead of trying to generate one.
      prefix = self._get_prefix(anchor)
      if self.dawg.node(prefix) is None:
        # Technically this should never happen as any word already on the board
        # would be a valid prefix--but you never know.
        return []
      else:
        return self._rright_part(self.dawg.node(prefix), prefix, rack, anchor, [], True)
    else:
      try:
        # Get the index of the closest letter already on the board to the left 
        # of the anchor.
        nearest = max(zip(*filter(lambda n: n[0] < anchor[0] and n[1] == anchor[1], self.anchors()))[0]) + 1
      except IndexError: nearest = 0

      # Get the maximum length of the left side of the word.
      limit = anchor[0] - nearest

      return self._rleft_part(self.dawg.root, '', limit, rack, anchor, [])

  def _already_played(self, move):
    word, start, end = move[0], move[2], move[3]

    if start[0] != end[0]:
      iter = lambda j: (start[0]+j, start[1])
    else:
      iter = lambda j: (start[0], start[1]+j)

    for i in xrange(len(word)):
      if '.' == self.square(*iter(i)):
        return False
    return True

  def _rright_part(self, node, partial, rack, (x,y), results, extended):
    if x >= GRID_SIZE or x < 0 or \
       y >= GRID_SIZE or y < 0:
       return results

    s = self.square(x, y)

    if '.' == s:
      # Check to see if a word as been formed at this point, and that the
      # left side has actually been extended.
      if node in self.dawg.accepts and '.' == s and extended:
        move = (self.dawg.accepts[node], partial, (x-len(partial), y), (x-1, y))

        # Make sure this isn't a word that's already on the board.
        if not self._already_played(move):
          results += [move]

      xs = self.cross_set(x,y)

      # Only allow if the letter from the rack is also in the cross-check
      # of this square.
      for e in self.dawg.graph[node]:
        if e[0] in rack and e[0] in xs:
          newrack = rack[:rack.index(e[0])] + rack[rack.index(e[0])+1:]
          results = self._rright_part(e[1], partial + e[0], newrack, (x+1,y), results, True)

      # If there's a blank in the rack, deal with that as well.
      if '_' in rack:
        for e in self.dawg.graph[node]:
          if e[0] in xs:
            newrack = rack[:rack.index('_')] + rack[rack.index('_')+1:]
            results = self._rright_part(e[1], partial + '_', newrack, (x+1,y), results, True)

    else:
      # See if the letter already on the board can form a valid move(s).
      for e in self.dawg.graph[node]:
        if s == e[0]:
          results = self._rright_part(e[1], partial + e[0], rack, (x+1,y), results, True)

    return results

  def _rleft_part(self, node, partial, limit, rack, anchor, results):
    results = self._rright_part(node, partial, rack, anchor, results, False)

    if limit > 0:
      # If there's a blank in the rack, deal with that as well.
      if '_' in rack:
        for e in self.dawg.graph[node]:
          newrack = rack[:rack.index('_')] + rack[rack.index('_')+1:]
          self._rleft_part(e[1], partial + '_', limit - 1, newrack, anchor, results)

      for e in self.dawg.graph[node]:
        if e[0] in rack:
          newrack = rack[:rack.index(e[0])] + rack[rack.index(e[0])+1:]
          self._rleft_part(e[1], partial + e[0], limit - 1, newrack, anchor, results)

    return results

  def _coord(self, x, y):
    if self._transposed:
      return (y, x)
    return (x, y)

  def _get_transposed(self):
    return self.__transposed

  def _set_transposed(self, value):
    self._anchors_dirty = True 
    self.__transposed = value

  _transposed = property(_get_transposed, _set_transposed)

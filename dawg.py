class Dawg (object):
  def __init__(self):
    self.root = self.index = 0

    self.graph = {self.root: []}
    self.accepts = {}

  def insert(self, word):
    self._rinsert(self.root, word, word)

  def words(self):
    return self.accepts.values()

  def search(self, rack, anchor, board, limit):
    return self._rleft_part(self.root, '', limit, rack, board, anchor, [])

  def node(self, word):
    return self._rnode(self.root, word)

  def pivot_search(self, substring):
    results = []

    # Check if this node is the start of the substring.
    pivot = substring.index('.')
    matches = self._rmatch_string(self.root, substring, [])
    for m in matches:
      results += [m[pivot]]

    return results

  def _rinsert(self, node, word, orig):
    try:
      # Unzip the edge values (letters) and the edge indices (targets).
      if len(self.graph[node]) > 0:
        letters, targets = map(lambda x: list(x), zip(*self.graph[node]))
      else:
        letters = targets = []

      if word[0] in letters:
        # If this edge already exists in the graph, recurse to it's target
        self._rinsert(targets[letters.index(word[0])], word[1:], orig)
      else:
        # If the edge doesn't already exist in the graph, create the edge
        self.index += 1
        self.graph[node].append((word[0],self.index))
        self.graph[self.index] = []

        # Move to the next letter
        self._rinsert(self.index, word[1:], orig)
    except IndexError:
      # Set this node to an accepting node once the whole word is inserted.
      if node not in self.accepts:
        self.accepts[node] = orig

  def _rmatch_string(self, node, string, results):
    if len(string) == 0:
      if node in self.accepts:
        results += [self.accepts[node]]
      return results

    letter = string[0]
    for e in self.graph[node]:
      if letter == e[0] or '.' == letter:
        results = self._rmatch_string(e[1], string[1:], results)

    return results

  def _rnode(self, node, word):
    if len(word) == 0:
      return node

    for n in self.graph[node]:
      if n[0] == word[0]:
        return self._rnode(n[1], word[1:])
    return None


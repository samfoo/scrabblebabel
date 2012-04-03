class Dawg (object):
  def __init__(self, digraphs=[]):
    self.root = self.index = 0

    self.digraphs = digraphs
    self.graph = {self.root: []}
    self.accepts = {}

  def tokenize(self, word):
    return self._rtokenize(word, [])

  def insert(self, word):
    self._rinsert(self.root, self.tokenize(word), word)

  def words(self):
    return self.accepts.values()

  def node(self, word):
    return self._rnode(self.root, self.tokenize(word))

  def pivot_search(self, substring):
    results = []

    tokens = self.tokenize(substring)

    # Check if this node is the start of the substring.
    pivot = tokens.index('.')
    matches = self._rmatch_string(self.root, self.tokenize(substring), [])

    for m in matches:
      results += [self.tokenize(m)[pivot]]

    return results

  def _rtokenize(self, word, tokens):
    if len(word) == 0:
      return tokens

    digraph = [dg for dg in self.digraphs if word.startswith(dg)]

    if len(digraph) > 0:
      return self._rtokenize(word[2:], tokens + [digraph[0]])
    else:
      return self._rtokenize(word[1:], tokens + [word[0]])

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

  def _rmatch_string(self, node, tokens, results):
    if len(tokens) == 0:
      if node in self.accepts:
        results += [self.accepts[node]]
      return results

    letter = tokens[0]
    for e in self.graph[node]:
      if letter == e[0] or '.' == letter:
        results = self._rmatch_string(e[1], tokens[1:], results)

    return results

  def _rnode(self, node, word):
    if len(word) == 0:
      return node

    for n in self.graph[node]:
      if n[0] == word[0]:
        return self._rnode(n[1], word[1:])
    return None


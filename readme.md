What is it?
===========

Scrabble babel is a general purpose, simple scrabble library. 

Given some board and some rack, scrabble babel can be used to pick out the
absolute best move (in terms of points), or can do a decision tree search of
the next N moves to predict what moves might be best for any given 
opponent.

General Usage
-------------

When just playing around with checking scores or finding all available moves
you only need the board object.

    >>> b = Board()
    >>> b.moves("abcdefg")[0] # Find the highest scoring move
    ('decaf', 'decaf', (7, 7), (11, 7), 30)

Moves are ordered by their point value descending. You can place words on the
board easily

    >>> b.play("decaf", (7,7), (11,7))
    >>> b
        0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
    0   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    1   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    2   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    3   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    4   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    5   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    6   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    7   .  .  .  .  .  .  .  d  e  c  a  f  .  .  .  
    8   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    9   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    10  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    11  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    12  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    13  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  
    14  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .

Babel is pretty forgiving about placing words/letters and if you screw up the 
coordinants, it will try to figure out what you meant. Also, it's important to
know that the board doesn't care if you play words in an invalid location.

Playing a game (experimental)
-----------------------------

Babel can attempt to provide better suggestions other than just the highest 
scoring word on any given turn. To do so it needs to keep track of the state of
the game (from one players perspective).

    >>> g = Game()
    >>> p = Player(g)
    >>> p.draw("rack_er") # Whenever you draw letters for your rack
    >>> p.move()
    (... listing the decision tree nodes)
    (('bracket', '_racket', (7, 7), (13, 7), 84), -110.19999999999999)

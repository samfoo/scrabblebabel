import sys

import game, player

def main(**args):
  print "Initializing game..."
  g = game.Game()
  p = player.Player(g)
  
  command = raw_input("scrabble% ")
  while command:
    eval(command)

if __name__ == "__main__": main()

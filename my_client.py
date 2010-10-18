#! /usr/bin/env python
"""
Usage: %s <client ID>

Solves the No Tipping problem (http://cs.nyu.edu/courses/fall10/G22.2965-001/mint.html)
"""
import os
import sys
import time
import math

## Infinity = ()
## Negative Infinity = None

start_time = time.time()
default_board = [0]*31
default_board[-4+15] = 3

class GameState:
    def __init__(self,max=True,board=default_board,my_weights=range(1,11),their_weights=range(1,11)):
        if max:
            self.max = True
        else:
            self.max = False
        if self.max:
            self.score = float('-Inf')
        else:
            self.score = float('Inf')
        self.board = board
        self.rt = float('-Inf')
        self.lt = float('-Inf')
        self.children = []
        self.my_weights = my_weights
        self.their_weights = their_weights

    def __repr__(self):
        return "Max: %s\tScore: %s\nBoard: %s\nMy Weights: %s\nTheir Weights: %s" % \
            (repr(self.max), repr(self.score), repr(self.board), repr(self.my_weights), repr(self.their_weights) )

    def __cmp__(self,n2):
        return self.score - n2.score

    # simple scoring
    def do_score(self):
        self.score = len(self.children)

    def p(self):
        for kg in self.board:
            print repr(kg) + " ",
        print ""

    def move_weight(self,weight,pos):
        try:
            # print "Moving " + repr(weight) + " to " + repr(pos)
            if self.max:
                self.my_weights.remove(weight)
            else:
                self.their_weights.remove(weight)
            if self.board[pos] > 0:
                print "Error! Weight " + repr(self.board[pos]) + " already at " + repr(pos)
                print repr(self.board)
                sys.exit(1)
            else:
                self.board[pos] = weight
        except ValueError:
            print self
            print weight
            print pos
            raise
        
    def tip(self):
        
        # formula to calulate torque:
        # in1 and out1 calculates torque on lever at -1
        # in3 and out3 calculates torque on lever at -3
        
        # At -3, the tip occurs when torque on the left > torque on right or out3-in3 > 0
        # At -1, the tip occurs when torque on the right > torque on left or in1-out1 > 0
        # If either of the conditions hold true, the player loses the game
        # the board weights 3 kgs which is concentrated at 0, so there is some intorque at -3 and -1

        in1 = 3
        out1 = 0
        in3 = 9
        out3 = 0
        
        # board contains each weight at its position

        pos = -15

        for kg in self.board:
            if pos < -3:
                out3 += -(pos+3)*kg
            else:
                in3 += (pos+3)*kg

            if pos < -1:
                out1 += -(pos+1)*kg
            else:
                in1 += (pos+1)*kg

            pos += 1

        self.rt = in1 - out1
        self.lt = out3 - in3
        
    def did_tip(self):
        if self.rt == float('-Inf') or self.lt == float('-Inf'):
            self.tip()
        return self.lt > 0 or self.rt > 0


def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

def make_babies(parent):
    for pos in range(0,len(parent.board)):
        if parent.board[pos] > 0:
            continue
        current_weights = []
        if parent.max:
            current_weights = parent.their_weights
        else:
            current_weights = parent.my_weights
    
        for kg in current_weights:
            # inherit from parents
            c = GameState(not parent.max, board = parent.board + [],\
                         my_weights = parent.my_weights + [],\
                         their_weights = parent.their_weights + [])
            # make the move :-*
            c.move_weight(kg,pos)
            # only claim children if they're successful :)
            if not c.did_tip():
                print c
                parent.children.append( c )
    parent.do_score()

## from http://en.wikipedia.org/wiki/Alpha-beta_pruning
def alphabeta(n, depth, a, b):
    ## b represents previous player best choice - doesn't want it if a would worsen it
    make_babies(n)
    if  depth == 0 or n.children == []:
        return n.score
    for child in n.children:
        t = -alphabeta(child, depth-1, -b, -a)
        a = max(a, t)
## use symmetry, -b becomes subsequently pruned a
        if b <= a:
            break ## Beta cut-off
    return a

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    root = GameState(False) # create a max node

    a, node = alphabeta( root, 3, float('-Inf'), float('Inf') )
    print a
    print node

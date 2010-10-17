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

class Node:
    def __init__(self,type):
        # self.max = type == "max" ? True : False
        # self.score = self.max ? float('-Inf') : float('Inf')
        self.score = float('-Inf')
        self.board = [-1]*31
        self.board[-4+15] = 3
        self.rt = float('-Inf')
        self.lt = float('-Inf')
        self.children = []
        self.my_weights = range(1,11)
        self.their_weights = range(1,11)

    def __repr__(self):
        return "Max: %s\tScore: %s" % (repr(self.max), repr(self.score))

    def __cmp__(self,n2):
        return self.score - n2.score

    def p():
        for kg in self.board:
            print repr(kg) + " ",
        print ""

    def tip():
        
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
        
    def did_tip():
        if self.rt == float('-Inf') || self.lt == float('-Inf'):
            self.tip()
        return self.lt > 0 || self.rt > 0


def usage():
    sys.stdout.write( __doc__ % os.path.basename(sys.argv[0]))

def make_babies(node):
    for pos in node.board:
        pos -= 15
        # make the move
        for kg in node.my_weights:
            # transfer state over
            child = Node
            child.board = node.board
            child.my_weights = node.my_weights
            child.their_weights = node.their_weights
            child.move(kg, pos)
            # only claim children if they're successful :)
            if !child.did_tip():
                node.children.append( child )

## from http://en.wikipedia.org/wiki/Alpha-beta_pruning
def alphabeta(n, depth, a, b):
    ## b represents previous player best choice - doesn't want it if a would worsen it
    n.children = make_babies(n)
    if  depth == 0 or n.children == []
        return n.score,n
    for child in n.children:
        a = max(a, -alphabeta(child, depth-1, -b, -a)[0])
        ## use symmetry, -b becomes subsequently pruned a
        if b <= a
            break ## Beta cut-off
    return a

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    alphabeta(root, 10, float('-Inf'), float('Inf') )

    

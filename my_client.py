#! /usr/bin/env python
"""
Usage: %s <client ID>

Solves the No Tipping problem (http://cs.nyu.edu/courses/fall10/G22.2965-001/mint.html)
"""
import os
import sys
import time
import math
import socket
import re

MSGLEN = 1024
start_time = time.time()
default_board = [0]*31
default_board[-4+15] = 3

class MySocket:
# from http://docs.python.org/howto/sockets.html
    '''demonstration class only
      - coded for clarity, not efficiency
    '''

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        sent = self.sock.send(msg + "\r\n")
        if sent == 0:
            raise RuntimeError("socket connection broken")
        
    def myrecv(self):
        while 1:
            data = self.sock.recv(1024)
            if not data or data == "Bye" or "\n" in data: break
        print 'Received',repr(data)
        return data

    def close(self):
        if self.sock is None:
            pass
        else:
            self.sock.close()

class GameState:
    def __init__(self,max=True,board=default_board,my_weights=range(1,11),their_weights=range(1,11),first_move=None,parent_node=None):
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
        self.first_move = first_move
        self.parent_node = parent_node

    def __repr__(self):
        return "Max: %s\tScore: %s\nBoard: %s\nMy Weights: %s\nTheir Weights: %s" % \
            (repr(self.max), repr(self.score), repr(self.board), repr(self.my_weights), repr(self.their_weights) )

    # simple scoring
    def do_score(self):
        if self.max:
            self.score = sum(self.their_weights) - sum(self.my_weights)
        else:
            self.score = sum(self.my_weights) - sum(self.their_weights)
        # print "Score: ",self.score,"\n",self.my_weights,"\n",self.their_weights

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
            if parent.first_move is None and c.max:
                c.first_move = repr(kg) + "," + repr(pos-15)
            else:
                c.first_move = parent.first_move
            c.move_weight(kg,pos)
            # only claim children if they're successful :)
            if not c.did_tip():
                parent.children.append( c )
                c.parent_node = parent

def remove_weights(parent):
    # new tree now that we're removing
    parent.children = []
    for kg in parent.board:
        c = GameState(not parent.max, board = parent.board + [],\
                          my_weights = parent.my_weights + [],\
                          their_weights = parent.their_weights + [])
        # make the move :-*
        if parent.first_move == "":
            c.first_move = repr(kg) + "," + repr(pos)
        else:
            c.first_move = parent.first_move
        c.move_weight(kg,pos)
        # only claim children if they're successful :)
        if not c.did_tip():
            parent.children.append( c )

def alphabeta(n, depth, a, b):
    ## b represents previous player best choice - doesn't want it if a would worsen it
    make_babies(n)
    # print len(n.children)
    if (depth == 0 or len(n.children) == 0):
        n.do_score()
        return (n.score,n)
    if n.max:
        v = a
        for child in n.children:
            t,node = alphabeta(child, depth-1, v, b)
            if t > v:
                v = t
            if v > b:
                return b,child
        return v,node
    else:
        v = b
        for child in n.children:
            t,node = alphabeta(child, depth-1, a, v)
            if t < v:
                v = t
            if v < a:
                return a,child
        return v,node

def get_move(root=GameState(True)):
    a = alphabeta( root, 2, float('-Inf'), float('Inf') )
    return a[1]

def get_remove(root=GameState(True)):
    a = alphabeta( root, 2, float('-Inf'), float('Inf') )
    return a[1]

def parse_data(data):
    # ADD|3,-4 10,-1|in=-6.0,out=-26.0
    data = data.split('\n')[1]
    for d in data:
        if "ADD" in d:
            data = d
            break
    mode = re.match('(?<=|)\w+',data)
    # take off beginning
    data = data[len(mode.group(0))+1:]
    data = data.split('|')[0]
    tuples = data.split(' ')
    this_board = [0]*31
    for t in tuples:
        t = t.split(',')
        this_board[int(t[1])+15] = int(t[0])
    all_used_weights = []
    their_used_weights = []
    their_weights_t = []
    my_used_weights = []
    for kg in this_board:
        if kg > 0:
            all_used_weights.append(kg)
    try:
        all_used_weights.remove(3) #for the initial weight
    except:
        pass
    print "All used weights: ",all_used_weights #actually used_weights
    # figure out what i've used
    for i in range(1,11):
        if i not in save_weights:
            my_used_weights.append(i)
    # remove those from all the used weights to find out
    # what the opponent has used
    print "My used weights: ",my_used_weights #actually used_weights
    for kg in my_used_weights:
        try:
            all_used_weights.remove(kg)
        except:
            # this is for the very last weight that i just moved
            # yes i know it's ugly.
            pass

    their_used_weights = all_used_weights
    for i in range(1,11):
        if i not in their_used_weights:
            their_weights_t.append(i)

    return GameState(True,board=this_board,\
                         my_weights=save_weights + [],\
                         their_weights=their_weights_t + [])

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    save_weights = range(1,11)
    
    tag = sys.argv[1]

    s = MySocket()
    s.connect("localhost", 44444)
    s.mysend(tag)
    while 1:
        data = s.myrecv()
        if "REJECT" in data:
            print "Oops..."
            break
        if "WIN" in data:
            print "Woot."
            break
        if "LOSE" in data:
            print ":'("
            break
        if "ADD" in data:
            root = parse_data(data)
            print root
            print "Calculating..."
            state = get_move(root)
            s.mysend(state.first_move + "\n")
            save_weights = state.my_weights
            print "Sent result ", state.first_move
        if "REMOVE" in data:
            root = parse_data(data)
            print root
            print "Calculating..."
            state = get_remove(root)
            s.mysend(state.first_move + "\n")
            save_weights = state.my_weights
            print "Sent result ", state.first_move

    s.close()

    print "Time: ",round(time.time() - start_time)

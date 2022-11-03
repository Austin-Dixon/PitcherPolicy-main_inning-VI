# -*- coding: utf-8 -*-
"""
Created on Thu May 26 09:59:15 2022

@author: nitsu
"""
import json
import numpy as np
from tensorflow.keras import models

from pitch_zone_config import (
    gen_pitches,
    gen_counts,
    gen_acc_mat,
    gen_trans_prob_mat,
    SWING_TRANS_PATH,
    NN_SWING_TRANS_PATH,
    gen_swing_trans_matrix,
    gen_take_mat
)
from stochastic_game import StochasticGame
from state import Inning
import copy
from time import time

def nxt(b):
    i=b.index(1)
    if i==8:
        nxt=0
    else:
        nxt=i+1
    batter=list(NONE)
    batter[nxt]=1
    return(tuple(batter))

start=time()
NONE=(0,0,0,0,0,0,0,0,0)
ACTIONS=("strike","foul","ball","strikeout","groundout","single","double","triple","home run")

#generate all possible Inning game states (with absolute order)
N=10
b=(1,0,0,0,0,0,0,0,0)
bs=[]
for i in range(9):
    bs.append(b)
    b=nxt(b)

#Alternative iteral brute force establishment of states    
states=[]
for b in bs:
    for b1 in range(2):
        for b2 in range(2):
            for b3 in range(2):
                for ball in range(4):
                    for strike in range(3):
                        for run in range(N):
                            for out in range(3):
                                states.append(Inning(b,{1:b1,2:b2,3:b3},{"balls":ball,"strikes":strike,"runs":run,"outs":out},N))
for i in range(N+1):
    states.append(Inning(NONE,{1:0,2:0,3:0},{"balls":0,"strikes":0,"runs":i,"outs":3},N))

#load pitch tensors
with open("./tensors/pitcher_tensors.json") as f:
    pitcher_tensors = json.load(f)

# load batter tensors
with open("./tensors/batter_tensors.json") as f:
    batter_tensors = json.load(f)

# open 3 TensorFlow models
take_model = models.load_model("../models/take_2015-2018.h5")
swing_trans_model = models.load_model("../models/transition_model_2015-2018.h5")
acc_model = models.load_model("../models/error_2015-2018.h5")

pitcher=pitcher_tensors['607536']
batters={}

#storage of take zones and transition probabilities for each batter
takes={}
transitions={}

#generate pitch types and possible count states
pitches = gen_pitches()
counts = gen_counts()

#generare accurracy matrix for selected pitcher
acc_mat = gen_acc_mat(acc_model, pitcher, pitches)

#generate batting team, map to positions, and transition probabilities for each batter
team=['572761','641933','502671','571448','405395','572816','657557','425877','542303']
for i in range(9):
    bid=list(NONE)
    bid[i]=1
    bid=tuple(bid)
    batters[bid]= batter_tensors[team[i]]
    take_mat = gen_take_mat(take_model, batters[bid], pitches, .2)
    nn_swing_trans_mat = gen_swing_trans_matrix(swing_trans_model, pitcher, batters[bid], take_mat, pitches)
    nn_trans_prob_mat = gen_trans_prob_mat(nn_swing_trans_mat, acc_mat, take_mat)
    takes[bid]=take_mat
    transitions[bid]=nn_trans_prob_mat

#generate entry for terminal states with no probability of transitioning
transitions[NONE]=copy.deepcopy(transitions[(1,0,0,0,0,0,0,0,0)])
for pitch in transitions[NONE]:
    for zone in transitions[NONE][pitch]:
        for count in transitions[NONE][pitch][zone]:
            for batact in transitions[NONE][pitch][zone][count]:
                for res in transitions[NONE][pitch][zone][count][batact]:
                    transitions[NONE][pitch][zone][count][batact][res]=0

#generate and solve game with given team and transitions
s1 = StochasticGame(states, transitions)
s1_vals, s1_pol = s1.solve_game()

#Measure time displacement
end = time()
total = end - start
hrs = int(total // 3600)
mins = int((total % 3600) // 60)
secs =  (total % 3600) % 60
print("In",hrs, "Hours,",mins,"Minutes,",format(secs,".2f"),"Seconds.")

#save data in files
# with open("fullvals10.json","w") as file:
#     file.write(json.dumps(s1_vals))

# with open("fullpols10.json","w") as file:
#     file.write(json.dumps(s1_pol))

# #load saved data
# with open("fullvals10.json") as file:
#     s1_vals=json.load(file)

# with open("fullpols10.json") as file:
#     s1_pol=json.load(file)
    
#Get date to an easier-to-read state
simple_vals={x:s1_vals[x][-1] for x in s1_vals}
simple_pol={}
for state in s1_pol:
    pitches={}
    for pitch in s1_pol[state]:
        for zone in s1_pol[state][pitch]:
            pitches[(pitch,zone)]=s1_pol[state][pitch][zone]
    simple_pol[state]=pitches
    
with open("results.json") as file:
    results=json.load(file)
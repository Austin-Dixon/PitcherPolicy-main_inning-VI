# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 18:53:51 2022

@author: nitsu
"""

import json
from tensorflow.keras import models

import pitch_zone_configa as a
import pitch_zone_configb as b
import numpy as np

with open("./tensors/pitcher_tensors.json") as f:
    pitcher_tensors = json.load(f)

# load batter tensors
with open("./tensors/batter_tensors.json") as f:
    batter_tensors = json.load(f)

# open 3 TensorFlow models
take_model = models.load_model("../models/take_2015-2018.h5")
acc_model = models.load_model("../models/error_2015-2018.h5")

# Set pitcher/batter matchup for the at bat
#pitcher_id, batter_id = 543037, 448801  # Gerrit Cole, Chris Davis
pitcher_id, batter_id = 607536, 572761  # Gerrit Cole, Chris Davis

pitcher = np.array(pitcher_tensors[str(pitcher_id)])
batter = np.array(batter_tensors[str(batter_id)])

pitches = b.gen_pitches()
counts = b.gen_counts()

swing_trans_model = models.load_model("transition_model_basic.h5")
acc_mat = b.gen_acc_mat(acc_model, pitcher, pitches)
take_mat = b.gen_take_mat(take_model, batter, pitches, .2)
nn_swing_trans_mat = b.gen_swing_trans_matrix(swing_trans_model, pitcher, batter, take_mat, pitches)
nn_trans_prob_mat_basic = b.gen_trans_prob_mat(nn_swing_trans_mat, acc_mat, take_mat)


swing_trans_model = models.load_model("transition_model_mine.h5")
acc_mat = a.gen_acc_mat(acc_model, pitcher, pitches)
take_mat = a.gen_take_mat(take_model, batter, pitches, .2)
nn_swing_trans_mat = a.gen_swing_trans_matrix(swing_trans_model, pitcher, batter, take_mat, pitches)
nn_trans_prob_mat_mine = a.gen_trans_prob_mat(nn_swing_trans_mat, acc_mat, take_mat)

swing_trans_model = models.load_model("transition_model_connor.h5")
acc_mat = a.gen_acc_mat(acc_model, pitcher, pitches)
take_mat = a.gen_take_mat(take_model, batter, pitches, .2)
nn_swing_trans_mat = a.gen_swing_trans_matrix(swing_trans_model, pitcher, batter, take_mat, pitches)
nn_trans_prob_mat_connor = a.gen_trans_prob_mat(nn_swing_trans_mat, acc_mat, take_mat)

ACTIONS=["hit","foul","strike","ball","out"]
swing={a:[0,0,0] for a in ACTIONS}
take={"strike":[0,0,0],"ball":[0,0,0]}

for pitch in nn_trans_prob_mat_basic:
    for zone in nn_trans_prob_mat_basic[pitch]:
        for count in nn_trans_prob_mat_basic[pitch][zone]:
            for res in nn_trans_prob_mat_basic[pitch][zone][count]["swing"]:
                swing[res][0]+=nn_trans_prob_mat_basic[pitch][zone][count]["swing"][res]
            for res in nn_trans_prob_mat_basic[pitch][zone][count]["take"]:
                take[res][0]+=nn_trans_prob_mat_basic[pitch][zone][count]["take"][res]

for pitch in nn_trans_prob_mat_mine:
    for zone in nn_trans_prob_mat_mine[pitch]:
        for count in nn_trans_prob_mat_mine[pitch][zone]:
            for res in nn_trans_prob_mat_mine[pitch][zone][count]["swing"]:
                if res in ["single","double","triple","home run"]:
                    swing["hit"][1]+=nn_trans_prob_mat_mine[pitch][zone][count]["swing"][res]
                else:
                    swing[res][1]+=nn_trans_prob_mat_mine[pitch][zone][count]["swing"][res]
            for res in nn_trans_prob_mat_mine[pitch][zone][count]["take"]:
                take[res][1]+=nn_trans_prob_mat_mine[pitch][zone][count]["take"][res]
                
for pitch in nn_trans_prob_mat_connor:
    for zone in nn_trans_prob_mat_connor[pitch]:
        for count in nn_trans_prob_mat_connor[pitch][zone]:
            for res in nn_trans_prob_mat_connor[pitch][zone][count]["swing"]:
                if res in ["single","double","triple","homerun"]:
                    swing["hit"][2]+=nn_trans_prob_mat_connor[pitch][zone][count]["swing"][res]
                else:
                    swing[res][2]+=nn_trans_prob_mat_connor[pitch][zone][count]["swing"][res]
            for res in nn_trans_prob_mat_connor[pitch][zone][count]["take"]:
                take[res][2]+=nn_trans_prob_mat_connor[pitch][zone][count]["take"][res]
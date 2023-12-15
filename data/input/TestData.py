# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 13:59:55 2023

@author: 20183233
"""
import pandas as pd
import numpy as np
import random

def test_deadlines(data: pd.DataFrame, deadlines: [int]):
    """
    Assigns new possible deadlines for test data. Deadlines will be assigned
    to 12:00:00 starting from day 0

    Parameters
    ----------
        data : Metal scheduling data.
        deadlines : New deadlines (days).
    
    Returns
    -------
        test : Test data with new deadlines.

    """
    new_deadlines_sec = [None] * len(deadlines)
    for i, j in enumerate(deadlines):  # make a list of the new deadlines relative to the starting time in seconds
        new_deadlines_sec[i] = new_deadlines_sec[i] = 259200 + j*24*3600 #first deadline at midnight of the 3rd day (production start just before midnight of the second day)

    k, m = divmod(len(data), len(new_deadlines_sec))  # determine the number of segments

    test = data.copy()

    # assign the new deadlines
    for l in range(len(test['due'])):
        test.loc[l,'due'] = random.choice(new_deadlines_sec)

    return test

def generate(numberRuns: int, numberPeaks: [int], numberDeadlines: int):
    means = [[2500, 16000, 30000],
             [3500, 8000, 12000],
             [14000, 18000, 25000]]

    numberPeaksTotal = sum(numberPeaks)

    num_machines = 3

    # generate deadlines
    d = list(range(7))
    random.shuffle(d)
    deadlines = d[:numberDeadlines]

    lijsten = []
    for i,ms in enumerate(means):
        lengths = np.concatenate([
                np.random.normal(m, 100, size=numberRuns // numberPeaksTotal) for m in ms])
        metallist = np.full(numberRuns*3 // numberPeaksTotal, i)
        lijsten.append(list(zip(lengths, metallist)))

    rows = []
    for i, (len3, metal) in enumerate(np.concatenate(lijsten)):
        len3 = max(1,int(len3))
        rows.append([
            "A" + str(i),
            max(0,len3-2),
            "B" + str(i),
            max(0,len3-1),
            "C" + str(i),
            len3,
            int(metal),
            0
        ])

    df = pd.DataFrame(rows, columns=["step1", "len1", "step2", "len2", "step3", "len3", "metal", "due"])
    df = test_deadlines(df, deadlines)

    df.to_csv("./data/input/random_data.csv", index=False)


generate(90, [3,3,3], 3)

# -*- coding: utf-8 -*-
"""
Created on 2020/1/21

@author: fk506cni=unkodaisuki!

expressions class.
"""

import pandas as pd
# from pyqubo import AddList, Binary, Express, Mul, Model, Num
import pandas as pd
from tqdm import tqdm
import itertools as it

class nsp_expressions():

    Q =dict()
    max_val=1
    keys = set()
    nodes = set()


    def __init__(self):
        print("nsp_expression activated!")

    def Q_update(self, dict, weight=1):
        for key, value in dict.items():
            if key in self.keys:
                self.Q[key] += weight*value
            elif (key[1], key[0]) in self.keys:
                self.Q[(key[1], key[0])] += weight * value
            else:
                self.Q[key] = weight*value
                self.keys.add(key)
                self.nodes.add(key[0])
                self.nodes.add(key[1])
    #     about max value..
    #     self.max_val = max(self.Q.values())

    def Q_show(self, key):
        print(self.Q[key])

    def Q_show_all(self):
        print(self.Q)

    def Q_reset(self):
        self.Q = dict()
        self.keys = set()
        self.max_val = 1
        print("Q dict is resetted!")

    def Q_normalize(self, max4compe=1):
        print("normalization!")
        self.max_val = max(list(self.Q.values()))
        div_val = self.max_val /max4compe
        for key, val in self.Q.items():
            self.Q[key] = self.Q[key] / div_val

    def getQ(self):
        return self.Q.copy()

    def getMaxVal(self):
        return self.max_val
    
    def getQ_asDF(self):
        l_n1 = []
        l_n2 = []
        l_val = []
        for key, val in tqdm(self.Q.items()):
            l_n1.append(key[0])
            l_n2.append(key[1])
            l_val.append(val)
        df = pd.DataFrame(columns = ["n1", "n2", "val"])
        df["n1"] = l_n1
        df["n2"] = l_n2
        df["val"] = l_val

        return df

    def saveQ_asCSV(self, path):
        df = self.getQ_asDF()
        df.to_csv(path, sep=",", index=None)

    def readQ_fromCSV(self,path):
        self.Q_reset()

        df = pd.read_csv(path)

        for r in tqdm(df.itertuples()):
            self.Q[(r.n1, r.n2)] = r.val
            self.keys = (r.n1, r.n2)
        st1 = set(list(df["n1"].unique().tolist()))
        st2 = set(list(df["n2"].unique().tolist()))

        self.nodes = st1.union(st2)
        self.max_val = df["val"].max()

    def getNodes(self):
        nodes = set()
        for e in self.keys:
            nodes.add(e[0])
            nodes.add(e[1])
        return nodes

    def decode(self, res):
        pos_nodes = set([k for k, v in res.items() if v != 0])
        q_vals = [v for c, v in self.Q.items() if c[0] in pos_nodes and c[1] in pos_nodes]
        # energy =0
        # pos_nodes2_list =[c for c in it.combinations_with_replacement(pos_nodes, 2) if (c in self.keys) or ((c[1], c[0]) in self.keys)]
        # pos_e = [self.Q[c] for c in pos_nodes2_list]


        # for c in it.combinations(pos_nodes, 2):
        #     if c in self.keys:
        #         energy += self.Q[c]
        #     elif (c[1], c[0]) in self.keys:
        #         energy += self.Q[(c[1], c[0])]
        #     else:
        #         pass
        # for k in pos_nodes:
        #     if (k, k) in self.keys:
        #         energy += self.Q[(k, k)]
        return sum(q_vals)
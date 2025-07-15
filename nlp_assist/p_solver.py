# -*- coding: utf-8 -*-
"""
Created on 2020/1/21

@author: fk506cni=unkodaisuki!

pallale solver

in Q
out res dict and Energy.
"""


# from pyqubo import solve_qubo, Model
from neal.sampler import SimulatedAnnealingSampler as sa
from multiprocessing import Manager
from multiprocessing import Pool
from collections import namedtuple
import gc


class psol():

    def __init__(self,
                 q,
                 num_reads=10,
                 sweeps=100,
                 seed=114514
                 ):
        print("pallalel processing!")
        print("process condition: num_reads=" +
              str(num_reads)+", sweeps="+str(sweeps))
        self.q = q
        self.num_reads = num_reads
        self.sweeps = sweeps
        manager = Manager()
        self.returned_dict = manager.dict()
        self.seed = seed

    def decodoE(self, res):
        pos_nodes = set([k for k, v in res.items() if v != 0])
        q_vals = [v for c, v in self.q.items() if c[0]
                  in pos_nodes and c[1] in pos_nodes]
        return sum(q_vals)

    def s_solve(self, ind):
        # print("solving...")
        s = sa()
        # res = solve_qubo(qubo=self.q,
        #                  num_reads=self.num_reads,
        #                  sweeps=self.sweeps)
        res = s.sample_qubo(self.q,
                            num_reads=self.num_reads,
                            # sweeps=self.sweeps,
                            num_sweeps=self.sweeps,
                            seed=self.seed + ind)

        # l_s = []
        # l_e = []
        # l_num = []
        # for s, e, n in res.data(["sample", "energy", "num_occurrences"]):
        #     l_s.append(s)
        #     l_e.append(e)
        #     l_num.append(n)
        #
        # s_min = [s for s in l_s ]

        # res_t = namedtuple("Result", "ind energy sample")
        res1 = next(res.data())
        # res_t.ind = ind
        # res_t.energy = res1.energy
        # res_t.sample = res1.sample

        # energy = 0
        l = [ind, res1.energy, res1.sample]
        del s
        gc.collect()

        return l

    def p_solve(self, threads=4, times=4):
        # rd = Manager().dict()
        # process_list = []
        p = Pool(threads)
        print("solving coditions:threds " +
              str(threads) + ",times "+str(times))
        result_list = p.map(self.s_solve, range(times))
        p.close()  # add this.
        p.terminate()  # add this.
        res = []
        for l in result_list:
            res_t = namedtuple("Result", "ind energy sample num sweep")
            res_t.ind = l[0]
            res_t.energy = l[1]
            res_t.sample = l[2]
            res_t.num = self.num_reads
            res_t.sweep = self.sweeps
            res.append(res_t)
        del p, result_list
        gc.collect()
        return res

    def p_solve_getMin(self, threads=4, times=4):
        res = self.p_solve(threads=threads, times=times)

        e_list = [r.energy for r in res]
        ind_list = [r.ind for r in res]
        print(e_list)
        print(ind_list)
        min_list = [r for r in res if r.energy == min(e_list)]
        min_t = min_list[0]

        res_t = namedtuple("mim_Result", "ind energy sample")
        res_t.ind = min_t.ind
        res_t.energy = min_t.energy
        res_t.sample = min_t.sample
        return res_t

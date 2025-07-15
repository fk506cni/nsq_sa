# -*- coding: utf-8 -*-
"""
Created on 2020/4/10

@author: fk506cni=unkodaisuki!
"""


class nsp_settings():

    check_list = ["1by1",
                  "cnight", "cwork", "fseq", "nseq",
                  "eqg3", "eqg2",
                  "rqn",
                  "rqh",
                  "tt",
                  "tn",
                  "sc",
                  "mps",
                  "dab",
                  "nnv",
                  # "oAb", "wres",
                  # "eq", "eqn",
                  "lfbd", "lnd", "lcnt", "lcnn"]
    param_dict = {
        "1by1": 500,
        # "1p1": 200,
        "cnight": 200,
        "cwork": 200,
        "fseq": 300,
        "nseq": 300,
        "eqg3": 10,
        "eqg2": 10,
        "rqn": 200,
        "rqh": 100,
        "tt": 100,
        "tn": 100,
        "sc": 100,
        "mps": 300,
        "dab": 100,
        "nnv": 100,

        # "oAb":200,
        # "wres":200,
        # "eq": 10,
        # "eqn": 10,
        "lfbd": 50,
        "lnd": 50,
        "lcnt": 200,
        "lcnn": 50
    }

    log_class = {
        1: "continuous_work",
        2: "dt1_to_dt2",
        3: "dt2_to_dt3",
        4: "continuous_night",
        5: "one_point_one",
        6: "ability",
        7: "takability",
        8: "work_equality",
        9: "over_total_works",
        10: "over_night_works",
        11: "night_work_equality",
        12: "each group dist dt3",
        13: "forbiden from last",
        14: "needpair from last",
        15: "cont work from last",
        16: "cont night from last",
        17: "xzxx",
        18: "xxxx"
    }


# p = ps.psol(q=qg.ne.getQ(),
#              num_reads=2,
#              sweeps=3000, seed=10)
#
# mins = p.p_solve_getMin(threads=5, times=5)

#
# import res_parser as rps
# importlib.reload(rps)
# rp = rps.res_parser(x=x)
# rp.prepRes(res=mins.sample, hideProgressBar=True)
# rc = rps.res_checker(x=x)

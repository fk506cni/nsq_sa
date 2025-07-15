# -*- coding: utf-8 -*-
"""
Created on 2020/1/4

@author: fk506cni=unkodaisuki!
"""

# from pyqubo import AddList, Binary, Express, Mul, Model, Num
from pyqubo import Num
import pandas as pd
import itertools as it
import nsp_expressions
from tqdm import tqdm
from collections import namedtuple
import nsp_settings


class dummy_var_gen():
    count = 0

    def __init__(self, start_count=0):
        self.count = start_count
        print("dummy var generator activated")
        print("start status is " + str(start_count))

    def getDVstr(self, m, prefix="dv"):
        l = [prefix + "_" + str(i + self.count + 1) for i in range(0, m)]
        self.count += m
        return l

    def getDVnum(self, m):
        l = [i + self.count + 1 for i in range(0, m)]
        self.count += m
        return l

    def get1DVstr(self, prefix="dv"):
        dv = prefix+"_"+str(self.count)
        self.count += 1
        return dv


class limiter():
    one = Num(1)
    zero = Num(0)
    dg = dummy_var_gen()

    # 制約項のペナルティウェイト
    param_cover = 1.0
    # プレースホルダーと合わせてQUBOを作成
    feed_dict = {'cover': param_cover}

    def __init__(self):
        print("limter activated!")

    # 準備関数群

    def dict_normalize(self, d, max4compe=1):
        # print("normalization!")
        max_val = max(list(d.values()))
        div_val = max_val / max4compe
        for key, val in d.items():
            d[key] = d[key] / div_val
        return d

    def getCoefVarsLimitM(self, m, get_minus_val=False):
        # 与えら得たmについて、0~mを満たす係数と変数のリストを吐く。

        bin_1 = bin(m)
        # b_ones = bin(2**(len(bin_1) -3) -1)
        b_sub = bin(m - 2 ** (len(bin_1) - 3) + 1)

        coef_list = []
        var_list = []
        for i in range(len(bin_1) - 3):
            coef_list.append(2 ** i)
            var_list.append(self.dg.get1DVstr())

        # ここから修正。要するに2の乗数で入れれないだけの数を入れる。
        sub_int = int(b_sub, 0)
        coef_list.append(sub_int)
        var_list.append(self.dg.get1DVstr())

        # b_sub_rev = b_sub[2:][::-1]

        # for i, s in enumerate(b_sub_rev):
        #     # print(i, s)
        #     if s == "1":
        #         # print(i)
        #         coef_list.append(2 ** i)
        #         var_list.append(self.dg.get1DVstr())
        if get_minus_val:
            coef_list = [-i for i in coef_list]
            return [coef_list, var_list]
        else:
            return [coef_list, var_list]

    def conv_list_2list2nest(self, l):
        # 長リスト2丁を、ペアネストリストに変換
        l1 = l[0]
        l2 = l[1]
        res = [[i, j] for i, j in zip(l[0], l[1])]
        return res

    def getQ_NtoXs2(self, n, xs):
        # 2式等号 N to multi
        # nは自然数
        # xsは、[coef, var]のペアネステッドリストである。
        # 負のcoefも対応可能なはず。

        if type(xs) == "tuple":
            xs = list(xs)
        exp_dict = dict()
        # はじめに2項演算
        for c1, c2 in it.combinations(xs, 2):
            exp_dict[(c1[1], c2[1])] = 2 * c1[0] * c2[0]

        # x^2の追加
        # -2xnの追加
        for x in xs:
            exp_dict[(x[1], x[1])] = x[0] ** 2 - 2 * n * x[0]  # -2*n +1

        return exp_dict

    def getQ_NtoXs(self, n, xs):
        # 2式等号 N to multi
        # Expressionを返す。Penalty係数はまだ。
        # n should be number
        # xs should be list of str, var name.
        if type(xs) == "tuple":
            xs = list(xs)

        exp_dict = dict()
        # はじめに2項演算
        for c in it.combinations(xs, 2):
            exp_dict[c] = 2

            # x^2の追加
            # -2xnの追加
        for x in xs:
            exp_dict[(x, x)] = -2*n + 1

        return exp_dict

    def getQ_fromVarAndCoef(self,
                            var_list,
                            coef_list=None,
                            min_int=None,
                            max_int=None):
        # 最大値、最小値の間に収まるようなQを作る。
        # if coef is null, should be all 1
        # if min int =null, will be 0
        # if max int =null, will be
        if coef_list is None:
            coef_list = [1 for i in var_list]
        if min_int is None:
            min_int = 0
        if max_int is None:
            coef_list_max = [i if i > 0 else 0 for i in coef_list]
            max_int = sum(coef_list_max)

        sub_int = max_int - min_int
        # print(sub_int)
        sub_dvs = self.getCoefVarsLimitM(sub_int, get_minus_val=True)
        # print(sub_dvs)
        sub_dvs = self.conv_list_2list2nest(sub_dvs)
        sum_vars = self.conv_list_2list2nest([coef_list, var_list])

        xs = sum_vars + sub_dvs

        q = self.getQ_NtoXs2(min_int, xs)
        # q = self.dict_normalize(d=q,max4compe=1)
        return q

    def getQ_fromVars_max1(self, var_list):
        # これだけは別に作ったほうが良さそう。最大で1の場合。
        # つまり2つ以上の変数が１になってはならない。
        exp_dict = dict()
        for c in it.combinations(var_list, 2):
            exp_dict[c] = 1
        return exp_dict

    def getQ_avoidAllPosV2(self, vart_2):
        # require tupel of 2
        return {vart_2: 1}

    def getQ_avoidAllPosV2_list(self, vart2_list):
        exp_dict = dict()
        # require tupel of 2
        for v in vart2_list:
            exp_dict[v] = 1
        return exp_dict

    def getQ_not1(self, vart_2):
        exp_dict = {
            (vart_2[0], vart_2[1]): -2,
            (vart_2[0], vart_2[0]): 1,
            (vart_2[1], vart_2[1]): 1
        }
        return exp_dict

    def getQ_not1_list(self, vart2_list):
        exp_dict = dict()
        for v in vart2_list:
            exp_dict[(v[0], v[0])] = exp_dict.get((v[0], v[0]), 0) + 1
            exp_dict[(v[1], v[1])] = exp_dict.get((v[1], v[1]), 0) + 1
            exp_dict[tuple(v)] = -2
        return exp_dict

    def getQ_not1_var1_list(self, xs):
        # require xs is all negative.
        exp_dict = dict()
        for x in xs:
            exp_dict[(x, x)] = 1
        return exp_dict

    def getQ_YsEqXs(self, ys, xs):
        if type(xs) == "tuple":
            xs = list(xs)
        if type(ys) == "tuple":
            ys = list(ys)

        exp_dict = dict()
        # はじめに二項演算
        for c in it.combinations(ys, 2):
            exp_dict[c] = 2

        for c in it.combinations(xs, 2):
            exp_dict[c] = 2

        for c in it.product(ys, xs):
            exp_dict[c] = -2

        # x^2の追加
        for x in xs:
            exp_dict[(x, x)] = 1
        for y in ys:
            exp_dict[(y, y)] = 1

        return exp_dict

    def getQ_forbidXs(self, xs):
        exp_dict = dict()
        for x in xs:
            exp_dict[(x, x)] = 1
        return exp_dict

    def getQ_avoidBothPos_list(self, xs, ys):
        # xs, ys両方が陽性になることを防ぐ
        # 係数は他の二項演算に習い2である。それには注意。

        # 片方0なら何もしない
        if len(xs) == 0 or len(ys) == 0:
            return dict()
        else:
            if type(xs) == "tuple":
                xs = list(xs)
            if type(ys) == "tuple":
                ys = list(ys)

            exp_dict = dict()

            for c in it.product(ys, xs):
                exp_dict[c] = 2
            return exp_dict

    def getQ_XsIsOne(self, xs):
        return self.getQ_NtoXs(n=1, xs=xs)

    # ここから全部消したい
    # タプルで与えられた変数ラベルをすべて掛けて返す。
    # def mul_tuple(self, t):
    #     t_len = len(t)
    #     b = Binary(label=t[0])
    #     for i in range(1, t_len):
    #         b = Mul(b, Binary(label=t[i]))
    #     return b
    #
    # # タプルで与えられた変数の否定をすべてかけて返す
    # def mul_inv_tuple(t):
    #     t_len = len(t)
    #     b = Num(1) - Binary(label=t[0])
    #     for i in range(1, t_len):
    #         b = Mul(b, Num(1) - Binary(label=t[i]))
    #     return b

    # 2式等号 one to multi
    # Expressionを返す。Penalty係数はまだ。
    # def getQ_eqYtoXy(self, y, xs):
    #     # y should be str
    #     # xs should be list of str, var name.
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #
    #     exp_dict=dict()
    #     # はじめに2項演算
    #     for c in it.combinations(xs, 2):
    #         # print(c)
    #         exp_dict[c] = 2
    #
    #     #x^2の追加
    #     #-2xyの追加
    #     for x in xs:
    #         exp_dict[(x, x)] = 1
    #         exp_dict[(x, y)] = -2
    #
    #     # yy
    #     exp_dict[(y,y)] =1
    #     return exp_dict
    #
    #
    # def eqYtoXs(self, y, xs):
    #     # y should be str
    #     # xs should be list of str, var name.
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #
    #     exp_list =[]
    #
    #     #はじめに2項演算
    #     for c in it.combinations(xs, 2):
    #         # print(c)
    #         x2_i = Mul(self.mul_tuple(c), Num(2))
    #         exp_list.append(x2_i)
    #
    #     #x^2の追加
    #     #-2xyの追加
    #     for x in xs:
    #         exp_list.append(Binary(x))
    #         xy_m2=Mul(Num(-2), self.mul_tuple((x, y)))
    #         exp_list.append(xy_m2)
    #
    #     exp_list.append(Binary(y))
    #
    #     return AddList(exp_list)
    #
    # def getQ_DeqXpl(self, dv, xs, l):
    #     # dummy vector:D = X +l
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #     if type(dv) == "tuple":
    #         dv = list(dv)
    #
    #     exp_dict = dict()
    #
    #     # (1 -2l)d
    #     for d in dv:
    #         exp_dict[d, d] = 1 -2*l
    #
    #     # d x d
    #     for c in it.combinations(dv, 2):
    #         exp_dict[c] = 2
    #
    #     # -2dx
    #     for c in it.product(dv, xs):
    #         exp_dict[c] = -2
    #
    #     # 2lx +x^2
    #     for x in xs:
    #         exp_dict[x, x] = 1 +2*l
    #
    #     # xi *xj
    #     for c in it.combinations(xs,2):
    #         exp_dict[c] = 2
    #
    #     return exp_dict
    #
    # def getQ_DX_less_than_m(self, dv, xs, m):
    #     max_len = len(dv)
    #     l = max_len -m
    #     q = self.getQ_DeqXpl(dv=dv, xs=xs, l=l)
    #     return q
    #
    # def getQ_less_than_m(self, xs, m):
    #     dv_l = self.dg.getDVstr(m)
    #     q = self.getQ_YsEqXs(ys=dv_l, xs=xs)
    #     return q
    #
    # def OR(self, exp1, exp2):
    #     exp_or = Mul(exp1, exp2) -exp1 -exp2
    #     return exp_or
    #
    # def getExp_notOr(self,t2):
    #     exp = Num(-2)*Binary(label=t2[0])* Binary(label=t2[1]) + Binary(label=t2[0]) + Binary(label=t2[1])
    #     return exp
    #
    # def getExp_OneMustPos(self,l1):
    #     exp = Num(1) - Binary(label=l1)
    #     return exp
    #
    # def getExp_OneMustNeg(self, l1):
    #     exp = Binary(label=l1)
    #     return exp
    #
    # # def getQ_OneMustNeg(self, l1):
    # #     exp_dict = dict()
    #
    #
    # def getQ_NtoXs(self,n, xs):
    #     # 2式等号 N to multi
    #     # Expressionを返す。Penalty係数はまだ。
    #     # n should be number
    #     # xs should be list of str, var name.
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #
    #     exp_dict = dict()
    #     # はじめに2項演算
    #     for c in it.combinations(xs, 2):
    #         exp_dict[c] = 2
    #
    #         # x^2の追加
    #         # -2xnの追加
    #     for x in xs:
    #         exp_dict[(x, x)] = -2*n +1
    #
    #     return exp_dict
    #
    #
    #
    # def eqNtoXs(self, n, xs):
    #     # 2式等号 N to multi
    #     # Expressionを返す。Penalty係数はまだ。
    #     # n should be number
    #     # xs should be list of str, var name.
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #
    #     exp_list = []
    #
    #     # はじめに2項演算
    #     for c in it.combinations(xs, 2):
    #         x2_i = Mul(self.mul_tuple(c), Num(2))
    #         exp_list.append(x2_i)
    #
    #     # x^2の追加
    #     # -2xnの追加
    #     for x in xs:
    #         exp_list.append(Binary(x))
    #         xn_m2 = Mul(Num(-2*n), Binary(x))
    #         exp_list.append(xn_m2)
    #
    #     exp_list.append(Num(n**2))
    #
    #     return AddList(exp_list)
    #

    #
    #
    # def getExp_YsEqXs(self, ys, xs):
    #     # ysのリストとxsのリストで、等しい
    #     if type(xs) == "tuple":
    #         xs = list(xs)
    #     if type(ys) == "tuple":
    #         ys = list(ys)
    #
    #     exp_list =[]
    #
    #     #はじめに二項演算
    #     for c in it.combinations(ys, 2):
    #         c2_i = Mul(self.mul_tuple(c), Num(2))
    #         exp_list.append(c2_i)
    #
    #     for c in it.combinations(xs, 2):
    #         c2_i = Mul(self.mul_tuple(c), Num(2))
    #         exp_list.append(c2_i)
    #
    #     for c in it.product(ys, xs):
    #         c2_i = Mul(self.mul_tuple(c), Num(-2))
    #         exp_list.append(c2_i)
    #
    #     # x^2の追加
    #     for x in xs:
    #         exp_list.append(Binary(x))
    #     for y in ys:
    #         exp_list.append(Binary(y))
    #
    #     return AddList(exp_list)
    #
    #
    # def getExp_avoidAllPos(self, t):
    #     # t: tuple of str variable name
    #     t_len = len(t)
    #     if t_len == 0:
    #         print("length of t is zero!")
    #         return None
    #     else:
    #         b = Binary(label=t[0])
    #         # t_inv = self.one -b
    #         for i in range(1, t_len):
    #             b = Mul(b, Binary(label=t[i]))
    #         return b
    #
    # def getExp_avoidAllNeg(self,t):
    #     t_len=len(t)
    #     if t_len == 0:
    #         print("length of t is zero!")
    #         return None
    #     else:
    #         b_inv = self.one -Binary(label=t[0])
    #         for i in range(1, t_len):
    #             bi_inv = self.one -Binary(label=t[i])
    #             b_inv = Mul(b_inv, bi_inv)
    #         return b_inv
    #
    # def getExp_avoidAllPos2(self,t):
    #     return self.eqNtoXs(0, t)
    #
    # def getQ_avoidAllPos2(self, t):
    #     return self.getQ_NtoXs(0, t)
    #
    # def getExp_avoidAllNeg2(self,t):
    #     return self.eqNtoXs(len(t),t)
    #
    # def getQ_avoidAllNeg2(self,t):
    #     return self.getQ_NtoXs(len(t), t)
    #
    # def getExp_reqAllPos(self,t):
    #     # t: tuple of str variable name
    #     return self.eqNtoXs(len(t), list(t))
    #
    #
    # def getExp_reqAllNeg(self,t):
    #     return self.eqNtoXs(0, t)
    #
    #
    # def getQubo(self, exp):
    #     # exp is expression list
    #     if type(exp) == type([]):
    #         exp = AddList(exp)
    #     model = exp.compile()
    #     qubo, offset = model.to_qubo(feed_dict=self.feed_dict)
    #     return qubo
    #
    # def getExp_less_than(self, t, n):
    #     exp_list = []
    #     for comb in it.combinations(t, n):
    #         exp_list.append(self.mul_tuple(comb))
    #     return exp_list
    #
    # def getExp_more_than(self, t, n):
    #     exp_list = []
    #     for comb in it.combinations(t, len(t) - n):
    #         exp_list.append(self.mul_inv_tuple(comb))
    #     return exp_list
    #
    #
    # def getQ_OneMustNeg(self, l1):
    #     return {(l1, l1): 1}
    #
    # def getQ_OneMustPos(self, l1):
    #     return {(l1, l1): -1}


class q_gen():
    # qを作るクラス
    # limiterを使ってqを作る。
    lm = limiter()
    hideProgressBar = False

    setting = nsp_settings.nsp_settings()

    check_list = setting.check_list

    param_dict = setting.param_dict

    def __init__(self, x2c):
        print("Q generator activated!")
        print("x2c need to pre make 3DT")
        self.x = x2c
        self.ne = nsp_expressions.nsp_expressions()

    def setParam(self, param_dict):
        self.param_dict = param_dict

    # def getQ_dt1_to_dt2(self,x2t, weight=400):
    #     # x2t is xlsx2condtion class after make3CTD.
    #     dt1 = x2t.dt1
    #     dt2 = x2t.dt2
    #     exp_list = []
    #     exp_dict = dict()
    #     for r in tqdm(dt1.itertuples(), disable=self.hideProgressBar):
    #         name_ind = r.name_ind
    #         date_number = r.date_number
    #         var_name = r.var_name
    #         df_r = dt2.query("name_ind == @name_ind & date_number == @date_number")
    #         exp_dict.update(self.lm.getQ_eqYtoXy(y=var_name, xs=df_r["var_name"].tolist()))
    #     self.ne.Q_update(exp_dict, weight=weight)
    #     pass
    #
    #
    # def getQ_dt2_to_dt3(self,x2t, weight=400):
    #     # x2t is xlsx2condtion class after make3CTD.
    #     dt2 = x2t.dt2
    #     dt3 = x2t.dt3
    #     exp_list=[]
    #     exp_dict = dict()
    #
    #     for r in tqdm(dt2.itertuples(), disable=self.hideProgressBar):
    #         # print(r)
    #         name_ind = r.name_ind
    #         date_number = r.date_number
    #         dclass_ind = r.dclass_ind
    #         var_name = r.var_name
    #         df_r = dt3.query("name_ind == @name_ind & date_number == @date_number & dclass_ind == @dclass_ind")
    #         exp_dict.update(self.lm.getQ_eqYtoXy(var_name, df_r["var_name"].tolist()))
    #
    #     self.ne.Q_update(exp_dict, weight=weight)
    #
    #
    #
    # def limit_3dts(self,weight = 10):
    #     print("make 3 table connections..")
    #     self.getQ_dt1_to_dt2(self.x)
    #     self.getQ_dt2_to_dt3(self.x)
    #     # self.ne.Q_update(self.getQ_dt1_to_dt2(self.x), weight=weight)
    #     # self.ne.Q_update(self.getQ_dt2_to_dt3(self.x), weight=weight)

    # 新規制約関数群

    def limit_one_day_one_task(self,  weight=100):
        # 各人1日に働くのは1シフトのみである。
        # 1by1
        print("one can do one task per day...")
        dt1 = self.x.dt1.copy()
        dt3 = self.x.dt3_able.copy()
        exp_dict = dict()
        for r in tqdm(dt1.itertuples(), disable=self.hideProgressBar):
            name_ind = r.name_ind
            date_number = r.date_number
            df_r = dt3.query(
                "name_ind == @name_ind & date_number == @date_number")
            if len(df_r) != 0:
                exp_dict.update(self.lm.getQ_fromVars_max1(
                    df_r["var_name"].to_list()))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_continuouswork(self, weight=50):
        # 連続勤務を制御
        # m_capaが最大許容数の設定のはず
        # cwork
        print("limit continuous work by dt1 and member capacity")
        dt1 = self.x.dt1.copy()
        dt3 = self.x.dt3_able.copy()
        exp_dict = dict()

        for m in self.x.dt1["name"].unique():
            m_capa = int(self.x.df_MemberCapacity.query(
                "name == @m")["CapableContinuousWorks"])
            m_min = int(self.x.df_MemberCapacity.query(
                "name == @m")["ReccomendedContinuousWorks"])
            max_date = int(self.x.dt1["date_number"].max())
            # print(m_capa, m_min, max_date)
            dt3m = dt3.query("name == @m")
            for d in range(0, max_date - m_capa):
                # dt1から、そもそも休みが入っているならやらなくてい
                dt1_d = dt1.query(
                    "name == @m and @d+1 <= date_number <= @d +@m_capa")
                dt3m_dn = dt3m.query(
                    "@d+1 <= date_number <= @d +@m_capa and ability ==1")["date_number"].unique()
                var_list = dt3m.query(
                    "@d+1 <= date_number <= @d +@m_capa +1")["var_name"].to_list()
                if len(dt1_d) < m_capa:
                    pass
                    # print("there is rest so not limited")
                elif len(dt3m_dn) < m_capa:
                    pass
                    # dt3から、そもそもできない仕事しかない日があるならやらなくて良い
                    # print("not able task only!")
                elif len(var_list) == 0:
                    pass
                    # print("unko")
                else:
                    self.ne.Q_update(self.lm.getQ_fromVarAndCoef(var_list=var_list,
                                                                 min_int=m_min,
                                                                 max_int=m_capa), weight=weight)

    # def limit_continuouswork(self, weight = 100):
    #
    #     print("limit continuous work by dt1 and member capacity")
    #     exp_list = []
    #     for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
    #         # print(m)
    #         m_capa = int(self.x.df_MemberCapacity.query("name == @m")["CapableContinuousWorks"])
    #         max_date = int(self.x.dt1["date_number"].max())
    #         # print(m_capa)
    #         dt1m = self.x.dt1.query("name == @m")
    #         #     and date_number < @max_date -@m_capa
    #         for d in range(0, max_date - m_capa + 1):
    #             #         print(d)
    #             var_tuple = dt1m.query("@d+1 <= date_number <= @d +@m_capa")["var_name"].to_list()
    #             var_tuple = tuple(var_tuple)
    #             self.ne.Q_update(self.lm.getQ_less_than_m(xs=var_tuple, m=m_capa), weight=weight)
    #             # exp_list.append(self.lm.getExp_avoidAllPos(var_tuple))
    #             # self.ne.Q_update(self.lm.getQ_avoidAllPos2(var_tuple), weight=weight)
    #     # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)

    def limit_continiousNightWork(self, weight=100):
        # 連続夜勤を制御
        # cnight
        print("limit continious night work by dt3...")

        exp_list = []

        for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
            # print(m)
            dt3m = self.x.dt3_able.query("name == @m and isNightWork ==1")
            m_capa = int(self.x.df_MemberCapacity.query(
                "name == @m")["CapableContinuousNightWorks"])
            m_min = 0

            max_date = self.x.max_date
            #print(m, m_capa, m_min, max_date)
            for d in range(0, max_date - m_capa):
                # print(d)
                #         print(d)
                # キャパ＋１日分を集める。
                dt3m_d = dt3m.query("@d +1 <= date_number <= @d +@m_capa +1")
                # できない日が挟まれていれば必要ない
                if len(dt3m_d.drop_duplicates(subset="date_number")) < m_capa + 1:
                    pass
                else:
                    var_list = dt3m_d["var_name"].to_list()
                    self.ne.Q_update(self.lm.getQ_fromVarAndCoef(var_list=var_list,
                                                                 min_int=m_min,
                                                                 max_int=m_capa), weight=weight)

            # print(var_list)

    def limit_ForbidSeq(self, weight=100):
        # 前後連続禁止の組み合わせ
        # fseq
        print("forbiden sequence is forbiden..")

        # これに禁止シフトの組み合わせが入る。
        # 禁止組み合わせのタプルセットを作っておく。
        #   これはxにすでに存在する。
        df = self.x.df_ForbiddenSequence.query("bef_num !=0 and aft_num !=0")
        fbd_set = self.x.set_ForbiddenSequence_ind
        # fbd_set = set()
        # for r in df.itertuples():
        #     fbd_set.add((r.bef_num, r.aft_num))

        # return df

        fbd_list = []
        for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
            # print(m)

            dt3m = self.x.dt3_able.query("name == @m")

            dt3m_ab = dt3m.loc[:, ["date_number", "week_num",
                                   "DutyClass", "dclass_ind", "var_name"]]
            dt3m_ab["after"] = dt3m_ab["date_number"] + 1
            # dt2m_ab
            dt3m_lim = dt3m.loc[:, ["date_number",
                                    "DutyClass", "dclass_ind", "var_name"]]
            dt3m_lim.columns = ["date_number2",
                                "DutyClass2", "dclass_ind2", "var_name2"]
            dt3m_ab2 = pd.merge(dt3m_ab, dt3m_lim, left_on="after",
                                right_on="date_number2", how="inner")

            dt3m_abm = pd.merge(dt3m_ab2, df, left_on=[
                                "DutyClass", "DutyClass2"], right_on=["Before", "After"])

            for r in dt3m_abm.itertuples():
                if (r.bef_num, r.aft_num) in fbd_set:
                    fbd_list.append((r.var_name, r.var_name2))

        self.ne.Q_update(self.lm.getQ_avoidAllPosV2_list(vart2_list=fbd_list),
                         weight=weight)

        # break
        #     # dt2m_abm
        #     for ind, pre, aft in dt2m_abm.loc[:, ["var_name", "var_name2"]].itertuples():
        #         # print(pre, aft)
        #         exp_list.append(self.lm.getExp_avoidAllPos(t=(pre, aft)))
        # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
        # return (df, dt3m, dt3m_ab2, dt3m_abm, fbd_set)
        # return fbd_list

    #
    # def limit_OnePointOne(self, weight = 200):
    #     print("limit one point one.")
    #
    #     exp_list = []
    #     exp_dict = dict()
    #
    #     dt3_uni = self.x.dt3.drop_duplicates(subset=["date_number", "task_num", "dclass_ind","count_in_task"]).loc[:,
    #               ["date_number", "task_num", "dclass_ind","count_in_task"]]
    #     # dt3_uni
    #     for ind, date_num, task_num, dclass_ind, count_in_task in tqdm(dt3_uni.itertuples(name=None), disable=self.hideProgressBar):
    #         #     print(date_num, task_num, count_in_task)
    #         df_i = self.x.dt3.query(
    #             "date_number == @date_num and task_num == @task_num and dclass_ind == @dclass_ind and count_in_task == @count_in_task")
    #         #     print(tuple(df_i["var_name"].to_list()))
    #         var_t = tuple(df_i["var_name"].to_list())
    #         # print(var_t)
    #         # print(lm.eqNtoXs(n=1, xs=var_t))
    #         # exp_list.append(self.lm.eqNtoXs(n=1, xs=var_t))
    #         exp_dict.update(self.lm.getQ_NtoXs(n=count_in_task, xs=var_t))
    #     self.ne.Q_update(exp_dict, weight=weight)
    #     # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
    #
    #
    #
    #
    # def limit_wantedRest(self, weight = 100):
    #     print("one must rest when one want...")
    #     # exp_list = []
    #     exp_dict = dict()
    #     dt1_nottake = self.x.dt1.query("takability == 0")
    #
    #     for var in tqdm(dt1_nottake["var_name"].to_list(), disable=self.hideProgressBar):
    #         exp_dict[(var, var)] = 1
    #         # exp_list.append(self.lm.getExp_OneMustNeg(var))
    #     # var_t = tuple(dt1_nottake["var_name"].to_list())
    #     # exp_list.append(self.lm.eqNtoXs(n=0, xs=var_t))
    #     # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
    #     self.ne.Q_update(exp_dict, weight=weight)
    #
    # def limit_OverAbility(self, weight=100):
    #     print("one cant do what one cant...")
    #     # exp_list = []
    #     exp_dict = dict()
    #     dt3_cannot = self.x.dt3.query("ability ==0")
    #     for var in tqdm(dt3_cannot["var_name"].to_list(), disable=self.hideProgressBar):
    #         exp_dict[(var, var)] = 1
    #         # exp_list.append(self.lm.getExp_OneMustNeg(var))
    #     # var_t = tuple(dt3_cannot["var_name"].to_list())
    #     # exp_list.append(self.lm.eqNtoXs(n=0, xs=var_t))
    #     # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
    #     self.ne.Q_update(exp_dict, weight=weight)
    #
    # # def limit_ForbidSeq(self, weight=100):
    # #     print("forbiden sequence is forbiden..")
    # #     exp_list = []
    # #
    # #     self.x.df_ForbiddenSequence["bef_num"] = [self.x.dclass_dict[task] if task in self.x.dclass_dict.keys() else 0 for
    # #                                             task in self.x.df_ForbiddenSequence["Before"]]
    # #     self.x.df_ForbiddenSequence["aft_num"] = [self.x.dclass_dict[task] if task in self.x.dclass_dict.keys() else 0 for
    # #                                             task in self.x.df_ForbiddenSequence["After"]]
    # #     df = self.x.df_ForbiddenSequence.query("bef_num !=0 and aft_num !=0")
    # #     for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
    # #         # print(m)
    # #         dt2m = self.x.dt2.query("name == @m")
    # #
    # #         dt2m_ab = dt2m.loc[:, ["date_number", "week_num", "DutyClass", "dclass_ind", "var_name"]]
    # #         dt2m_ab["after"] = dt2m_ab["date_number"] + 1
    # #         # dt2m_ab
    # #         dt2m_lim = dt2m.loc[:, ["date_number", "DutyClass", "dclass_ind", "var_name"]]
    # #         dt2m_lim.columns = ["date_number2", "DutyClass2", "dclass_ind2", "var_name2"]
    # #         dt2m_ab2 = pd.merge(dt2m_ab, dt2m_lim, left_on="after", right_on="date_number2", how="inner")
    # #
    # #         dt2m_abm = pd.merge(dt2m_ab2, df, left_on=["DutyClass", "DutyClass2"], right_on=["Before", "After"])
    # #         # dt2m_abm
    # #         for ind, pre, aft in dt2m_abm.loc[:, ["var_name", "var_name2"]].itertuples():
    # #             # print(pre, aft)
    # #             exp_list.append(self.lm.getExp_avoidAllPos(t=(pre, aft)))
    # #     self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)

    def limit_NeedSeq(self, weight=100):
        # 必須の組み合わせ
        # nseq
        print("must pair must nor...")
        test_list = []
        exp_list = []

        df = self.x.df_NeededSequence.query("bef_num !=0 and aft_num !=0")
        needs_set = self.x.set_NeedSeq_ind

        # test_list.append((df.copy(), needs_set))

        # 禁止組み合わせリストペア
        fbd_pair_list = []

        #　単品禁止
        fbd_one_list = []

        if len(df) == 0:
            pass
        else:
            not_one_list = []
            for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
                # print(m)

                dt3m = self.x.dt3_able.query("name == @m")

                dt3m_ab = dt3m.loc[:, ["date_number", "week_num",
                                       "DutyClass", "dclass_ind", "var_name"]]
                dt3m_ab["after"] = dt3m_ab["date_number"] + 1
                # dt2m_ab
                dt3m_lim = dt3m.loc[:, ["date_number",
                                        "DutyClass", "dclass_ind", "var_name"]]
                dt3m_lim.columns = ["date_number2",
                                    "DutyClass2", "dclass_ind2", "var_name2"]

                # ここまでは全組み合わせあるはず。
                dt3m_ab2 = pd.merge(
                    dt3m_ab, dt3m_lim, left_on="after", right_on="date_number2", how="inner")

                # ここからNeedのペアのみになるはず。
                dt3m_abm = pd.merge(dt3m_ab2, df, left_on=[
                                    "DutyClass", "DutyClass2"], right_on=["Before", "After"])

                # test_list.append((dt3m_ab2,dt3m_abm))

                for r in df.itertuples():
                    dt3m_abm_r = dt3m_abm.query(
                        "bef_num == @r.bef_num and aft_num == @r.aft_num")
                    for d in dt3m_abm_r["date_number"].unique():
                        dt3m_abm_r_d = dt3m_abm_r.query("date_number == @d")
                        xs_bef = dt3m_abm_r_d["var_name"].to_list()
                        xs_aft = dt3m_abm_r_d["var_name2"].to_list()
                        # Need pair求む
                        self.ne.Q_update(self.lm.getQ_YsEqXs(
                            ys=xs_bef, xs=xs_aft), weight=weight)
        # return test_list

        # それ以外のペア禁止
        # self.ne.Q_update(self.lm.getQ_avoidAllPosV2_list(),
        #                  weight=weight)

        #         for r in dt3m_abm.itertuples():
        #             if (r.bef_num, r.aft_num) in needs_set:
        #                 not_one_list.append([r.var_name, r.var_name2])
        # if len(not_one_list) != 0:
        #     q = self.lm.getQ_not1_list(not_one_list)
        #     self.ne.Q_update(q,
        #                      weight=weight)
        # return l_s1 + l_s2, dt3m_abm_r_not

    def limit_ReqNumberStaff(self, weight=10):
        # シフトの人数を規定人数に
        # rqn
        print("limitting as req numbers")
        df_req = self.x.df_RequireTask.query("count != 0")
        dt3 = self.x.dt3_able
        for r in df_req.itertuples():
            # print(r)
            r_count = r.count
            r_date = r.date_number
            r_task = r.task_ind
            vars_r = dt3.query(
                "date_number == @r_date and task_ind == @r_task")["var_name"].to_list()
            self.ne.Q_update(self.lm.getQ_NtoXs(n=r_count, xs=vars_r),
                             weight=weight)

    def limit_ReqNumberWorkTime(self, weight=10):
        # 各人のトータル勤務時間を制限
        print("limitting as req work times")
        exp_dict = dict()

        # num_wk_min_proc = self.x.num_wk_min_proc
        # num_wk_max_proc = self.x.num_wk_max_proc
        # max_work_hour = num_wk_max_proc * self.x.total_weekdays
        # min_work_hour = num_wk_min_proc * self.x.total_weekdays
        # max_work_hour = self.x.num_wk_min_proc
        # min_work_hour = self.x.num_wk_max_proc
        # for m in self.x.df_MemberCapacity["name"]:
        #     # print(m)
        #     dt3_m = self.x.dt3_able.query("name == @m")
        #     var_names = dt3_m["var_name"].to_list()
        #     var_coefs = dt3_m["WORK_TIME"].to_list()

        #     q_m = self.lm.getQ_fromVarAndCoef(var_list=var_names,
        #                                       coef_list=var_coefs,
        #                                       min_int=min_work_hour,
        #                                       max_int=max_work_hour)
        #     exp_dict.update(q_m)

        #     # exp_dict.update(self.lm.dict_normalize(q_m))
        # self.ne.Q_update(exp_dict, weight=weight)
        max_work_hour = int(self.x.num_wk_max_proc/4)
        min_work_hour = int(self.x.num_wk_min_proc/4)

        for m in self.x.df_MemberCapacity["name"]:
            # print(m)
            dt3_m = self.x.dt3_able.query("name == @m")
            var_names = dt3_m["var_name"].to_list()
            var_coefs = dt3_m["WORK_TIME"].to_list()

            # div4
            var_coefs = [int(i/4) for i in var_coefs]

            q_m = self.lm.getQ_fromVarAndCoef(var_list=var_names,
                                              coef_list=var_coefs,
                                              min_int=min_work_hour,
                                              max_int=max_work_hour)
            self.ne.Q_update(q_m, weight=weight)

    def limit_TotalTask(self, weight=5):
        # 全シフト数を制限
        # この場合はシフト数である。
        # tt
        print("limit total tasks...")
        ss_days = ["Sunday", "Saturday"]
        len_ss = self.x.df_weeks.query("days in @ss_days")["days"].count()

        len_month = self.x.df_weeks["days"].count()

        max_work_shifts = len_month - len_ss
        # max_work_shifts

        exp_dict = dict()
        exp_list = []
        for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
            # print(m)
            m_work = int(self.x.df_MemberCapacity.query(
                "name == @m")["CapableTotalWorks"])
            if max_work_shifts < m_work:
                m_work = max_work_shifts

            # print(m_work)
            dt3m = self.x.dt3_able.query("name == @m")
            var_l = dt3m["var_name"].to_list()
            exp_dict.update(self.lm.getQ_fromVarAndCoef(var_list=var_l,
                                                        max_int=m_work))
            # self.ne.Q_update(self.lm.getQ_DX_less_than_m(dv=self.x.dv_date, xs=var_t, m=m_work), weight=weight)

            # q = self.lm.getQ_DX_less_than_m(dv=self.x.dv_date, xs=var_t, m=m_work)
            # exp_list.append(self.lm.eqNtoXs(n=m_work, xs=var_t))
        # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_TotalNights(self, weight=5):
        # 各人のトータル夜勤時間を制限
        # この場合の時間制限は、hour単位で制限している。回数ではない。
        # tn
        print("limit tatal nights...")
        exp_dict = dict()
        exp_list = []
        for m in tqdm(self.x.df_MemberCapacity["name"], disable=self.hideProgressBar):
            # print(m)
            m_work = int(self.x.df_MemberCapacity.query(
                "name == @m")["CapableTotalWorkNightHours"])
            # print(m_work)
            dt3m = self.x.dt3_able.query("name == @m and isNightWork ==1")
            var_l = dt3m["var_name"].to_list()
            coef_l = dt3m["WorkHours"].to_list()

            exp_dict.update(self.lm.getQ_fromVarAndCoef(var_list=var_l, coef_list=coef_l,
                                                        max_int=m_work))
            # self.ne.Q_update(self.lm.getQ_DX_less_than_m(dv=self.x.dv_night,xs=var_t, m= m_work), weight=weight)
            # exp_list.append(self.lm.eqNtoXs(n=m_work, xs=var_t))
        # self.ne.Q_update(self.lm.getQubo(exp_list), weight=weight)
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_EquGroup_dt3(self, weight=1):
        # 各シフトにおけるA、Bグループの数を調整
        # eqg3
        print("each dclass have equal group members..")
        dt3_lim = self.x.dt3_able.loc[:, [
            "date_number", "task_ind", "dclass_ind"]].drop_duplicates()

        exp_dict = dict()

        # dt3_lim

        for ind, dat, task, dclass in tqdm(dt3_lim.itertuples(), disable=self.hideProgressBar):
            # print(dat, task, dclass)
            dt3_sub = self.x.dt3_able.query(
                "date_number == @dat and task_ind == @task and dclass_ind == @dclass")
            dt3_sub_max = dt3_sub["count_in_task"].max()
            if dt3_sub_max >= 2:
                subA = dt3_sub.query("group == 'A'")["var_name"].to_list()
                subB = dt3_sub.query("group == 'B'")["var_name"].to_list()
                exp_dict.update(self.lm.getQ_YsEqXs(subA, subB))
                # q = self.lm.getQ_YsEqXs(subA, subB)

                # q = self.lm.getQubo(self.lm.getExp_YsEqXs(subA, subB))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_EquGroup_dt2(self, weight=1):
        # 各日におけるグループの数を調整
        # eqg2
        print("each shift have equal members")
        dt3_lim = self.x.dt3_able.loc[:, [
            "date_number", "dclass_ind"]].drop_duplicates()
        exp_dict = dict()
        # dt2_lim

        for ind, dat, dclass in tqdm(dt3_lim.itertuples(), disable=self.hideProgressBar):
            dt3_sub = self.x.dt3_able.query(
                "date_number == @dat and dclass_ind == @dclass")
            subA = dt3_sub.query("group == 'A'")["var_name"].to_list()
            subB = dt3_sub.query("group == 'B'")["var_name"].to_list()
            exp_dict.update(self.lm.getQ_YsEqXs(subA, subB))

        self.ne.Q_update(exp_dict, weight=weight)

    def limit_ForbidSeq_fromLast(self, weight=100):
        # 先月の状態から禁止シークエンス規定
        # lfbd
        print("last month info: duty class to forbiden seq...")
        exp_dict = dict()
        dt3 = pd.merge(self.x.dt3_able, self.x.df_FinalStatusAtLastMonth, on="name")\
            .query("date_number ==1")\
            .dropna(subset=["LastDay_DutyClass"])
        df_fbd = self.x.df_ForbiddenSequence.query(
            "bef_num != 0 and aft_num != 0")
        dt3_lim = pd.merge(dt3, df_fbd, left_on=["DutyClass", "LastDay_DutyClass"],
                           right_on=["After", "Before"],
                           how="inner")
        fbd_var = dt3_lim["var_name"]
        exp_dict.update(self.lm.getQ_not1_var1_list(fbd_var))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_NeedPair_fromLast(self, weight=100):
        # 先月の状態から必須シークエンス
        # lnd
        print("last month info: duty class to need seq...")
        exp_dict = dict()

        dt3 = pd.merge(self.x.dt3_able, self.x.df_FinalStatusAtLastMonth, on="name").query("date_number ==1").dropna(
            subset=["LastDay_DutyClass"])
        # dt3.head()

        df_need = self.x.df_NeededSequence.query(
            "bef_num != 0 and aft_num != 0")
        # df_need
        dt3_lim = pd.merge(dt3, df_need, left_on=["DutyClass", "LastDay_DutyClass"], right_on=["After", "Before"],
                           how="inner")
        for m in dt3_lim["name"].unique():
            # print(m)
            dt3m_lim = dt3_lim.query("name == @m")
            needs_vars = dt3m_lim["var_name"].to_list()
            exp_dict.update(self.lm.getQ_XsIsOne(needs_vars))
            # print(needs_vars)
        self.ne.Q_update(exp_dict, weight=weight)

        #
        # dt2_last = pd.merge(self.x.dt2, self.x.df_FinalStatusAtLastMonth, on="name").query("date_number ==1").dropna(
        #     subset=["LastDay_DutyClass"])
        # dt2_last["is_need"] =  [(r.LastDay_DutyClass, r.DutyClass) in self.x.set_NeedSeq for r in dt2_last.itertuples()]
        # for r in tqdm(dt2_last.itertuples(), disable=self.hideProgressBar):
        #     if r.is_need:
        #         exp_dict.update(self.lm.getQ_OneMustPos(r.var_name))
        # self.ne.Q_update(exp_dict, weight=weight)
        # # return dt2_last

    def limit_ContWork_fromLast(self, weight=100):
        # 先月の状態からトータル連続勤務
        # lcnt
        print("last month info: cont work...")
        exp_dict = dict()
        # dt2_last = pd.merge(self.x.dt2, self.x.df_FinalStatusAtLastMonth, on="name")

        for mr in self.x.df_CapaAndLast.itertuples():
            m = mr.name
            m_max = mr.max_1st_cont + 1
            # print(m_max)
            # if int(m_max) != m_max:
            #     print(m_max)
            dt3m = self.x.dt3_able.query(
                "name == @m and date_number <= @m_max")
            if len(dt3m["date_number"].unique()) == m_max:
                var_t = dt3m["var_name"].to_list()
                exp_dict.update(self.lm.getQ_fromVarAndCoef(var_list=var_t,
                                                            max_int=int(m_max) - 1))
            else:
                pass

        self.ne.Q_update(exp_dict, weight=weight)

    def limit_ContNight_fromLast(self, weight=100):
        # 先月の状態から連続夜勤
        # lcnn
        print("last month info: cont night work...")
        exp_dict = dict()
        for mr in self.x.df_CapaAndLast.itertuples():
            m = mr.name
            m_max = mr.max_1st_cont_night + 1
            dt3mn = self.x.dt3_able.query(
                "name == @m and date_number <= @m_max and isNightWork ==1")
            if len(dt3mn["date_number"].unique()) == m_max:
                var_t = dt3mn["var_name"].to_list()
                exp_dict.update(self.lm.getQ_fromVarAndCoef(var_list=var_t,
                                                            max_int=int(m_max) - 1))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_ShiftCount(self, weight=100):
        # 人によって特定シフト帯の回数上限がある
        # 例えばある人は夜勤3回的な。
        # sc
        print("shift count quantified...")
        exp_dict = dict()
        dt3 = self.x.dt3_able.copy()
        memcap = self.x.df_MemberCapacity.copy()
        # memcap.head()
        cols = memcap.columns.to_list()
        shifts = self.x.df_DutyClass["DutyClass"].unique().tolist()
        cols = [c for c in cols if c.replace("Capable", "") in shifts]
        # cols = ["name"] + cols
        # cols
        memcap = memcap \
            .set_index("name")\
            .loc[:, cols].copy()\
            .unstack()\
            .reset_index()\
            .rename(columns={"level_0": "DutyClass",
                             0: "capable_count"})
        memcap["DutyClass"] = memcap["DutyClass"].str.replace("Capable", "")
        for r in memcap.itertuples():
            # print(r)
            #     name = r.name
            #     dc = r.DutyClass
            #     cc = r.capable_count
            var_t = dt3\
                .query("name == @r.name and DutyClass == @r.DutyClass")["var_name"]\
                .to_list()
            # print(var_t)

            exp_dict.update(
                self.lm.getQ_fromVarAndCoef(var_list=var_t, max_int=r.capable_count))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_MemberPairShift(self, weight=100):
        # 同じ勤務帯に勤務できないペアが存在する。
        # msp
        print("limit member pair shift...")
        exp_dict = dict()
        dt3 = self.x.dt3_able.copy()
        df_fbd = self.x.df_ForbiddenPairShift.copy()
        for r in df_fbd.itertuples():
            n1 = r.name1
            n2 = r.name2
            s = r.shift
            # print(n1, n2, s)
            for c in dt3["date_number"].unique():
                t1 = dt3.query(
                    "name == @n1 and date_number == @c and DutyClass == @s")["var_name"].to_list()
                t2 = dt3.query(
                    "name == @n2 and date_number == @c and DutyClass == @s")["var_name"].to_list()
                if len(t1) == 0 or len(t2) == 0:
                    # print("NULL!")
                    # print(t1, t2)
                    pass
                else:
                    # print("not NULL!")
                    # print(len(t1), len(t2))
                    exp_dict.update(self.lm.getQ_avoidBothPos_list(t1, t2))
        self.ne.Q_update(exp_dict, weight=weight)

    def limit_DayABVetran(self, weight=100):
        # 日勤帯ﾆB_Sにおいて、ベテラン半数を確保
        # dab
        print("Veteran in each group should be preserverd.")
        exp_dict_A = dict()
        exp_dict_B = dict()
        dt3 = self.x.dt3_able.copy()
        dfw = self.x.df_week_task.query("tasks == 'ﾆB_S'").copy()
        As = ["A", "A/B"]
        Bs = ["B", "A/B"]
        for d in dt3["date_number"].unique():
            # print(d)
            n_vet_total = dfw\
                .query("date_number == @d")["count_in_task"].to_list()[0]
            n_min_vet_group = int(n_vet_total/2)
            # A ﾆB_S
            if n_min_vet_group > 0:
                vars_a = dt3\
                    .query("date_number == @d")\
                    .query("DutyLabel == 'ﾆB_S'")\
                    .query("group in @As")["var_name"]

                exp_dict_A.update(
                    self.lm.getQ_fromVarAndCoef(var_list=vars_a, max_int=n_vet_total, min_int=n_min_vet_group))

                vars_b = dt3\
                    .query("date_number == @d")\
                    .query("DutyLabel == 'ﾆB_S'")\
                    .query("group in @Bs")["var_name"]

                exp_dict_B.update(
                    self.lm.getQ_fromVarAndCoef(var_list=vars_b, max_int=n_vet_total, min_int=n_min_vet_group))
        self.ne.Q_update(exp_dict_A, weight=weight)
        self.ne.Q_update(exp_dict_B, weight=weight)

    def limit_NightNovis(self, weight=100):
        # 夜勤帯で同じグループのノービス2名はだめ絶対
        # nnv
        print("Night time novis should not be two in group.")
        exp_dict_A = dict()
        exp_dict_B = dict()
        dt3 = self.x.dt3_able.copy()
        tag_nights = ["MY_I", "YY_I"]
        As = ["A", "A/B"]
        Bs = ["B", "A/B"]
        for t in tag_nights:
            # print(t)
            dfw = self.x.df_week_task.query("tasks == @t").copy()

            for d in dt3["date_number"].unique():
                # print(d)
                # n_vet_total = dfw\
                #     .query("date_number == @d")["count_in_task"].to_list()[0]
                # n_min_vet_group = int(n_vet_total/2)
                # A ﾆB_S

                vars_a = dt3\
                    .query("date_number == @d")\
                    .query("DutyLabel == @t")\
                    .query("group in @As")["var_name"]

                exp_dict_A.update(
                    self.lm.getQ_fromVars_max1(var_list=vars_a))

                vars_b = dt3\
                    .query("date_number == @d")\
                    .query("DutyLabel == @t")\
                    .query("group in @Bs")["var_name"]

                exp_dict_B.update(
                    self.lm.getQ_fromVars_max1(var_list=vars_b))

        self.ne.Q_update(exp_dict_A, weight=weight)
        self.ne.Q_update(exp_dict_B, weight=weight)

    def tags_in(self, tag):
        return (len(self.exclude_list) == 0 and tag in self.include_list) or (len(self.include_list) == 0 and tag not in self.exclude_list)

    def makeAllLimitation(self, include=[], exclude=[], param_dict=dict(),
                          do_normalize=False,
                          hideProgressBar=False):
        self.ne.Q_reset()
        self.hideProgressBar = hideProgressBar
        self.include_list = include
        self.exclude_list = exclude

        if len(param_dict) != 0:
            self.param_dict.update(param_dict)

        # ひどいハードコーディングになっている。。。。
        # コールバック関数としてリファクタリング汁

        tag = "1by1"
        if self.tags_in(tag):
            self.limit_one_day_one_task(weight=self.param_dict[tag])

        tag = "cwork"
        if self.tags_in(tag):
            self.limit_continuouswork(weight=self.param_dict[tag])

        tag = "cnight"
        if self.tags_in(tag):
            self.limit_continiousNightWork(weight=self.param_dict[tag])

        tag = "fseq"
        if self.tags_in(tag):
            self.limit_ForbidSeq(weight=self.param_dict[tag])

        tag = "nseq"
        if self.tags_in(tag):
            self.limit_NeedSeq(weight=self.param_dict[tag])

        tag = "eqg3"
        if self.tags_in(tag):
            self.limit_EquGroup_dt3(weight=self.param_dict[tag])

        tag = "eqg2"
        if self.tags_in(tag):
            self.limit_EquGroup_dt2(weight=self.param_dict[tag])

        tag = "rqn"
        if self.tags_in(tag):
            self.limit_ReqNumberStaff(weight=self.param_dict[tag])

        tag = "rqh"
        if self.tags_in(tag):
            self.limit_ReqNumberWorkTime(weight=self.param_dict[tag])

        tag = "tt"
        if self.tags_in(tag):
            self.limit_TotalTask(weight=self.param_dict[tag])

        tag = "tn"
        if self.tags_in(tag):
            self.limit_TotalNights(weight=self.param_dict[tag])

        tag = "lfbd"
        if self.tags_in(tag):
            self.limit_ForbidSeq_fromLast(weight=self.param_dict[tag])

        tag = "lnd"
        if self.tags_in(tag):
            self.limit_NeedPair_fromLast(weight=self.param_dict[tag])

        tag = "lcnt"
        if self.tags_in(tag):
            self.limit_ContWork_fromLast(weight=self.param_dict[tag])

        tag = "lcnn"
        if self.tags_in(tag):
            self.limit_ContNight_fromLast(weight=self.param_dict[tag])

        tag = "sc"
        if self.tags_in(tag):
            self.limit_ShiftCount(weight=self.param_dict[tag])

        tag = "mps"
        if self.tags_in(tag):
            self.limit_MemberPairShift(weight=self.param_dict[tag])

        tag = "dab"
        if self.tags_in(tag):
            self.limit_DayABVetran(weight=self.param_dict[tag])

        tag = "nnv"
        if self.tags_in(tag):
            self.limit_NightNovis(weight=self.param_dict[tag])

        if do_normalize:
            self.ne.Q_normalize()

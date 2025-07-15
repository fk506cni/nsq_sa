# -*- coding: utf-8 -*-
"""
Created on 2020/1/2

@author: fk506cni=unkodaisuki!
"""
import pandas as pd
import datetime as dt
import calendar as cal

class x_read():
    # xsxを読み込むだけのクラスである。
    # これをオーバーライドして条件前テーブル群クラスにする。
    # todo parameter check
    # 全角半角チェック プライベート関数で良いだろう。
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_dict={}
    days_dict_rev={}

    def __init__(self, f=None):

        if f is None:
            print("xslx not given.")
        else:
            print("xlsx file is")
            print(f)
            self.df_MemberSchedules = pd.read_excel(f, sheet_name="MemberSchedules")
            self.df_DutySchedules = pd.read_excel(f, sheet_name="DutySchedules")
            self.df_MemberAbility = pd.read_excel(f, sheet_name="MemberAbility")
            self.df_SchedulesStatus = pd.read_excel(f, sheet_name="SchedulesStatus")

            self.df_MemberCapacity = pd.read_excel(f, sheet_name="MemberCapacity")
            self.df_MemberAbility_stack = self.df_MemberAbility.drop(columns=["memo", "group"]).set_index("name").stack().reset_index()
            self.df_MemberAbility_stack.columns = ["name", "tasks", "ability"]

            self.df_DutyClass = pd.read_excel(f, sheet_name="DutyClass")
            try:
                self.df_ShiftInfo = pd.read_excel(f, sheet_name="ShiftInfo").loc[:,["WS_SYMBOL","WORK_TIME"]]
                self.df_DutyClass = pd.merge(self.df_DutyClass, self.df_ShiftInfo, left_on="DutyClass", right_on="WS_SYMBOL", how="left").drop("WS_SYMBOL", axis=1)
            except TypeError as e:
                print(e)

            self.df_ForbiddenSequence = pd.read_excel(f, sheet_name="ForbiddenSequence")
            self.df_Holidays = pd.read_excel(f, sheet_name="Holidays")

            #"LastContinuousWorks"とLastContinuousNightWorksについてはNA補完しておく。
            self.df_FinalStatusAtLastMonth =pd.read_excel(f, sheet_name="FinalStatusAtLastMonth")
            self.df_FinalStatusAtLastMonth["LastContinuousWorks"].fillna(0,inplace=True)
            self.df_FinalStatusAtLastMonth["LastContinuousNightWorks"].fillna(0,inplace=True)

            self.df_ForbiddenPairShift = pd.read_excel(f, sheet_name="ForbiddenPairShift")

            self.df_NeededSequence = pd.read_excel(f, sheet_name="NeededSequence")

            self.df_MemberGroups = pd.read_excel(f, sheet_name="MemberInfo")

            for day, i in zip(["Holiday"] + self.days, range(0, len(self.days) + 1)):
                self.days_dict[day] = i
                self.days_dict_rev[i] =day
            
            self.df_params = pd.read_excel(f, sheet_name="MetaParams")
            self.param_dict = self.df_params.set_index("params").T.to_dict()
            self.num_wk_min_proc = self.param_dict["num_wk_min_proc"]["val"]
            self.num_wk_max_proc = self.param_dict["num_wk_max_proc"]["val"]
    


class xlsx2condtion(x_read):
    # xslxデータから、3種の条件テーブルを用意するクラス
    # 最終的には、リード→条件付きmake table→3種テーブル出来上がり


    holiday_mode =("asHoliday",
                   "asSaturday",
                   "asSunday")

    df_weeks = pd.DataFrame()

    num_working_days=0
    non_hols = ["Holiday", "Sunday", "Saturday"]

    max_date =0

    #平日数x8の時間は働く時間を確保するルールがあるとか。
    # num_wk_min_proc = 8
    # num_wk_max_proc = 15

    def echoU(self):
        print("wueeei!")



    def getWDdf(self):

        days5 = self.days * 6
        weeks5 = sum([[str(i)] * 7 for i in range(1, 7)], [])

        df_weeks = pd.DataFrame(columns=["days", "weeks"])
        df_weeks["days"] = days5
        df_weeks["weeks"] = weeks5
        df_weeks["days_number"] = df_weeks["weeks"] + "_" + df_weeks["days"]
        df_weeks["ind"] = df_weeks.index
        return df_weeks

    # 日付情報関連
    def getWDdf_arg(self, year, month):
        if len(str(month)) ==1:
            month_str = "0"+str(month)
        else:
            month_str = str(month)

        df = self.getWDdf()
        date1 = self.get1day(year, month)
        # date2 = self.getLastday(year, month)
        date2num = self.getLastdayNum(year, month)
        date1_day = self.days[date1.weekday()]
        ind_1st = int(df.query("days == @date1_day & weeks == '1'")["ind"])
        ind_last = ind_1st + date2num - 1
        df_weeks_arg = df.query("@ind_1st <= ind & ind <= @ind_last ")
        df_weeks_arg = df_weeks_arg.reset_index(drop=True)
        df_weeks_arg["date_number"] = df_weeks_arg.index +1
        df_weeks_arg["date_number_str"] = ["0" + str(i) if len(str(i)) == 1 else str(i) for i in df_weeks_arg["date_number"]]
        df_weeks_arg["yymmdd"] = str(year) + "/" + month_str+"/" +df_weeks_arg["date_number_str"].astype(str)
        df_weeks_arg["isHoliday"] = df_weeks_arg["yymmdd"].isin(self.df_Holidays["holidays"].astype(str).str.replace("-", "/"))
        # df_weeks_arg["days_ind"] = [self.days_dict[day] for day in df_weeks_arg["days"]]

        return df_weeks_arg

    def getDF_HolidayMode(self, year, month, holiday_mode):
        df_weeks = self.getWDdf_arg(year=year, month=month)

        if holiday_mode == "asHoliday":
            print("holidaymode:" + holiday_mode)
            print("days that is holiday and not sunday will be Holiday.")
            df_weeks["days4proc"] = ["Holiday" if j and i != "Sunday" else i for i, j in zip(df_weeks["days"], df_weeks["isHoliday"])]
        elif holiday_mode == "asSaturday":
            print("holidaymode:" + holiday_mode)
            print("days that is holiday and not sunday will be Saturday.")
            df_weeks["days4proc"] = ["Saturday" if j and i != "Sunday" else i for i, j in zip(df_weeks["days"], df_weeks["isHoliday"])]
        elif holiday_mode == "asSunday":
            print("holidaymode:" + holiday_mode)
            print("days that is holiday and not sunday will be Sunday.")
            df_weeks["days4proc"] = ["Sunday" if j and i != "Sunday" else i for i, j in
                                     zip(df_weeks["days"], df_weeks["isHoliday"])]
        else:
            print("holidaymode:" +holiday_mode)
            print("this not proper arg...")
            df_weeks["days4proc"] = df_weeks["days"]

        df_weeks["num_days4proc"] = [str(i) + "_" + j if j != "Holiday" else "0_" + j for i, j in zip(df_weeks["weeks"], df_weeks["days4proc"])]




        return df_weeks

    def get1day(self, year, month):
        return dt.date(year=year, month=month, day=1)

    def getLastday(self, year, month):
        return dt.date(year=year, month=month, day=1)+dt.timedelta(days= cal.monthrange(year, month)[1] -1)

    def getLastdayNum(self, year, month):
        return cal.monthrange(year, month)[1]

    # タスクテーブル関連
    def getTaskTable(self):
        df = self.df_DutySchedules.copy()
        df_stack = df.set_index(["week_num", "days"], drop=True).stack()
        df_stack = df_stack.reset_index()
        df_stack.columns = ["week_num", "days", "tasks", "count_in_task"]

        self.task_dict = dict()
        self.task_dict_rev = dict()
        dx_tasks = df_stack["tasks"].unique()
        for i in range(0, len(dx_tasks)):
            self.task_dict[dx_tasks[i]] = i + 1
            self.task_dict_rev[i+1] = dx_tasks[i]

        # task_factors
        # dx2_len = df_stack["count"].sum()

        #modify!
        dx2_len = len(df_stack)

        # dx2 = pd.DataFrame(columns=["week_num", "days", "tasks", "task_num", "count_in_task"], index=range(0, dx2_len))
        dx2 = df_stack.copy()
        dx2["task_num"] = [self.task_dict[task] for task in dx2["tasks"]]
        dx2 = dx2.query("count_in_task != 0").copy()

        numd = dx2["week_num"].astype(str) + "_" + dx2["days"]

        # dx2.loc[:,"num_days"] = numd.to_list()
        dx2["num_days"] = numd.to_list()
        

        df_dcla = self.df_DutyClass.copy()
        df_dcla["task_ind"] = df_dcla.index + 1
        dx3 = pd.merge(dx2, df_dcla, left_on="tasks", right_on="DutyLabel")

        self.dclass_dict = {}
        self.dclass_dict_rev ={}

        dclass_unique = dx3["DutyClass"].unique()
        for dc, k in zip(dclass_unique, range(0, len(dclass_unique))):
            # print(task, k)
            self.dclass_dict[dc] = k+1
            self.days_dict_rev[k+1] = dc

        dx3["dclass_ind"] = [self.dclass_dict[dc] for dc in dx3["DutyClass"]]
        dx3["days_ind"] = [self.days_dict[day] for day in dx3["days"]]

        dx3.sort_values(['week_num', 'days_ind'], inplace=True)
        return dx3

    # member scedule 関連
    def getMenDfStack(self, year, month):

        xmen_pre = self.df_MemberSchedules.copy().drop(columns=["memo", "group", "membermemo", "shiftmemo"]).set_index("name").T
        xmen_pre = xmen_pre.stack().reset_index()
        xmen_pre = xmen_pre.rename(columns={0: 'status', "level_0":"date_number"})

        xmen_pre2 = pd.merge(xmen_pre, self.df_SchedulesStatus, left_on="status", right_on="code", how="left")
        xmen_pre2 = xmen_pre2.drop(columns=["status", "code"]).set_index(["date_number", "name"]).stack().reset_index().rename(columns={"level_2":"DutyClass", 0:"takability"})

        wd = self.getWDdf_arg(year=year, month=month).drop(columns=["ind","isHoliday","date_number_str","yymmdd"]).rename(columns ={"days_number":"num_days"})
        xmen = pd.merge(xmen_pre2, wd, on="date_number", how="left").dropna(subset=["num_days"])

        # xmen_pre2.head()

        # xmen = self.df_MemberSchedules.copy().set_index(["name", "week"], drop=True).stack().reset_index()
        # xmen.columns = ["name", "weeks", "days", "takability"]
        # xmen["num_days"] = xmen["weeks"].astype(str) + "_" + xmen["days"]

        self.men_dict = {}
        self.men_dict_rev ={}
        men_unique = xmen["name"].unique()

        self.num_day_dict = {}
        self.num_day_dict_rev={}
        num_day_unique = xmen["num_days"].unique()

        for men, i in zip(men_unique, range(0, len(men_unique))):
            self.men_dict[men] = i + 1
            self.men_dict_rev[i+1] = men

        for num_day, i in zip(num_day_unique, range(0, len(num_day_unique))):
            self.num_day_dict[num_day] = i + 1
            self.num_day_dict_rev[i+i] = num_day

        xmen["name_ind"] = [self.men_dict[men] for men in xmen["name"]]
        xmen["num_days_ind"] = [self.num_day_dict[num_day] for num_day in xmen["num_days"]]

        xmen = xmen.drop(columns = ["date_number"])
        return xmen

    def make3CDT(self, year=2020, month=1, holiday_mode="asHoliday"):
        print("make condition tables.")
        print("holidaymode:", holiday_mode)
        print("year: ", year)
        print("month: ", month)


        #cap last df is created this phase... not elegant.
        self.set_CapLastDF()

        self.df_weeks = self.getDF_HolidayMode(year=year, month=month, holiday_mode=holiday_mode)
        self.num_working_days = len(self.df_weeks.query("days4proc not in @self.non_hols"))
        self.df_mens = self.getMenDfStack(year=year, month=month)

        # 1st dt1
        # self.dt1 = self.df_mens.copy()

        # 1st dt3
        self.df_week_task = pd.merge(self.df_weeks.copy().drop(["days", "weeks", "ind"], axis=1), self.getTaskTable(), left_on="num_days4proc", right_on="num_days").drop("num_days",axis=1)
        dt3 = pd.merge(self.df_mens.copy().drop("days", axis=1), self.df_week_task, left_on=["num_days","DutyClass"],right_on=["days_number","DutyClass"], how='inner').drop("days_number", axis=1)

        dt3["var_name"] = dt3["name_ind"].astype(str) + "_" + \
                          dt3["date_number"].astype(str) + "_" + \
                          dt3["dclass_ind"].astype(str) + "_" + \
                          dt3["task_ind"].astype(str) + "_" + \
                          dt3["count_in_task"].astype(str)
        dt3.reset_index(drop=True, inplace=True)



        dt3_cap = pd.merge(dt3, self.df_MemberAbility_stack, on=["name", "tasks"])
        dt3_cap.reset_index(drop=True, inplace=True)
        dt3_g = pd.merge(dt3_cap, self.df_MemberGroups, on="name")
        dt3_g.reset_index(drop=True, inplace=True)


        self.dt3 = dt3_g
        self.max_date = dt3_g["date_number"].max()



        # need seqの独立前後問題のフィルタリングを追加。
        df_need = self.df_NeededSequence.copy()
        pre_not_only = df_need["Before"].to_list()
        # print(pre_not_only)
        post_not_only = df_need["After"].to_list()
        # print(post_not_only)

        dt3_able = dt3_g.query("ability == 1 and takability ==1").copy()


        dt3_ab = dt3_able.loc[:, ["name", "date_number", "week_num", "DutyClass", "dclass_ind", "var_name"]].copy()
        dt3_ab["after"] = dt3_ab["date_number"] + 1
        # dt2m_ab
        dt3_lim = dt3_able.loc[:, ["name", "date_number", "DutyClass", "dclass_ind", "var_name"]].copy()
        dt3_lim.columns = ["name", "date_number2", "DutyClass2", "dclass_ind2", "var_name2"]
        dt3_ab2 = pd.merge(dt3_ab, dt3_lim, left_on=["name", "after"], right_on=["name", "date_number2"], how="outer")

        # 最終日は除く?
        max_date = self.max_date
        #
        # .query("date_number != 1")
        fbd_pre = dt3_ab2.query("var_name2 != var_name2").query("DutyClass in @pre_not_only").query("date_number != @max_date")["var_name"].to_list()
        fbd_post = dt3_ab2.query("var_name != var_name").query("date_number2 != 1").query("DutyClass2 in @post_not_only")["var_name2"].to_list()
        fbd_lack_pair = fbd_pre + fbd_post

        self.dt3_able = dt3_g.query("ability == 1 and takability ==1").query("var_name not in @fbd_lack_pair")


        # 2nd dt2
        dt2_pre = self.dt3.copy()
        dt2_pre.drop(["DutyLabel", "task_ind"], inplace=True, axis=1)
        # dt2_pre.shape
        dt2_pre.drop_duplicates(subset=["weeks", "name_ind", "date_number", "dclass_ind"], inplace=True)
        dt2_pre.sort_values(["name_ind", "date_number", "dclass_ind"], inplace=True)
        dt2_pre.drop(["days", "tasks", "num_days_ind"], axis=1, inplace=True)
        dt2_pre["var_name"] = dt2_pre["name_ind"].astype(str) + "_" + \
                              dt2_pre["date_number"].astype(str) + "_" + \
                              dt2_pre["dclass_ind"].astype(str) + "_0_0"


        dt2_pre.reset_index(drop=True, inplace=True)
        self.dt2 = dt2_pre

        # 3rd dt1
        dt1 = self.dt2.copy()
        dt1.drop(["task_num", "count_in_task", "DutyClass", "dclass_ind", "days_ind"], axis=1, inplace=True)
        dt1.drop_duplicates(subset=["name_ind", "date_number"], inplace=True)
        dt1.reset_index(drop=True, inplace=True)
        dt1["var_name"] = dt1["name_ind"].astype(str) + "_" + \
                          dt1["date_number"].astype(str) + "_0_0_0"
        self.dt1 = dt1

        # dummys
        # dummy dates
        max_date = self.df_MemberCapacity["CapableTotalWorks"].max()

        self.dv_date = ["dd_" + str(i) for i in range(1, max_date+1)]

        # dummy night
        # ここはそれぞれの夜勤クラスの個数になる。抽象度が低くて涙が出ますよ。
        # max_nights = self.df_MemberCapacity["CapableNights"].max()
        # self.dv_night = ["dn_"+ str(i) for i in range(1, max_nights +1)]

        # seq set
        self.set_ForbiddenSequence = set()
        self.set_ForbiddenSequence_ind = set()
        for r in self.df_ForbiddenSequence.itertuples():
            if r.Before in self.dclass_dict.keys() and r.After in self.dclass_dict.keys():
                # print(r.Before)
                # print(r.After)
                self.set_ForbiddenSequence.add((r.Before, r.After))
                self.set_ForbiddenSequence_ind.add((self.dclass_dict[r.Before], self.dclass_dict[r.After]))

            # forbid setting
        self.df_ForbiddenSequence["bef_num"] = [self.dclass_dict[task] if task in self.dclass_dict.keys() else 0
                                                  for
                                                  task in self.df_ForbiddenSequence["Before"]]
        self.df_ForbiddenSequence["aft_num"] = [self.dclass_dict[task] if task in self.dclass_dict.keys() else 0
                                                  for
                                                  task in self.df_ForbiddenSequence["After"]]

        self.set_NeedSeq = set()
        self.set_NeedSeq_ind = set()
        for r in self.df_NeededSequence.itertuples():
            if r.Before in self.dclass_dict.keys() and r.After in self.dclass_dict.keys():
                # print(r.Before)
                # print(r.After)
                self.set_NeedSeq.add((r.Before, r.After))
                self.set_NeedSeq_ind.add((self.dclass_dict[r.Before], self.dclass_dict[r.After]))


        self.dict_NeedSeq = dict()
        for bef in self.df_NeededSequence["Before"].unique():
            df_b = self.df_NeededSequence.query("Before == @bef")["After"].to_list()
            self.dict_NeedSeq[bef] = set(df_b)

        self.df_NeededSequence["bef_num"] = [self.dclass_dict[task] if task in self.dclass_dict.keys() else 0
                                               for
                                               task in self.df_NeededSequence["Before"]]
        self.df_NeededSequence["aft_num"] = [self.dclass_dict[task] if task in self.dclass_dict.keys() else 0
                                               for
                                               task in self.df_NeededSequence["After"]]

        #このdfが多分変なことになっている。 修正済み。条件エクセルが第6週を含んでいなかったため。
        df_req = self.df_DutySchedules.set_index(["week_num", "days"]).stack().reset_index()


        # df_req
        df_req.columns = ["week_num", "days", "task", "count"]
        df_req["num_days4proc"] = df_req["week_num"].astype(str) + "_" + df_req["days"]
        df_req.drop("days", axis=1, inplace=True)
        df_req_jn = pd.merge(self.df_weeks, df_req, on="num_days4proc", how="left")
        df_req_jn["task_ind"] = [self.task_dict[i] for i in df_req_jn["task"]]
        self.df_RequireTask = df_req_jn
        # self.df_RequireTask = df_req

        wd = ['Holiday', 'Saturday', 'Sunday']
        self.total_weekdays= len(self.df_weeks.query("days4proc not in @wd"))







    def save3cond(self, prefix="cond_"):
        f1 = prefix+"dt1.csv"
        f2 = prefix+"dt2.csv"
        f3 = prefix+"dt3.csv"
        self.dt1.to_csv(f1, sep=",", index=None, encoding='utf_8_sig')
        self.dt2.to_csv(f2, sep=",", index=None, encoding='utf_8_sig')
        self.dt3.to_csv(f3, sep=",", index=None, encoding='utf_8_sig')

    def set_CapLastDF(self):
        self.df_CapaAndLast = pd.merge(self.df_MemberCapacity, self.df_FinalStatusAtLastMonth, on="name")
        self.df_CapaAndLast["max_1st_cont"] = self.df_CapaAndLast["CapableContinuousWorks"] -self.df_CapaAndLast["LastContinuousWorks"]
        self.df_CapaAndLast["max_1st_cont_night"] = self.df_CapaAndLast["CapableContinuousNightWorks"] -self.df_CapaAndLast["LastContinuousNightWorks"]


    
    def getCapaEvalDf(self
            # df_DutyClass,
            #       df_DutySchedules,
            #       df_MemberCapacity
                  ):
        memcap = self.df_MemberCapacity.copy() \
            .loc[:,["CapableNN","CapableMY","CapableYy"]] \
            .apply(sum, axis = 0) \
            .reset_index() \
            .rename(columns={
            "index":"CapaLabel",
            0:"DutyClass_capa"
                }) \
            .assign(CapaLabel = lambda df:df.CapaLabel.str.replace("Capable", ""))
        
        df_dc_count = self.df_week_task \
            .groupby("DutyClass") \
            ["count_in_task"].sum() \
            .reset_index()
            
        dc_eval = pd.merge(memcap, df_dc_count,
                     left_on="CapaLabel",
                     right_on="DutyClass", how="outer")
        return dc_eval
    





import  time
import os
from contextlib import redirect_stdout

def SetQG(f = "../demos/demo10.xlsx"):
    global importlib
    importlib = __import__('importlib', globals(), locals())

    #条件もとの3テーブルを作るモジュール
    global nl
    nl = __import__('nlp_connect', globals(), locals())
    importlib.reload(nl)

    # setting
    global nst
    nst =  __import__("nsp_settings", globals(), locals())
    importlib.reload(nst)

    global pd
    pd = __import__('pandas', globals(), locals())

    global np
    np = __import__('numpy', globals(), locals())

    global lmt
    lmt = __import__("nlp_limiter", globals(), locals())
    importlib.reload(lmt)

    global ps
    ps =  __import__("p_solver", globals(), locals())
    importlib.reload(ps)

    global rps
    rps =  __import__("res_parser", globals(), locals())
    importlib.reload(rps)

    global x
    x = nl.xlsx2condtion(f)
    x.make3CDT(yaer=2020, month=1, holiday_mode="asHoliday")

    global qg
    qg = lmt.q_gen(x2c=x)
    qg.ne.Q_reset()

def setQG_null(f = "../demos/demo10.xlsx"):
    with redirect_stdout(open(os.devnull, 'w')):
        SetQG(f = f)




def AftLmt(sw=30000):
    print("total nodes:", str(len(qg.ne.nodes)))
    print("length of q:", str(len(qg.ne.getQ())))
    start_time = time.time()
    global p
    p = ps.psol(q=qg.ne.getQ(),
                num_reads=2,
                sweeps=sw, seed=10)
    global mins
    mins = p.p_solve_getMin(threads=5, times=5)
    end_time = time.time()
    el_time = (end_time - start_time)/60

    print(f"経過時間：{el_time}_min")

    global rps
    rps = __import__("res_parser", globals(), locals())
    importlib.reload(rps)

    import res_parser as rps
    importlib.reload(rps)

    global rp
    rp = rps.res_parser(x=x)
    rp.prepRes(res=mins.sample, hideProgressBar=True)

    global rc
    rc = rps.res_checker(x=x)

    global tm
    tm = rps.table_maker(x=x, res=mins.sample)


#!/usr/bin/python3
# =============================================================================
# bankroll_1_buywrite.py — does options income earn its keep, or just cap your upside?
#
# (A) THE COMPLEX vs SPY (total return): naive always-write (XYLD/QYLD/RYLD) vs active/selective (DIVO/JEPI)
#     vs the index. The buy-write trade: keep the fat LEFT tail, sell the right tail for premium. Does the
#     premium beat the surrendered upside risk-adjusted (M²), and is the "high yield" real or return-of-capital
#     (total return < SPY ⇒ the yield was partly your own capital back)?
# (B) GATED buy-write — can TIMING the call-writing rescue it? Hold SPY, switch to XYLD (write calls) by a
#     causal vol regime. Both directions: write-when-vol-is-RICH (high, fat premium) vs write-when-CALM
#     (clip steady premium, keep upside in storms). vs always-XYLD and always-SPY.
# Alpaca SIP daily TOTAL return, causal. The honest frame: is this a return source, or a vol/income tool?
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bankroll_common import panel, rets, lag, riskadj, stats
import numpy as np

P, dates = panel(["SPY", "XYLD", "QYLD", "RYLD", "DIVO", "PBP", "JEPI"])
R = {s: rets(P[s]) for s in P}; spy = R["SPY"]
print("="*96); print(f"BANKROLL #1 — options income: earns its keep, or caps upside?  ({dates[0]} → {dates[-1]}, {len(dates)} days)"); print("="*96)

# ---- (A) the complex vs SPY --------------------------------------------------------------------------
print(f"\n(A) COMPLEX vs SPY (total return)   {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'vol':>7}{'skew':>7}{'β/SPY':>7}{'M²exc':>8}")
labels={"SPY":"index","XYLD":"S&P buy-write","QYLD":"NDX buy-write","RYLD":"R2k buy-write",
        "DIVO":"active/selective","PBP":"classic BuyWrite","JEPI":"active (short hist)"}
for s in ["SPY","XYLD","QYLD","RYLD","DIVO","PBP","JEPI"]:
    if s not in R: continue
    a=riskadj(R[s],spy[-len(R[s]):]) if s!="SPY" else riskadj(R[s],spy)
    print(f"  {s:5} {labels[s]:20}{a['sh']:>+8.2f}{a['cagr']*100:>+7.0f}%{a['dd']*100:>+7.0f}%{a['vol']*100:>6.0f}%{a['skew']:>+7.2f}{a.get('beta',1):>+7.2f}{a['m2_excess']*100:>+7.1f}%")

# ---- (B) gated buy-write (SPY <-> XYLD on a causal vol regime) ---------------------------------------
# align SPY & XYLD
m=min(len(R["SPY"]),len(R["XYLD"])); sp=R["SPY"][-m:]; xy=R["XYLD"][-m:]
rv21=np.array([sp[max(0,t-21):t].std()*np.sqrt(252) if t>21 else np.nan for t in range(m)])
med =np.array([np.nanmedian(rv21[max(0,t-252):t]) if t>60 else np.nan for t in range(m)])
rich = lag((rv21>=med).astype(float))                    # vol high = premium rich
write_rich = np.where(rich==1, xy, sp)                   # write calls when vol rich, else hold SPY
write_calm = np.where(rich==0, xy, sp)                   # write calls when calm, else hold SPY
print(f"\n(B) GATED buy-write (SPY↔XYLD)      {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'M²exc':>8}")
for nm,r in [("always SPY",sp),("always XYLD (buy-write)",xy),("write when vol RICH",write_rich),("write when CALM",write_calm)]:
    a=riskadj(r,sp); print(f"  {nm:28}{a['sh']:>+8.2f}{a['cagr']*100:>+7.0f}%{a['dd']*100:>+8.0f}%{a['m2_excess']*100:>+7.1f}%")

# ---- verdict -----------------------------------------------------------------------------------------
xa=riskadj(R["XYLD"],spy[-len(R["XYLD"]):]); da=riskadj(R["DIVO"],spy[-len(R["DIVO"]):])
best_gate=max(riskadj(write_rich,sp)['m2_excess'], riskadj(write_calm,sp)['m2_excess'])
naive_caps = xa['cagr']<stats(spy[-len(R["XYLD"]):])['cagr'] and xa['m2_excess']<0
active_ok  = da['m2_excess']>0 or da['sh']>riskadj(spy[-len(R["DIVO"]):],spy[-len(R["DIVO"]):])['sh']
if best_gate>0.01 and best_gate>xa['m2_excess']:
    v=f"CONDITIONAL+: timing helps — a gated buy-write beats always-writing (M²exc {best_gate*100:+.1f}%). Options income done RIGHT (write selectively) is a real low-vol/income tool, not a pure drag."
elif active_ok and naive_caps:
    v="CONDITIONAL: NAIVE buy-write (XYLD/QYLD) is a DRAG — it caps the upside for less than it's worth (negative M², lower CAGR), confirming brace. But ACTIVE/selective (DIVO/JEPI) ~holds SPY at lower vol — an income/vol-reduction tool, not an alpha source."
else:
    v="NULL-ish: options income does not clear the hurdle — the premium collected does not pay for the upside surrendered; the high distribution yield is largely return-of-capital. A vol-dampener at best (brace confirmed)."
print(f"\n  VERDICT: {v}")
print("  (Total-return basis already nets the distributions, so 'underperforms SPY' = the yield was partly your own")
print("   capital. The honest niche: lower-vol equity income for a drawdown-sensitive holder — not a return edge.)")

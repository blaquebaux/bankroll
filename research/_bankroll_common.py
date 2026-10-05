#!/usr/bin/python3
# =============================================================================
# _bankroll_common.py — shared helpers for Blaque Baux BANKROLL (systematic options income).
# Alpaca SIP daily bars (adjustment=all → TOTAL return, so distributions are counted); read-only.
#
# BANKROLL tests whether writing options for income EARNS ITS KEEP or just caps your upside. Unlike naked
# short-vol (brace/bushel = landmine), a COVERED overlay keeps the underlying — the question is whether the
# premium collected beats the upside surrendered. Liquid embodiments: XYLD/QYLD/RYLD (naive always-write
# buy-write), DIVO/JEPI/JEPQ (active/selective), PBP (classic BuyWrite). Compared on TOTAL return vs SPY,
# because a 10%+ distribution yield that underperforms SPY is return-of-capital, not income. Verdicts weigh
# M² (risk-adjusted, benchmark-relative) and skew — buy-write trades a fat left tail kept for a capped right.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1
def lag(x):   x = np.asarray(x, float); o = np.zeros_like(x); o[1:] = x[:-1]; return o

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=(cum/np.maximum.accumulate(cum)-1).min(), vol=r.std()*math.sqrt(252))

def jarque_bera(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]; n = len(r)
    if n < 30 or r.std() == 0: return dict(jb=float('nan'), p=float('nan'), skew=float('nan'), exkurt=float('nan'))
    z = (r - r.mean())/r.std(); sk = float(np.mean(z**3)); ku = float(np.mean(z**4)-3.0)
    jb = n/6.0*(sk**2 + ku**2/4.0)
    return dict(jb=jb, p=math.exp(-jb/2.0), skew=sk, exkurt=ku)

def jensens_alpha(r, rb, rf=0.0):
    r = np.asarray(r, float); rb = np.asarray(rb, float); m = np.isfinite(r) & np.isfinite(rb); r, rb = r[m], rb[m]
    if len(r) < 30 or np.var(rb) == 0: return dict(alpha_ann=float('nan'), beta=float('nan'))
    beta = float(np.cov(r, rb)[0, 1]/np.var(rb))
    return dict(alpha_ann=(r.mean() - beta*rb.mean())*252, beta=beta)

def m_squared(r, rb, rf=0.0):
    r = np.asarray(r, float); rb = np.asarray(rb, float); r = r[np.isfinite(r)]; rb = rb[np.isfinite(rb)]
    if len(r) < 30 or r.std() == 0 or rb.std() == 0: return dict(m2_excess=float('nan'))
    shp = r.mean()/r.std()*math.sqrt(252); shb = rb.mean()/rb.std()*math.sqrt(252)
    return dict(m2_excess=(shp - shb)*rb.std()*math.sqrt(252))

def riskadj(r, rb, rf=0.0):
    out = dict(stats(r)); out.update(jarque_bera(r)); out.update(jensens_alpha(r, rb, rf)); out.update(m_squared(r, rb, rf))
    return out

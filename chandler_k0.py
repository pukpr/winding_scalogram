import json, sys
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize
from winding_rank import find_ridges, continuity
from winding_scalogram import winding_transform

YL = 365.2463
P_N = 27.21222
alias = YL / P_N % 1.0
print(f"alias: yl/P={YL/P_N:.5f} frac={alias:.5f} -> {1/alias*YL:.2f} d ;  2*frac -> {1/(2*alias)*YL:.2f} d")

def load_pole(fn, m0=None, m1=None):
    raw = np.loadtxt(fn, comments="#")
    if raw.shape[1] >= 10:                       # eopc01.1846-now: MJD(col0), x, y, ...
        yrs = 1858.88 + raw[:,0]/365.2422        # MJD incl. negative pre-1858 values
        x, y = raw[:,1], raw[:,2]
    else:                                        # c04 already reduced upstream? not used
        raise SystemExit("unexpected format")
    good = ~(np.isnan(x) | np.isnan(y))
    yrs, x, y = yrs[good], x[good], y[good]
    sel = np.ones(len(yrs), bool)
    if m0 is not None: sel &= yrs >= m0
    if m1 is not None: sel &= yrs < m1
    yrs, x, y = yrs[sel], x[sel], y[sel]
    edges = np.arange(yrs[0], yrs[-1], 1/12.)
    idx = np.clip(np.searchsorted(edges, yrs)-1, 0, len(edges)-2)
    tg = (edges[:-1]+edges[1:])/2
    def mm(v):
        out = np.array([v[idx==k].mean() if np.any(idx==k) else np.nan for k in range(len(tg))])
        g = ~np.isnan(out)
        return np.interp(tg, tg[g], out[g])
    return tg, mm(x), mm(y)

def load_pole_c04(fn, m0=None, m1=None):
    raw = np.loadtxt(fn, comments="#", usecols=(0,1,2,3,5,6))
    yrs = raw[:,0] + (raw[:,1]-1)/12 + (raw[:,2]-0.5)/365.2422
    x, y = raw[:,4], raw[:,5]
    sel = (yrs >= (m0 or -1e9)) & (yrs < (m1 or 1e9))
    yrs, x, y = yrs[sel], x[sel], y[sel]
    edges = np.arange(yrs[0], yrs[-1], 1/12.)
    idx = np.clip(np.searchsorted(edges, yrs)-1, 0, len(edges)-2)
    tg = (edges[:-1]+edges[1:])/2
    def mm(v):
        out = np.array([v[idx==k].mean() if np.any(idx==k) else np.nan for k in range(len(tg))])
        g = ~np.isnan(out)
        return np.interp(tg, tg[g], out[g])
    return tg, mm(x), mm(y)

t4, x4, y4 = load_pole_c04("/home/paul/campaign/blind/AG1/eopc04_20.1962-now", 1962, 2025)
tL, xL, yL = load_pole("/home/paul/campaign/blind/AG1/eopc01.1846-now", 1846, 2025)
rho4 = float(np.corrcoef(x4[1:],x4[:-1])[0,1]); rhoL = float(np.corrcoef(xL[1:],xL[:-1])[0,1])
print(f"c04 n={len(t4)} rho={rho4:.3f}   c01 n={len(tL)} rho={rhoL:.3f}")
for nm, s in (("c04",x4),("c01",xL)):
    N=len(s); w=np.hanning(N); S=np.abs(np.fft.rfft(s*w)); fr=np.fft.rfftfreq(N,1/12)
    m_=(fr>0.5)&(fr<1.4); fpk=fr[m_][np.argmax(S[m_])]
    print(f"obs CW line {nm}: {fpk:.4f} c/yr = {YL/fpk:.2f} d")

p = json.load(open("/home/paul/eval/winding_scalogram/qbo30/lt.exe.p"))
L = np.array(p["lpap"]); per, amp = L[:,0], L[:,1:3]
B = {k: float(p[k]) for k in ("delA","delB","asym","ma","mp","init","shfT")}
mNfam = np.logical_or(np.logical_and(per>=26.9, per<=27.7), np.logical_and(per>=13.5, per<=13.9))
mfull = np.ones(len(per), bool)
DPOS = int(round(B["delB"]*12)) % 12

def manifold(tt, subset, mode="comb"):
    idx = np.where(subset)[0]
    tf = tide_sum(tt, amp[idx], per[idx], YL, integ=B["shfT"])
    if mode == "comb":
        raw = tf * impulse_delta(tt, B["delA"], B["delB"], B["asym"], 12)
    elif mode == "equal2p":   # article: two equal hemisphere pulses / yr
        comb = np.zeros_like(tf)
        mo = np.rint((tt - tt[0])*12).astype(int) % 12
        comb[mo==DPOS] += B["delA"]; comb[mo==(DPOS+6)%12] += B["delA"]
        raw = tf*comb
    elif mode == "singlep":   # one impulse / yr
        comb = np.zeros_like(tf)
        mo = np.rint((tt - tt[0])*12).astype(int) % 12
        comb[mo==DPOS] += B["delA"]
        raw = tf*comb
    elif mode == "rect":      # square wave at 2/yr: strongest 2-pole comb
        mo = ((tt - tt[0])*12)
        comb = np.sign(np.cos(np.pi*(mo - DPOS)))   # + on slot DPOS..DPOS+5 etc
        raw = tf*comb*abs(B["delA"])
    else: raw = tf
    f = iir(raw, lag_a=1.0-B["ma"], lag_c=B["mp"], init=B["init"], start_date=tt[0], dates=tt)
    return f - f.mean()

def ar1_floor(tt, F, m_grid, t0_grid, sigma, rho, n_reps=30):
    rng = np.random.default_rng(1)
    acc = np.zeros((len(m_grid), len(t0_grid)))
    for _ in range(n_reps):
        e = rng.standard_normal(len(tt)); s = np.empty(len(tt)); s[0]=e[0]
        for i in range(1,len(tt)): s[i]=rho*s[i-1]+np.sqrt(1-rho**2)*e[i]
        G,_,_ = winding_transform(tt, standardize(s), F, m_grid, t0_grid, sigma)
        acc += np.abs(G)**2
    return acc/n_reps

def scan(tag, tt, F, target, rho):
    m_grid = np.arange(0.0, 2.001, 0.01)
    t0_grid = np.arange(tt[0]+5, tt[-1]-5+1e-9, 2.5)
    G,_,_ = winding_transform(tt, standardize(target), F, m_grid, t0_grid, 10.0)
    lp = np.log2(np.maximum(np.abs(G)**2/ar1_floor(tt,F,m_grid,t0_grid,10.0,rho), 1e-9))
    prof = np.abs(G).mean(axis=1)
    out = sorted([(round(M,3),round(float(pk),2),round(float(ct),2))
                  for M,pk,fw in find_ridges(m_grid,prof,lp,2.0,0.12)
                  for ct in [continuity(lp,m_grid,M)]], key=lambda r:-r[1])
    at={}
    for q,lab in [(alias,"0.422"),(2*alias,"0.844")]:
        i=np.argmin(abs(m_grid-q))
        at[lab]=(float(m_grid[i]), round(float(prof[i]),3), round(float(lp.mean(axis=1)[i]),2),
                 round(float(continuity(lp,m_grid,q)),2))
    print(f"\n== {tag} == teeth: {out[:6]}")
    print(f"   pred@0.422: {at['0.422']}  @0.844: {at['0.844']}")
    return {"teeth": out, "at": at}

res = {}
res["c04_equal2p"] = scan("c04 x: Nfam + equal 2-pole comb", t4, manifold(t4,mNfam,"equal2p"), x4, rho4)
res["c04_prodcomb"] = scan("c04 x: Nfam + prod comb (asym .1)", t4, manifold(t4,mNfam,"comb"), x4, rho4)
res["c04_singlep"] = scan("c04 x: Nfam + single-pole (1/yr)", t4, manifold(t4,mNfam,"singlep"), x4, rho4)
res["c04_rect"]    = scan("c04 x: Nfam + square-wave 2/yr", t4, manifold(t4,mNfam,"rect"), x4, rho4)
res["c04_nocomb"]  = scan("c04 x: Nfam NO comb", t4, manifold(t4,mNfam,"none"), x4, rho4)
res["c04_full2p"]  = scan("c04 x: FULL 42-line + equal 2-pole", t4, manifold(t4,mfull,"equal2p"), x4, rho4)
res["c04_rectfull"]= scan("c04 x: FULL 42-line + square 2/yr", t4, manifold(t4,mfull,"rect"), x4, rho4)
res["c04_y_equal"] = scan("c04 y: Nfam + equal 2-pole", t4, manifold(t4,mNfam,"equal2p"), y4, rho4)
res["c01_x_rect"]  = scan("c01(1846-) x: Nfam square 2/yr", tL, manifold(tL,mNfam,"rect"), xL, rhoL)
res["c01_x_equal"] = scan("c01(1846-) x: Nfam equal 2-pole", tL, manifold(tL,mNfam,"equal2p"), xL, rhoL)
json.dump(res, open("/home/paul/eval/winding_scalogram/chandler_k0_ridges.json","w"))
print("\nsaved chandler_k0_ridges.json")

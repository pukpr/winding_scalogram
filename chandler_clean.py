import json, sys
import numpy as np
sys.path.insert(0, "/home/paul/eval/winding_scalogram")
from lte_forward import tide_sum, impulse_delta, iir
from wavelet_scalogram import standardize
from winding_rank import find_ridges, continuity
from winding_scalogram import winding_transform

YL = 365.2463
P_N = 27.21222
alias = YL / P_N % 1.0        # 0.42214 -> 865.2 d ;  2*alias -> 432.6 d (CW)

# ---------- targets: IERS pole x, monthly and daily, ANNUAL-NUISANCE CLEANED
def clean(tt, v, freqs=(1.0, 2.0)):
    """remove quadratic trend + sin/cos at each freq (c/yr) — annual wobble
    and semiannual are nuisance terms for the CW winding test (user directive)."""
    y = (tt - tt.mean())
    A = [np.ones_like(tt), y, y**2]
    for f in freqs:
        A += [np.cos(2*np.pi*f*(tt - tt[0])), np.sin(2*np.pi*f*(tt - tt[0]))]
    A = np.stack(A, 1)
    b, *_ = np.linalg.lstsq(A, v, rcond=None)
    return v - A @ b, b

raw4 = np.loadtxt("/home/paul/campaign/blind/AG1/eopc04_20.1962-now", comments="#", usecols=(0,1,2,5,6))
td = raw4[:,0] + (raw4[:,1]-1)/12 + (raw4[:,2]-0.5)/365.2422
xd, yd = raw4[:,3], raw4[:,4]
sel = (td>=1962)&(td<2025)
td, xd = td[sel], xd[sel]
xc_d, coef = clean(td, xd)
# monthly block means of the DAILY-cleaned series (same edges as before)
edges = np.arange(td[0], td[-1], 1/12.)
idx = np.clip(np.searchsorted(edges, td)-1, 0, len(edges)-2)
tm = (edges[:-1]+edges[1:])/2
xm = np.array([xc_d[idx==k].mean() for k in range(len(tm))])
for lab, s in (("daily raw", xd), ("daily cleaned", xc_d), ("monthly cleaned", xm)):
    w=np.hanning(len(s)); S=np.abs(np.fft.rfft((s-s.mean())*w)); fr=np.fft.rfftfreq(len(s),1/ (365.2422 if 'daily' in lab else 12))
    m_=(fr>0.6)&(fr<1.1); i=np.argmax(S[m_])
    m2=(fr>0.8)&(fr<1.15)
    ann=S[(np.abs(fr-1)<0.04)].max()
    print(f"{lab:16s}: CW peak {fr[m_][i]:.4f} c/yr ({365.2422/fr[m_][i]:.1f} d)  amp {S[m_][i]:.1f} | annual-band amp {ann:.1f}  ratio CW/ann {S[m_][i]/max(ann,1e-9):.2f}")
rho_m = float(np.corrcoef(xm[1:],xm[:-1])[0,1]); rho_d = float(np.corrcoef(xc_d[1:],xc_d[:-1])[0,1])
print("rho1 monthly-cleaning:", round(rho_m,3), " daily:", round(rho_d,4))

# ---------- manifolds (production qbo30 knobs, draconic family)
p = json.load(open("/home/paul/eval/winding_scalogram/qbo30/lt.exe.p"))
L = np.array(p["lpap"]); per, amp = L[:,0], L[:,1:3]
B = {k: float(p[k]) for k in ("delA","delB","asym","ma","mp","init","shfT")}
mNfam = np.logical_or(np.logical_and(per>=26.9, per<=27.7), np.logical_and(per>=13.5, per<=13.9))
DPOS = int(round(B["delB"]*12)) % 12   # =2 (March) after mod 12

def comb_seq(tt, mode):
    mo = np.rint((tt - tt[0])*12).astype(int) % 12
    c = np.zeros_like(tt)
    if mode == "singlep":  c[mo==DPOS] = B["delA"]
    elif mode == "equal2p": c[mo==DPOS] = B["delA"]; c[mo==(DPOS+6)%12] = B["delA"]
    elif mode == "rect":   c = np.sign(np.cos(np.pi*((tt-tt[0])*12 - DPOS)))*abs(B["delA"])
    return c

def manifold(tt, mode):
    idx_ = np.where(mNfam)[0]
    tf = tide_sum(tt, amp[idx_], per[idx_], YL, integ=B["shfT"])
    raw = tf*comb_seq(tt, mode) if mode != "none" else tf
    f = iir(raw, lag_a=1.0-B["ma"], lag_c=B["mp"], init=B["init"], start_date=tt[0], dates=tt)
    return f - f.mean()

def ar1_floor(tt, F, m_grid, t0_grid, sigma, rho, n_reps=30):
    rng = np.random.default_rng(1); acc = np.zeros((len(m_grid), len(t0_grid)))
    for _ in range(n_reps):
        e = rng.standard_normal(len(tt)); s = np.empty(len(tt)); s[0]=e[0]
        for i in range(1,len(tt)): s[i]=rho*s[i-1]+np.sqrt(1-rho**2)*e[i]
        G,_,_ = winding_transform(tt, standardize(s), F, m_grid, t0_grid, sigma)
        acc += np.abs(G)**2
    return acc/n_reps

def scan(tag, tt, F, target, rho, m_max=2.0):
    m_grid = np.arange(0.0, m_max+0.005, 0.01)
    t0_grid = np.arange(tt[0]+5, tt[-1]-5+1e-9, 2.5)
    G,_,_ = winding_transform(tt, standardize(target), F, m_grid, t0_grid, 10.0)
    lp = np.log2(np.maximum(np.abs(G)**2/ar1_floor(tt,F,m_grid,t0_grid,10.0,rho), 1e-9))
    prof = np.abs(G).mean(axis=1); lpm = lp.mean(axis=1)
    out=[]
    for M,pk,fw in find_ridges(m_grid,prof,lpm,2.0,0.12):
        out.append((round(M,3), round(float(pk),2), round(float(continuity(lp,m_grid,M)),2)))
    out.sort(key=lambda r:-r[1])
    at={}
    for q,lab in [(alias,"0.422"),(2*alias,"0.844")]:
        i=int(np.argmin(abs(m_grid-q)))
        at[lab]=(round(float(prof[i]),3), round(float(lpm[i]),2), round(float(continuity(lp,m_grid,q)),2))
    print(f"\n== {tag} ==\n   teeth>=2b: {out[:6]}\n   pred@0.422 {at['0.422']}   pred@0.844 {at['0.844']}")
    return {"teeth":out, "at":at}

res={}
for mode in ("equal2p","singlep","rect","none"):
    res[f"m_{mode}"] = scan(f"monthly cleaned, comb={mode}", tm, manifold(tm,mode), xm, rho_m)
for mode in ("equal2p","singlep","rect","none"):
    res[f"d_{mode}"] = scan(f"daily cleaned, comb={mode}", td, manifold(td,mode), xc_d, rho_d, m_max=2.0)
json.dump(res, open("/home/paul/eval/winding_scalogram/chandler_clean_ridges.json","w"))
print("\nsaved")

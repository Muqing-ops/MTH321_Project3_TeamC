"""Deterministic experiments. Values are measured, never supplied as results."""
from pathlib import Path
import csv,json,time,platform,sys,hashlib
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, LogLocator
from src.grid import grid
from src.initial_conditions import initial
from src.exact_solution import exact
from src.solver import METHODS,evolve
from src.tvd import rhs
from src.diagnostics import norms,diagnostics,mode_coefficient
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
COLORS={'upwind':'#0072B2','lw':'#D55E00','mc':'#009E73','minmod':'#CC79A7'}
LABELS={'upwind':'Upwind','lw':'Lax–Wendroff','mc':'TVD (MC)','minmod':'TVD (Minmod)'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'lines.linewidth':1.5,'savefig.bbox':'tight','pdf.fonttype':42})

def save(name,rows):
    with (OUT/'tables'/f'{name}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def fig(name,f):
    for ax in f.axes:
        for axis,scale in [(ax.xaxis,ax.get_xscale()),(ax.yaxis,ax.get_yscale())]:
            if scale=='log':
                axis.set_minor_formatter(NullFormatter())
                axis.set_major_locator(LogLocator(base=10,numticks=5))
    f.savefig(OUT/'figures'/f'{name}.pdf');f.savefig(OUT/'figures'/f'{name}.png',dpi=170);plt.close(f)

def symbol(method,xi,c):
    if method=='upwind': return 1-c+c*np.exp(-1j*xi)
    return 1-1j*c*np.sin(xi)+c*c*(np.cos(xi)-1)

def semi(u,T,method,rtol=2e-11):
    n=len(u)
    if method in ['upwind','lw']:
        xi=2*np.pi*np.fft.fftfreq(n)
        lam=-n*(1-np.exp(-1j*xi)) if method=='upwind' else -1j*n*np.sin(xi)
        return np.fft.ifft(np.fft.fft(u)*np.exp(T*lam)).real,0
    sol=solve_ivp(lambda t,v:rhs(t,v,n),[0,T],u,method='DOP853',rtol=rtol,atol=rtol*.01)
    if not sol.success: raise RuntimeError(sol.message)
    return sol.y[:,-1],sol.nfev

def add_orders(rows,key='L2',scale='N'):
    prev=None
    for r in rows:
        r['order']='' if prev is None else float(np.log(prev[key]/r[key])/np.log(r[scale]/prev[scale]))
        prev=r

def square_zoom(snap):
    x=np.arange(200)/200
    f,axs=plt.subplots(1,2,figsize=(9,3.3))
    for ax,limits,title in zip(axs,[(.43,.60),(.68,.85)],['Rising front','Falling front']):
        ax.step(x,exact(x,.25,'square'),'k--',where='post',lw=2,label='Exact samples')
        for m in ['upwind','lw','mc','minmod']:
            ax.plot(x,snap['square',m],'.-',ms=3,color=COLORS[m],label=LABELS[m])
        ax.set(xlim=limits,xlabel='x (dimensionless)',ylabel='u',title=title+' (N=200, C=0.5, T=0.25)')
    axs[0].legend(fontsize=7);fig('square_zoom',f)

def run():
    for folder in ['tables','figures','raw']: (OUT/folder).mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'config/protocol.json').read_text())
    print('E1 / E2 joint and square profiles',flush=True)
    joint=[];snap={};square=[]
    for profile in cfg['profiles']:
      for method in METHODS:
       for c in cfg['C']:
        group=[]
        for n in cfg['N']:
            x,h=grid(n);u,meta,_=evolve(initial(x,profile),method,cfg['T'],c)
            row=dict(profile=profile,method=method,requested_C=c,**meta,**norms(u-exact(x,cfg['T'],profile)),**diagnostics(u))
            row['mass_residual']=row['mass']-float(initial(x,profile).mean())
            group.append(row)
            if n==200 and c==.5:snap[profile,method]=u
        add_orders(group);joint.extend(group)
        if profile=='square':square.extend(group)
    save('joint_convergence',joint);save('square_diagnostics',square)
    np.savez_compressed(OUT/'raw/profiles.npz',**{f'{p}_{m}':u for (p,m),u in snap.items()},x=np.arange(200)/200)
    f,axs=plt.subplots(1,3,figsize=(12,3.2))
    for ax,p in zip(axs,cfg['profiles']):
        x=np.arange(200)/200;ax.plot(x,exact(x,.25,p),'k--',label='Exact',lw=2)
        for m in ['upwind','lw','mc']:ax.plot(x,snap[p,m],color=COLORS[m],label=LABELS[m])
        ax.set(xlabel='x (dimensionless)',ylabel='u',title=f'{p}, N=200, C=0.5, T=0.25')
    axs[0].legend(fontsize=8);fig('profiles',f)
    square_zoom(snap)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for m in ['upwind','lw','mc','minmod']:
        g=[r for r in joint if r['profile']=='packet' and r['method']==m and r['requested_C']==.5]
        axs[0].loglog([1/r['N'] for r in g],[r['L2'] for r in g],'o-',color=COLORS[m],label=LABELS[m])
        g=[r for r in square if r['method']==m and r['requested_C']==.5]
        axs[1].loglog([1/r['N'] for r in g],[r['L1'] for r in g],'o-',color=COLORS[m],label=LABELS[m])
    h=np.array([1/800,1/50]);axs[0].loglog(h,.3*h,'k:',label='slope 1');axs[0].loglog(h,8*h*h,'k--',label='slope 2');axs[1].loglog(h,.4*np.sqrt(h),'k:',label='slope 0.5')
    for ax,title in zip(axs,['Smooth packet: joint refinement','Square: joint refinement']):ax.set(xlabel='h',ylabel='Error',title=title);ax.legend(fontsize=7)
    fig('joint_convergence',f)
    print('E2 separated semidiscrete space and time',flush=True)
    spatial=[];temporal=[];oracle=[]
    T=cfg['convergence_T']
    for method in ['upwind','lw','mc']:
      for profile in ['sine','packet']:
        group=[]
        for n in cfg['N']:
            x,h=grid(n);u0=initial(x,profile);v,nfev=semi(u0,T,method)
            delta=0
            if method=='mc':
                v2,nf2=semi(u0,T,method,rtol=2e-13);delta=norms(v-v2)['L2'];v=v2
                oracle.append(dict(study='space',method=method,profile=profile,N=n,rtol_coarse=2e-11,rtol_fine=2e-13,change_L2=delta,nfev_coarse=nfev,nfev_fine=nf2))
            row=dict(method=method,profile=profile,N=n,h=h,T=T,**norms(v-exact(x,T,profile)),oracle_change=delta)
            row['contamination_fraction']=delta/max(row['L2'],1e-300);group.append(row)
        add_orders(group);spatial.extend(group)
      n=100;x,h=grid(n);u0=initial(x,'sine');ref,_=semi(u0,T,method,2e-13)
      if method=='mc':
        coarse,_=semi(u0,T,method);delta=norms(ref-coarse)['L2']
      else:delta=0
      group=[]
      for steps in [40,80,160,320,640,1280]:
        dt=T/steps;c=dt*n;u=u0.copy()
        for _ in range(steps):u=METHODS[method](u,c)
        group.append(dict(method=method,N=n,T=T,steps=steps,dt=dt,C=c,**norms(u-ref),PDE_L2=norms(u-exact(x,T,'sine'))['L2'],spatial_floor=norms(ref-exact(x,T,'sine'))['L2'],oracle_change=delta,contamination_fraction=delta/max(norms(u-ref)['L2'],1e-300)))
      add_orders(group,scale='steps');temporal.extend(group)
    save('spatial_separated',spatial);save('temporal_separated',temporal);save('nonlinear_oracle_checks',oracle)
    # Independent dense matrix exponential check of the FFT oracle.
    cross=[]
    n=24;x,h=grid(n);u0=initial(x,'packet');I=np.eye(n)
    for m in ['upwind','lw']:
        L=np.column_stack([-(I[:,j]-np.roll(I[:,j],1))*n if m=='upwind' else -.5*n*(np.roll(I[:,j],-1)-np.roll(I[:,j],1)) for j in range(n)])
        v,_=semi(u0,T,m);cross.append(dict(method=m,N=n,T=T,max_difference=float(abs(v-expm(T*L)@u0).max())))
    save('matrix_oracle_crosscheck',cross)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for m in ['upwind','lw','mc']:
        g=[r for r in spatial if r['method']==m and r['profile']=='sine'];axs[0].loglog([r['h'] for r in g],[r['L2'] for r in g],'o-',color=COLORS[m],label=LABELS[m])
        g=[r for r in temporal if r['method']==m];axs[1].loglog([r['dt'] for r in g],[r['L2'] for r in g],'o-',color=COLORS[m],label=LABELS[m])
    h=np.array([1/800,1/50]);axs[0].loglog(h,h,'k:',label='slope 1');axs[0].loglog(h,h*h,'k--',label='slope 2')
    dt=np.array([T/1280,T/40]);axs[1].loglog(dt,dt,'k:',label='slope 1')
    for ax,title in zip(axs,['Exact-in-time spatial error (sine)','Time error vs same-grid limit (sine)']):ax.set(xlabel='h' if ax is axs[0] else 'dt',ylabel='L2 error',title=title);ax.legend(fontsize=8)
    fig('separated_convergence',f)
    print('E3 CFL / E5 modal fidelity',flush=True)
    stability=[];history=[]
    n=100;u0=(-1.)**np.arange(n)
    for m in METHODS:
      for c in [.25,.5,.9,.99,1,1.01,1.1]:
        u=u0.copy();g=1-2*c if m in ['upwind','mc','minmod'] else 1-2*c*c
        first=METHODS[m](u,c);measured=float(np.dot(first,u)/n)
        reason='step cap';error=0
        for k in range(301):
            amp=float(np.max(abs(u)));error=float(np.sqrt(np.mean((u-u0*np.cos(np.pi*c*k))**2)))
            history.append(dict(method=m,C=c,step=k,time=k*c/n,amplitude=amp,L2_error=error,theory_amplitude=abs(g)**k))
            if amp>1e6:reason='amplitude safety stop';break
            if k<300:u=METHODS[m](u,c)
        stability.append(dict(method=m,C=c,predicted_first_factor=g,observed_first_factor=measured,factor_error=abs(g-measured),last_step=k,last_amplitude=amp,stop_reason=reason))
    save('stability_summary',stability);save('stability_history',history)
    xi=np.linspace(0,np.pi,1001)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for c,style in [(.5,'-'),(.9,'--'),(1.01,':')]:
      for m in ['upwind','lw']:
        g=symbol(m,xi,c);axs[0].plot(xi/np.pi,abs(g),style,color=COLORS[m],label=f'{LABELS[m]}, C={c}')
        # Phase is undefined where G=0; mask amplitude floor.
        phase=np.unwrap(np.angle(g));phase[abs(g)<1e-10]=np.nan
        axs[1].plot(xi/np.pi,phase+c*xi,style,color=COLORS[m],label=f'{LABELS[m]}, C={c}')
    axs[0].axhline(1,color='k',lw=.7);axs[0].set(ylabel='|G|',xlabel='xi / pi',title='Amplification magnitude');axs[0].legend(fontsize=7)
    axs[1].set(ylabel='arg G + C xi (rad)',xlabel='xi / pi',title='Unwrapped one-step phase defect');fig('amplification',f)
    f,ax=plt.subplots(figsize=(6.5,3.2))
    for c in [.99,1,1.01,1.1]:
      for m,sty in [('upwind','-'),('lw','--')]:
        g=[r for r in history if r['method']==m and r['C']==c]
        ax.semilogy([r['step'] for r in g],[r['amplitude'] for r in g],sty,label=f'{LABELS[m]}, C={c}')
    ax.set(xlabel='Step',ylabel='Checkerboard amplitude',title='Dangerous-mode growth with explicit safety stop');ax.legend(fontsize=7,ncol=2);fig('stability_growth',f)
    modes=[]
    for m in METHODS:
      for c in cfg['C']:
       for k in [1,2,4,8,16,32,48]:
        n=200;x,h=grid(n);u0=initial(x,'sine',k);u=u0.copy();A0=mode_coefficient(u,k);phases=[np.angle(A0)]
        for j in range(100):u=METHODS[m](u,c);phases.append(np.angle(mode_coefficient(u,k)))
        ratio=mode_coefficient(u,k)/A0;amp=abs(ratio)
        phase=float(np.unwrap(phases)[-1]-np.unwrap(phases)[0]);exphase=-100*c*2*np.pi*k/n
        harmonic=float(np.sqrt(np.mean((u-2*np.real(mode_coefficient(u,k)*np.exp(2j*np.pi*k*x)))**2)))
        theory=symbol(m,2*np.pi*k/n,c)**100 if m in ['upwind','lw'] else None
        modes.append(dict(method=m,C=c,N=n,mode=k,steps=100,T=100*c/n,amplitude_ratio=amp,phase_reliable=amp>1e-10,unwrapped_phase=phase,phase_error=phase-exphase,numerical_speed=-phase/(2*np.pi*k*(100*c/n)),harmonic_L2=harmonic,predicted_amplitude='' if theory is None else abs(theory),complex_factor_error='' if theory is None else abs(ratio-theory)))
    save('fourier_modes',modes)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for m in ['upwind','lw','mc']:
        g=[r for r in modes if r['method']==m and r['C']==.5]
        axs[0].semilogy([r['mode'] for r in g],[r['amplitude_ratio'] for r in g],'o-',color=COLORS[m],label=LABELS[m]);axs[1].plot([r['mode'] for r in g],[r['numerical_speed'] if r['phase_reliable'] else np.nan for r in g],'o-',color=COLORS[m],label=LABELS[m])
    axs[0].set(xlabel='Fourier mode k',ylabel='Amplitude / initial',title='100 steps, N=200, C=0.5');axs[1].set(xlabel='Fourier mode k',ylabel='Numerical speed',title='Phase tracked at every step')
    for ax in axs:ax.legend(fontsize=8)
    fig('modal_fidelity',f)
    print('E6 diagnostics / E7 long-time',flush=True)
    histories=[];long=[]
    for p in cfg['profiles']:
      for m in METHODS:
       for c in cfg['C']:
        n=200;x,h=grid(n);u0=initial(x,p);u,meta,states=evolve(u0,m,1,c,record=True)
        prev=diagnostics(u0)['TV'];mass=u0.mean()
        for j,v in enumerate(states):
            d=diagnostics(v);d['TV_increment']=d['TV']-prev;prev=d['TV']
            histories.append(dict(profile=p,method=m,requested_C=c,time=j*meta['dt'],step=j,actual_C=meta['C'],mass_residual=d['mass']-mass,**d))
       for T in [.37,1,1.37,5,5.37,10]:
        u,meta,states=evolve(initial(x,p),m,T,.5,record=p=='sine')
        if p=='sine':
            coeffs=np.array([mode_coefficient(v) for v in states]);phase=float(np.unwrap(np.angle(coeffs))[-1]-np.angle(coeffs[0]));phase_error=phase+2*np.pi*T;amp=abs(coeffs[-1]/coeffs[0])
        else: phase_error='';amp=''
        long.append(dict(profile=p,method=m,**meta,**norms(u-exact(x,T,p)),**diagnostics(u),mass_residual=float(u.mean()-initial(x,p).mean()),amplitude_ratio=amp,unwrapped_phase_error=phase_error))
    save('diagnostic_history',histories);save('long_time',long)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for m in ['upwind','lw','mc']:
        g=[r for r in histories if r['profile']=='square' and r['method']==m and r['requested_C']==.5];axs[0].plot([r['time'] for r in g],[r['TV'] for r in g],color=COLORS[m],label=LABELS[m]);axs[1].plot([r['time'] for r in g],[r['mass_residual'] for r in g],color=COLORS[m],label=LABELS[m])
    axs[0].set(xlabel='t',ylabel='Periodic TV',title='Square pulse, N=200, C=0.5');axs[1].set(xlabel='t',ylabel='Discrete mass residual',title='Conservation diagnostic')
    axs[0].legend(fontsize=8);fig('mass_tv',f)
    f,axs=plt.subplots(1,2,figsize=(9,3.4))
    for m in ['upwind','lw','mc']:
        g=[r for r in long if r['profile']=='sine' and r['method']==m];axs[0].plot([r['T'] for r in g],[r['amplitude_ratio'] for r in g],'o-',color=COLORS[m],label=LABELS[m]);axs[1].plot([r['T'] for r in g],[r['unwrapped_phase_error'] for r in g],'o-',color=COLORS[m],label=LABELS[m])
    axs[0].set(xlabel='t (periods)',ylabel='Amplitude ratio',title='Long-time sine, N=200, C=0.5');axs[1].set(xlabel='t (periods)',ylabel='Unwrapped phase defect (rad)',title='Intermediate observations prevent aliasing');axs[0].legend(fontsize=8);fig('long_time',f)
    print('E8 warmed repeated cost measurements',flush=True)
    costs=[];samples=[];targets=[]
    for p in ['packet','square']:
      for m in ['upwind','lw','mc']:
       for n in cfg['cost_N']:
        x,h=grid(n);u0=initial(x,p)
        u,meta,_=evolve(u0,m,.25,.5) # warmup
        error=norms(u-exact(x,.25,p))
        times=[]
        for r in range(cfg['cost_repeats']):
            start=time.perf_counter_ns();v,_,_=evolve(u0,m,.25,.5);seconds=(time.perf_counter_ns()-start)*1e-9
            times.append(seconds);samples.append(dict(profile=p,method=m,N=n,repeat=r,seconds=seconds))
        costs.append(dict(profile=p,method=m,**meta,**error,median_seconds=float(np.median(times)),IQR_seconds=float(np.percentile(times,75)-np.percentile(times,25)),min_seconds=min(times),max_seconds=max(times),grid_updates=n*meta['steps']))
       for target in cfg['cost_targets'][p]:
        feasible=[r for r in costs if r['profile']==p and r['method']==m and r['L1']<=target]
        if feasible:
            best=min(feasible,key=lambda r:r['median_seconds']);targets.append(dict(profile=p,method=m,target_L1=target,status='achieved',N=best['N'],dt=best['dt'],steps=best['steps'],L1=best['L1'],median_seconds=best['median_seconds'],IQR_seconds=best['IQR_seconds'],grid_updates=best['grid_updates']))
        else:targets.append(dict(profile=p,method=m,target_L1=target,status='not achieved on tested grid set',N='',dt='',steps='',L1='',median_seconds='',IQR_seconds='',grid_updates=''))
    save('cost_accuracy',costs);save('timing_samples',samples);save('matched_targets',targets)
    f,axs=plt.subplots(1,2,figsize=(9,3.5))
    pareto=[]
    for ax,p in zip(axs,['packet','square']):
      for m in ['upwind','lw','mc']:
        g=[r for r in costs if r['profile']==p and r['method']==m]
        ax.loglog([r['L1'] for r in g],[r['median_seconds'] for r in g],'o-',color=COLORS[m],alpha=.55,label=LABELS[m])
        for r in g:
            dominated=any(s['L1']<=r['L1'] and s['median_seconds']<=r['median_seconds'] and (s['L1']<r['L1'] or s['median_seconds']<r['median_seconds']) for s in costs if s['profile']==p)
            if not dominated:ax.plot(r['L1'],r['median_seconds'],'ko',mfc='none',ms=9);pareto.append(r)
      for target in cfg['cost_targets'][p]:ax.axvline(target,color='grey',ls=':',lw=.8)
      ax.set(xlabel='L1 error',ylabel='Median runtime (s)',title=p+' (black rings: global Pareto set)');ax.legend(fontsize=8)
    fig('cost_accuracy',f);save('pareto_front',pareto)
    metadata=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,platform=platform.platform(),processor=platform.processor(),machine=platform.machine(),config=cfg,timing='perf_counter_ns; warmup=1; repeats=7; IQR; stepping and copy only',reference='PDE exact shift; linear semidiscrete FFT; nonlinear tolerance-refined DOP853')
    (OUT/'raw/environment.json').write_text(json.dumps(metadata,indent=2))
    print('All eight experiment families completed.',flush=True)

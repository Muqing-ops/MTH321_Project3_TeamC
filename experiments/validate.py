from pathlib import Path
import csv,json,subprocess,sys
import numpy as np
from src.solver import METHODS,evolve
from src.initial_conditions import initial
from src.grid import grid
from src.diagnostics import norms
ROOT=Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((ROOT/'results/tables'/f'{name}.csv').open()))
def validate():
    rows=[]
    def check(id,expected,value,tolerance,passed,evidence):
        rows.append(dict(ID=id,expected=expected,actual=value,tolerance=tolerance,status='PASS' if passed else 'FAIL',evidence=evidence))
    p=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'results/raw/pytest.log').write_text(p.stdout+p.stderr)
    check('V01','all automated checks pass',p.stdout.strip().splitlines()[-1],0,p.returncode==0,'tests/test_numerics.py; results/raw/pytest.log')
    d=read('diagnostic_history');mass=max(abs(float(r['mass_residual'])) for r in d)
    check('V02','all discrete masses conserved',mass,5e-12,mass<5e-12,'diagnostic_history.csv')
    for m in ['mc','minmod']:
        subset=[r for r in d if r['method']==m];v=max(float(r['TV_increment']) for r in subset)
        check('V03-'+m,'maximum TV increment <= tolerance',v,5e-12,v<=5e-12,'diagnostic_history.csv (three profiles and Courant numbers)')
        ext=max(max(0,-float(r['minimum']),float(r['maximum'])-1) for r in subset if r['profile']!='sine')
        check('V04-'+m,'nonnegative packet/square remain in [0,1]',ext,5e-12,ext<=5e-12,'diagnostic_history.csv')
    for m in ['upwind','lw']:
        v=max(float(r['complex_factor_error']) for r in read('fourier_modes') if r['method']==m)
        check('V05-'+m,'measured mode agrees with analytic G^100',v,5e-12,v<5e-12,'fourier_modes.csv')
        for profile in ['sine','packet']:
            r=[r for r in read('spatial_separated') if r['method']==m and r['profile']==profile][-1];order=float(r['order']);target=1 if m=='upwind' else 2
            check('V06-'+m+'-'+profile,'spatial order '+str(target),order,.1,abs(order-target)<.1,'spatial_separated.csv; exact semidiscrete time evolution')
        r=[r for r in read('temporal_separated') if r['method']==m][-1];order=float(r['order'])
        check('V07-'+m,'time order 1 vs C->0 same-grid limit',order,.1,abs(order-1)<.1,'temporal_separated.csv')
    v=max(float(r['factor_error']) for r in read('stability_summary'))
    check('V08','checkerboard signed first factors match',v,2e-13,v<2e-13,'stability_summary.csv')
    for m in ['upwind','lw']:
        r=[r for r in read('stability_summary') if r['method']==m and float(r['C'])==1.01][0]
        check('V09-'+m,'growth above sharp CFL limit',r['last_amplitude'],'>1',float(r['last_amplitude'])>1,'stability_summary.csv')
    v=max(float(r['contamination_fraction']) for r in read('spatial_separated')+read('temporal_separated'))
    check('V10','nonlinear oracle tolerance change <1% measured error',v,.01,v<.01,'nonlinear_oracle_checks.csv; spatial_separated.csv; temporal_separated.csv')
    v=max(float(r['max_difference']) for r in read('matrix_oracle_crosscheck'))
    check('V11','dense matrix expm matches independent FFT reference',v,2e-13,v<2e-13,'matrix_oracle_crosscheck.csv')
    # Recompute one full solution with independent scalar indexing loops.
    for m in ['upwind','lw','mc']:
        n=100;x,h=grid(n);u0=initial(x);v,meta,_=evolve(u0,m,.25);w=u0.copy();c=meta['C']
        for _ in range(meta['steps']):
            if m=='mc':
                flux=[]
                for j in range(n):
                    b=w[j]-w[(j-1)%n];f=w[(j+1)%n]-w[j]
                    s=np.sign(f)*min(2*abs(b),2*abs(f),abs(b+f)/2) if b*f>0 else 0
                    flux.append(w[j]+.5*(1-c)*s)
                z=np.array([w[j]-c*(flux[j]-flux[(j-1)%n]) for j in range(n)])
            elif m=='upwind':z=np.array([(1-c)*w[j]+c*w[(j-1)%n] for j in range(n)])
            else:z=np.array([(.5*c+.5*c*c)*w[(j-1)%n]+(1-c*c)*w[j]+(-.5*c+.5*c*c)*w[(j+1)%n] for j in range(n)])
            w=z
        delta=float(abs(v-w).max());check('V12-'+m,'independent scalar-loop reproduction',delta,2e-13,delta<2e-13,'experiments/validate.py')
        v2,_,_=evolve(u0,m,.25);delta=float(abs(v-v2).max());check('V13-'+m,'same-process deterministic rerun',delta,0,delta==0,'experiments/validate.py')
    save=ROOT/'results/tables/validation.csv'
    with save.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    text='# Validation report\n\nAutomated and analytic cross-checks performed by the AI agent. No student or external peer verification is claimed. Original failed hand-oracle tests and corrections remain in docs/FAILURE_HISTORY.md.\n\n|Test ID|Expected|Actual|Tolerance|Verdict|Evidence|\n|---|---|---|---|---|---|\n'
    for r in rows:text+='|'+ '|'.join(str(r[k]) for k in ['ID','expected','actual','tolerance','status','evidence'])+'|\n'
    text+='\n## Failure investigation and corrective action\nF01: two incorrect AI hand-oracle literals; see full arithmetic in docs/FAILURE_HISTORY.md. Fixed expected literals, unchanged numerical updates, rerun passed. Formal run integration initially reached the end of experiment generation before experiments.validate existed (F02); no numerical data were lost. Added the validation module and ran it explicitly, then verified the complete entry point on rerun.\n\n## Scope\nTolerance checks support these tested configurations. They are not proofs for arbitrary inputs. MC spatial/time rates are empirical and are not assigned a forced pass band. DOP853 differences are a numerical tolerance check, not a rigorous error certificate. Same-machine rerun and independent scalar-loop checks do not replace the official teammate clean-room reproduction. That remains pending in the role/ICS templates.\n'
    (ROOT/'VALIDATION_REPORT.md').write_text(text)
    print(f"Validation: {sum(r['status']=='PASS' for r in rows)}/{len(rows)} passed")
    if any(r['status']=='FAIL' for r in rows):raise RuntimeError('validation failures; inspect validation.csv')
if __name__=='__main__':validate()

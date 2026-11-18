import numpy as np
import pytest
from src.solver import METHODS,evolve
from src.grid import grid,time_grid
from src.initial_conditions import initial
from src.diagnostics import diagnostics
from src.tvd import limited_jump

@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('c',[-1,-.5,0,.5,1])
def test_constant(method,c):
    np.testing.assert_allclose(METHODS[method](np.full(8,2.3),c),2.3,atol=2e-14,rtol=0)

@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('c',[-1,1])
def test_shift(method,c):
    u=np.array([0.,1.,3.,-2.,.5])
    np.testing.assert_allclose(METHODS[method](u,c),np.roll(u,c),atol=2e-14,rtol=0)

@pytest.mark.parametrize('method,answer',[('upwind',[0,.5,1.5,1]),('lw',[-.125,.5,1.875,.75]),('mc',[0,.375,1.625,1]),('minmod',[0,.375,1.625,1])])
def test_hand(method,answer):
    np.testing.assert_allclose(METHODS[method](np.array([0.,1.,2.,0.]),.5),answer,atol=2e-14,rtol=0)

@pytest.mark.parametrize('method',METHODS)
def test_conservation(method):
    x,h=grid(100)
    u,_,_=evolve(initial(x),method,1,.5)
    assert abs(u.mean()-initial(x).mean())<5e-12

@pytest.mark.parametrize('method',['upwind','lw'])
@pytest.mark.parametrize('c',[-.9,-.5,.25,.5,.9,1.01])
def test_fourier(method,c):
    n=64;k=11;xi=2*np.pi*k/n
    u=np.exp(1j*xi*np.arange(n))
    g=1-abs(c)+abs(c)*np.exp(-1j*np.sign(c)*xi) if method=='upwind' else 1-1j*c*np.sin(xi)+c*c*(np.cos(xi)-1)
    assert abs(METHODS[method](u,c)-g*u).max()<2e-13

@pytest.mark.parametrize('method',['mc','minmod'])
@pytest.mark.parametrize('c',[.01,.25,.5,.9,1])
def test_tvd_random(method,c):
    rng=np.random.default_rng(3212026)
    for _ in range(30):
        u=rng.normal(size=40);v=METHODS[method](u,c)
        assert diagnostics(v)['TV']<=diagnostics(u)['TV']+5e-12
        assert v.min()>=u.min()-5e-12 and v.max()<=u.max()+5e-12

@pytest.mark.parametrize('method,pmin',[('upwind',.85),('lw',1.8)])
def test_joint_smooth(method,pmin):
    errors=[]
    for n in [100,200,400]:
        x,_=grid(n);u,_,_=evolve(initial(x,'sine'),method,.25)
        errors.append(np.mean(abs(u-initial((x-.25)%1,'sine'))))
    assert np.log2(errors[-2]/errors[-1])>pmin

def test_periodic_tv():
    assert diagnostics(np.array([1.,1.,0.,0.]))['TV']==2

def test_zero_jumps():
    np.testing.assert_array_equal(limited_jump(np.array([0.,1.,-1.,1.]),np.array([0.,0.,1.,-1.])),0)

@pytest.mark.parametrize('n',[0,3,2.5,True])
def test_bad_grid(n):
    with pytest.raises(ValueError): grid(n)

@pytest.mark.parametrize('T,C,a',[(-1,.5,1),(1,0,1),(1,1.01,1),(1,.5,0),(np.nan,.5,1),(1,np.inf,1)])
def test_bad_parameters(T,C,a):
    with pytest.raises(ValueError): time_grid(20,T,C,a)

@pytest.mark.parametrize('u',[[],[np.nan]*4,[[1]*4]*4])
def test_bad_state(u):
    with pytest.raises(ValueError): evolve(u,'upwind',1)

def test_final_time_and_zero():
    u=np.arange(20.)
    v,m,_=evolve(u,'upwind',.103,.7)
    assert m['steps']*m['dt']==pytest.approx(.103,abs=1e-16)
    v,_,_=evolve(u,'mc',0)
    np.testing.assert_array_equal(u,v)

def test_sign_symmetry():
    u=np.arange(10.)**2
    for method in METHODS:
        np.testing.assert_allclose(METHODS[method](u,-.5),METHODS[method](u[::-1],.5)[::-1],atol=1e-13)

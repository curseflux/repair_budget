"""Reference decoder: interval-data proposals plus protected error/erasure syndromes.

NumPy code is executable on CPU. The optional batched PyTorch proposal uses CUDA
when its inputs do. Algebraic decoding uses Python integers (exact arithmetic).
No function is allowed access to the original except the pre-tamper encoder.
"""
import random
import numpy as np

P = 2147483647  # Prime; products of two residues fit signed int64.


class DecodeFailure(ValueError):
    pass


def syndrome(labels, checks, chunk=65536):
    """Full vector encoder, O(d*checks), bounded memory; labels in [0,P).

    CPU reference, not a full-head performance implementation. Public locator
    for zero-based position j is j+1. Supports d<P, including a Llama-8B head.
    """
    x = np.asarray(labels, dtype=np.int64).reshape(-1)
    if checks < 0 or len(x) >= P or np.any((x < 0) | (x >= P)):
        raise ValueError('Invalid labels, dimension, or number of checks')
    if not 0 < chunk <= 65536:
        raise ValueError('chunk must be in [1,65536] for bounded int64 sums')
    out = np.zeros(checks, dtype=np.int64)
    for start in range(0, len(x), chunk):
        vals = x[start:start+chunk]
        a = np.arange(start+1, start+1+len(vals), dtype=np.int64)
        power = np.ones(len(vals), dtype=np.int64)
        for k in range(checks):
            # Reduce each product BEFORE summing: chunk*(P-1) fits int64.
            out[k] = (int(out[k]) + int(((vals*power) % P).sum())) % P
            power = (power*a) % P
    return out


def sparse_syndrome(indices, differences, checks):
    out = [0]*checks
    for j, value in zip(indices, differences):
        a, power, value = int(j)+1, 1, int(value) % P
        if not 1 <= a < P:
            raise ValueError('Index outside supported field')
        for k in range(checks):
            out[k] = (out[k]+value*power) % P
            power = power*a % P
    return np.array(out, dtype=np.int64)


def syndrome_torch(labels, checks, chunk=1048576):
    """Optional CUDA encoder using exact int64 and Mersenne-prime reduction.

    O(d*checks); one-time encoding cost must be benchmarked on the actual GPU.
    Numerical model values must first be converted to their public integer labels.
    """
    import torch
    x=labels.reshape(-1)
    if x.dtype!=torch.int64 or checks<0 or len(x)>=P or not 0<chunk<=1048576:
        raise ValueError('Expected int64 labels, d<P, and chunk<=2**20')
    if bool(((x<0)|(x>=P)).any()): raise ValueError('Labels outside field')
    def mod_product(a,b):
        v=a*b  # <P**2 < 2**62: exact and no signed overflow
        v=(v&P)+(v>>31)
        v=(v&P)+(v>>31)
        return torch.where(v>=P,v-P,v)
    out=torch.zeros(checks,device=x.device,dtype=torch.int64)
    for start in range(0,len(x),chunk):
        vals=x[start:start+chunk]
        a=torch.arange(start+1,start+1+len(vals),device=x.device,dtype=torch.int64)
        power=torch.ones_like(a)
        for k in range(checks):
            # Sum of reduced terms <=2**20*(P-1), safely inside int64.
            out[k]=(out[k]+mod_product(vals,power).sum())%P
            power=mod_product(power,a)
    return out


def apply_label_patch(labels, indices, correction, alphabet_size):
    result=np.asarray(labels,dtype=np.int64).copy()
    result[indices]=(result[indices]+correction)%P
    if np.any((result<0)|(result>=alphabet_size)):
        raise DecodeFailure('Recovered labels outside declared alphabet')
    return result


def _trim(a):
    a = [int(x) % P for x in a]
    while len(a)>1 and a[-1]==0:
        a.pop()
    return a or [0]


def _sub(a, b):
    return _trim([(a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0)
                  for i in range(max(len(a),len(b)))])


def _mul(a, b):
    c = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            c[i+j] = (c[i+j]+x*y) % P
    return _trim(c)


def _divmod(a, b):
    a,b = _trim(a),_trim(b)
    if b == [0]:
        raise ZeroDivisionError()
    q=[0]*max(1,len(a)-len(b)+1)
    inv=pow(b[-1],-1,P)
    while a != [0] and len(a)>=len(b):
        k=len(a)-len(b); v=a[-1]*inv % P; q[k]=v
        for i,x in enumerate(b):
            a[i+k]=(a[i+k]-v*x)%P
        a=_trim(a)
    return _trim(q),a


def _gcd(a,b):
    while b != [0]:
        a,b=b,_divmod(a,b)[1]
    return _trim([x*pow(a[-1],-1,P) % P for x in a])


def _powmod(a,n,f):
    out=[1]; a=_divmod(a,f)[1]
    while n:
        if n&1: out=_divmod(_mul(out,a),f)[1]
        a=_divmod(_mul(a,a),f)[1]; n >>= 1
    return out


def _roots(f, seed=0):
    """Factor a squarefree, fully split polynomial; no scan over d coordinates.

    Bounded randomized splitting: a failed attempt raises, never hangs.
    """
    f=_trim(f)
    if len(f)==1:
        return []
    f=[v*pow(f[-1],-1,P)%P for v in f]
    if _divmod(_sub(_powmod([0,1],P,f),[0,1]),f)[1] != [0]:
        raise DecodeFailure('Locator is not a product of distinct field roots')
    rng=random.Random(seed)
    def split(g):
        n=len(g)-1
        if n==1:
            return [(-g[0]*pow(g[1],-1,P))%P]
        for _ in range(64):
            a=[rng.randrange(P) for _ in range(n)]
            h=_gcd(g,a)
            if len(h) in (1,len(g)):
                h=_gcd(g,_sub(_powmod(a,(P-1)//2,g),[1]))
            if 1<len(h)<len(g):
                return split(h)+split(_divmod(g,h)[0])
        raise DecodeFailure('Polynomial splitting budget exhausted; retry seed')
    return split(f)


def _bm(sequence):
    C=[1]; B=[1]; L=0; shift=1; b=1
    for n in range(len(sequence)):
        disc=(int(sequence[n])+sum(C[i]*int(sequence[n-i])
                                  for i in range(1,L+1)))%P
        if disc==0:
            shift+=1; continue
        old=C[:]; coef=disc*pow(b,-1,P)%P
        C += [0]*max(0,len(B)+shift-len(C))
        for j in range(len(B)):
            C[j+shift]=(C[j+shift]-coef*B[j])%P
        if 2*L<=n:
            L=n+1-L; B=old; b=disc; shift=1
        else:
            shift+=1
    return C[:L+1],L


def _solve(A,b):
    n=len(b)
    M=[[int(x)%P for x in row]+[int(v)%P] for row,v in zip(A,b)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if M[i][j]),None)
        if pivot is None: raise DecodeFailure('Singular recovery matrix')
        M[j],M[pivot]=M[pivot],M[j]
        inv=pow(M[j][j],-1,P)
        M[j]=[x*inv%P for x in M[j]]
        for i in range(n):
            if i!=j:
                v=M[i][j]
                M[i]=[(x-v*y)%P for x,y in zip(M[i],M[j])]
    return [row[-1] for row in M]


def decode_patch(residual_syndrome, dimension, erasures=(), seed=0):
    """Return indices and field corrections relative to a provisional checkpoint.

    Guarantee: exact if |erasures|+2*(wrong provisional labels outside erasures)
    <= number of checks. Outside that radius this can fail OR miscorrect.
    Passing syndrome checks is not an unconditional success certificate.
    """
    S=[int(x)%P for x in residual_syndrome]; t=len(S)
    E=sorted(set(map(int,erasures)))
    if not 0<dimension<P or any(j<0 or j>=dimension for j in E) or len(E)>t:
        raise ValueError('Invalid dimension or erasure set')
    F=[1]
    for j in E: F=_mul(F,[-(j+1),1])
    filtered=[sum(F[l]*S[k+l] for l in range(len(F)))%P
              for k in range(t-len(E))]
    C,r=_bm(filtered)
    if 2*r>len(filtered):
        raise DecodeFailure('Insufficient checks for inferred errors')
    # BM connection polynomial prod(1-alpha*z); reverse to get prod(x-alpha).
    roots=_roots(C[::-1],seed=seed)
    outside=[a-1 for a in roots]
    if len(outside)!=r or any(j<0 or j>=dimension or j in E for j in outside):
        raise DecodeFailure('Invalid error locations')
    locations=sorted(E+outside); k=len(locations)
    if k>t: raise DecodeFailure('Insufficient equations')
    A=[[pow(j+1,i,P) for j in locations] for i in range(k)]
    values=_solve(A,S[:k]) if k else []
    predicted=sparse_syndrome(locations,values,t)
    if not np.array_equal(predicted,np.asarray(S,dtype=np.int64)):
        raise DecodeFailure('Recovered patch does not match every stored check')
    keep=[i for i,v in enumerate(values) if v]
    return (np.asarray([locations[i] for i in keep],dtype=np.int64),
            np.asarray([values[i] for i in keep],dtype=np.int64))


def interval_proposal(H, lower, upper, rho, steps=400, tol=1e-7):
    """CPU reference: min ||E||_1, lower<=E H.T<=upper, |E|<=rho.

    lower/upper are ORIGINAL output-cell bounds minus current logits, rows x N.
    Returns a continuous proposal and feasibility diagnostics, not a guarantee.
    Caller declares a rounding rule and chooses erasures without oracle support.
    """
    H=np.asarray(H,dtype=float); lo=np.atleast_2d(lower).astype(float)
    hi=np.atleast_2d(upper).astype(float)
    if H.ndim!=2 or lo.shape!=hi.shape or lo.shape[1]!=len(H) or np.any(lo>hi) or rho<0:
        raise ValueError('Invalid shapes, intervals or rho')
    E=np.zeros((len(lo),H.shape[1])); extrap=E.copy(); dual=np.zeros_like(lo)
    norm=float(np.linalg.norm(H,2)) if H.size else 0.
    if norm==0:
        violation=max(float(np.max(lo,initial=0)),float(np.max(-hi,initial=0)))
        return E, {'interval_violation':violation,'iterations':0}
    step=.99/norm
    for it in range(steps):
        u=dual+step*(extrap@H.T)
        dual=u-step*np.clip(u/step,lo,hi)
        z=E-step*(dual@H)
        new=np.clip(np.sign(z)*np.maximum(np.abs(z)-step,0),-rho,rho)
        diff=np.max(np.abs(new-E),initial=0)
        extrap=2*new-E; E=new
        if (it+1)%25==0:
            v=E@H.T
            violation=max(float(np.max(lo-v,initial=0)),float(np.max(v-hi,initial=0)))
            if violation<=tol and diff<=tol: break
    v=E@H.T
    return E, {'interval_violation':max(float(np.max(lo-v,initial=0)),float(np.max(v-hi,initial=0))),
               'iterations':it+1,'last_step':float(diff)}


def interval_proposal_torch(H, lower, upper, rho, steps=400):
    """Batched GPU variant. Bounded iterations; no original checkpoint input.

    Torch imported only on demand. H, lower, upper share device/dtype (FP32/64).
    Returns proposal plus interval violation. Rounding can change feasibility.
    """
    import torch
    if H.dtype not in (torch.float32,torch.float64):
        raise ValueError('Use FP32 or FP64 solver arithmetic, independently of storage format')
    if steps<1 or rho<0 or lower.shape!=upper.shape or lower.ndim!=2 or lower.shape[1]!=len(H):
        raise ValueError('Invalid inputs')
    if bool((lower>upper).any()): raise ValueError('Empty interval')
    E=torch.zeros((len(lower),H.shape[1]),device=H.device,dtype=H.dtype)
    if not H.numel() or not bool(H.abs().max()>0):
        violation=torch.maximum(lower.clamp_min(0).sum(),(-upper).clamp_min(0).sum())
        return E,violation
    # Largest singular value from the smaller Gram matrix (usually N x N).
    gram=H@H.T if H.shape[0]<=H.shape[1] else H.T@H
    norm=torch.linalg.eigvalsh(gram)[-1].clamp_min(1e-30).sqrt()
    step=.99/norm; extrap=E.clone(); dual=torch.zeros_like(lower)
    for _ in range(steps):
        u=dual+step*(extrap@H.T)
        dual=u-step*torch.maximum(lower,torch.minimum(upper,u/step))
        z=E-step*(dual@H)
        new=(z.sign()*(z.abs()-step).clamp_min(0)).clamp(-rho,rho)
        extrap=2*new-E; E=new
    v=E@H.T
    violation=torch.maximum((lower-v).clamp_min(0).max(),(v-upper).clamp_min(0).max())
    return E,violation

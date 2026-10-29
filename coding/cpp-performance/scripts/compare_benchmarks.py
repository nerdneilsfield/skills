#!/usr/bin/env python3
"""Describe repeated benchmark JSON runs conservatively; do not infer statistical significance."""
import argparse
import json
import math
from pathlib import Path
import sys

MAX_BYTES=1024*1024

def validate(run, label):
    if not isinstance(run,dict): raise ValueError(f'{label}: expected JSON object')
    for key in ('metric','unit'):
        if not isinstance(run.get(key),str) or not run[key].strip(): raise ValueError(f'{label}.{key}: expected nonempty string')
    if run.get('direction') not in ('lower','higher'): raise ValueError(f'{label}.direction: lower or higher required')
    if type(run.get('correctness_passed')) is not bool: raise ValueError(f'{label}.correctness_passed: boolean required')
    metadata=run.get('metadata')
    if not isinstance(metadata,dict) or not metadata: raise ValueError(f'{label}.metadata: nonempty object required')
    if not all(isinstance(k,str) and k for k in metadata): raise ValueError(f'{label}.metadata: nonempty string keys required')
    samples=run.get('samples')
    if not isinstance(samples,list) or len(samples)<3: raise ValueError(f'{label}.samples: at least three repeats required; this is not a significance guarantee')
    for x in samples:
        try:
            valid=type(x) in (int,float) and math.isfinite(x) and x>=0
        except OverflowError:
            valid=False
        if not valid: raise ValueError(f'{label}.samples: finite nonnegative numeric samples required')

def median(samples):
    ordered=sorted(samples); mid=len(ordered)//2
    if len(ordered)%2: return ordered[mid]
    low, high=ordered[mid-1:mid+1]
    return low+(high-low)/2

def summary(samples):
    med=median(samples)
    return {'count':len(samples),'median':med,'min':min(samples),'max':max(samples),
            'median_absolute_deviation':median([abs(x-med) for x in samples])}

def json_equal(left, right):
    """Compare JSON values without treating bool/int/float metadata as interchangeable."""
    if type(left) is not type(right): return False
    if isinstance(left,dict):
        return left.keys()==right.keys() and all(json_equal(left[k],right[k]) for k in left)
    if isinstance(left,list):
        return len(left)==len(right) and all(json_equal(a,b) for a,b in zip(left,right))
    return left==right

def compare(before, after, allow_metadata_difference=()):
    validate(before,'before'); validate(after,'after')
    allowed=set(allow_metadata_difference)
    keys=set(before['metadata'])|set(after['metadata'])
    unknown=allowed-keys
    if unknown: raise ValueError('allowed metadata keys do not exist: '+', '.join(sorted(unknown)))
    missing=object()
    differences=sorted(k for k in keys if not json_equal(before['metadata'].get(k,missing),after['metadata'].get(k,missing)))
    unapproved=[k for k in differences if k not in allowed]
    reasons=[]
    for key in ('metric','unit','direction'):
        if before[key]!=after[key]: reasons.append(f'{key} differs; no automatic conversion')
    if unapproved: reasons.append('metadata differs: '+', '.join(unapproved))
    if not before['correctness_passed'] or not after['correctness_passed']: reasons.append('a correctness check did not pass')
    result={'status':'incomparable' if reasons else 'comparable','reasons':reasons,
        'metric':before['metric'],'unit':before['unit'],'direction':before['direction'],
        'before':summary(before['samples']),'after':summary(after['samples']),
        'metadata_differences':differences,'allowed_metadata_differences':sorted(set(differences)&allowed),
        'statistical_significance_established':False,
        'limitations':[
            'Descriptive unpaired summaries only; no confidence interval or hypothesis test.',
            'Metadata/correctness are caller assertions; this tool does not verify workload identity or correctness.',
            'Three repeats are an input floor, not proof of adequate sampling; control drift, load and warmup.',
            'Separated observed ranges do not establish statistical significance or causality.'
        ]}
    if reasons: return result
    a=result['before']; b=result['after']
    sign=1 if before['direction']=='lower' else -1
    result['median_delta']=b['median']-a['median']
    relative=None if a['median']==0 else sign*((a['median']-b['median'])/a['median'])*100
    if relative is None or not math.isfinite(relative):
        result['relative_improvement_percent']=None
        result['unavailable']='relative percentage: zero baseline' if a['median']==0 else 'relative percentage: result exceeds finite numeric range'
    else:
        result['relative_improvement_percent']=relative
    result['spread_relation']='overlapping_ranges' if max(a['min'],b['min'])<=min(a['max'],b['max']) else 'separated_ranges'
    result['interpretation']='Observed medians only. Overlap makes a simple speedup claim especially weak; use the experiment design and quality checks before acceptance.'
    return result

def load(path):
    with path.open('rb') as stream:
        raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES: raise ValueError(f'{path}: input exceeds 1 MiB')
    return json.loads(raw,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'non-finite JSON token: {x}')))

def main():
    parser=argparse.ArgumentParser(description=__doc__,epilog='JSON fields: metric, unit, direction (lower/higher), samples (>=3 finite nonnegative numbers), correctness_passed (boolean), metadata (nonempty object). Exit 0 comparable descriptive output; 1 incomparable; 2 invalid input. Comparable does not mean faster, significant or accepted.')
    parser.add_argument('before',type=Path)
    parser.add_argument('after',type=Path)
    parser.add_argument('--allow-metadata-difference',action='append',default=[],metavar='KEY',help='explicitly permit a deliberate experimental variable (e.g. compiler); repeat for each key, and document why the comparison remains meaningful')
    args=parser.parse_args()
    try: result=compare(load(args.before),load(args.after),args.allow_metadata_difference)
    except (OSError,ValueError) as exc:
        print(f'input error: {exc}',file=sys.stderr); return 2
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
    return 0 if result['status']=='comparable' else 1

if __name__=='__main__':
    raise SystemExit(main())

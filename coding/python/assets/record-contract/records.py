#!/usr/bin/env python3
"""Original bounded record boundary, Python 3.9+ stdlib; run directly for self-checks.
This example validates and takes ownership of a small in-memory batch. It is not
an array library, streaming parser, precision policy or generic schema framework.
"""
import math

MAX_ROWS=10000


def prepare_records(rows, unit):
    if unit not in ('m','mm'):
        raise ValueError('explicit supported coordinate unit required: m or mm')
    if not isinstance(rows,list) or len(rows)>MAX_ROWS:
        raise ValueError('example requires a list of at most 10000 records')
    scale=1.0 if unit=='m' else 0.001
    prepared=[]
    seen=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'id','xyz'}:
            raise ValueError('record requires id and xyz only')
        ident=row['id']
        if not isinstance(ident,str) or not ident or len(ident)>128 or ident in seen:
            raise ValueError('IDs must be nonempty, unique and <=128 characters')
        xyz=row['xyz']
        if not isinstance(xyz,(tuple,list)) or len(xyz)!=3:
            raise ValueError('xyz requires exactly three coordinates')
        owned=[]
        for value in xyz:
            if type(value) not in (int,float):
                raise ValueError('coordinates require numeric values, not bool/string')
            try: number=float(value)*scale
            except (OverflowError,ValueError):raise ValueError('coordinate outside float range') from None
            if not math.isfinite(number):raise ValueError('coordinate must be finite')
            owned.append(number)
        seen.add(ident)
        prepared.append((ident,tuple(owned)))
    return tuple(prepared)


def main():
    source=[{'id':'p1','xyz':[1000,2000,3000]}]
    published=prepare_records(source,'mm')
    source[0]['xyz'][0]=999
    if published!=(('p1',(1.0,2.0,3.0)),):raise RuntimeError('ownership/unit check failed')
    try:
        candidate=prepare_records([{'id':'new','xyz':[1,2,3]}, {'id':'bad','xyz':[1,float('nan'),3]}],'m')
    except ValueError:
        pass
    else:
        published=candidate
        raise RuntimeError('invalid tail accepted')
    if published[0][0]!='p1':raise RuntimeError('partial publication')
    print('record contract: PASS (no performance claim)')

if __name__=='__main__':main()

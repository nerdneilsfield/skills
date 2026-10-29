#!/usr/bin/env python3
"""Bounded read-only Linux /proc interval sampler; no profiler, command execution or network."""
import argparse
import json
import math
import os
import re
from pathlib import Path, PurePosixPath
import sys
import time

MAX_FILE_BYTES=262144
MAX_ERRORS=256
MAX_TASK_SCAN=4096
MAX_OUTPUT_BYTES=16*1024*1024

class Reader:
    def __init__(self): self.errors=[]
    def error(self,message):
        if len(self.errors)<MAX_ERRORS:self.errors.append(message)
    def text(self,path):
        try:
            with path.open('rb') as stream: raw=stream.read(MAX_FILE_BYTES+1)
            if len(raw)>MAX_FILE_BYTES:
                self.error(f'{path}: oversized');return None
            return raw.decode('utf-8',errors='replace')
        except OSError as exc:
            self.error(f'{path}: {exc.__class__.__name__}');return None

def parse_stat(text):
    # comm can contain spaces and ')'; the remaining fields contain no parentheses.
    end=text.rfind(')'); start=text.find('(')
    if start<0 or end<start:raise ValueError('invalid proc stat record')
    fields=text[end+1:].split()
    if len(fields)<37:raise ValueError('short proc stat record')
    result={'pid':int(text[:start].strip()),'state':fields[0]}
    for key,index in [('minflt',7),('majflt',9),('utime_ticks',11),('stime_ticks',12),
                      ('num_threads',17),('starttime_ticks',19),('virtual_bytes',20),('rss_pages',21),('processor',36)]:
        result[key]=int(fields[index])
    return result

def parse_status(text):
    result={}
    for line in text.splitlines():
        if ':' in line:
            key,value=line.split(':',1);result[key]=value.strip()
    return result

def cpu_count_from_list(value):
    ids=set()
    for part in value.strip().split(','):
        if not part:continue
        ends=part.split('-'); low=int(ends[0]);high=int(ends[-1])
        if len(ends)>2 or low<0 or high<low or high>1048576:raise ValueError('invalid CPU list')
        ids.update(range(low,high+1))
    return len(ids)

def parse_pressure(text):
    result={}
    for line in text.splitlines():
        parts=line.split()
        if not parts:continue
        for item in parts[1:]:
            key,value=item.split('=',1)
            result[parts[0]+'_'+('total_us' if key=='total' else key)]=int(value) if key=='total' else float(value)
    return result

def safe_parse(reader,path,parser):
    text=reader.text(path)
    if text is None:return None
    try:return parser(text)
    except (ValueError,IndexError,OverflowError) as exc:
        reader.error(f'{path}: malformed ({exc.__class__.__name__})');return None

def numeric_lines(text):
    result={}
    for line in text.splitlines():
        fields=line.replace(':',' ').split()
        if len(fields)>=2:
            try:result[fields[0]]=int(fields[1])
            except ValueError:pass
    return result

def read_task(reader,path,include_memory=False):
    first=safe_parse(reader,path/'stat',parse_stat)
    if first is None:return None
    status=safe_parse(reader,path/'status',parse_status) or {}
    for key,dest in [('voluntary_ctxt_switches','voluntary_context_switches'),('nonvoluntary_ctxt_switches','nonvoluntary_context_switches')]:
        try:
            if key in status:first[dest]=int(status[key])
        except ValueError:reader.error(f'{path}/status: malformed {key}')
    first['cpus_allowed_list']=status.get('Cpus_allowed_list')
    if include_memory:
        for key in ('VmRSS','VmSwap','VmHWM'):
            if key in status:
                try:first[key+'_kib']=int(status[key].split()[0])
                except (ValueError,IndexError):reader.error(f'{path}/status: malformed {key}')
    else:
        schedstat=reader.text(path/'schedstat')
        if schedstat is not None:
            try:
                run,wait,slices=map(int,schedstat.split()[:3])
                first.update(runtime_ns=run,runqueue_wait_ns=wait,timeslices=slices)
            except ValueError:reader.error(f'{path}/schedstat: malformed')
        sched=reader.text(path/'sched')
        if sched is not None:
            for line in sched.splitlines():
                if line.strip().startswith('se.nr_migrations') and ':' in line:
                    try:first['cpu_migrations']=int(line.split(':',1)[1])
                    except ValueError:reader.error(f'{path}/sched: malformed migrations')
    last=safe_parse(reader,path/'stat',parse_stat)
    if last is None or first['starttime_ticks']!=last['starttime_ticks'] or first['pid']!=last['pid']:
        reader.error(f'{path}: identity changed/disappeared during read');return None
    return first

def cgroup_capacity(reader,pid_path,cgroup_root,status_affinity):
    result={'leader_affinity_logical_cpus':None,'cgroup_v2_quota_cpu_equivalents':None,
            'cgroup_v2_effective_cpuset_logical_cpus':None,'quota_scope':'visible cgroup-v2 ancestors only; namespace/mount visibility may hide constraints'}
    if status_affinity:
        try:result['leader_affinity_logical_cpus']=cpu_count_from_list(status_affinity)
        except ValueError:reader.error('leader Cpus_allowed_list malformed')
    text=reader.text(pid_path/'cgroup')
    path=None
    if text:
        for line in text.splitlines():
            if line.startswith('0::'):path=line[3:];break
    if path is None:
        result['status']='cgroup_v2_unavailable_or_v1';return result
    root=cgroup_root.resolve()
    mountinfo=reader.text(pid_path.parent/'self/mountinfo')
    mappings=[]
    if mountinfo:
        for line in mountinfo.splitlines():
            if ' - ' not in line:continue
            left,right=line.split(' - ',1);fields=left.split();fstype=right.split()
            if len(fields)<5 or not fstype or fstype[0]!='cgroup2':continue
            unescape=lambda text: re.sub(r'\\([0-7]{3})',lambda m:chr(int(m.group(1),8)),text)
            mount_root=unescape(fields[3]);mountpoint=unescape(fields[4])
            if Path(mountpoint).resolve()==root:mappings.append(mount_root)
    if len(mappings)!=1:
        result['status']='cgroup_mount_mapping_unknown';return result
    try:
        membership=PurePosixPath(path);mount_root=PurePosixPath(mappings[0])
        if not membership.is_absolute() or '..' in membership.parts or '..' in mount_root.parts:raise ValueError('unsafe cgroup path')
        relative=membership.relative_to(mount_root)
        candidate=(root/str(relative)).resolve();candidate.relative_to(root)
    except ValueError:
        result['status']='cgroup_path_outside_visible_mount';return result
    result['verified_mount_root']=str(mount_root)
    result['cgroup_path']=path
    quotas=[];records=[];current=candidate;reached_root=False
    for _ in range(64):
        text=reader.text(current/'cpu.max')
        if text is not None:
            try:
                quota,period=text.split()[:2];period=int(period)
                if period<=0:raise ValueError('nonpositive period')
                if quota!='max':
                    quota=int(quota)
                    if quota<=0:raise ValueError('nonpositive quota')
                    quotas.append(quota/period)
                records.append({'relative_path':str(current.relative_to(root)),'cpu_max':text.strip()})
            except (ValueError,OverflowError):reader.error(f'{current}/cpu.max: malformed')
        if current==root:
            reached_root=True;break
        current=current.parent
    result['ancestry_truncated']=not reached_root
    if not reached_root:reader.error('cgroup ancestry truncated at 64 levels before visible mount root')
    result['visible_cpu_max_records']=records
    if quotas:result['cgroup_v2_quota_cpu_equivalents']=min(quotas)
    cpuset=reader.text(candidate/'cpuset.cpus.effective')
    if cpuset:
        try:result['cgroup_v2_effective_cpuset_logical_cpus']=cpu_count_from_list(cpuset)
        except ValueError:reader.error('cgroup effective cpuset malformed')
    stats=safe_parse(reader,candidate/'cpu.stat',numeric_lines)
    result['cgroup_cpu_stat']=stats
    result['status']='visible_v2_records' if records else 'quota_unknown'
    return result

def snapshot(pid,proc_root=Path('/proc'),cgroup_root=Path('/sys/fs/cgroup'),max_threads=64,smaps=False):
    reader=Reader();path=proc_root/str(pid)
    started=time.monotonic();process=read_task(reader,path,True)
    result={'process':process,'threads':[],'system':{},'errors':reader.errors,
            'thread_samples_truncated':False,'task_scan_truncated':False}
    if process is not None:
        # /proc/PID/status context switches describe the leader, not all process threads.
        for key in ('voluntary_context_switches','nonvoluntary_context_switches'):
            if key in process:process['leader_'+key]=process.pop(key)
        if smaps:
            values=safe_parse(reader,path/'smaps_rollup',numeric_lines)
            if values is not None:process['smaps_rollup_kib']={k:values[k] for k in ('Rss','Pss','Private_Clean','Private_Dirty','Swap','SwapPss') if k in values}
        tids=[]
        try:
            with os.scandir(path/'task') as entries:
                for entry in entries:
                    if entry.name.isdigit():tids.append(int(entry.name))
                    if len(tids)>=MAX_TASK_SCAN:
                        result['task_scan_truncated']=True;break
        except OSError as exc:reader.error(f'{path}/task: {exc.__class__.__name__}')
        result['observed_task_entries']=len(tids)
        result['thread_samples_truncated']=len(tids)>max_threads or result['task_scan_truncated']
        for tid in sorted(tids)[:max_threads]:
            task=read_task(reader,path/'task'/str(tid))
            if task is not None:result['threads'].append(task)
        result['selected_thread_state_counts']={state:sum(t['state']==state for t in result['threads']) for state in ('R','S','D','T','t','Z','I')}
        result['capacity']=cgroup_capacity(reader,path,cgroup_root,process.get('cpus_allowed_list'))
        last=safe_parse(reader,path/'stat',parse_stat)
        if last is None or last['starttime_ticks']!=process['starttime_ticks']:
            result['process']=None;result['threads']=[];reader.error('process identity changed/disappeared during snapshot')
    stat=reader.text(proc_root/'stat')
    if stat is not None:
        result['system'].update({k:v for k,v in numeric_lines(stat).items() if k in ('ctxt','procs_running','procs_blocked')})
        result['system']['visible_logical_cpu_count']=sum(line.startswith('cpu') and line[3:4].isdigit() for line in stat.splitlines())
    vm=safe_parse(reader,proc_root/'vmstat',numeric_lines)
    if vm is not None:result['system'].update({k:v for k,v in vm.items() if k in ('pswpin','pswpout','pgfault','pgmajfault','oom_kill') or k.startswith(('pgscan_','pgsteal_','allocstall'))})
    mem=safe_parse(reader,proc_root/'meminfo',numeric_lines)
    if mem is not None:result['system']['meminfo_kib']={k:mem[k] for k in ('MemTotal','MemAvailable','SwapTotal','SwapFree','Dirty','Writeback') if k in mem}
    for resource in ('cpu','memory','io'):
        pressure=safe_parse(reader,proc_root/'pressure'/resource,parse_pressure)
        if pressure is not None:result['system'][resource+'_pressure']=pressure
    result['schedstats_enabled_raw']=reader.text(proc_root/'sys/kernel/sched_schedstats')
    if result['schedstats_enabled_raw'] is not None:result['schedstats_enabled_raw']=result['schedstats_enabled_raw'].strip()
    result['monotonic_seconds']=started
    result['snapshot_read_seconds']=time.monotonic()-started
    return result

def counter_delta(before,after,elapsed):
    if before is None or after is None:return {'status':'unavailable'}
    if after<before:return {'status':'counter_decreased'}
    return {'delta':after-before,'per_second':(after-before)/elapsed}

TASK_COUNTERS=('utime_ticks','stime_ticks','minflt','majflt','voluntary_context_switches','nonvoluntary_context_switches',
               'leader_voluntary_context_switches','leader_nonvoluntary_context_switches','runtime_ns','runqueue_wait_ns','timeslices','cpu_migrations')
def task_delta(before,after,elapsed,hz):
    result={'pid':after['pid'],'starttime_ticks':after['starttime_ticks']}
    for key in TASK_COUNTERS:
        if key in before or key in after:result[key]=counter_delta(before.get(key),after.get(key),elapsed)
    if all(k in before and k in after and after[k]>=before[k] for k in ('utime_ticks','stime_ticks')):
        result['cpu_percent_one_logical_cpu']=100*((after['utime_ticks']-before['utime_ticks'])+(after['stime_ticks']-before['stime_ticks']))/hz/elapsed
    return result

def interval(before,after,elapsed,hz):
    if elapsed<=0:raise ValueError('sample elapsed time must be positive')
    result={'elapsed_seconds':elapsed,'process':{'status':'unavailable'},'threads':[],'system_rates':{}}
    a=before.get('process');b=after.get('process')
    same=a and b and a['pid']==b['pid'] and a['starttime_ticks']==b['starttime_ticks']
    if a and b:
        result['process']=task_delta(a,b,elapsed,hz) if same else {'status':'pid_reused'}
    old={t['pid']:t for t in before['threads']}
    if same:
        for thread in after['threads']:
            previous=old.get(thread['pid'])
            if previous and previous['starttime_ticks']==thread['starttime_ticks']:result['threads'].append(task_delta(previous,thread,elapsed,hz))
            else:result['threads'].append({'pid':thread['pid'],'status':'new_or_reused_thread'})
    for key,value in after['system'].items():
        if key in ('ctxt','pswpin','pswpout','pgfault','pgmajfault','oom_kill') or key.startswith(('pgscan_','pgsteal_','allocstall')):
            result['system_rates'][key]=counter_delta(before['system'].get(key),value,elapsed)
        elif key.endswith('_pressure'):
            for name,count in value.items():
                if name.endswith('_total_us'):result['system_rates'][key+'.'+name]=counter_delta(before['system'].get(key,{}).get(name),count,elapsed)
    ac=before.get('capacity',{}).get('cgroup_cpu_stat') or {};bc=after.get('capacity',{}).get('cgroup_cpu_stat') or {}
    if before.get('capacity',{}).get('cgroup_path')==after.get('capacity',{}).get('cgroup_path'):
        result['cgroup_cpu_stat_rates']={k:counter_delta(ac.get(k),v,elapsed) for k,v in bc.items() if k in ('nr_periods','nr_throttled','throttled_usec')}
    return result

def validate_limits(pid,duration,step,max_threads):
    if pid<=0:raise ValueError('PID must be positive')
    if not math.isfinite(duration) or duration<=0 or duration>3600:raise ValueError('duration must be >0 and <=3600 seconds')
    if not math.isfinite(step) or step<0.1 or step>duration:raise ValueError('interval must be >=0.1 and <=duration')
    if math.ceil(duration/step)>600:raise ValueError('at most 600 sampling intervals are allowed')
    if not 1<=max_threads<=256:raise ValueError('max-threads must be 1..256')

class JsonlOutput:
    def __init__(self,stream,limit=MAX_OUTPUT_BYTES):
        self.stream=stream;self.limit=limit;self.written=0;self.closed=False
    def emit(self,value):
        if self.closed:return False
        data=json.dumps(value,sort_keys=True,allow_nan=False)+'\n'
        if self.written+len(data.encode('utf-8'))>self.limit-128:
            terminal=json.dumps({'type':'end','reason':'output_limit'})+'\n'
            if self.written+len(terminal.encode('utf-8'))<=self.limit:
                self.stream.write(terminal);self.stream.flush()
                self.written+=len(terminal.encode('utf-8'))
            self.closed=True;return False
        self.stream.write(data);self.stream.flush()
        self.written+=len(data.encode('utf-8'));return True

def main():
    parser=argparse.ArgumentParser(description=__doc__,epilog='Python 3.9+ standard library, Linux only. JSON Lines on stdout; max 600 intervals/256 threads/16 MiB. No sudo, installs, signals, attach or target execution. Exit 0 duration complete, 1 target unavailable/reused, 2 usage/platform error, 3 output bound. Snapshots miss transient states and cannot prove cache misses, lock cause or swap ownership.')
    parser.add_argument('--pid',type=int,required=True)
    parser.add_argument('--duration',type=float,default=5)
    parser.add_argument('--interval',type=float,default=1)
    parser.add_argument('--max-threads',type=int,default=64)
    parser.add_argument('--smaps',action='store_true',help='opt in to bounded smaps_rollup reads (PSS; may require permission and cost extra CPU)')
    args=parser.parse_args()
    try:validate_limits(args.pid,args.duration,args.interval,args.max_threads)
    except ValueError as exc:parser.error(str(exc))
    if not sys.platform.startswith('linux'):parser.error('Linux /proc is required; no cross-platform emulation')
    hz=os.sysconf('SC_CLK_TCK');page=os.sysconf('SC_PAGE_SIZE')
    writer=JsonlOutput(sys.stdout);emit=writer.emit
    if not emit({'type':'header','schema_version':1,'pid':args.pid,'clock_ticks_per_second':hz,'page_size_bytes':page,
          'limits':{'intervals':600,'selected_threads':args.max_threads,'task_entries_scanned':MAX_TASK_SCAN,'output_bytes':MAX_OUTPUT_BYTES},
          'limitations':['System counters are host-visible totals, not attribution to this PID.','R state snapshots and thread counts miss transient scheduling; S/D are not proven lock waits.','schedstat zero can mean disabled statistics; inspect schedstats_enabled_raw.','Affinity is per-thread; quota is visible ancestor CPU bandwidth, not physical core count.','No cache/HITM/lock stack events collected; use supported targeted profilers.','Paths/cgroup identities may be sensitive; review JSON before sharing.']}):return 3
    previous=snapshot(args.pid,max_threads=args.max_threads,smaps=args.smaps)
    if not emit({'type':'snapshot','sample':previous}):return 3
    if previous['process'] is None:return 1
    origin=previous['monotonic_seconds'];deadline=origin+args.duration
    while time.monotonic()<deadline:
        time.sleep(min(args.interval,max(0,deadline-time.monotonic())))
        current=snapshot(args.pid,max_threads=args.max_threads,smaps=args.smaps)
        rates=interval(previous,current,current['monotonic_seconds']-previous['monotonic_seconds'],hz)
        if not emit({'type':'snapshot','sample':current,'interval':rates}):return 3
        if current['process'] is None or rates['process'].get('status')=='pid_reused':return 1
        previous=current
    return 0 if emit({'type':'end','reason':'duration_complete'}) else 3

if __name__=='__main__':
    try:raise SystemExit(main())
    except KeyboardInterrupt:
        print(json.dumps({'type':'end','reason':'interrupted'}));raise SystemExit(130)

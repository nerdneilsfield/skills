import importlib.util
from pathlib import Path
import tempfile
import unittest
import io
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1]/'coding/cpp-performance/scripts/sample_linux_proc.py'
def module():
    spec=importlib.util.spec_from_file_location('proc_sampler',SCRIPT)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def stat_line(pid=123,start=100,utime=20,stime=10,minflt=2,majflt=1):
    fields=['0']*50
    fields[0]='S';fields[7]=str(minflt);fields[9]=str(majflt)
    fields[11]=str(utime);fields[12]=str(stime);fields[17]='2'
    fields[19]=str(start);fields[20]='4096';fields[21]='3';fields[36]='1'
    return f'{pid} (worker (odd) name) '+' '.join(fields)+'\n'

class ProcSamplerTests(unittest.TestCase):
    def test_stat_parser_handles_parentheses_and_spaces(self):
        m=module();data=m.parse_stat(stat_line())
        self.assertEqual(data['starttime_ticks'],100)
        self.assertEqual(data['utime_ticks'],20)
        self.assertEqual(data['minflt'],2)
        self.assertEqual(data['rss_pages'],3)
        self.assertEqual(data['processor'],1)
        self.assertNotIn('comm',data)
        with self.assertRaises(ValueError):m.parse_stat('broken')

    def test_delta_rates_and_reset(self):
        m=module();self.assertEqual(m.counter_delta(10,16,2),{'delta':6,'per_second':3})
        self.assertEqual(m.counter_delta(16,10,2)['status'],'counter_decreased')
        self.assertEqual(m.counter_delta(None,10,2)['status'],'unavailable')

    def test_pid_reuse_and_thread_reuse_never_subtracted(self):
        m=module()
        before={'process':{'pid':123,'starttime_ticks':1,'utime_ticks':1,'stime_ticks':1},'threads':[],'system':{}}
        after={'process':{'pid':123,'starttime_ticks':2,'utime_ticks':100,'stime_ticks':100},'threads':[],'system':{}}
        self.assertEqual(m.interval(before,after,1,100)['process']['status'],'pid_reused')
        before['process']['starttime_ticks']=2
        before['threads']=[{'pid':7,'starttime_ticks':1,'utime_ticks':1,'stime_ticks':1}]
        after['threads']=[{'pid':7,'starttime_ticks':2,'utime_ticks':10,'stime_ticks':10}]
        self.assertEqual(m.interval(before,after,1,100)['threads'][0]['status'],'new_or_reused_thread')

    def test_cpu_uses_one_logical_cpu_units(self):
        m=module()
        a={'process':{'pid':123,'starttime_ticks':1,'utime_ticks':0,'stime_ticks':0},'threads':[],'system':{}}
        b={'process':{'pid':123,'starttime_ticks':1,'utime_ticks':150,'stime_ticks':50},'threads':[],'system':{}}
        self.assertEqual(m.interval(a,b,1,100)['process']['cpu_percent_one_logical_cpu'],200)

    def test_snapshot_missing_pid_and_restricted_file(self):
        m=module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            result=m.snapshot(123,root,root,2,False)
            self.assertIsNone(result['process'])
            self.assertTrue(result['errors'])
            reader=m.Reader()
            path=root/'huge';path.write_bytes(b'x'*(m.MAX_FILE_BYTES+1))
            self.assertIsNone(reader.text(path))
            self.assertTrue(any('oversized' in x for x in reader.errors))

    def test_fixture_snapshot_thread_limit_and_no_mutation(self):
        m=module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);proc=root/'proc';cg=root/'cgroup';(proc/'123/task').mkdir(parents=True);cg.mkdir()
            (proc/'self').mkdir();(proc/'self/mountinfo').write_text(f'1 0 0:1 / {cg} rw - cgroup2 cgroup rw\n')
            (proc/'123/stat').write_text(stat_line())
            (proc/'123/status').write_text('Cpus_allowed_list:\t0-1\nVmRSS:\t12 kB\nvoluntary_ctxt_switches:\t4\nnonvoluntary_ctxt_switches:\t2\n')
            (proc/'123/cgroup').write_text('0::/team/job\n')
            for tid in (123,124,125):
                p=proc/'123/task'/str(tid);p.mkdir();(p/'stat').write_text(stat_line(tid))
                (p/'status').write_text('Cpus_allowed_list:\t0-1\nvoluntary_ctxt_switches:\t3\nnonvoluntary_ctxt_switches:\t1\n')
                (p/'schedstat').write_text('1000 2000 3\n')
            (proc/'stat').write_text('cpu 10 2 3 4 5 6 7 8 9 10\ncpu0 1 2 3 4\nctxt 500\nprocs_running 2\nprocs_blocked 0\n')
            (proc/'vmstat').write_text('pswpin 2\npswpout 3\npgfault 5\npgmajfault 1\n')
            (proc/'meminfo').write_text('MemTotal: 1000 kB\nMemAvailable: 400 kB\nSwapTotal: 200 kB\nSwapFree: 100 kB\n')
            (cg/'team/job').mkdir(parents=True);(cg/'cpu.max').write_text('max 100000')
            (cg/'team/cpu.max').write_text('100000 100000');(cg/'team/job/cpu.max').write_text('200000 100000')
            before=sorted(str(p) for p in root.rglob('*'))
            result=m.snapshot(123,proc,cg,2,False)
            self.assertEqual(len(result['threads']),2)
            self.assertTrue(result['thread_samples_truncated'])
            self.assertEqual(result['capacity']['cgroup_v2_quota_cpu_equivalents'],1)
            self.assertEqual(result['capacity']['leader_affinity_logical_cpus'],2)
            self.assertEqual(result['threads'][0]['runqueue_wait_ns'],2000)
            self.assertEqual(result['system']['pswpin'],2)
            self.assertEqual(sorted(str(p) for p in root.rglob('*')),before)

    def test_cgroup_mount_root_mapping(self):
        m=module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'proc/self').mkdir(parents=True);(root/'proc/123').mkdir()
            cg=root/'cgroup';(cg/'job').mkdir(parents=True)
            (root/'proc/self/mountinfo').write_text(f'1 0 0:1 /slice {cg} rw - cgroup2 cgroup rw\n')
            (root/'proc/123/cgroup').write_text('0::/slice/job\n')
            (cg/'job/cpu.max').write_text('50000 100000')
            reader=m.Reader()
            result=m.cgroup_capacity(reader,root/'proc/123',cg,'0-1')
            self.assertEqual(result['cgroup_v2_quota_cpu_equivalents'],0.5)
            (root/'proc/self/mountinfo').write_text('')
            result=m.cgroup_capacity(m.Reader(),root/'proc/123',cg,'0-1')
            self.assertIsNone(result['cgroup_v2_quota_cpu_equivalents'])
            self.assertEqual(result['status'],'cgroup_mount_mapping_unknown')

    def test_cgroup_ancestor_limit_is_explicit(self):
        m=module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);proc=root/'proc';cg=root/'cgroup';(proc/'self').mkdir(parents=True);(proc/'123').mkdir();cg.mkdir()
            relative='/'.join(['level']*70);leaf=cg/relative;leaf.mkdir(parents=True)
            (proc/'self/mountinfo').write_text(f'1 0 0:1 / {cg} rw - cgroup2 cgroup rw\n')
            (proc/'123/cgroup').write_text('0::/'+relative+'\n')
            (leaf/'cpu.max').write_text('100000 100000')
            result=m.cgroup_capacity(m.Reader(),proc/'123',cg,'0')
            self.assertTrue(result['ancestry_truncated'])

    def test_cpuset_and_pressure_parsers(self):
        m=module();self.assertEqual(m.cpu_count_from_list('0-3,8,10-11'),7)
        with self.assertRaises(ValueError):m.cpu_count_from_list('3-1')
        self.assertEqual(m.parse_pressure('some avg10=1.00 avg60=2.00 avg300=3.00 total=100\n')['some_total_us'],100)

    def test_permission_and_disappearance_are_explicit(self):
        m=module();reader=m.Reader();path=mock.Mock()
        path.open.side_effect=PermissionError('denied')
        self.assertIsNone(reader.text(path))
        self.assertIn('PermissionError',reader.errors[0])
        before={'process':{'pid':1,'starttime_ticks':1},'threads':[],'system':{}}
        after={'process':None,'threads':[],'system':{}}
        self.assertEqual(m.interval(before,after,1,100)['process']['status'],'unavailable')

    def test_output_limit_is_enforced_in_bytes(self):
        m=module();stream=io.StringIO();writer=m.JsonlOutput(stream,256)
        self.assertTrue(writer.emit({'small':'ok'}))
        self.assertFalse(writer.emit({'oversized':'x'*300}))
        self.assertFalse(writer.emit({'another':'record'}))
        self.assertLessEqual(len(stream.getvalue().encode('utf-8')),256)
        self.assertIn('output_limit',stream.getvalue())

    def test_cli_limits(self):
        m=module()
        with self.assertRaises(ValueError):m.validate_limits(0,1,1,64)
        with self.assertRaises(ValueError):m.validate_limits(1,3601,1,64)
        with self.assertRaises(ValueError):m.validate_limits(1,1,0,64)
        with self.assertRaises(ValueError):m.validate_limits(1,1,1,10000)

if __name__=='__main__':unittest.main()

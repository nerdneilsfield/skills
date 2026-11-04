"""Synthetic event -> checked dimension join -> explicit denominator -> chart.
No network. Import only installed pandas; matplotlib only on explicit render.
"""
import argparse
import json
from pathlib import Path


def fixture():
    import pandas as pd
    events = pd.DataFrame({
        'event_id': ['e1', 'e2', 'e3', 'e4'],
        'subject_id': ['s1', 's1', 's2', 's3'],
        'timestamp': ['2026-01-01T00:00:00Z', '2026-01-01T01:00:00Z',
                      '2026-01-02T00:00:00Z', '2026-01-02T01:00:00Z'],
        'success': pd.array([1, 0, None, 1], dtype='Int64')})
    groups = pd.DataFrame({'subject_id': ['s1', 's2', 's3'], 'group': ['A', 'A', 'B']})
    return events, groups


def analyze(events, groups):
    import pandas as pd
    events, groups = events.copy(), groups.copy()
    if not {'event_id','subject_id','timestamp','success'}.issubset(events.columns):
        raise ValueError('missing event columns')
    if not {'subject_id','group'}.issubset(groups.columns):
        raise ValueError('missing dimension columns')
    if events['event_id'].isna().any() or events['event_id'].duplicated().any():
        raise ValueError('event identity must be non-null and unique')
    if events['subject_id'].isna().any() or groups['subject_id'].isna().any():
        raise ValueError('null join keys must be resolved before merge')
    if groups['subject_id'].duplicated().any() or groups['group'].isna().any():
        raise ValueError('dimension must have one non-null group per subject')
    if not events['success'].dropna().isin([0, 1]).all():
        raise ValueError('outcome must be 0, 1 or missing')
    # Fixture timestamps have offsets. Do not infer UTC for arbitrary naive local data.
    events['timestamp'] = pd.to_datetime(events['timestamp'], utc=True, errors='raise')
    if events['timestamp'].isna().any():
        raise ValueError('missing timestamps')
    joined = events.merge(groups, on='subject_id', how='left', validate='many_to_one', indicator=True)
    unmatched = int((joined['_merge'] != 'both').sum())
    if unmatched:
        raise ValueError('unmatched subjects; decide coverage policy before estimating')
    if len(joined) != len(events):
        raise ValueError('join changed event count')
    # size counts eligible rows; count excludes unknown outcomes. Both are reported.
    summary = joined.groupby('group', observed=True, dropna=False).agg(
        eligible=('event_id','size'), known=('success','count'), successes=('success','sum'))
    summary['unknown'] = summary['eligible'] - summary['known']
    summary['known_success_rate'] = summary['successes'].div(summary['known'].where(summary['known'] > 0))
    summary = summary.reset_index()
    audit = {'input_rows': len(events), 'joined_rows': len(joined), 'unmatched_rows': unmatched,
             'unknown_outcomes': int(summary['unknown'].sum()),
             'estimand': 'event success fraction among observed outcomes; not subject success probability'}
    return summary, audit


def render(summary, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output = Path(output)
    fig, ax = plt.subplots(figsize=(6, 3.6), layout='constrained')
    try:
        # Unknown rates remain gaps; no invented zero or tiny epsilon.
        y = summary['known_success_rate'].to_numpy(dtype=float, na_value=float('nan'))
        ax.scatter(range(len(summary)), y, marker='o', color='#0072B2')
        labels = [f"{row.group}\nknown={row.known}/{row.eligible}" for row in summary.itertuples()]
        ax.set_xticks(range(len(summary)), labels)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel('Success fraction among known outcomes')
        ax.set_title('Synthetic events: descriptive, not an inference')
        ax.grid(axis='y', alpha=.2)
        # Exclusive create avoids overwriting existing output; no directory creation.
        with output.open('xb') as stream:
            fig.savefig(stream, format='png', dpi=150)
    finally:
        plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--png', type=Path, help='Explicit new local PNG output; requires installed matplotlib')
    args=parser.parse_args()
    summary,audit=analyze(*fixture())
    print(summary.to_string(index=False))
    print(json.dumps(audit, indent=2))
    if args.png: render(summary,args.png)


if __name__ == '__main__': main()

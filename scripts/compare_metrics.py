#!/usr/bin/env python3
"""Compare complete FTS reports; output measured reductions, never inferred points."""
import argparse
import json
import math
from pathlib import Path
import statistics

CATEGORIES = {
    'build': ('build_ik_all_sec', 'build_ik_content_sec', 'build_beng_en_sec'),
    'tokenize': ('tokenize_ik_avg_ms', 'tokenize_beng_avg_ms'),
    'query': ('query_cn_avg_ms', 'query_beng_avg_ms', 'query_mixed_avg_ms', 'query_limit_avg_ms'),
}
CONFIG = ('rows', 'batch', 'rounds', 'query_rounds', 'samples', 'warmup', 'skip_load')
HITS = ('query_cn_hits', 'query_beng_hits', 'query_mixed_hits', 'query_limit_hits')


def metrics(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    value = value.get('metrics', value)
    if not isinstance(value, dict):
        raise ValueError('Report must contain a metrics object')
    for key in (*CONFIG, *HITS, *(key for group in CATEGORIES.values() for key in group)):
        number = value.get(key)
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError('Missing or invalid metric: ' + key)
        if key in CONFIG or key in HITS:
            if number < 0 or number != int(number):
                raise ValueError('Expected a nonnegative integer: ' + key)
        elif number <= 0:
            raise ValueError('Elapsed time must be positive: ' + key)
    for key in CONFIG:
        if key not in ('warmup', 'skip_load') and value[key] <= 0:
            raise ValueError('Benchmark parameter must be positive: ' + key)
    if value['skip_load'] not in (0, 1):
        raise ValueError('skip_load must be zero or one')
    return value


def compare(before, after):
    for key in (*CONFIG, *HITS):
        if before[key] != after[key]:
            raise ValueError('Reports differ in ' + key)
    if before['skip_load'] != 0:
        raise ValueError('Full build comparison requires skip_load=0')
    categories = {}
    for category, names in CATEGORIES.items():
        items = {name: {'before': before[name], 'after': after[name],
                        'elapsed_reduction': (before[name] - after[name]) / before[name]}
                 for name in names}
        categories[category] = {
            'elapsed_reduction': statistics.mean(item['elapsed_reduction'] for item in items.values()),
            'metrics': items,
        }
    return {
        'categories': categories,
        'category_mean_elapsed_reduction': statistics.mean(v['elapsed_reduction'] for v in categories.values()),
        'query_hit_counts_match': True,
        'complete_result_equivalence_proven': False,
        'platform_points_predicted': False,
        'note': 'A before/after comparison does not establish the official grading baseline or isolate host noise.',
    }


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    args = parser.parse_args()
    try:
        result = compare(metrics(args.before), metrics(args.after))
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

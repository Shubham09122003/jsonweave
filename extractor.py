import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from .utils import group_paths_by_root, extract_operations, apply_filters, apply_sorting
from .joiner import join_multiple_datasets

__all__ = ["extract_json_paths", "parse_paths_and_operations"]
RESERVED_KEYS = {"join_by", "sort_by", "filter_by", "group_by"}

def parse_path(path: str) -> Tuple[List[str], str]:
    if ' as ' in path:
        raw_path, alias = path.split(' as ')
        return raw_path.strip().split('.'), alias.strip()
    parts = path.strip().split('.')
    return parts, parts[-1]


def extract(data: Any, components: List[str], coords: Dict[str, int], key: str, results: List[Dict]):
    if not components:
        results.append({'value': data, 'coords': coords.copy(), 'key': key})
        return

    head, *tail = components
    match = re.fullmatch(r'(.*)?(?:\{(\w+)\}|\*)(.*)?', head)

    if match:
        prefix, var, suffix = match.groups()
        if var is None:
            var = f'_anon_{len(coords)}'
        segment = data
        if prefix:
            segment = segment.get(prefix, [])
        if suffix:
            tail = [suffix] + tail
        if isinstance(segment, list):
            for idx, item in enumerate(segment):
                new_coords = coords.copy()
                new_coords[var] = idx
                extract(item, tail, new_coords, key, results)
    elif isinstance(data, dict) and head in data:
        extract(data[head], tail, coords, key, results)


def join_values_by_scope(extracted: List[Dict]) -> List[Dict]:
    grouped_by_key = defaultdict(list)
    for item in extracted:
        grouped_by_key[item['key']].append(item)

    def depth(item): return len(item['coords'])
    base_items = max(grouped_by_key.values(), key=lambda group: max(depth(i) for i in group))

    results = []
    for base in base_items:
        base_coords = base['coords']
        record = {base['key']: base['value']}
        for key, items in grouped_by_key.items():
            if key == base['key']:
                continue
            for item in items:
                if all(base_coords.get(k) == item['coords'].get(k) for k in base_coords.keys() & item['coords'].keys()):
                    record[key] = item['value']
                    break
        results.append(record)
    return results


def extract_json_paths(data: Dict, paths: List[str]) -> List[Dict]:
    data_paths, _ = parse_paths_and_operations(paths)
    all_extracted = []
    for path in data_paths:
        components, key = parse_path(path)
        extract(data, components, {}, key, all_extracted)
    return join_values_by_scope(all_extracted)


def parse_paths_and_operations(paths: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    data_paths = []
    operations = defaultdict(list)

    for path in paths:
        if ':' in path and path.split(':', 1)[0].strip() in RESERVED_KEYS:
            key, val = path.split(':', 1)
            key = key.strip()
            val = val.strip().strip('[]')
            values = [v.strip() for v in val.split(',') if v.strip()]
            operations[key].extend(values)
        else:
            data_paths.append(path.strip())

    return data_paths, dict(operations)



def get_data_from_path(data, paths, yield_mode=False):
    """
    Extract and transform JSON data using a pipeline of path expressions.

    Args:
        data (dict): The input nested JSON.
        paths (list[str]): Flat list of extraction paths and transformation directives.
        yield_mode (bool): 
            - True = returns a generator that yields each result row.
            - False = returns a fully materialized list.

    Returns:
        Union[List[dict], Generator[dict]]: Output rows, as list or generator.
    """
    pure_paths = [p for p in paths if ':' not in p]
    operations = extract_operations(paths)

    path_groups = group_paths_by_root(pure_paths)
    extracted_datasets = [
        extract_json_paths(data, group_paths)
        for group_paths in path_groups.values()
    ]

    if 'join_by' in operations:
        result_iter = join_multiple_datasets(
            datasets=extracted_datasets,
            on=operations['join_by'],
            yield_mode=yield_mode
        )
    else:
        result_iter = (row for dataset in extracted_datasets for row in dataset)

    if 'filter_by' in operations:
        result_iter = apply_filters(result_iter, operations['filter_by'])

    if 'sort_by' in operations:
        result_iter = apply_sorting(result_iter, operations['sort_by'])

    return result_iter if yield_mode else list(result_iter)


from collections import defaultdict
from typing import List, Dict, Union, Any
import operator


def group_paths_by_root(paths: List[str]) -> Dict[str, List[str]]:
    """
    Group path strings by their root object (before first iterator `{}`).

    Example:
    - "data.students.{i}.name" → group under "data.students"
    """
    groups = defaultdict(list)
    for path in paths:
        if ':' in path:  # skip reserved operations
            continue
        parts = path.strip().split('.')
        root = []
        for part in parts:
            if '{' in part or '}' in part:
                break
            root.append(part)
        groups['.'.join(root)].append(path)
    return groups


def extract_operations(paths: List[str]) -> Dict[str, List[str]]:
    """
    Extract reserved operations like join_by, filter_by, sort_by.

    Format supported:
    - "join_by: [field1, field2]"
    - "filter_by: [score > 80, age < 18]"
    - "sort_by: [score DESC, name ASC]"
    """
    ops = defaultdict(list)
    for path in paths:
        if ':' in path:
            key, value = path.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('[') and value.endswith(']'):
                value = value[1:-1]
                items = [v.strip() for v in value.split(',') if v.strip()]
                ops[key].extend(items)
            else:
                ops[key].append(value)
    return ops


def apply_filters(data: List[Dict[str, Any]], filters: List[str]) -> List[Dict[str, Any]]:
    """
    Apply filter conditions like "score > 80", "age <= 18".
    """
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }

    def parse_condition(expr: str):
        for op_str in sorted(ops.keys(), key=lambda x: -len(x)):  # longest match first
            if op_str in expr:
                left, right = expr.split(op_str, 1)
                return left.strip(), ops[op_str], right.strip()
        return None, None, None

    for condition in filters:
        key, op_fn, value = parse_condition(condition)
        if key is None:
            continue
        try:
            value = int(value)
        except ValueError:
            pass
        data = [item for item in data if key in item and op_fn(item[key], value)]
    return data


def apply_sorting(data: List[Dict[str, Any]], sort_keys: List[str]) -> List[Dict[str, Any]]:
    """
    Sort records by given sort keys (supports ASC/DESC).
    """
    def parse_sort_key(sort_expr):
        if ' ' in sort_expr:
            key, direction = sort_expr.rsplit(' ', 1)
            return key.strip(), direction.strip().upper() != 'DESC'
        return sort_expr.strip(), True  # default to ascending

    for sort_expr in reversed(sort_keys):  # right to left priority
        key, asc = parse_sort_key(sort_expr)
        data.sort(key=lambda x: x.get(key), reverse=not asc)
    return data

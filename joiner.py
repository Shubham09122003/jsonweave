from typing import List, Dict, Any, Iterable, Union

def join_multiple_datasets(
    datasets: Union[List[List[Dict[str, Any]]], Iterable[List[Dict[str, Any]]]],
    on: List[str],
    yield_mode: bool = False
) -> Union[List[Dict[str, Any]], Iterable[Dict[str, Any]]]:
    """
    Perform a full outer join across multiple datasets using specified join keys.

    Args:
        datasets: List (or iterable) of datasets, each a list of dicts.
        on: List of field names to join on.
        yield_mode: If True, yields results one-by-one as a generator.

    Returns:
        List or generator of joined dict rows.
    """

    indexes = []
    for dataset in datasets:
        index = {}
        for item in dataset:
            key = tuple(item.get(k) for k in on)
            if None in key:
                continue  
            index.setdefault(key, []).append(item)
        indexes.append(index)

    all_keys = set()
    for index in indexes:
        all_keys.update(index.keys())

    def generate_joins():
        for key in all_keys:
            combined = {}
            for index in indexes:
                match = index.get(key, [{}])[0]
                combined.update(match)
            yield combined

    return generate_joins() if yield_mode else list(generate_joins())

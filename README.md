# 🧩 jsonweave

jsonweave is a powerful, lightweight library for extracting and transforming deeply nested JSON using a flat, pipeline-style syntax. It supports path-based traversal, joins, sorting, and filtering—making complex JSON transformations readable and composable.

## ✨ Features

- 🔍 **Iterator-style path extraction**: Supports nested access like `a.{i}.b.{j}.c`
- 🏷️ **Aliasing**: Use `as` for creating custom output fields
- 🧩 **Multi-dataset joining**: Combine different parts of your JSON with `join_by`
- 🔃 **Filtering, sorting, and grouping**: Simple syntax for powerful data manipulation
- 🧵 **Generator-based streaming**: Process large datasets efficiently without loading everything into memory
- 🔧 **Pluggable**: Fully extensible with your own transformation functions

## 📦 Installation

Install from PyPI:
```bash
pip install jsonweave
```

Or, for local development:
```bash
git clone https://github.com/Shubham09122003/jsonweave
cd jsonweave && pip install -e .
```

## 🧠 Concept

Each JSON path is specified in a flat list using dot notation with optional iterators (`{i}`, `{j}`, etc.) and aliases.

This declarative list defines a transformation pipeline:

```python
paths = [
  "data.students.{i}.first_name as student_name",
  "data.students.{i}.subjects.{j}.subject_name as subject_name",
  "data.teachers.{k}.name as teacher_name",
  "data.teachers.{k}.subjects.{l}.subject_name as subject_name",
  "join_by: [subject_name]",
  "sort_by: [score DESC]",
  "filter_by: [score > 85]"
]
```

This pipeline will:
1. Traverse students and teachers arrays
2. Extract `subject_name` and other specified fields
3. Join the datasets based on a common `subject_name`
4. Filter out any results where the score is not greater than 85
5. Sort the final result in descending order by score

## 🛠️ Basic Usage

```python
from jsonweave import get_data_from_path
from pprint import pprint

data = {
  "data": {
    "students": [
      {
        "first_name": "John",
        "subjects": [
          {"subject_name": "Math", "score": 85},
          {"subject_name": "English", "score": 90}
        ]
      }
    ],
    "teachers": [
      {
        "name": "Shubh",
        "subjects": [
          {"subject_name": "Math"},
          {"subject_name": "English"}
        ]
      }
    ]
  }
}

paths = [
  "data.students.{i}.first_name as student_name",
  "data.students.{i}.subjects.{j}.subject_name as subject_name",
  "data.students.{i}.subjects.{j}.score as score",
  "data.teachers.{k}.name as teacher_name",
  "data.teachers.{k}.subjects.{l}.subject_name as subject_name",
  "join_by: [subject_name]",
  "filter_by: [score > 85]",
  "sort_by: [score DESC]"
]

result = get_data_from_path(data, paths)

pprint(result)
```

## 🧵 Generator Mode

For large datasets, use the generator-based function `get_data_from_path_gen` to process data row-by-row, minimizing memory usage.

```python
from jsonweave import get_data_from_path_gen

# Assume `large_data` is a very large JSON object
result_iter = get_data_from_path_gen(large_data, paths)

for row in result_iter:
    print(row)
```

## 🧪 Advanced

### Custom Transform Function

You can easily apply custom logic to the results after extraction.

```python
def concat_fields(row):
    return f"{row['student_name']} - {row['teacher_name']}"

# `result` is the output from get_data_from_path
output = [concat_fields(r) for r in result]
```

## ⚡ Performance

jsonweave handles over 1 million nested rows efficiently with its generator support. It is ideal for processing:

- Survey results
- Logs
- Nested analytics data
- Event payloads

## 🗂️ Path Syntax Reference

| Syntax | Meaning |
|--------|---------|
| `a.b.c` | Access a statically nested path |
| `a.{i}.b` | Iterate over a list `a` |
| `as key` | Rename the output field to `key` |
| `join_by: [field]` | Join datasets on one or more fields |
| `filter_by: [expr]` | Filter the result based on an expression |
| `sort_by: [field ASC/DESC]` | Sort the result by a field |

## 🔧 Roadmap

- [ ] Group-by operations
- [ ] Nested function transformations
- [ ] Command-Line Interface (CLI) support
- [ ] Native XML/YAML input

## 📄 License

This project is licensed under the MIT License.

## 🧑‍💻 Author

Built by Shubham Chauhan.

## ⭐ Star if useful

If you find this project helpful, please ⭐️ it on GitHub!
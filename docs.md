# jsonweave Developer Guide

A comprehensive guide for developers working with complex JSON data structures using jsonweave.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Path Syntax Deep Dive](#path-syntax-deep-dive)
4. [Common Patterns](#common-patterns)
5. [Advanced Techniques](#advanced-techniques)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)
8. [Real-World Examples](#real-world-examples)

## Quick Start

### Installation & Setup
```bash
pip install jsonweave
```

### Your First Transform
```python
from jsonweave import get_data_from_path

# Sample nested JSON
data = {
    "users": [
        {"id": 1, "name": "Alice", "orders": [{"id": 101, "amount": 50}]},
        {"id": 2, "name": "Bob", "orders": [{"id": 102, "amount": 75}]}
    ]
}

# Simple extraction
paths = [
    "users.{i}.name as user_name",
    "users.{i}.orders.{j}.amount as order_amount"
]

result = get_data_from_path(data, paths)
print(result)
# Output: [{'user_name': 'Alice', 'order_amount': 50}, {'user_name': 'Bob', 'order_amount': 75}]
```

## Core Concepts

### 1. Path Traversal
jsonweave uses dot notation to navigate JSON structures:

```python
# Static paths
"user.profile.email"

# Dynamic paths with iterators
"users.{i}.profile.email"

# Nested iterations
"users.{i}.orders.{j}.items.{k}.name"
```

### 2. Iterator Variables
Use `{i}`, `{j}`, `{k}`, etc. to iterate over arrays:

```python
data = {
    "departments": [
        {"name": "Engineering", "employees": [{"name": "Alice"}, {"name": "Bob"}]},
        {"name": "Marketing", "employees": [{"name": "Charlie"}]}
    ]
}

paths = [
    "departments.{i}.name as dept_name",
    "departments.{i}.employees.{j}.name as employee_name"
]

# Result: Cartesian product of departments and employees
```

### 3. Aliasing
Rename fields in the output using `as`:

```python
paths = [
    "user.firstName as first_name",
    "user.lastName as last_name",
    "user.email as contact_email"
]
```

## Path Syntax Deep Dive

### Basic Navigation
```python
# Simple object access
"config.database.host"

# Array access with iteration
"servers.{i}.hostname"

# Mixed navigation
"api.endpoints.{i}.methods.{j}.name"
```

### Aliasing Patterns
```python
# Simple alias
"user.name as username"

# Descriptive aliases
"metrics.{i}.value as metric_value"
"metrics.{i}.timestamp as recorded_at"

# Avoiding conflicts
"orders.{i}.id as order_id"
"customers.{j}.id as customer_id"
```

### Post-Processing Operations
```python
paths = [
    "data.{i}.field as value",
    "join_by: [common_field]",     # Join multiple datasets
    "filter_by: [value > 100]",    # Filter results
    "sort_by: [value DESC]"        # Sort output
]
```

## Common Patterns

### 1. Flattening Nested Arrays
```python
# E-commerce order data
ecommerce_data = {
    "customers": [
        {
            "id": 1,
            "name": "John Doe",
            "orders": [
                {"id": 101, "total": 250, "items": [{"product": "Laptop", "qty": 1}]},
                {"id": 102, "total": 50, "items": [{"product": "Mouse", "qty": 2}]}
            ]
        }
    ]
}

paths = [
    "customers.{i}.name as customer_name",
    "customers.{i}.orders.{j}.id as order_id",
    "customers.{i}.orders.{j}.total as order_total",
    "customers.{i}.orders.{j}.items.{k}.product as product_name",
    "customers.{i}.orders.{j}.items.{k}.qty as quantity"
]
```

### 2. Joining Related Data
```python
# Join students with their teachers by subject
school_data = {
    "students": [
        {"name": "Alice", "subjects": [{"name": "Math", "grade": "A"}]},
        {"name": "Bob", "subjects": [{"name": "Science", "grade": "B"}]}
    ],
    "teachers": [
        {"name": "Dr. Smith", "subjects": [{"name": "Math"}]},
        {"name": "Ms. Johnson", "subjects": [{"name": "Science"}]}
    ]
}

paths = [
    "students.{i}.name as student_name",
    "students.{i}.subjects.{j}.name as subject_name",
    "students.{i}.subjects.{j}.grade as grade",
    "teachers.{k}.name as teacher_name",
    "teachers.{k}.subjects.{l}.name as subject_name",
    "join_by: [subject_name]"
]
```

### 3. Filtering and Sorting
```python
# Extract high-value transactions
paths = [
    "transactions.{i}.user_id as user_id",
    "transactions.{i}.amount as amount",
    "transactions.{i}.timestamp as timestamp",
    "filter_by: [amount > 1000]",
    "sort_by: [amount DESC]"
]
```

## Advanced Techniques

### 1. Memory-Efficient Processing
```python
from jsonweave import get_data_from_path_gen

# For large datasets, use generator version
def process_large_dataset(data, paths):
    for row in get_data_from_path_gen(data, paths):
        # Process one row at a time
        yield transform_row(row)

# Batch processing
def batch_process(data, paths, batch_size=1000):
    batch = []
    for row in get_data_from_path_gen(data, paths):
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
```

### 2. Custom Post-Processing
```python
def enrich_data(rows):
    """Add computed fields to extracted data"""
    for row in rows:
        # Add full name
        if 'first_name' in row and 'last_name' in row:
            row['full_name'] = f"{row['first_name']} {row['last_name']}"
        
        # Add categorization
        if 'amount' in row:
            row['category'] = 'high' if row['amount'] > 100 else 'low'
    
    return rows

# Usage
result = get_data_from_path(data, paths)
enriched = enrich_data(result)
```

### 3. Dynamic Path Generation
```python
def generate_paths(fields, base_path="data.{i}"):
    """Generate paths dynamically based on field list"""
    return [f"{base_path}.{field} as {field}" for field in fields]

# Usage
user_fields = ['name', 'email', 'age']
paths = generate_paths(user_fields, "users.{i}")
```

## Performance Optimization

### 1. Choose the Right Function
```python
# For small datasets (<10K rows)
result = get_data_from_path(data, paths)

# For large datasets (>10K rows)
for row in get_data_from_path_gen(data, paths):
    process_row(row)
```

### 2. Optimize Path Order
```python
# ❌ Bad: Expensive operations first
paths = [
    "complex.{i}.nested.{j}.deep.{k}.value as value",
    "simple.field as simple_field",
    "filter_by: [value > 100]"
]

# ✅ Good: Filter early, complex operations later
paths = [
    "simple.field as simple_field",
    "complex.{i}.nested.{j}.deep.{k}.value as value",
    "filter_by: [value > 100]"
]
```

### 3. Minimize Joins
```python
# ❌ Avoid unnecessary joins
paths = [
    "users.{i}.name as user_name",
    "users.{i}.id as user_id",
    "orders.{j}.user_id as order_user_id",
    "orders.{j}.total as order_total",
    "join_by: [user_id]"  # Only if you really need combined data
]

# ✅ Extract separately if no relationship needed
user_paths = ["users.{i}.name as user_name", "users.{i}.id as user_id"]
order_paths = ["orders.{i}.total as order_total", "orders.{i}.user_id as user_id"]
```

## Troubleshooting

### Common Issues

#### 1. Missing Fields
```python
# Problem: Field doesn't exist in some records
paths = ["users.{i}.profile.avatar as avatar"]  # profile might be null

# Solution: Check your data structure first
def safe_extract(data, paths):
    try:
        return get_data_from_path(data, paths)
    except KeyError as e:
        print(f"Missing field: {e}")
        return []
```

#### 2. Incorrect Iterator Usage
```python
# ❌ Wrong: Reusing iterator variables
paths = [
    "users.{i}.name as user_name",
    "users.{i}.orders.{i}.total as order_total"  # Should be {j}
]

# ✅ Correct: Use different variables for nested arrays
paths = [
    "users.{i}.name as user_name",
    "users.{i}.orders.{j}.total as order_total"
]
```

#### 3. Join Failures
```python
# ❌ Problem: Join field doesn't exist in both datasets
paths = [
    "users.{i}.id as user_id",
    "orders.{j}.customer_id as customer_id",  # Different field name
    "join_by: [user_id]"  # Will fail
]

# ✅ Solution: Ensure consistent field names
paths = [
    "users.{i}.id as user_id",
    "orders.{j}.customer_id as user_id",  # Alias to same name
    "join_by: [user_id]"
]
```

## Real-World Examples

### 1. Processing Survey Data
```python
survey_data = {
    "responses": [
        {
            "respondent_id": "R001",
            "demographics": {"age": 25, "location": "NYC"},
            "questions": [
                {"id": "Q1", "answer": "Yes", "rating": 5},
                {"id": "Q2", "answer": "No", "rating": 2}
            ]
        }
    ]
}

paths = [
    "responses.{i}.respondent_id as respondent_id",
    "responses.{i}.demographics.age as age",
    "responses.{i}.demographics.location as location",
    "responses.{i}.questions.{j}.id as question_id",
    "responses.{i}.questions.{j}.answer as answer",
    "responses.{i}.questions.{j}.rating as rating"
]

# Result: Flat table ready for analysis
```

### 2. API Response Normalization
```python
# GitHub API response structure
github_data = {
    "repositories": [
        {
            "name": "jsonweave",
            "owner": {"login": "user1"},
            "languages": [{"name": "Python", "bytes": 5000}],
            "issues": [{"title": "Bug fix", "state": "open"}]
        }
    ]
}

paths = [
    "repositories.{i}.name as repo_name",
    "repositories.{i}.owner.login as owner",
    "repositories.{i}.languages.{j}.name as language",
    "repositories.{i}.languages.{j}.bytes as language_bytes",
    "repositories.{i}.issues.{k}.title as issue_title",
    "repositories.{i}.issues.{k}.state as issue_state"
]
```

### 3. Log Analysis
```python
# Application logs
log_data = {
    "logs": [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "level": "ERROR",
            "service": "api",
            "events": [
                {"type": "request", "duration": 150, "status": 500},
                {"type": "database", "duration": 75, "status": 200}
            ]
        }
    ]
}

paths = [
    "logs.{i}.timestamp as log_time",
    "logs.{i}.level as log_level",
    "logs.{i}.service as service_name",
    "logs.{i}.events.{j}.type as event_type",
    "logs.{i}.events.{j}.duration as duration",
    "logs.{i}.events.{j}.status as status_code",
    "filter_by: [log_level == 'ERROR']",
    "sort_by: [duration DESC]"
]
```

### 4. E-commerce Analytics
```python
# Complete e-commerce data processing
def analyze_ecommerce_data(data):
    # Extract customer order patterns
    customer_paths = [
        "customers.{i}.id as customer_id",
        "customers.{i}.name as customer_name",
        "customers.{i}.orders.{j}.id as order_id",
        "customers.{i}.orders.{j}.date as order_date",
        "customers.{i}.orders.{j}.total as order_total",
        "customers.{i}.orders.{j}.items.{k}.product_id as product_id",
        "customers.{i}.orders.{j}.items.{k}.quantity as quantity",
        "customers.{i}.orders.{j}.items.{k}.price as item_price"
    ]
    
    # Process in batches for memory efficiency
    results = []
    for batch in batch_process(data, customer_paths, batch_size=1000):
        # Add computed fields
        for row in batch:
            row['item_total'] = row['quantity'] * row['item_price']
            row['order_month'] = row['order_date'][:7]  # Extract YYYY-MM
        results.extend(batch)
    
    return results

# Usage
ecommerce_results = analyze_ecommerce_data(large_ecommerce_data)
```

## Best Practices

### 1. Code Organization
```python
# Create reusable path configurations
class PathConfigs:
    USER_BASIC = [
        "users.{i}.id as user_id",
        "users.{i}.name as user_name",
        "users.{i}.email as user_email"
    ]
    
    ORDER_DETAILS = [
        "orders.{i}.id as order_id",
        "orders.{i}.user_id as user_id",
        "orders.{i}.total as order_total",
        "orders.{i}.date as order_date"
    ]
    
    @classmethod
    def user_orders(cls):
        return cls.USER_BASIC + cls.ORDER_DETAILS + ["join_by: [user_id]"]
```

### 2. Error Handling
```python
def safe_json_extract(data, paths, default=None):
    """Safely extract data with error handling"""
    try:
        result = get_data_from_path(data, paths)
        return result if result else default or []
    except Exception as e:
        logger.error(f"JSON extraction failed: {e}")
        return default or []
```

### 3. Testing
```python
import unittest

class TestJsonWeave(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "users": [{"id": 1, "name": "Alice"}]
        }
    
    def test_basic_extraction(self):
        paths = ["users.{i}.name as user_name"]
        result = get_data_from_path(self.sample_data, paths)
        self.assertEqual(result, [{"user_name": "Alice"}])
    
    def test_empty_data(self):
        result = get_data_from_path({}, ["field.{i}.value"])
        self.assertEqual(result, [])
```

This developer guide provides a comprehensive foundation for working with jsonweave effectively. Remember to always validate your data structure and test your paths with sample data before processing large datasets.
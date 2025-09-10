# Named Output Test

Test example demonstrating docstring-based named output pins with type visibility.

## Node: Math Operations (ID: math-test)

Simple math operations with named outputs using the @outputs docstring annotation.

### Metadata

```json
{
  "uuid": "math-test",
  "title": "Math Operations",
  "pos": [100, 100],
  "size": [200, 150]
}
```

### Logic

```python
from typing import Tuple

@node_entry
def math_operations(x: int, y: int) -> Tuple[int, int, float]:
    """
    Perform basic math operations on two numbers.
    @outputs: sum, product, average
    """
    sum_result = x + y
    product_result = x * y
    average_result = (x + y) / 2.0
    
    return sum_result, product_result, average_result
```

### Expected Output Pins

With both the named output feature AND type visibility enabled, this node will show:
- **Sum (int)** - instead of "Output 1 (int)"
- **Product (int)** - instead of "Output 2 (int)"  
- **Average (float)** - instead of "Output 3 (float)"

This demonstrates both features working together:
1. **Named outputs from docstring**: `@outputs: sum, product, average`
2. **Type visibility**: Shows the data type for each pin
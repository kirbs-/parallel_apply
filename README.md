# parallel_apply
Drastically speed up pandas's apply methods via parallel processing.

## Installation
`pip install parallel_apply`

## Usage
Call `parallel_apply` on a DataFrame, Series, or DataFrameGroupBy and pass a defined function as an argument. parallel_apply takes two optional keyword arguments `n_workers` (defaults to 75% of CPUs) and `chunksize` (defaults to 50).
```python 
import pandas as pd
import parallel_apply # Note, import after importing pandas

df = pd.DataFrame(list(range(1, 1000000)))
df['b'] = 'b'

# Must define a function that takes a single argument. If called on a :
# - Series each value is passed. 
# - DataFrame, a tuple of each row is passed.
# - DataFrameGroupby, a DataFrame of each each group is passed.
# Lambdas are not currently supported.
def abc(row):
    return str(row)

# parallel_apply assumes row-wise processing. No need for axis=1
res = df.parallel_apply(abc)
print(res.head(5))
```
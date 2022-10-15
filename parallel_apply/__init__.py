import multiprocessing as mp
import functools

from pandas.core.frame import DataFrame
from pandas.core.series import Series

try:  # pandas>=0.25.0
    from pandas.core.groupby.generic import SeriesGroupBy  # , NDFrameGroupBy
    from pandas.core.groupby.generic import DataFrameGroupBy
except ImportError:  # pragma: no cover
    try:  # pandas>=0.23.0
        from pandas.core.groupby.groupby import DataFrameGroupBy, SeriesGroupBy
    except ImportError:
        from pandas.core.groupby import DataFrameGroupBy, SeriesGroupBy

from tqdm import tqdm

def p_apply(df, func, *args, **kwargs):
    n_jobs = kwargs.get('n_jobs', mp.cpu_count() - 3)
    chunksize = kwargs.get('chunksize', 50)
    out = []
    with mp.Pool(processes=n_jobs) as p:
        with tqdm(total=len(df)+1) as pbar:
            for _ in p.imap_unordered(func, [group for idx, group in df], chunksize=chunksize):
                out.append(_)
                pbar.update()
    return out

def row_apply(df, func, *args, **kwargs):
    n_jobs = kwargs.get('n_jobs', mp.cpu_count() - 3)
    chunksize = kwargs.get('chunksize', 50)
    out = []
    # func = functools.partial(func, *args, **kwargs)
    with mp.Pool(processes=n_jobs) as p:
        with tqdm(total=len(df)+1) as pbar:
            # for _ in p.imap_unordered(func, [group for idx, group in df.iterrows()], chunksize=chunksize):
            for _ in p.imap(func, _iter(df), chunksize=chunksize):
                out.append(_)
                pbar.update()
    return Series(out)

def _iter(df):
    for i in df.values:
        yield dict(zip(df.columns, i))

Series.parrale_apply = row_apply
DataFrame.parallel_apply = row_apply
DataFrameGroupBy.parallel_apply = p_apply
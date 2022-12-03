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
import tempfile, itertools, inspect
import os


tempfile._get_candidate_names = lambda: itertools.repeat('papply') 


def p_apply(df, func, *args, **kwargs):
    n_jobs = kwargs.get('n_workers', mp.cpu_count() - 3)
    chunksize = kwargs.get('chunksize', 50)
    out = []

    func_name = func.__name__
    with tempfile.NamedTemporaryFile(mode='w+', prefix='', suffix='.py', dir=os.getcwd()) as f:
        f.write(inspect.getsource(func))
        f.flush()

        import papply
        _func = getattr(papply, func_name)
        if inspect.getmodule(func).__name__ != '__main__':
            _func = func
        with mp.Pool(processes=n_jobs) as p:
            with tqdm(total=len(df)) as pbar:
                for _ in p.imap_unordered(_func, df, chunksize=chunksize):
                    out.append(_)
                    pbar.update()
    return out


def row_apply(df, func, *args, **kwargs):
    n_jobs = kwargs.get('n_workers', mp.cpu_count() - 3)
    chunksize = kwargs.get('chunksize', 50)
    out = []
    # func = functools.partial(func, *args, **kwargs)
    func_name = func.__name__
    with tempfile.NamedTemporaryFile(mode='w+', prefix='', suffix='.py', dir=os.getcwd()) as f:
        f.write(inspect.getsource(func))
        f.flush()

        import papply
        _func = getattr(papply, func_name)
        if inspect.getmodule(func).__name__ != '__main__':
            _func = func
        with mp.Pool(processes=n_jobs) as p:
            with tqdm(total=len(df)) as pbar:
                # for _ in p.imap_unordered(func, [group for idx, group in df.iterrows()], chunksize=chunksize):
                for _ in p.imap(_func, _iter(df), chunksize=chunksize):
                    out.append(_)
                    pbar.update()
    return Series(out)

def _iter(df):
    for i in df.values:
        yield dict(zip(df.columns, i))

Series.parallel_apply = row_apply
DataFrame.parallel_apply = row_apply
DataFrameGroupBy.parallel_apply = p_apply
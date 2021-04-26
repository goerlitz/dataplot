import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
import pandas as pd

thousand_format = FuncFormatter(lambda x, p: format(int(x), ','))


def plot_cat(df: pd.DataFrame, col: str, title: str = None, figsize=None):
    fig, ax = plt.subplots(figsize=figsize)
    
    df[col].value_counts().plot.barh(title=title, zorder=2, ax=ax)
    
    # add grid lines
    ax.xaxis.grid(True, linestyle='--')
    
    fig.tight_layout()
    
    return fig


def plot_cat2(df: pd.DataFrame, cols: list, title: str = None, figsize=None) -> Figure:
    """Plot categories with subsets."""
    fig, ax = plt.subplots(figsize=figsize)
    
    # get number of value combinations in columns and transform to matrix
    mat_df = df.groupby(cols).size().unstack(level=-1, fill_value=0)
    
    # sort rows and columns by sum (default is lexicographic)
    row_sorted = mat_df.sum(axis=1).sort_values(ascending=True).index
    col_sorted = mat_df.sum(axis=0).sort_values(ascending=True).index
    mat_df = mat_df.reindex(labels=row_sorted, columns=col_sorted)

    # create plot
    mat_df.plot.barh(stacked=True, title=title, zorder=2, ax=ax)
    
    # add grid lines
    ax.xaxis.grid(True, linestyle='--', zorder=1)
    ax.xaxis.set_major_formatter(thousand_format)
    
    ax.set_ylabel(None)
    
    fig.tight_layout()
    
    return fig

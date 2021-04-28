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


def plot_cat2(df: pd.DataFrame, cols: list, title: str = None, stacked=True, show=None, figsize=None, ax=None):
    """Plot categories with subsets."""

    # todo: check that we only get two columns

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    barwidth = 0.45 if stacked else 0.85

    # get number of value combinations in columns and transform to matrix
    mat_df = df.groupby(cols).size().unstack(level=-1, fill_value=0)

    # sort rows and columns by sum (default is lexicographic)
    row_sorted = mat_df.sum(axis=1).sort_values(ascending=True).index
    col_sorted = mat_df.sum(axis=0).sort_values(ascending=True).index

    # reorder rows and columns and plot
    mat_df = mat_df.reindex(labels=row_sorted, columns=col_sorted)
    mat_df.plot.barh(stacked=stacked, title=title, zorder=2, width=barwidth, ax=ax)

    # compute max value
    max_val = mat_df.max().max()
    # compute total count
    points = [p.get_bbox().get_points() for p in ax.patches]
    count = int(sum([p[1, 0] - p[0, 0] for p in points]))

    # add grid lines
    ax.xaxis.grid(True, linestyle='--', zorder=1)
    ax.xaxis.set_major_formatter(thousand_format)

    if show in ["value", "percent"]:
        """https://stackoverflow.com/questions/33179122/seaborn-countplot-with-frequencies"""
        for p in ax.patches:
            points = p.get_bbox().get_points()
            x, y = points[1, 0], points[:, 1].mean()
            halign = "right" if x / max_val > 0.1 else "left"

            if show == "value":
                s = f"{int(x)}"
            if show == "percent":
                s = f"{x / count:.1%}"

            ax.annotate(s, (x, y), ha=halign, va="center")

    ax.set_ylabel(None)

    if fig is not None:
        fig.tight_layout()

    return fig

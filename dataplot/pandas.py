import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd

thousand_format = FuncFormatter(lambda x, p: format(int(x), ','))


# countplot - count categories like sns.countplot (optionally by second dimension)
# requires long table format

def countplot(df: pd.DataFrame, col: str, by: str = None, title: str = None, stacked=True, annotate=None, figsize=None,
              ax=None) -> Figure:
    """Plot counts of categorial variables in given DataFrame."""

    # create new figure or use given Axis object for drawing
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None

    # define width of bars
    barwidth = 0.45 if (stacked or by is None) else 0.85

    if by is not None:
        # get number of value combinations in columns and transform to matrix
        mat_df = df.groupby([col, by]).size().unstack(level=-1, fill_value=0)

        # reorder rows and columns by sum (default is lexicographic)
        row_sorted = mat_df.sum(axis=1).sort_values(ascending=True).index
        col_sorted = mat_df.sum(axis=0).sort_values(ascending=True).index
        count_df = mat_df.reindex(labels=row_sorted, columns=col_sorted)
    else:
        count_df = df[col].value_counts(ascending=True).to_frame()

    count_df.plot.barh(stacked=stacked, title=title, zorder=2, width=barwidth, ax=ax)

    # compute max value
    max_val = count_df.max().max()
    # compute total count
    points = [p.get_bbox().get_points() for p in ax.patches]
    count = int(sum([p[1, 0] - p[0, 0] for p in points]))

    # add grid lines
    ax.xaxis.grid(True, linestyle='--', zorder=1)
    ax.xaxis.set_major_formatter(thousand_format)

    if annotate in ["value", "percent"]:
        """https://stackoverflow.com/questions/33179122/seaborn-countplot-with-frequencies"""
        for p in ax.patches:
            points = p.get_bbox().get_points()
            x, y = points[1, 0], points[:, 1].mean()

            color, halign = "white", "right"
            if x / max_val < 0.1:
                color, halign = p.get_fc(), "left"

            if annotate == "value":
                s = f"{int(x)}"
            if annotate == "percent":
                s = f"{x / count:.1%}"

            ax.annotate(s, (x, y), ha=halign, va="center", color=color)

    if by is None:
        ax.legend().remove()

    ax.set_ylabel(None)

    if fig is not None:
        fig.tight_layout()

    return fig


def histplot(df: pd.DataFrame, col: str, by: str = None, bins: int = 10, title: str = None, annotate=None, figsize=None,
             ax=None):
    """Plot histogram of values in specific column of given DataFrame."""

    if by is None:
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = None

        values_s = df[col]
        values_s.plot.hist(bins=bins, ax=ax, zorder=2)

        # add grid lines
        ax.yaxis.grid(True, linestyle=':', zorder=1)
        ax.yaxis.set_major_formatter(thousand_format)
        ax.xaxis.grid(True, linestyle='--', zorder=1)
        ax.xaxis.set_major_formatter(thousand_format)

        ax.set_title(title)
        ax.set_ylabel(None)

        if annotate == "mean":
            mean = values_s.mean()
            ax.axvline(mean, color="red", linestyle=":", lw=1.5)
            ax.annotate(f" mean={int(mean):,}", (mean, 0.85 * ax.get_ylim()[1]), ha="left", va="center", color="red",
                        size=rcParams['axes.labelsize'])

        return fig

    # count observations by facet (for ordering and indexing)
    counts_s = df[by].value_counts()

    facets = counts_s.index
    ncols = -int(-len(facets) ** 0.5 // 1)  # ceil of sqrt
    nrows = -(-len(facets) // ncols)  # ceil of facets/ncols

    # create new figure or use given Axis object for drawing
    if ax is None:
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharex=True, sharey=True, figsize=figsize)
    else:
        fig = None

    # todo: need calculate bin manually - otherwise they will be different for each facet

    for t, ax in zip(facets, axs.flat):
        values_s = df[lambda x: x[by] == t][col]
        values_s.plot.hist(bins=bins, ax=ax, zorder=2)

        # show title as wide as axes (needs a hack because does not work with ax.set_title())
        # https://stackoverflow.com/questions/40796117/how-do-i-make-the-width-of-the-title-box-span-the-entire-plot
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("top", size=0.20, pad=0)
        cax.get_xaxis().set_visible(False)
        cax.get_yaxis().set_visible(False)
        cax.set_facecolor('lightgrey')
        cax.annotate(f"{t} ({counts_s[t]:,})", (0.5, 0.45), ha="center", va="center", size=rcParams['axes.labelsize'])

        # add grid lines
        ax.yaxis.grid(True, linestyle=':', zorder=1)
        ax.yaxis.set_major_formatter(thousand_format)
        ax.xaxis.grid(True, linestyle='--', zorder=1)
        ax.xaxis.set_major_formatter(thousand_format)
        ax.set_ylabel(None)

    # show mean value (need to happen after everything was drawn and all axes scales adjusted)
    if annotate == "mean":
        for t, ax in zip(facets, axs.flat):
            values_s = df[lambda x: x[by] == t][col]

            mean = values_s.mean()
            ax.axvline(mean, color="red", linestyle=":", lw=1.5)
            # format mean value for int and float
            meanstr = f"{int(mean):,}" if pd.api.types.is_integer_dtype(values_s) else f"{mean:.1f}"
            ax.annotate(f" mean={meanstr}", (mean, 0.9 * ax.get_ylim()[1]), ha="left", va="top", color="red",
                        size=rcParams['axes.labelsize'])

    if fig is not None:
        fig.suptitle(title)
        fig.tight_layout()

    return fig

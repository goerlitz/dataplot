import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
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


"""Trois figures : l'écart actif, son attribution chaînée, l'accord des quatre méthodes."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]


def use_style():
    import matplotlib as mpl
    from cycler import cycler
    from matplotlib.ticker import FuncFormatter

    mpl.rcParams.update({
        "figure.dpi": 200, "savefig.dpi": 200, "figure.constrained_layout.use": True,
        "font.size": 11, "axes.titlesize": 12, "axes.prop_cycle": cycler(color=OKABE_ITO),
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linewidth": 0.5,
        "legend.frameon": False, "lines.linewidth": 1.7,
    })
    return FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def fig_active(monthly: pd.DataFrame, dest: Path) -> None:
    """Le portefeuille tactique contre sa politique, et l'écart actif cumulé à attribuer."""
    fr = use_style()
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, height_ratios=[2, 1])
    wp = (1 + monthly["rp"]).cumprod() * 100
    wb = (1 + monthly["rb"]).cumprod() * 100
    ax.plot(wp.index, wp, color=OKABE_ITO[0],
            label=f"Portefeuille tactique ({wp.iloc[-1]:,.0f} $)".replace(",", " "))
    ax.plot(wb.index, wb, color=OKABE_ITO[1],
            label=f"Politique 65/35 ({wb.iloc[-1]:,.0f} $)".replace(",", " "))
    ax.set_ylabel("Valeur de 100 $")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Le portefeuille tactique et sa politique : l'écart entre les deux est la matière à attribuer")
    actif = (wp / wb - 1) * 100
    ax2.plot(actif.index, actif, color=OKABE_ITO[2])
    ax2.axhline(0, color="0.4", linewidth=0.8)
    ax2.set_ylabel("Écart actif cumulé (%)", fontsize=9.5)
    ax2.yaxis.set_major_formatter(fr)
    fig.savefig(dest)
    plt.close(fig)


def fig_linked(linked: pd.DataFrame, actif_cumule: float, methode: str, dest: Path) -> None:
    """L'attribution chaînée cumulée : allocation + sélection + interaction = écart actif, exactement."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    cum = linked[["allocation", "selection", "interaction"]].cumsum() * 100
    for col, color in zip(["allocation", "selection", "interaction"], OKABE_ITO, strict=False):
        nom = {"selection": "sélection"}.get(col, col)
        ax.plot(cum.index, cum[col], color=color,
                label=f"{nom} ({cum[col].iloc[-1]:+.2f} pt)".replace(".", ","))
    total = cum.sum(axis=1)
    ax.plot(total.index, total, color="0.2", linewidth=2.0, linestyle="--",
            label=f"somme = écart actif ({actif_cumule * 100:+.2f} pt)".replace(".", ","))
    ax.axhline(0, color="0.5", linewidth=0.8)
    ax.set_ylabel("Effet cumulé chaîné (points de %)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9, loc="best")
    ax.set_title(f"Attribution chaînée ({methode}) : la somme des trois effets retombe sur l'écart actif")
    fig.savefig(dest)
    plt.close(fig)


LABELS_FR = {"allocation": "allocation", "selection": "sélection", "interaction": "interaction"}


def fig_methods(totaux: pd.DataFrame, actif_cumule: float, dest: Path) -> None:
    """Les quatre méthodes côte à côte : mêmes totaux par construction, chemins presque confondus."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    x = np.arange(len(totaux.index))
    width = 0.19
    for i, m in enumerate(totaux.columns):
        ax.bar(x + (i - 1.5) * width, totaux[m] * 100, width, label=m,
               color=OKABE_ITO[i])
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS_FR.get(i_, i_) for i_ in totaux.index])
    ax.axhline(0, color="0.3", linewidth=0.9)
    ax.set_ylabel("Effet total chaîné (points de %)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9)
    spread = float(((totaux.max(axis=1) - totaux.min(axis=1)) * 100).max())
    ax.set_title(f"Quatre chaînages, une histoire : au plus {spread:.2f} point d'écart "
                 f"sur un actif cumulé de {actif_cumule * 100:.1f}".replace(".", ","))
    fig.savefig(dest)
    plt.close(fig)

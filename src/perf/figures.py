"""Trois figures : l'écart actif, son attribution chaînée, l'accord des quatre méthodes."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gvf.style import OKABE_ITO, appliquer, formateur  # noqa: F401

# La palette et les réglages viennent de la couche partagée du portefeuille : les mêmes
# couleurs et la même virgule décimale dans tous les dépôts, corrigées à un seul endroit.

# les clés internes des colonnes ne sont pas des libellés de lecture : chaque chaînage porte le nom
# de son auteur et l'année de sa publication, comme dans la bibliographie du README
LABELS_FR = {"allocation": "Allocation", "selection": "Sélection", "interaction": "Interaction"}
NOMS_CHAINAGES = {"carino": "Cariño (1999)", "menchero": "Menchero (2000)",
                  "grap": "GRAP (1997)", "frongello": "Frongello (2002)"}


def use_style():
    """Les réglages communs, puis le formateur d'axe en français."""
    appliquer()
    return formateur()


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
    ax.set_ylabel("Valeur (dollars, base 100 au départ)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Le portefeuille tactique et sa politique : l'écart entre les deux est la matière à attribuer")
    actif = wp - wb                          # deux valeurs en dollars : leur écart l'est aussi
    ax2.plot(actif.index, actif, color=OKABE_ITO[2])
    ax2.axhline(0, color="0.4", linewidth=0.8)
    ax2.set_ylabel("Écart actif cumulé (dollars)", fontsize=9.5)
    ax2.yaxis.set_major_formatter(fr)
    fig.savefig(dest)
    plt.close(fig)


def fig_linked(linked: pd.DataFrame, actif_cumule: float, methode: str, dest: Path) -> None:
    """L'attribution chaînée cumulée : allocation + sélection + interaction = écart actif, exactement."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    cum = linked[["allocation", "selection", "interaction"]].cumsum() * 100
    for col, color in zip(["allocation", "selection", "interaction"], OKABE_ITO, strict=False):
        ax.plot(cum.index, cum[col], color=color,
                label=f"{LABELS_FR[col]} ({cum[col].iloc[-1]:+.2f} pp)".replace(".", ","))
    total = cum.sum(axis=1)
    # la somme n'égale l'écart actif qu'AU DERNIER POINT : le coefficient GRAP du mois i contient
    # les rendements du portefeuille et du repère POSTÉRIEURS à i, donc une somme partielle n'est
    # pas l'attribution arrêtée à cette date
    ax.plot(total.index, total, color="0.2", linewidth=2.0, linestyle="--",
            label=f"Somme des trois effets ({actif_cumule * 100:+.2f} pp au terme)".replace(".", ","))
    ax.axhline(0, color="0.5", linewidth=0.8)
    ax.set_ylabel("Effet cumulé chaîné (points de pourcentage)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9, loc="best")
    ax.set_title(f"Attribution chaînée, {methode} : la somme des trois effets retombe sur l'écart\nactif au dernier mois, et sur lui seul", fontsize=11.5)
    fig.savefig(dest)
    plt.close(fig)


def fig_methods(totaux: pd.DataFrame, actif_cumule: float, dest: Path) -> None:
    """Les quatre méthodes côte à côte : mêmes totaux par construction, chemins presque confondus."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    x = np.arange(len(totaux.index))
    width = 0.19
    # les NIVEAUX (jusqu'à 41,8 points) écrasaient les écarts à mesurer (0,83 point au plus) :
    # la figure trace donc l'écart de chaque méthode à la moyenne des quatre, en points de base.
    # Les niveaux restent dans la table du README, où ils sont à leur place.
    ecart_pb = (totaux.sub(totaux.mean(axis=1), axis=0)) * 1e4
    for i, m in enumerate(totaux.columns):
        ax.bar(x + (i - 1.5) * width, ecart_pb[m], width,
               label=NOMS_CHAINAGES.get(m, m), color=OKABE_ITO[i])
    ax.set_xticks(x)
    ax.set_xticklabels([LABELS_FR.get(i_, i_) for i_ in totaux.index])
    ax.set_xlabel("Effet de Brinson-Fachler")
    ax.axhline(0, color="0.3", linewidth=0.9)
    ax.set_ylabel("Écart à la moyenne des quatre méthodes\n(points de base)", fontsize=10)
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9)
    spread_pb = float(((totaux.max(axis=1) - totaux.min(axis=1)) * 1e4).max())
    ax.set_title(f"Quatre chaînages, un même verdict : au plus {spread_pb:.0f} points de base d'écart "
                 f"entre méthodes\nsur un écart actif cumulé de {actif_cumule * 1e4:.0f} points de "
                 f"base ; GRAP et Frongello se superposent exactement".replace(".", ","), fontsize=11)
    fig.savefig(dest)
    plt.close(fig)

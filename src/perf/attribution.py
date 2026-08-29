"""Brinson-Fachler à une période : allocation, sélection, interaction, par classe.

Brinson et Fachler (1985) découpent l'écart actif d'une période en trois morceaux :
l'allocation (avoir surpondéré une classe qui bat le benchmark TOTAL), la sélection
(avoir mieux fait que le benchmark DANS la classe, au poids du benchmark), et
l'interaction (le croisement des deux). La somme des trois, sommée sur les classes,
redonne EXACTEMENT Rp - Rb de la période : c'est l'identité qui fonde tout le dépôt.
"""

from __future__ import annotations

import pandas as pd


def brinson_fachler(panel: pd.DataFrame) -> pd.DataFrame:
    """Les effets par (mois, classe) : allocation, sélection, interaction (identité exacte).

    `panel` porte wp, wb, rp, rb par (mois, classe). Le rendement total du benchmark du
    mois entre dans l'effet d'allocation à la Brinson-Fachler.
    """
    out = panel.copy()
    rb_total = (panel["wb"] * panel["rb"]).groupby(level="mois").sum()
    rp_total = (panel["wp"] * panel["rp"]).groupby(level="mois").sum()
    rb_tot_aligned = rb_total.reindex(panel.index, level="mois")
    out["allocation"] = (panel["wp"] - panel["wb"]) * (panel["rb"] - rb_tot_aligned)
    out["selection"] = panel["wb"] * (panel["rp"] - panel["rb"])
    out["interaction"] = (panel["wp"] - panel["wb"]) * (panel["rp"] - panel["rb"])
    out.attrs["rp_total"] = rp_total
    out.attrs["rb_total"] = rb_total
    return out


def monthly_effects(effects: pd.DataFrame) -> pd.DataFrame:
    """Les effets agrégés par mois (sommés sur les classes) plus Rp, Rb et l'écart actif."""
    agg = effects.groupby(level="mois")[["allocation", "selection", "interaction"]].sum()
    agg["rp"] = effects.attrs["rp_total"]
    agg["rb"] = effects.attrs["rb_total"]
    agg["actif"] = agg["rp"] - agg["rb"]
    return agg

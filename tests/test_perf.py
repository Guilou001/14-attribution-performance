"""Les identités de l'attribution : chaque chaînage réconcilie à 1e-12, le GIPS au centième."""

import numpy as np
import pandas as pd
import pytest

from perf.attribution import brinson_fachler, monthly_effects
from perf.linking import METHODES
from perf.metrics import modified_dietz, mwr_irr, twr_chain


def _panel_aleatoire(seed: int = 0, n_mois: int = 60) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    mois = pd.period_range("2010-01", periods=n_mois, freq="M")
    rows = []
    for t in mois:
        tilt = rng.uniform(-0.08, 0.08)
        for c, wb in [("actions", 0.65), ("obligations", 0.35)]:
            wp = wb + (tilt if c == "actions" else -tilt)
            rb = rng.normal(0.005, 0.03)
            rp = rb + rng.normal(0.0, 0.01)
            rows.append({"mois": t, "classe": c, "wp": wp, "wb": wb, "rp": rp, "rb": rb})
    return pd.DataFrame(rows).set_index(["mois", "classe"])


def test_brinson_identity_each_period():
    # allocation + sélection + interaction = Rp - Rb, mois par mois, exactement
    panel = _panel_aleatoire()
    eff = brinson_fachler(panel)
    m = monthly_effects(eff)
    somme = m[["allocation", "selection", "interaction"]].sum(axis=1)
    assert np.allclose(somme, m["actif"], atol=1e-14)


@pytest.mark.parametrize("methode", list(METHODES))
def test_each_linking_reconciles_exactly(methode):
    # LA propriété : la somme des effets chaînés égale l'écart actif CUMULÉ, à 1e-12
    panel = _panel_aleatoire(seed=1, n_mois=120)
    m = monthly_effects(brinson_fachler(panel))
    eff = m[["allocation", "selection", "interaction"]]
    linked = METHODES[methode](eff, m["rp"], m["rb"])
    actif_cum = float((1 + m["rp"]).prod() - (1 + m["rb"]).prod())
    assert float(linked.to_numpy().sum()) == pytest.approx(actif_cum, abs=1e-12)


def test_linkings_degenerate_when_returns_are_equal():
    # portefeuille = benchmark : zéro effet, zéro écart, aucune division par zéro
    mois = pd.period_range("2020-01", periods=12, freq="M")
    r = pd.Series(np.full(12, 0.01), index=mois)
    eff = pd.DataFrame(0.0, index=mois, columns=["allocation", "selection", "interaction"])
    for name, fn in METHODES.items():
        linked = fn(eff, r, r.copy())
        assert float(linked.to_numpy().sum()) == pytest.approx(0.0, abs=1e-15), name


def test_grap_single_period_is_identity():
    mois = pd.period_range("2020-01", periods=1, freq="M")
    eff = pd.DataFrame({"allocation": [0.02], "selection": [0.01], "interaction": [0.0]}, index=mois)
    rp, rb = pd.Series([0.05], index=mois), pd.Series([0.02], index=mois)
    from perf.linking import grap

    linked = grap(eff, rp, rb)
    assert np.allclose(linked, eff)          # une seule période : rien à chaîner


def test_modified_dietz_gips_handbook_example():
    # GIPS Standards Handbook for Firms (2020), p. 103-104 : VB 100 000, -2 000 au jour 6,
    # +20 000 au jour 11, VE 135 000, mois de 30 jours -> 15,31 %
    r = modified_dietz(100_000.0, 135_000.0, [(6.0, -2_000.0), (11.0, 20_000.0)], 30.0)
    assert r * 100 == pytest.approx(15.31, abs=0.005)


def test_twr_chain_gips_handbook_example():
    # les deux sous-périodes revalorisées du même exemple : 7,06 % puis 8,00 %
    assert twr_chain([0.0706, 0.08]) == pytest.approx(1.0706 * 1.08 - 1.0, abs=1e-15)
    assert twr_chain([0.0706, 0.08]) * 100 == pytest.approx(15.62, abs=0.01)


def test_mwr_closed_forms():
    # sans flux : le taux interne est VE/VB - 1, exactement
    assert mwr_irr(100.0, 110.0, [], 30.0) == pytest.approx(0.10, abs=1e-10)
    # un flux au dernier jour ne travaille pas : r = (VE - F - VB)/VB
    assert mwr_irr(100.0, 130.0, [(30.0, 20.0)], 30.0) == pytest.approx(0.10, abs=1e-10)


def test_panel_weights_are_clean():
    from perf.data import CLASSES, POLICY_CLASS

    for c, mix in CLASSES.items():
        assert sum(mix.values()) == pytest.approx(1.0, abs=1e-12), c
    assert sum(POLICY_CLASS.values()) == pytest.approx(1.0)


def test_frongello_totals_equal_grap_totals_theorem():
    # théorème : en développant la récursion de Frongello, le coefficient TOTAL de chaque
    # effet A_t vaut exactement le facteur GRAP ; les chemins diffèrent, les totaux non
    from perf.linking import frongello, grap

    panel = _panel_aleatoire(seed=7, n_mois=90)
    m = monthly_effects(brinson_fachler(panel))
    eff = m[["allocation", "selection", "interaction"]]
    t_frong = frongello(eff, m["rp"], m["rb"]).sum()
    t_grap = grap(eff, m["rp"], m["rb"]).sum()
    assert np.allclose(t_frong, t_grap, atol=1e-12)

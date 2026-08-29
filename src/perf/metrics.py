"""Les trois rendements du GIPS : pondéré par le temps, Dietz modifié, pondéré par l'argent.

Le rendement pondéré par le temps (TWR) neutralise les flux du client : on revalorise le
portefeuille à chaque flux important et on enchaîne géométriquement les sous-périodes.
Le Dietz modifié l'approxime sans revalorisation, en pondérant chaque flux par la fraction
de période où il est investi. Le rendement pondéré par l'argent (MWR) est le taux interne
qui égalise valeurs et flux : c'est le rendement DU CLIENT, sensible au moment des flux.
Les trois sont validés sur l'exemple chiffré officiel du GIPS Standards Handbook for Firms
(CFA Institute, 2020, p. 103-105), jamais commité, cité valeur par valeur dans les tests.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq


def modified_dietz(vb: float, ve: float, flows: list[tuple[float, float]],
                   days_in_period: float) -> float:
    """Dietz modifié : (VE - VB - F) / (VB + somme des flux pondérés par le temps restant).

    `flows` : liste de (jour du flux, montant signé) ; le poids d'un flux du jour D vaut
    (CD - D)/CD, la fraction de la période où il travaille (convention GIPS).
    """
    f_total = sum(a for _, a in flows)
    weighted = sum(a * (days_in_period - d) / days_in_period for d, a in flows)
    return (ve - vb - f_total) / (vb + weighted)


def twr_chain(subperiod_returns: list[float]) -> float:
    """L'enchaînement géométrique des sous-périodes : (1+r1)(1+r2)... - 1."""
    return float(np.prod([1.0 + r for r in subperiod_returns]) - 1.0)


def mwr_irr(vb: float, ve: float, flows: list[tuple[float, float]],
            days_in_period: float) -> float:
    """Le taux interne de la période : VB(1+r) + somme f_i (1+r)^((CD-D_i)/CD) = VE."""
    def f(r: float) -> float:
        acc = vb * (1.0 + r)
        for d, a in flows:
            acc += a * (1.0 + r) ** ((days_in_period - d) / days_in_period)
        return acc - ve

    return float(brentq(f, -0.9999, 10.0, xtol=1e-12))

"""Les quatre chaînages multi-périodes : Cariño, Menchero, GRAP, Frongello.

Le problème qu'ils résolvent : les effets d'une période s'additionnent à Rp_t - Rb_t, mais
les écarts actifs mensuels ne s'additionnent pas à l'écart cumulé (les rendements se
composent). Chaque méthode redistribue les effets pour que leur somme redonne EXACTEMENT
(1+Rp_1)...(1+Rp_T) - (1+Rb_1)...(1+Rb_T), et chacune le fait par un chemin différent.
Formules recoupées contre R-Finance/PortfolioAttribution (MIT) et le papier de
Frongello (Journal of Performance Measurement, 2002).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _cum(r: np.ndarray) -> float:
    return float(np.prod(1.0 + r) - 1.0)


def carino(effects: pd.DataFrame, rp: pd.Series, rb: pd.Series) -> pd.DataFrame:
    """Chaînage logarithmique de Cariño (1999) : coefficients k_t / K."""
    rpc, rbc = _cum(rp.to_numpy()), _cum(rb.to_numpy())
    if rpc == rbc:
        big_k = 1.0 / (1.0 + rpc)
    else:
        big_k = (np.log1p(rpc) - np.log1p(rbc)) / (rpc - rbc)
    diff = rp - rb
    kt = pd.Series(np.where(diff == 0.0, 1.0 / (1.0 + rp),
                            (np.log1p(rp) - np.log1p(rb)) / diff.replace(0.0, np.nan)),
                   index=rp.index)
    return effects.mul(kt / big_k, axis=0)


def menchero(effects: pd.DataFrame, rp: pd.Series, rb: pd.Series) -> pd.DataFrame:
    """Chaînage optimisé de Menchero (2000) : coefficient commun M plus correctif alpha_t."""
    rpc, rbc = _cum(rp.to_numpy()), _cum(rb.to_numpy())
    t = len(rp)
    if rpc == rbc:
        m = (1.0 + rbc) ** ((t - 1) / t)
        alpha = pd.Series(0.0, index=rp.index)
    else:
        m = ((rpc - rbc) / t) / ((1.0 + rpc) ** (1.0 / t) - (1.0 + rbc) ** (1.0 / t))
        diff = rp - rb
        alpha = (rpc - rbc - m * diff.sum()) * diff / float((diff**2).sum())
    return effects.mul(m + alpha, axis=0)


def grap(effects: pd.DataFrame, rp: pd.Series, rb: pd.Series) -> pd.DataFrame:
    """Chaînage GRAP (1997) : le passé au portefeuille, le futur au benchmark."""
    rp_np, rb_np = rp.to_numpy(), rb.to_numpy()
    t = len(rp_np)
    g = np.empty(t)
    for i in range(t):
        g[i] = np.prod(1.0 + rp_np[:i]) * np.prod(1.0 + rb_np[i + 1:])
    return effects.mul(pd.Series(g, index=rp.index), axis=0)


def frongello(effects: pd.DataFrame, rp: pd.Series, rb: pd.Series) -> pd.DataFrame:
    """Chaînage récursif de Frongello (2002) : chaque mois porte l'histoire des ajustés."""
    rp_np, rb_np = rp.to_numpy(), rb.to_numpy()
    adj = effects.to_numpy(dtype=float).copy()
    for i in range(1, len(rp_np)):
        adj[i] = adj[i] * np.prod(1.0 + rp_np[:i]) + rb_np[i] * adj[:i].sum(axis=0)
    return pd.DataFrame(adj, index=effects.index, columns=effects.columns)


METHODES = {"carino": carino, "menchero": menchero, "grap": grap, "frongello": frongello}


def link_all(effects: pd.DataFrame, rp: pd.Series, rb: pd.Series) -> dict[str, pd.DataFrame]:
    """Les quatre chaînages ; chacun DOIT sommer à l'écart actif cumulé (testé à 1e-12)."""
    return {name: fn(effects, rp, rb) for name, fn in METHODES.items()}

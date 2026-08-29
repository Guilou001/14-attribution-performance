"""Les six FNB du dépôt 03 et le portefeuille tactique déclaré contre sa politique.

Le banc d'essai : un portefeuille de deux classes (actions, obligations) dont la politique
est celle du dépôt 03 (65/35, mélanges internes fixes), et un portefeuille tactique qui
s'écarte de la politique par une règle déclarée de momentum 12-1 : il surpondère la classe
la mieux classée (allocation) ET, dans chaque classe, le FNB le mieux classé (sélection).
Les deux effets de Brinson existent donc par construction, sans données nouvelles.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw")

CLASSES: dict[str, dict[str, float]] = {
    # mélanges internes de la POLITIQUE, en poids de classe (somme 1 par classe)
    "actions": {"XIU.TO": 0.25 / 0.65, "XSP.TO": 0.20 / 0.65, "XIN.TO": 0.15 / 0.65, "XRE.TO": 0.05 / 0.65},
    "obligations": {"XBB.TO": 0.25 / 0.35, "XSB.TO": 0.10 / 0.35},
}
POLICY_CLASS = {"actions": 0.65, "obligations": 0.35}
TILT_CLASSE = 0.05        # surpondération de la classe gagnante au momentum (déclaré)
TILT_INTRA = 0.10         # surpondération du FNB gagnant DANS sa classe (déclaré)


def fetch() -> None:
    """Cours ajustés des six FNB (yfinance, usage personnel, jamais commités)."""
    import yfinance as yf

    RAW.mkdir(parents=True, exist_ok=True)
    tickers = [t for c in CLASSES.values() for t in c]
    px = yf.download(tickers, period="max", auto_adjust=True, progress=False)["Close"]
    px.to_csv(RAW / "prix_fnb.csv")


def monthly_returns() -> pd.DataFrame:
    """Rendements mensuels des six FNB, échantillon commun."""
    px = pd.read_csv(RAW / "prix_fnb.csv", index_col=0, parse_dates=True)
    return px.resample("ME").last().pct_change().dropna(how="any")


def build_panel(rets: pd.DataFrame) -> pd.DataFrame:
    """Le panel mensuel : poids et rendements du portefeuille et de la politique, par classe.

    Le momentum 12-1 (rendement cumulé des mois t-12 à t-2) est calculé au DÉBUT du mois t :
    aucune information du mois attribué n'entre dans les poids. Une ligne par (mois, classe)
    avec wp, wb, rp, rb ; les rendements de classe sont les moyennes pondérées des FNB.
    """
    mom = (1.0 + rets).rolling(11).apply(np.prod, raw=True).shift(2) - 1.0
    rows = []
    for t in rets.index:
        if not np.isfinite(mom.loc[t].to_numpy()).all():
            continue
        # classement des classes par le momentum de leur composite de politique
        mom_classe = {c: float(sum(w * mom.loc[t, tk] for tk, w in CLASSES[c].items()))
                      for c in CLASSES}
        gagnante = max(mom_classe, key=mom_classe.get)
        for c, mix in CLASSES.items():
            wb = POLICY_CLASS[c]
            wp = wb + (TILT_CLASSE if c == gagnante else -TILT_CLASSE)
            # à l'intérieur de la classe : le FNB au meilleur momentum est surpondéré
            best = max(mix, key=lambda tk: float(mom.loc[t, tk]))
            worst = min(mix, key=lambda tk: float(mom.loc[t, tk]))
            mix_p = dict(mix)
            shift = min(TILT_INTRA, mix_p[worst])          # jamais de poids négatif
            mix_p[best] += shift
            mix_p[worst] -= shift
            rb = float(sum(w * rets.loc[t, tk] for tk, w in mix.items()))
            rp = float(sum(w * rets.loc[t, tk] for tk, w in mix_p.items()))
            rows.append({"mois": t, "classe": c, "wp": wp, "wb": wb, "rp": rp, "rb": rb})
    return pd.DataFrame(rows).set_index(["mois", "classe"])

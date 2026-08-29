"""Ligne de commande : télécharger, attribuer et chaîner, valider les rendements GIPS."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(help="Attribution de performance : Brinson-Fachler mensuel, quatre chaînages "
                       "multi-périodes réconciliés exactement, TWR/MWR/Dietz validés sur les "
                       "exemples du GIPS Handbook 2020.")


@app.callback()
def main() -> None:
    """Sous-commandes nommées."""


@app.command()
def fetch() -> None:
    """Les six FNB du dépôt 03 (yfinance, usage personnel)."""
    from perf import data

    data.fetch()
    r = data.monthly_returns()
    typer.echo(f"rendements : {len(r)} mois, {r.index[0]:%Y-%m} -> {r.index[-1]:%Y-%m}")


@app.command()
def attribute(out: Path = Path("results")) -> None:
    """Le banc complet : panel tactique, effets mensuels, quatre chaînages, trois figures."""
    import pandas as pd

    from perf import attribution, data, figures, linking

    rets = data.monthly_returns()
    panel = data.build_panel(rets)
    effects = attribution.brinson_fachler(panel)
    monthly = attribution.monthly_effects(effects)

    tables, figs = out / "tables", out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)
    monthly.round(6).to_csv(tables / "effets_mensuels.csv")

    eff_m = monthly[["allocation", "selection", "interaction"]]
    linked = linking.link_all(eff_m, monthly["rp"], monthly["rb"])
    actif_cum = float((1 + monthly["rp"]).prod() - (1 + monthly["rb"]).prod())

    totaux = pd.DataFrame({name: df.sum() for name, df in linked.items()})
    totaux.round(6).to_csv(tables / "totaux_par_methode.csv")
    residus = {name: float(df.to_numpy().sum() - actif_cum) for name, df in linked.items()}
    pd.DataFrame([residus]).to_csv(tables / "residus_reconciliation.csv", index=False)

    # l'écart maximal entre méthodes, composante par composante (le verdict du dépôt)
    spread = (totaux.max(axis=1) - totaux.min(axis=1)) * 1e4
    spread.round(2).to_csv(tables / "ecart_entre_methodes_pb.csv")

    figures.fig_active(monthly, figs / "actif.png")
    figures.fig_linked(linked["grap"], actif_cum, figures.NOMS_CHAINAGES["grap"], figs / "attribution_chainee.png")
    figures.fig_methods(totaux, actif_cum, figs / "quatre_methodes.png")

    typer.echo(f"{len(monthly)} mois ; écart actif cumulé {actif_cum * 100:+.2f} pt ; "
               f"résidu max de réconciliation {max(abs(v) for v in residus.values()):.2e}")
    typer.echo("totaux chaînés (points de pourcentage) :")
    typer.echo((totaux * 100).round(3).to_string())
    typer.echo(f"écart max entre méthodes : {float(spread.max()):.1f} pb "
               f"({spread.idxmax()})")


@app.command()
def gips(out: Path = Path("results")) -> None:
    """L'exemple chiffré du GIPS Handbook 2020 (p. 103-105) refait par les trois moteurs."""
    import pandas as pd

    from perf.metrics import modified_dietz, mwr_irr, twr_chain

    vb, ve = 100_000.0, 135_000.0
    flows = [(6.0, -2_000.0), (11.0, 20_000.0)]
    dietz = modified_dietz(vb, ve, flows, 30.0)
    # le TWR revalorise au grand flux (jour 11, valeur 125 000 $ APRÈS l'apport) : la
    # sous-période 1 est elle-même un Dietz (7 000/99 091, le Handbook l'imprime), la 2 vaut 8 %
    sp1 = modified_dietz(100_000.0, 125_000.0, flows, 11.0)
    twr = twr_chain([sp1, 0.08])
    mwr = mwr_irr(vb, ve, flows, 30.0)
    table = pd.DataFrame([
        {"mesure": "Dietz modifié", "valeur_pct": dietz * 100, "handbook": 15.31},
        {"mesure": "sous-période 1 (Dietz au jour 11)", "valeur_pct": sp1 * 100, "handbook": 7.06},
        {"mesure": "TWR (chaînage des deux sous-périodes)", "valeur_pct": twr * 100, "handbook": 15.63},
        {"mesure": "MWR (taux interne du mois)", "valeur_pct": mwr * 100, "handbook": float("nan")},
    ])
    (out / "tables").mkdir(parents=True, exist_ok=True)
    table.round(4).to_csv(out / "tables" / "gips_exemples.csv", index=False)
    typer.echo(table.round(3).to_string(index=False))


if __name__ == "__main__":
    app()

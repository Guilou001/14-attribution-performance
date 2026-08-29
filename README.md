# L'attribution de performance qui tombe juste : quatre chaînages, un exemple GIPS, zéro pouce

Les effets de Brinson d'un mois s'additionnent exactement ; ceux de vingt-trois ans, non.
Ce dépôt implémente les quatre méthodes de chaînage qui réconcilient l'attribution
multi-périodes, exige la réconciliation à 1e-12 près par test, et valide les trois
rendements du GIPS sur l'exemple chiffré officiel du Handbook. *English summary below.*

## En bref

1. **Les quatre chaînages racontent la même histoire.** Sur 274 mois d'un portefeuille
   tactique contre sa politique (+58,74 points d'écart actif cumulé), Cariño, Menchero,
   GRAP et Frongello attribuent l'allocation entre +16,11 et +16,93 points et la sélection
   entre +41,01 et +41,79 : au plus 0,83 point d'écart entre méthodes, soit 1,4 % du total
   à expliquer. Le choix de la méthode est un choix de présentation, pas de verdict.
   (Mesuré.)
2. **GRAP et Frongello ont des totaux EXACTEMENT égaux, et c'est un théorème.** En
   développant la récursion de Frongello, le coefficient total de l'effet du mois t vaut
   le facteur GRAP (le passé au portefeuille, le futur au benchmark) : les chemins mensuels
   diffèrent, les totaux coïncident à 1e-12 (testé). (Mesuré et démontré.)
3. **Chaque méthode réconcilie exactement, ou le test échoue.** La somme des effets
   chaînés doit égaler (1+Rp_1)...(1+Rp_T) - (1+Rb_1)...(1+Rb_T) : résidu maximal observé
   4,8e-15. Et les trois rendements réglementaires (TWR, Dietz modifié, MWR) retombent sur
   l'exemple du GIPS Standards Handbook for Firms 2020 : 15,31 % et 15,63 % (p. 103-105,
   rapporté), au centième. (Mesuré.)

## La question

Un comité de placement lit « l'allocation a rapporté +2,1 points cette année ». Or ce
chiffre n'existe pas naturellement : les effets mensuels de Brinson s'additionnent à
l'écart actif du mois, mais leur somme sur l'année ne retombe PAS sur l'écart actif
annuel, car les rendements se composent. Quatre méthodes concurrentes redistribuent les
effets pour forcer la réconciliation. Donnent-elles le même verdict, ou l'attribution
dépend-elle de la méthode ?

## Le banc d'essai (données du dépôt 03, règle déclarée)

Aucune donnée nouvelle : les six FNB canadiens du dépôt 03 (Yahoo, usage personnel,
jamais commités), 274 mois de novembre 2003 à août 2026. La politique : 65 % actions
(XIU, XSP, XIN, XRE en mélange fixe), 35 % obligations (XBB, XSB). Le portefeuille
tactique s'en écarte par une règle déclarée de momentum 12-1 (le rendement cumulé des
mois t-12 à t-2, calculé au début du mois : rien du mois attribué n'entre dans les
poids) : +5 points à la classe gagnante (matière à ALLOCATION), +10 points de poids de
classe au FNB gagnant dans chaque classe (matière à SÉLECTION). Résultat brut : 7,54 %
par an contre 6,99 % pour la politique, +0,56 point par an AVANT tout coût de
transaction (déclaré ; la règle tourne chaque mois, les coûts mangeraient une partie).

## Volet 1 : Brinson-Fachler, l'identité de départ

L'attribution de Brinson et Fachler (1985) découpe l'écart actif d'UNE période en trois :
l'allocation, récompense d'avoir surpondéré une classe qui bat le benchmark total ; la
sélection, récompense d'avoir mieux fait que le benchmark dans la classe ; l'interaction,
le croisement des deux. La somme des trois, sommée sur les classes, égale Rp - Rb du mois,
exactement (testé à 1e-14 sur panels aléatoires).

![Actif](results/figures/actif.png)

**Comment lire cette figure.** En haut, 100 $ dans le portefeuille tactique et dans la
politique ; en bas, l'écart cumulé entre les deux : +58,74 points en fin de période.
C'est ce trait vert que l'attribution doit expliquer morceau par morceau.

## Volet 2 : les quatre chaînages (mesuré, `results/tables/totaux_par_methode.csv`)

Chaque méthode multiplie l'effet du mois t par un coefficient qui force la somme totale
à retomber sur l'écart actif cumulé. Cariño (1999) passe par les logarithmes ; Menchero
(2000) par un coefficient commun plus un correctif proportionnel à l'écart du mois ;
GRAP (1997) capitalise le passé au portefeuille et le futur au benchmark ; Frongello
(2002) par une récursion qui porte l'histoire des effets déjà ajustés. Les formules sont
recoupées contre l'implémentation de référence R-Finance/PortfolioAttribution (MIT).

| Effet total chaîné (pt) | Cariño | Menchero | GRAP | Frongello |
|---|---|---|---|---|
| Allocation | +16,38 | +16,93 | +16,11 | +16,11 |
| Sélection | +41,58 | +41,01 | +41,79 | +41,79 |
| Interaction | +0,78 | +0,79 | +0,85 | +0,85 |
| **Somme** | **+58,74** | **+58,74** | **+58,74** | **+58,74** |

**Lecture guidée.** Les sommes sont identiques par construction (résidu maximal 4,8e-15,
table `residus_reconciliation.csv`) ; le verdict, lui, ne dépend pas de la méthode : la
sélection intra-classe explique 70 % de la valeur ajoutée quel que soit le chaînage, et
l'écart maximal entre méthodes (0,83 point, sur l'allocation) vaut 1,4 % du total à
expliquer. Les colonnes GRAP et Frongello sont identiques ligne à ligne : c'est le
théorème du dépôt (test `test_frongello_totals_equal_grap_totals_theorem`), une identité
algébrique que les deux papiers ne signalent pas l'un pour l'autre.

![Quatre méthodes](results/figures/quatre_methodes.png)

**Comment lire cette figure.** Une barre par méthode et par effet. Si les quatre barres
d'un groupe avaient des hauteurs visiblement différentes, le choix de la méthode
changerait le message au comité ; elles sont presque confondues.

![Attribution chaînée](results/figures/attribution_chainee.png)

**Comment lire cette figure.** Le chemin cumulé des trois effets chaînés (GRAP). La
sélection (jaune) fait le gros du travail et accélère après 2020 ; l'allocation (bleu)
donne et reprend (elle perd 17 points entre 2018 et 2021 : surpondérer la classe
momentum a coûté cher dans les retournements) ; l'interaction reste marginale. La somme
(tirets) retombe exactement sur l'écart actif de la figure précédente.

## Volet 3 : TWR, Dietz modifié, MWR, validés sur l'exemple officiel

Le rendement pondéré par le temps (TWR), la norme GIPS pour juger le GESTIONNAIRE,
neutralise les flux du client en revalorisant à chaque flux important et en enchaînant
les sous-périodes. Le Dietz modifié l'approxime sans revalorisation, chaque flux pondéré
par la fraction de période où il travaille. Le rendement pondéré par l'argent (MWR), le
taux interne, juge l'EXPÉRIENCE DU CLIENT, moment des flux compris.

Exemple du GIPS Standards Handbook for Firms 2020, p. 103-105 (rapporté ; PDF public
chez CFA Institute, jamais commité) : valeur initiale 100 000 $, retrait de 2 000 $ au
jour 6, apport de 20 000 $ au jour 11, valeur finale 135 000 $, mois de 30 jours.

| Mesure | Notre moteur | Handbook |
|---|---|---|
| Dietz modifié | 15,306 % | 15,31 % |
| TWR (sous-périodes 7,06 % et 8,00 %) | 15,625 % | 15,63 % |
| MWR (taux interne du mois) | 15,349 % | non imprimé |

**Lecture guidée.** Le Dietz au denominateur : 100 000 - 2 000 x 24/30 + 20 000 x 19/30
= 111 067 $ ; gain de 17 000 $ ; 15,31 %. Le TWR enchaîne les deux sous-périodes
revalorisées du Handbook (l'écart au 15,63 imprimé vient de leurs décimales non
publiées, déclaré). Le MWR tombe entre les deux : l'apport de 20 000 $ est arrivé avant
la bonne sous-période, le client a fait un peu mieux que le Dietz ne le dit.

## Reproduire

```bash
uv sync --locked --all-extras
uv run pytest           # 12 tests : identités exactes, GIPS au centième, théorème GRAP-Frongello
uv run perf fetch       # six FNB (yfinance)
uv run perf attribute   # panel, effets, quatre chaînages, trois figures
uv run perf gips        # l'exemple du Handbook refait par les trois moteurs
```

## Limites, avec statut

1. **La règle tactique est un prétexte.** Le momentum 12-1 à tilts fixes sert à générer
   de la matière à attribuer, pas à recommander une stratégie ; ses +0,56 point par an
   sont AVANT coûts de transaction et hors taxes (déclaré). Le verdict du dépôt porte
   sur les méthodes, pas sur la règle.
2. **Deux niveaux, six actifs.** L'attribution réelle d'une caisse porte des dizaines de
   classes, des devises et des dérivés ; l'effet devise (Karnosky-Singer) n'est pas
   traité, déclaré comme suite naturelle avec le dépôt 13.
3. **Les tables du papier de Frongello (JPM 2002) ne sont pas répliquées** : le site qui
   l'héberge a un certificat expiré ; la contre-vérification passe par l'implémentation
   R de référence et par les identités exactes. (Déclaré ; le papier GRAP original de
   1997 est introuvable en libre, statut non trouvé, la formule vient de la référence R
   et de Bacon.)
4. **Le Handbook n'imprime pas le MWR de son propre exemple** : notre 15,35 % est calculé
   par le moteur testé sur formes fermées, pas recopié. (Mesuré.)
5. **Aucune prétention de conformité GIPS.** GIPS est une marque de CFA Institute ; ce
   dépôt implémente des méthodes de calcul à des fins pédagogiques et ne revendique
   aucune conformité. (Déclaré.)

## Références

- Brinson, G. P. et N. Fachler (1985), « Measuring non-US equity portfolio performance »,
  *Journal of Portfolio Management*.
- Cariño, D. (1999), « Combining attribution effects over time », *Journal of
  Performance Measurement*.
- Menchero, J. (2000), « An optimized approach to linking attribution effects »,
  *Journal of Performance Measurement*.
- Frongello, A. (2002), « Linking single period attribution results », *Journal of
  Performance Measurement* ; comparatif JPM printemps 2002.
- GRAP (1997), Groupe de Réflexion en Attribution de Performance, Paris (non trouvé en
  libre ; formule via R-Finance/PortfolioAttribution et Bacon 2008).
- CFA Institute (2020), *GIPS Standards Handbook for Firms*, exemples p. 103-105.
- R-Finance/PortfolioAttribution (MIT) : implémentation de référence des chaînages.

## English summary

Single-period Brinson-Fachler effects sum exactly to the period's active return, but not
across periods. This repo implements the four linking algorithms that reconcile
multi-period attribution (Cariño, Menchero, GRAP, Frongello), cross-checked against the
R-Finance/PortfolioAttribution reference (MIT), and REQUIRES exact reconciliation by
test: the linked effects must sum to the cumulative active return within 1e-12 (max
observed residual 4.8e-15). Test bench: a declared 12-1 momentum tilt portfolio vs the
repo-03 65/35 policy, 274 months (2003-11 to 2026-08), +58.74 pts cumulative active
return (+0.56 pt/yr, BEFORE costs, declared). Verdict: the four methods agree, at most
0.83 pt apart (1.4 % of the total); selection explains ~70 % under every linking; and
GRAP and Frongello produce IDENTICAL totals, which we show is an algebraic theorem
(expanding Frongello's recursion yields the GRAP factors) and test to 1e-12. GIPS-style
returns (TWR, Modified Dietz, MWR) are validated to the cent on the official GIPS
Standards Handbook 2020 worked example (pp. 103-105): 15.31 % and 15.63 %. No GIPS
compliance claimed; 12 closed-form tests, no network.

## Licence et citation

Code sous licence MIT ; rapport et figures CC BY 4.0. Données : Yahoo Finance (usage
personnel). Le Handbook (c) CFA Institute est cité, jamais redistribué. Citer via
`CITATION.cff`.

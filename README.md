# T cell modular nomenclature generator

Converts flow-cytometry-style categorical marker data (+ / - / not measured)
into the modular T cell nomenclature proposed in:

> Masopust et al., "Guidelines for T cell nomenclature", *Nat Rev Immunol* (2026).

Instead of a single subset label (e.g. "TRM"), the nomenclature composes a
name from independently-evidenced slots: **Lineage · Function · Migration ·
Differentiation state · Antigen status**. Each slot is only filled in when
there is direct evidence for it — a slot with no supporting marker data is
left blank (or `U` for migration's explicit "unknown" code), never guessed.
This "silence is a legitimate result" principle is the core design
constraint of this program; see [Design principles](#design-principles).

## Install

Python 3.9+, no third-party dependencies for the core program.
`pytest` is only needed to run the test suite:

```
pip install pytest
```

## Usage

### Interactive mode

```
python main.py
```

Walks through one T cell population at a time: label/location/lineage/
function, then +/-/blank for each of the 13 markers the program understands,
then optional migration-subscript evidence, differentiation override, and
antigen status. Prints the nomenclature string plus a full rationale for
every slot, and can save everything to CSV at the end.

### CSV batch mode

```
python main.py --csv input.csv --out output.csv
```

`input.csv` columns (all optional, matched case-insensitively, ignoring
spaces/underscores/hyphens):

- Marker columns: `CD62L`, `CCR7`, `CD45RA`, `CD45RO`, `CD95`, `CD69`,
  `CD25`, `PD1`/`PD-1`, `TOX`, `TCF1`, `SLAMF6`, `TIM3`, `CD101` — values
  `+` / `-` / blank (or `NA`). Missing columns are treated as not-measured
  for every row.
- Metadata columns: `label`, `location`, `lineage`, `function`,
  `migration_evidence` (`B`/`W`/`R`), `migration_evidence_note`,
  `differentiation_override` (e.g. `G`), `differentiation_override_note`,
  `antigen_status` (`+`/`0`/blank), `antigen_note`.

Output = input columns + `nomenclature`, `migration`, `migration_subscript`,
`differentiation`, `differentiation_subscript`, `antigen`, `rationale`.

## Nomenclature format

```
[Location] [Lineage] T[Function][Migration][MigSub][Differentiation][DiffSub][Antigen]
```

`Location` is not one of the paper's 5 module slots but is supported as an
optional free-text prefix (matches the worked examples this program was
validated against). Examples:

- `CD8+ TDRXp+` — CD8+ lineage, Disseminated + Resident, eXhausted-progenitor, persistent antigen
- `Liver CD8+ TD` — liver-derived CD8+, Disseminated, differentiation state unknown

## Slot logic

### Migration (S / D / U)

| Rule | Code |
|---|---|
| CD62L+ AND CCR7+ | `S` |
| CD62L- and/or CCR7- (at least one confirmed negative) | `D` |
| CD62L and CCR7 both not measured | `U` |
| Only one of CD62L/CCR7 measured, and it's positive (can't confirm S or D) | `U` (extension beyond the paper's literal wording — see code comment in `nomenclature/slots.py`) |

Migration subscript `B`/`W`/`R` only applies when migration = `D`, and is
**never** inferred from markers — it requires an explicit user-supplied
evidence code + justification, because the subscript is itself a claim
about additional assay evidence (recirculation study, parabiosis, etc.).

### Differentiation (N / A / M / X / G)

Checked in priority order **X > N > A > M** (if input data is contradictory
and matches more than one, this is flagged in the rationale as a conflict
warning rather than silently resolved). Every required "negative" marker
must be *explicitly measured* negative — a missing marker never satisfies a
negative condition.

| State | Requires |
|---|---|
| `X` Exhausted | PD-1+ AND TOX+ |
| ` `↳ `p` progenitor | TCF1+, SLAMF6+, TIM3- |
| ` `↳ `t` terminal | TCF1-, SLAMF6-, TIM3+, CD101+ |
| `N` Naive | CCR7+ AND (CD45RA+ or CD45RO-) AND CD95- |
| `A` Activated | (CD69+ or CD25+) AND PD-1- AND TOX- |
| `M` Memory | (CD45RO+ or CD45RA-) AND CD69- AND CD25- |
| `G` Anergic | never marker-derived — user override only |
| none of the above | left blank, rationale explains what's missing |

### Antigen status (+ / 0 / blank)

Never inferred from markers. User-asserted only, with an optional
justification note.

## Design principles

1. **Over-claiming is the failure mode this program is built to avoid.** If
   a marker wasn't measured, its slot stays blank/`U` — never guessed.
2. Migration subscripts (B/W/R) are claims about additional assay evidence;
   they require explicit user input, never auto-derived from CD62L/CCR7.
3. Antigen status is never marker-derived — always a direct user assertion.
4. Every slot is optional; a bare lineage alone is a valid, complete run.

## Scope / out of scope

This MVP only handles categorical flow-cytometry-style marker calls
(`+`/`-`/not measured). Continuous scRNA-seq expression values would need a
threshold/binarization step before reuse of this logic — noted as a TODO in
`nomenclature/models.py` but not implemented here. Likewise, full automatic
mapping to every named subset in the paper's Tables 1-6 (TCM, TEM, TPEX,
...) is out of scope; this program implements the core marker rules only.

## Tests

```
python -m pytest tests/ -v
```

Two tests reproduce the worked examples given in the project brief
(representative of the paper's Table 7 style); the rest are additional
logic-coverage tests written for this implementation.

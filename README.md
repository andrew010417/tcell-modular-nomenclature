# T cell modular nomenclature generator

Converts flow-cytometry-style categorical marker data (+ / - / not measured)
into the modular T cell nomenclature proposed in:

> Masopust et al., "Guidelines for T cell nomenclature", *Nat Rev Immunol* (2026).

Instead of a single subset label (e.g. "TRM"), the nomenclature composes a
name from independently-evidenced slots: **Lineage · Function · Migration ·
Differentiation state · Antigen status**. Each slot is only filled in when
there is direct evidence for it — a slot with no supporting marker data is
left blank, never guessed. `U` (migration's explicit "unknown" code) is no
exception: per the paper, it is only ever produced by an explicit user
assertion, not defaulted to when data is simply missing (see
[Migration](#migration-s--d--u)). This "silence is a legitimate result"
principle is the core design constraint of this program; see
[Design principles](#design-principles).

This implementation has been checked line-by-line against the primary
source — Masopust et al., "Guidelines for T cell nomenclature", *Nat Rev
Immunol* 26:298–313 (2026) — including its Fig. 1 module definitions and
Table 7 worked examples (several of which are reproduced verbatim in
`tests/test_table7.py`).

## Install

Python 3.9+, no third-party dependencies for the core program.
`pytest` is only needed to run the test suite:

```
pip install pytest
```

## Quickstart (try it in under a minute)

Don't type anything yet — just run the bundled example and see what comes out:

```
python main.py --csv examples/template.csv --out examples/template_output.csv
```

Open `examples/template_output.csv`. Two rows should read:

- `example_naive` → `CD4+ TSN`
- `example_exhausted_progenitor` → `CD8+ TDRXp+`

Once that makes sense, open [`examples/template.csv`](examples/template.csv),
duplicate the blank `my_sample_1` row, fill in whatever markers/columns you
actually have (leave the rest blank), and re-run the command above. See
[`examples/README.md`](examples/README.md) for what every column means.

If you'd rather be walked through it question-by-question instead of editing
a CSV, use interactive mode instead — see below.

## Usage

### Interactive mode

```
python main.py
```

Walks through one T cell population at a time. Markers are asked in
logical groups (migration, naive/memory, activation, exhaustion, exhaustion
subtype), each with a short explanation of what the group determines and
what each marker means, so you don't need to already have the marker panel
memorized. For every marker: type `+`, `-`, or just press Enter if it wasn't
measured — nothing is ever guessed from a blank answer.

After each population, you get the nomenclature string plus a slot-by-slot
breakdown and a full audit trail explaining why each slot was called the
way it was. You can add more populations and save everything to CSV at the
end.

### CSV batch mode

```
python main.py --csv input.csv --out output.csv
```

Easiest way to start: copy [`examples/template.csv`](examples/template.csv)
and edit it — see [`examples/README.md`](examples/README.md) for a full
column-by-column reference.

`input.csv` columns (all optional, matched case-insensitively, ignoring
spaces/underscores/hyphens):

- Marker columns: `CD62L`, `CCR7`, `CD45RA`, `CD45RO`, `CD95`, `CD69`,
  `CD25`, `PD1`/`PD-1`, `TOX`, `TCF1`, `SLAMF6`, `TIM3`, `CD101`, `KLRG1`,
  `CD127`, `CD27` — values `+` / `-` / blank (or `NA`). Missing columns are
  treated as not-measured for every row.
- Metadata columns: `label`, `location`, `lineage`, `function`,
  `migration_override` (`S`/`D`/`U`, explicit assertion — see
  [Migration](#migration-s--d--u)), `migration_override_note`,
  `migration_evidence` (`B`/`W`/`R`), `migration_evidence_note`,
  `differentiation_override` (e.g. `G`), `differentiation_override_note`,
  `antigen_status` (`+`/`0`/blank), `antigen_note`.

Output = input columns + `nomenclature`, `migration`, `migration_subscript`,
`differentiation`, `differentiation_subscript`, `antigen`, `rationale`.

## What do these markers mean?

If the marker abbreviations aren't already familiar, here's what each one
is and which slot it feeds into:

| Marker | What it is | Feeds into |
|---|---|---|
| `CD62L` | L-selectin — needed to enter lymph nodes through HEVs | Migration |
| `CCR7` | Chemokine receptor that guides homing to lymph nodes | Migration |
| `CD45RA` | Isoform typically seen on naive (and some terminally-differentiated) T cells | Differentiation (N) |
| `CD45RO` | Isoform typically seen on memory T cells | Differentiation (N/M) |
| `CD95` | Fas — separates true naive cells from stem-cell memory cells | Differentiation (N) |
| `CD69` | Early marker of recent TCR/cytokine activation | Differentiation (A) |
| `CD25` | IL-2 receptor alpha chain, induced by recent activation | Differentiation (A) |
| `PD1` | Inhibitory receptor induced by chronic antigen stimulation | Differentiation (X) |
| `TOX` | Transcription factor that drives the exhaustion program | Differentiation (X) |
| `TCF1` | Maintains stem-like/progenitor exhausted cells | Exhaustion subtype (p) |
| `SLAMF6` | Surface marker associated with progenitor exhausted cells | Exhaustion subtype (p) |
| `TIM3` | Surface marker associated with terminally exhausted cells | Exhaustion subtype (t) |
| `CD101` | Surface marker associated with terminally exhausted cells | Exhaustion subtype (t) |
| `KLRG1` | Marks short-lived terminal effector cells (SLEC) | Activated subtype (t) |
| `CD127` | IL-7 receptor; lost on SLEC, retained on memory-precursor (MPEC) cells | Activated subtype (p/t) |
| `CD27` | Co-stimulatory receptor retained on MPEC and stem-cell memory (TSCM) cells | Activated/Memory subtype (p) |

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
| Neither confirmed (unmeasured, or only one measured and positive) | *(blank)* |

Per the paper, migration is an **optional** descriptor, and `U` is not a
silent default for missing data — Table 7's own worked examples render a
fully-uncharacterized cell as plain `CD4+ T cell` (no `U`), and Box 2's
"`CD4+ TN`" example omits migration entirely despite a known CD62L+ result.
So here, `U` (or an S/D that overrides the marker-derived call) is only ever
produced via an explicit `migration_override` + justification — the same
pattern as `differentiation_override` for `G` (anergic).

Migration subscripts are **never** inferred from markers — each requires an
explicit user-supplied evidence code + justification, because the subscript
is itself a claim about additional assay evidence (blood draw, recirculation
study, parabiosis, etc.). Which subscript is valid depends on the migration
code it's attached to (per the paper's "Migration properties" section):

| Subscript | Valid on | Meaning |
|---|---|---|
| `B` | S, D, **or U** | isolated from blood, no further migration claim |
| `W` | S **or** D | widespread — recirculates through non-lymphoid tissue |
| `R` | D only | resident — parked within an organ/vascular compartment |

(e.g. `CD8+ TUBM` — blood-drawn, migration otherwise unknown, memory — is a
valid worked example from the paper's Table 7.)

### Differentiation (N / A / M / X / G)

Checked in priority order **X > N > A > M** (if input data is contradictory
and matches more than one, this is flagged in the rationale as a conflict
warning rather than silently resolved). Every required "negative" marker
must be *explicitly measured* negative — a missing marker never satisfies a
negative condition.

| State | Requires |
|---|---|
| `X` Exhausted | PD-1+ AND TOX+ |
| ` `↳ `p` progenitor (Xp / TPEX) | TCF1+, SLAMF6+, TIM3- |
| ` `↳ `t` terminal (Xt / TEX-term) | TCF1-, SLAMF6-, TIM3+, CD101+ |
| `N` Naive | CCR7+ AND (CD45RA+ or CD45RO-) AND CD95- |
| `A` Activated | (CD69+ or CD25+) AND PD-1- AND TOX- |
| ` `↳ `p` progenitor (Ap / MPEC) | KLRG1-, CD127+, CD27+, TCF1+ |
| ` `↳ `t` terminal (At / SLEC) | KLRG1+, CD127- |
| `M` Memory | (CD45RO+ or CD45RA-) AND CD69- AND CD25- |
| ` `↳ `p` progenitor (Mp / TSCM) | CD95+, CCR7+, CD27+ (an alternative path into `M`, not gated behind the base memory check above — a TSCM profile is CD45RA+/CCR7+ like naive, but CD95+ distinguishes it) |
| `G` Anergic | never marker-derived — user override only |
| none of the above | left blank, rationale explains what's missing |

Ap/At and Mp are per Table 2 (SLEC/MPEC) and Table 4 (TSCM) of the paper —
the modular nomenclature section itself doesn't redefine their marker basis,
so this program reuses those existing-nomenclature marker sets as proxies.

### Antigen status (+ / 0 / blank)

Never inferred from markers. User-asserted only, with an optional
justification note.

## Design principles

1. **Over-claiming is the failure mode this program is built to avoid.** If
   a marker wasn't measured, its slot stays blank — never guessed, and never
   defaulted to a "claim" code like `U` or `G` either.
2. Migration (S/D/U) and its subscripts (B/W/R), and differentiation's
   `Ap`/`At`/`Mp` subscripts, are marker-derived where the paper gives a
   marker basis; `U`, `G`, and any override are only ever set via explicit
   user assertion + justification, never auto-derived.
3. Antigen status is never marker-derived — always a direct user assertion.
4. Every slot is optional; a bare lineage alone is a valid, complete run.

## Scope / out of scope

This MVP only handles categorical flow-cytometry-style marker calls
(`+`/`-`/not measured). Continuous scRNA-seq expression values would need a
threshold/binarization step before reuse of this logic — noted as a TODO in
`nomenclature/models.py` but not implemented here. Likewise, full automatic
mapping to every named subset in the paper's Tables 1-6 (TCM, TEM, TPEX,
...) is out of scope; this program implements the core marker rules only.

## Web UI

A Flask front end (`app.py`) wraps the same `nomenclature` package used by
the CLI — no naming logic is duplicated. Run it locally:

```
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000. It has two pages:

- **Single population** (`/`) — a form version of interactive mode: fill in
  markers, get the nomenclature string plus the slot-by-slot breakdown and
  audit trail.
- **Batch CSV** (`/batch`) — upload a CSV (e.g. `examples/template.csv`),
  get back the same file with `nomenclature`/`migration`/`differentiation`/
  `antigen`/`rationale` columns appended.

### Deploying to Railway

The repo already has what Railway's Nixpacks builder needs — `requirements.txt`
and a `Procfile` (`web: gunicorn app:app --bind 0.0.0.0:$PORT`). From the
[Railway dashboard](https://railway.app): New Project → Deploy from GitHub repo
→ pick this repo. Railway sets `$PORT` automatically; no other environment
variables are required.

To use a different logo, replace `static/logo.png` (falls back to a plain
"CHOI LAB" text mark if the file is missing).

## Tests

```
python -m pytest tests/ -v
```

Two layers of validation against the primary source:

- `tests/test_table7.py` — four cases reproduce worked examples straight
  from the paper's own Table 7 (`Liver CD8+ TD`, `CD8+ TDRXp+`, `CD8+ TUBM`,
  and the prose `SW` example); the rest are logic-coverage tests for this
  implementation (migration blank/override mechanics, subscript validity,
  conflict warnings, CSV round-trip, etc.).
- `tests/test_named_subsets.py` — cross-checks against the *existing*-
  nomenclature marker definitions the paper gives for well-known named
  subsets in Tables 1-6 (TCM, TEM, TEMRA, TRM, TSCM, SLEC, MPEC, TPEX,
  TEX-int, TEX-term), verifying each maps to the modular code the paper
  itself assigns it — including two cases (TEMRA, TRM) where the correct
  behavior is to leave a slot unassigned rather than force a guess.

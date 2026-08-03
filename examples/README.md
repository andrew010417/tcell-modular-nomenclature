# Example / template CSV

`template.csv` has 3 rows:

1. `example_naive` — a fully worked naive CD4+ example
2. `example_exhausted_progenitor` — the `CD8+ TDRXp+` example from the project brief
3. `my_sample_1` — a blank starter row: copy this row and fill in whatever columns you have data for, delete the rest

Try it as-is first, to see what the output looks like before touching anything:

```
python main.py --csv examples/template.csv --out examples/template_output.csv
```

## Column reference

Every column is optional — leave a cell blank if you don't have that piece of information. Nothing is guessed from a blank cell.

| Column | Meaning | Example |
|---|---|---|
| `label` | Your own name for this sample/population | `patient1_liver_cd8` |
| `location` | Tissue/anatomical site (not a paper module slot, just a display prefix) | `Liver` |
| `lineage` | Module slot 1 — free text | `CD8+` |
| `function` | Module slot 2 — free text | `TH1` |
| `CD62L`, `CCR7` | Migration markers | `+`, `-`, or blank |
| `CD45RA`, `CD45RO`, `CD95` | Naive/memory markers | `+`, `-`, or blank |
| `CD69`, `CD25` | Recent-activation markers | `+`, `-`, or blank |
| `PD1`, `TOX` | Chronic-stimulation/exhaustion markers | `+`, `-`, or blank |
| `TCF1`, `SLAMF6`, `TIM3`, `CD101` | Exhaustion subtype markers (progenitor vs. terminal) | `+`, `-`, or blank |
| `migration_evidence` | Only used if migration comes out `D`. One of `B` (blood only), `W` (widespread recirculation confirmed), `R` (tissue residency confirmed) | `R` |
| `migration_evidence_note` | Free text — what evidence backs the code above | `Parabiosis confirms tissue residency` |
| `differentiation_override` | Manually force the differentiation slot (mainly for `G`, anergic, which can't be read from markers) | `G` |
| `differentiation_override_note` | Free text justification for the override | `No IL-2 on restimulation` |
| `antigen_status` | Never inferred from markers. `+` (persistent), `0` (cleared/irrelevant), or blank (no claim) | `+` |
| `antigen_note` | Free text justification for antigen status | `Chronic LCMV infection model` |

See the top-level [README.md](../README.md) for what each marker biologically means and how the slot decisions are made.

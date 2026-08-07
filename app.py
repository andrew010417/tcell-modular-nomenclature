"""Web front end for the T cell modular nomenclature generator.

Thin Flask wrapper around the existing `nomenclature` package (models /
slots / assemble / csv_batch) — no naming logic lives here, only request
handling and rendering.
"""
from __future__ import annotations

import io
import os

from flask import Flask, Response, render_template, request, send_file

from nomenclature.assemble import generate_nomenclature
from nomenclature.csv_batch import _build_header_map, _row_to_record
from nomenclature.models import MARKER_DESCRIPTIONS, MARKER_GROUPS, TCellRecord

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    form_values = {}

    if request.method == "POST":
        markers = {name: request.form.get(name, "NA") for group in MARKER_GROUPS for name in group[1]}
        form_values = request.form.to_dict()

        migration_evidence = request.form.get("migration_evidence") or None
        differentiation_override = request.form.get("differentiation_override", "").strip() or None

        record = TCellRecord(
            label=request.form.get("label", "").strip(),
            location=request.form.get("location", "").strip(),
            lineage=request.form.get("lineage", "").strip(),
            function=request.form.get("function", "").strip(),
            markers=markers,
            migration_evidence=migration_evidence,
            migration_evidence_note=request.form.get("migration_evidence_note", "").strip(),
            differentiation_override=differentiation_override,
            differentiation_override_note=request.form.get("differentiation_override_note", "").strip(),
            antigen_status=request.form.get("antigen_status", "").strip(),
            antigen_note=request.form.get("antigen_note", "").strip(),
        )
        result = generate_nomenclature(record)

    return render_template(
        "index.html",
        marker_groups=MARKER_GROUPS,
        marker_descriptions=MARKER_DESCRIPTIONS,
        result=result,
        form_values=form_values,
    )


@app.route("/batch", methods=["GET", "POST"])
def batch():
    error = None

    if request.method == "POST":
        uploaded = request.files.get("csv_file")
        if not uploaded or not uploaded.filename:
            error = "Please choose a CSV file to upload."
        else:
            try:
                input_text = uploaded.stream.read().decode("utf-8-sig")
                output_buffer = io.StringIO()
                n = process_csv_stream(input_text, output_buffer)
                output_bytes = io.BytesIO(output_buffer.getvalue().encode("utf-8"))
                base = os.path.splitext(uploaded.filename)[0]
                return send_file(
                    output_bytes,
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name=f"{base}_output.csv",
                )
            except Exception as exc:  # noqa: BLE001 - surface any parse/logic error to the user
                error = f"Could not process that file: {exc}"

    return render_template("batch.html", error=error)


@app.route("/template.csv")
def template_csv():
    return send_file(
        os.path.join(os.path.dirname(__file__), "examples", "template.csv"),
        mimetype="text/csv",
        as_attachment=True,
        download_name="template.csv",
    )


def process_csv_stream(input_text: str, output_buffer: io.StringIO) -> int:
    """In-memory variant of nomenclature.csv_batch.process_csv.

    The library function works on file paths; a web request only has
    in-memory text, so this re-implements the same read/transform/write
    steps against StringIO instead of touching disk.
    """
    import csv as csv_module

    reader = csv_module.DictReader(io.StringIO(input_text))
    fieldnames = reader.fieldnames or []
    rows = list(reader)

    header_map = _build_header_map(fieldnames)

    new_cols = [
        "nomenclature",
        "migration",
        "migration_subscript",
        "differentiation",
        "differentiation_subscript",
        "antigen",
        "rationale",
    ]
    out_fieldnames = list(fieldnames) + [c for c in new_cols if c not in fieldnames]

    writer = csv_module.DictWriter(output_buffer, fieldnames=out_fieldnames)
    writer.writeheader()
    for row in rows:
        record = _row_to_record(row, header_map)
        result = generate_nomenclature(record)
        out_row = dict(row)
        out_row["nomenclature"] = result.nomenclature
        out_row["migration"] = result.migration
        out_row["migration_subscript"] = result.migration_subscript
        out_row["differentiation"] = result.differentiation
        out_row["differentiation_subscript"] = result.differentiation_subscript
        out_row["antigen"] = result.antigen
        out_row["rationale"] = result.rationale.replace("\n", " | ")
        writer.writerow(out_row)

    return len(rows)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

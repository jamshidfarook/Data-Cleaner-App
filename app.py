from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import sqlite3
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GLOBAL_DF = None

def load_data(filepath, has_header):
    """Load CSV, Excel, TSV, JSON, or SQLite into a DataFrame respecting header option."""
    ext = filepath.split(".")[-1].lower()
    header_option = 0 if has_header else None

    if ext == "csv":
        return pd.read_csv(filepath, header=header_option)
    elif ext in ["xlsx", "xls"]:
        return pd.read_excel(filepath, header=header_option)
    elif ext == "tsv":
        return pd.read_csv(filepath, sep="\t", header=header_option)
    elif ext == "json":
        return pd.read_json(filepath)
    elif ext in ["db", "sqlite"]:
        conn = sqlite3.connect(filepath)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        table_name = tables.iloc[0, 0]
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    else:
        raise ValueError("Unsupported file type")


@app.route("/", methods=["GET", "POST"])
def index():
    global GLOBAL_DF
    info = None
    message = None

    if request.method == "POST":
        # Upload file
        if "file" in request.files:
            file = request.files["file"]
            has_header = request.form.get("header", "yes").lower() == "yes"
            if file and file.filename != "":
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                GLOBAL_DF = load_data(filepath, has_header)
                message = "File uploaded successfully!"

        # Remove duplicate rows
        if request.form.get("action") == "remove_duplicates" and GLOBAL_DF is not None:
            GLOBAL_DF = GLOBAL_DF.drop_duplicates()

        # Remove duplicate columns by data
        if request.form.get("action") == "remove_dup_columns" and GLOBAL_DF is not None:
            GLOBAL_DF = GLOBAL_DF.loc[:, ~GLOBAL_DF.T.duplicated()]

        # Remove rows with missing values
        if request.form.get("action") == "remove_missing" and GLOBAL_DF is not None:
            GLOBAL_DF = GLOBAL_DF.dropna()

    # Prepare dataset info and previews
    if GLOBAL_DF is not None:
        rows, cols = GLOBAL_DF.shape
        duplicate_rows_count = GLOBAL_DF.duplicated().sum()
        duplicate_columns_count = GLOBAL_DF.T.duplicated().sum()
        missing_values_count = GLOBAL_DF.isna().any(axis=1).sum()

        # Previews
        preview_rows = (
            GLOBAL_DF[GLOBAL_DF.duplicated(keep=False)].to_html()
            if duplicate_rows_count > 0
            else "<p>No duplicate rows</p>"
        )
        preview_columns = (
            GLOBAL_DF.loc[:, GLOBAL_DF.T.duplicated(keep=False)].to_html()
            if duplicate_columns_count > 0
            else "<p>No duplicate columns</p>"
        )
        preview_missing = (
            GLOBAL_DF[GLOBAL_DF.isna().any(axis=1)].to_html()
            if missing_values_count > 0
            else "<p>No missing values</p>"
        )

        info = {
            "rows": rows,
            "cols": cols,
            "duplicate_rows": duplicate_rows_count,
            "duplicate_columns": duplicate_columns_count,
            "missing_values": missing_values_count,
            "preview": GLOBAL_DF.head().to_html(),
            "preview_rows": preview_rows,
            "preview_columns": preview_columns,
            "preview_missing": preview_missing,
        }

    return render_template("index.html", info=info, message=message)


@app.route("/download")
def download():
    global GLOBAL_DF
    if GLOBAL_DF is None:
        return "No dataset loaded"

    buffer = BytesIO()
    GLOBAL_DF.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="cleaned_data.csv",
        mimetype="text/csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
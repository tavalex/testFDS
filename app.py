import os
import uuid

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

import config
import db
from extractor import extract_from_pdf
from label_generator import format_label_plaintext, generate_label_data

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)


@app.before_request
def ensure_db():
    db.init_db()


@app.route("/")
def index():
    products = db.get_all_products()
    return render_template("index.html", products=products)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("pdf_file")
        if not file or not file.filename:
            flash("Veuillez sélectionner un fichier PDF.", "error")
            return redirect(url_for("upload"))

        if not file.filename.lower().endswith(".pdf"):
            flash("Seuls les fichiers PDF sont acceptés.", "error")
            return redirect(url_for("upload"))

        # Save with UUID to avoid conflicts
        original_name = file.filename
        safe_name = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(config.UPLOAD_FOLDER, safe_name)
        file.save(filepath)

        # Extract data
        try:
            data = extract_from_pdf(filepath)
        except Exception as e:
            flash(f"Erreur lors de l'extraction: {e}", "error")
            return redirect(url_for("upload"))

        data["source_filename"] = original_name

        if data.get("error"):
            flash(
                "Le PDF ne contient pas de texte extractible. "
                "Vérifiez qu'il ne s'agit pas d'un scan.",
                "warning",
            )

        product_id = db.insert_product(data)
        flash(f"Produit \"{data.get('product_name', '')}\" importé avec succès.", "success")
        return redirect(url_for("product_view", product_id=product_id))

    return render_template("upload.html")


@app.route("/product/<int:product_id>")
def product_view(product_id):
    product = db.get_product(product_id)
    if not product:
        flash("Produit non trouvé.", "error")
        return redirect(url_for("index"))
    return render_template("product.html", product=product)


@app.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = db.get_product(product_id)
    if not product:
        flash("Produit non trouvé.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Collect form data
        updated = {
            "product_name": request.form.get("product_name", ""),
            "manufacturer": request.form.get("manufacturer", ""),
            "supplier_info": request.form.get("supplier_info", ""),
            "ghs_pictograms": ",".join(request.form.getlist("ghs_pictograms")),
            "signal_word": request.form.get("signal_word", ""),
            "supplemental_info": request.form.get("supplemental_info", ""),
            "ufi_code": request.form.get("ufi_code", ""),
            "first_aid": request.form.get("first_aid", ""),
            "storage_handling": request.form.get("storage_handling", ""),
            "net_quantity": request.form.get("net_quantity", ""),
        }

        # Parse H-statements from textarea (one per line: "H225 - description")
        h_lines = request.form.get("hazard_statements_text", "").strip().split("\n")
        h_statements = []
        for line in h_lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" - ", 1)
            code = parts[0].strip()
            text = parts[1].strip() if len(parts) > 1 else ""
            h_statements.append({"code": code, "text": text})
        updated["hazard_statements"] = h_statements

        # Parse P-statements similarly
        p_lines = request.form.get("precautionary_statements_text", "").strip().split("\n")
        p_statements = []
        for line in p_lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" - ", 1)
            code = parts[0].strip()
            text = parts[1].strip() if len(parts) > 1 else ""
            p_statements.append({"code": code, "text": text})
        updated["precautionary_statements"] = p_statements

        # Parse CAS numbers from textarea (one per line: "CAS - name - percent")
        cas_lines = request.form.get("cas_numbers_text", "").strip().split("\n")
        cas_numbers = []
        for line in cas_lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" | ")
            cas = parts[0].strip() if len(parts) > 0 else ""
            name = parts[1].strip() if len(parts) > 1 else ""
            pct = parts[2].strip() if len(parts) > 2 else ""
            cas_numbers.append({"cas": cas, "name": name, "percent": pct})
        updated["cas_numbers"] = cas_numbers

        db.update_product(product_id, updated)
        flash("Produit mis à jour.", "success")
        return redirect(url_for("product_view", product_id=product_id))

    return render_template("product_edit.html", product=product)


@app.route("/product/<int:product_id>/delete", methods=["POST"])
def product_delete(product_id):
    db.delete_product(product_id)
    flash("Produit supprimé.", "success")
    return redirect(url_for("index"))


@app.route("/product/<int:product_id>/label")
def product_label(product_id):
    product = db.get_product(product_id)
    if not product:
        flash("Produit non trouvé.", "error")
        return redirect(url_for("index"))

    label_data = generate_label_data(product)
    label_text = format_label_plaintext(label_data)
    return render_template("label.html", product=product, label=label_data, label_text=label_text)


@app.route("/product/<int:product_id>/label/download")
def label_download(product_id):
    product = db.get_product(product_id)
    if not product:
        flash("Produit non trouvé.", "error")
        return redirect(url_for("index"))

    label_data = generate_label_data(product)
    text = format_label_plaintext(label_data)

    # Write to temp file
    import tempfile

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(text)
    tmp.close()

    safe_name = product["product_name"].replace(" ", "_")[:30]
    return send_file(
        tmp.name,
        as_attachment=True,
        download_name=f"etiquette_{safe_name}.txt",
        mimetype="text/plain; charset=utf-8",
    )


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

from extractor import GHS_PICTOGRAMS


def generate_label_data(product):
    """Generate structured label data from a product dict (CLP-compliant)."""

    # Product identifier
    product_id = product.get("product_name", "")
    cas_list = product.get("cas_numbers", [])
    if cas_list:
        substances = []
        for cas in cas_list:
            name = cas.get("name", "")
            cas_num = cas.get("cas", "")
            if name and cas_num:
                substances.append(f"{name} (CAS {cas_num})")
            elif cas_num:
                substances.append(f"CAS {cas_num}")
        if substances:
            product_id += " - Contient: " + ", ".join(substances)

    # Supplier
    supplier = product.get("manufacturer", "")
    supplier_info = product.get("supplier_info", "")
    if supplier and supplier_info:
        supplier = f"{supplier} | {supplier_info}"
    elif supplier_info:
        supplier = supplier_info

    # Pictograms
    pictograms = product.get("ghs_pictograms_list", [])

    # Signal word
    signal_word = product.get("signal_word", "")

    # Hazard statements
    h_statements = []
    for h in product.get("hazard_statements", []):
        code = h.get("code", "")
        text = h.get("text", "")
        if code and text:
            h_statements.append(f"{code} - {text}")
        elif code:
            h_statements.append(code)

    # Precautionary statements (CLP recommends max 6, but include all - user can trim)
    p_statements = _prioritize_p_statements(product.get("precautionary_statements", []))

    # UFI
    ufi = product.get("ufi_code", "")

    # Supplemental info
    supplemental = product.get("supplemental_info", "")

    # Net quantity
    net_quantity = product.get("net_quantity", "")

    return {
        "product_identifier": product_id,
        "supplier": supplier,
        "pictograms": pictograms,
        "pictogram_descriptions": {p: GHS_PICTOGRAMS.get(p, p) for p in pictograms},
        "signal_word": signal_word,
        "hazard_statements": h_statements,
        "precautionary_statements": p_statements,
        "supplemental_info": supplemental,
        "ufi": ufi,
        "net_quantity": net_quantity,
    }


def format_label_plaintext(label_data):
    """Format label data as plain text for printing or copying."""
    lines = []
    lines.append("=" * 60)
    lines.append("ÉTIQUETTE CLP / CLP LABEL")
    lines.append("=" * 60)
    lines.append("")

    # Product identifier
    lines.append(f"PRODUIT: {label_data['product_identifier']}")
    lines.append("")

    # Supplier
    if label_data["supplier"]:
        lines.append(f"FOURNISSEUR: {label_data['supplier']}")
        lines.append("")

    # Net quantity
    if label_data["net_quantity"]:
        lines.append(f"QUANTITÉ: {label_data['net_quantity']}")
        lines.append("")

    # UFI
    if label_data["ufi"]:
        lines.append(f"UFI: {label_data['ufi']}")
        lines.append("")

    # Pictograms
    if label_data["pictograms"]:
        lines.append("PICTOGRAMMES DE DANGER:")
        for p in label_data["pictograms"]:
            desc = label_data["pictogram_descriptions"].get(p, "")
            lines.append(f"  [{p}] {desc}")
        lines.append("")

    # Signal word
    if label_data["signal_word"]:
        lines.append(f"MENTION D'AVERTISSEMENT: {label_data['signal_word'].upper()}")
        lines.append("")

    # Hazard statements
    if label_data["hazard_statements"]:
        lines.append("MENTIONS DE DANGER:")
        for h in label_data["hazard_statements"]:
            lines.append(f"  {h}")
        lines.append("")

    # Precautionary statements
    if label_data["precautionary_statements"]:
        lines.append("CONSEILS DE PRUDENCE:")
        for p in label_data["precautionary_statements"]:
            lines.append(f"  {p}")
        lines.append("")

    # Supplemental info
    if label_data["supplemental_info"]:
        lines.append("INFORMATIONS SUPPLÉMENTAIRES:")
        lines.append(f"  {label_data['supplemental_info']}")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def _prioritize_p_statements(p_statements, max_count=6):
    """Prioritize P-statements per CLP guidance. Returns formatted strings."""
    # Always keep P101, P102, P103 (general)
    # Prioritize response statements (P3xx), then prevention (P2xx), then storage/disposal (P4xx/P5xx)
    general = []
    prevention = []
    response = []
    storage_disposal = []

    for p in p_statements:
        code = p.get("code", "")
        text = p.get("text", "")
        formatted = f"{code} - {text}" if text else code

        base = code.split("+")[0]
        if base in ("P101", "P102", "P103"):
            general.append(formatted)
        elif base.startswith("P2"):
            prevention.append(formatted)
        elif base.startswith("P3"):
            response.append(formatted)
        else:
            storage_disposal.append(formatted)

    # Build prioritized list
    result = general + response + prevention + storage_disposal

    # CLP recommends max 6 P-statements on label (excluding P101/P102/P103)
    # We include all but mark the cutoff
    return result

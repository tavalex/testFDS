import re

import pdfplumber

# --- H-statement reference (French) ---
H_STATEMENTS_FR = {
    "H200": "Explosif instable",
    "H201": "Explosif; danger d'explosion en masse",
    "H202": "Explosif; danger grave de projection",
    "H203": "Explosif; danger d'incendie, d'effet de souffle ou de projection",
    "H204": "Danger d'incendie ou de projection",
    "H205": "Danger d'explosion en masse en cas d'incendie",
    "H220": "Gaz extrêmement inflammable",
    "H221": "Gaz inflammable",
    "H222": "Aérosol extrêmement inflammable",
    "H223": "Aérosol inflammable",
    "H224": "Liquide et vapeurs extrêmement inflammables",
    "H225": "Liquide et vapeurs très inflammables",
    "H226": "Liquide et vapeurs inflammables",
    "H228": "Matière solide inflammable",
    "H229": "Récipient sous pression: peut éclater sous l'effet de la chaleur",
    "H230": "Peut exploser même en l'absence d'air",
    "H231": "Peut exploser même en l'absence d'air à une pression et/ou température élevée(s)",
    "H240": "Peut exploser en cas d'échauffement",
    "H241": "Peut s'enflammer ou exploser en cas d'échauffement",
    "H242": "Peut s'enflammer en cas d'échauffement",
    "H250": "S'enflamme spontanément au contact de l'air",
    "H251": "Matière auto-échauffante; peut s'enflammer",
    "H252": "Matière auto-échauffante en grandes quantités; peut s'enflammer",
    "H260": "Dégage au contact de l'eau des gaz inflammables qui peuvent s'enflammer spontanément",
    "H261": "Dégage au contact de l'eau des gaz inflammables",
    "H270": "Peut provoquer ou aggraver un incendie; comburant",
    "H271": "Peut provoquer un incendie ou une explosion; comburant puissant",
    "H272": "Peut aggraver un incendie; comburant",
    "H280": "Contient un gaz sous pression; peut exploser sous l'effet de la chaleur",
    "H281": "Contient un gaz réfrigéré; peut causer des brûlures ou blessures cryogéniques",
    "H290": "Peut être corrosif pour les métaux",
    "H300": "Mortel en cas d'ingestion",
    "H301": "Toxique en cas d'ingestion",
    "H302": "Nocif en cas d'ingestion",
    "H304": "Peut être mortel en cas d'ingestion et de pénétration dans les voies respiratoires",
    "H310": "Mortel par contact cutané",
    "H311": "Toxique par contact cutané",
    "H312": "Nocif par contact cutané",
    "H314": "Provoque des brûlures de la peau et des lésions oculaires graves",
    "H315": "Provoque une irritation cutanée",
    "H317": "Peut provoquer une allergie cutanée",
    "H318": "Provoque des lésions oculaires graves",
    "H319": "Provoque une sévère irritation des yeux",
    "H330": "Mortel par inhalation",
    "H331": "Toxique par inhalation",
    "H332": "Nocif par inhalation",
    "H334": "Peut provoquer des symptômes allergiques ou d'asthme ou des difficultés respiratoires par inhalation",
    "H335": "Peut irriter les voies respiratoires",
    "H336": "Peut provoquer somnolence ou vertiges",
    "H340": "Peut induire des anomalies génétiques",
    "H341": "Susceptible d'induire des anomalies génétiques",
    "H350": "Peut provoquer le cancer",
    "H351": "Susceptible de provoquer le cancer",
    "H360": "Peut nuire à la fertilité ou au fœtus",
    "H361": "Susceptible de nuire à la fertilité ou au fœtus",
    "H362": "Peut être nocif pour les enfants nourris au lait maternel",
    "H370": "Risque avéré d'effets graves pour les organes",
    "H371": "Risque présumé d'effets graves pour les organes",
    "H372": "Risque avéré d'effets graves pour les organes à la suite d'expositions répétées ou d'une exposition prolongée",
    "H373": "Risque présumé d'effets graves pour les organes à la suite d'expositions répétées ou d'une exposition prolongée",
    "H400": "Très toxique pour les organismes aquatiques",
    "H410": "Très toxique pour les organismes aquatiques, entraîne des effets néfastes à long terme",
    "H411": "Toxique pour les organismes aquatiques, entraîne des effets néfastes à long terme",
    "H412": "Nocif pour les organismes aquatiques, entraîne des effets néfastes à long terme",
    "H413": "Peut être nocif à long terme pour les organismes aquatiques",
    "H420": "Nuit à la santé publique et à l'environnement en détruisant l'ozone dans la haute atmosphère",
}

# --- P-statement reference (French, common ones) ---
P_STATEMENTS_FR = {
    "P101": "En cas de consultation d'un médecin, garder à disposition le récipient ou l'étiquette",
    "P102": "Tenir hors de portée des enfants",
    "P103": "Lire attentivement et bien respecter toutes les instructions",
    "P201": "Se procurer les instructions avant utilisation",
    "P202": "Ne pas manipuler avant d'avoir lu et compris toutes les précautions de sécurité",
    "P210": "Tenir à l'écart de la chaleur, des surfaces chaudes, des étincelles, des flammes nues et de toute autre source d'inflammation. Ne pas fumer",
    "P211": "Ne pas vaporiser sur une flamme nue ou sur toute autre source d'inflammation",
    "P220": "Tenir à l'écart des vêtements et d'autres matières combustibles",
    "P221": "Prendre toutes précautions pour éviter de mélanger avec des matières combustibles",
    "P222": "Ne pas laisser au contact de l'air",
    "P223": "Éviter tout contact avec l'eau",
    "P230": "Maintenir humidifié avec...",
    "P231": "Manipuler et stocker sous gaz inerte/...",
    "P232": "Protéger de l'humidité",
    "P233": "Maintenir le récipient fermé de manière étanche",
    "P234": "Ne conserver que dans le récipient d'origine",
    "P235": "Tenir au frais",
    "P240": "Mise à la terre et liaison équipotentielle du récipient et du matériel de réception",
    "P241": "Utiliser du matériel électrique, de ventilation, d'éclairage antidéflagrant",
    "P242": "Ne pas utiliser d'outils produisant des étincelles",
    "P243": "Prendre des mesures de précaution contre les décharges électrostatiques",
    "P244": "S'assurer de l'absence de graisse ou d'huile sur les soupapes de réduction",
    "P250": "Ne pas soumettre à un broyage, un choc, un frottement",
    "P251": "Ne pas perforer, ni brûler, même après usage",
    "P260": "Ne pas respirer les poussières/fumées/gaz/brouillards/vapeurs/aérosols",
    "P261": "Éviter de respirer les poussières/fumées/gaz/brouillards/vapeurs/aérosols",
    "P262": "Éviter tout contact avec les yeux, la peau ou les vêtements",
    "P263": "Éviter tout contact au cours de la grossesse et de l'allaitement",
    "P264": "Se laver soigneusement après manipulation",
    "P270": "Ne pas manger, boire ou fumer en manipulant ce produit",
    "P271": "Utiliser seulement en plein air ou dans un endroit bien ventilé",
    "P272": "Les vêtements de travail contaminés ne devraient pas sortir du lieu de travail",
    "P273": "Éviter le rejet dans l'environnement",
    "P280": "Porter des gants de protection/des vêtements de protection/un équipement de protection des yeux/du visage",
    "P281": "Utiliser l'équipement de protection individuel requis",
    "P301": "EN CAS D'INGESTION:",
    "P302": "EN CAS DE CONTACT AVEC LA PEAU:",
    "P303": "EN CAS DE CONTACT AVEC LA PEAU (ou les cheveux):",
    "P304": "EN CAS D'INHALATION:",
    "P305": "EN CAS DE CONTACT AVEC LES YEUX:",
    "P306": "EN CAS DE CONTACT AVEC LES VÊTEMENTS:",
    "P308": "EN CAS d'exposition prouvée ou suspectée:",
    "P310": "Appeler immédiatement un CENTRE ANTIPOISON/un médecin",
    "P311": "Appeler un CENTRE ANTIPOISON/un médecin",
    "P312": "Appeler un CENTRE ANTIPOISON/un médecin en cas de malaise",
    "P313": "Consulter un médecin",
    "P314": "Consulter un médecin en cas de malaise",
    "P315": "Consulter immédiatement un médecin",
    "P320": "Un traitement spécifique est urgent (voir sur cette étiquette)",
    "P321": "Traitement spécifique (voir sur cette étiquette)",
    "P330": "Rincer la bouche",
    "P331": "NE PAS faire vomir",
    "P332": "En cas d'irritation cutanée:",
    "P333": "En cas d'irritation ou d'éruption cutanée:",
    "P334": "Rincer à l'eau fraîche/poser une compresse humide",
    "P335": "Enlever avec précaution les particules déposées sur la peau",
    "P336": "Dégeler les parties gelées avec de l'eau tiède. Ne pas frotter les zones touchées",
    "P337": "Si l'irritation oculaire persiste:",
    "P338": "Enlever les lentilles de contact si la victime en porte et si elles peuvent être facilement enlevées. Continuer à rincer",
    "P340": "Transporter la personne à l'extérieur et la maintenir dans une position où elle peut confortablement respirer",
    "P342": "En cas de symptômes respiratoires:",
    "P351": "Rincer avec précaution à l'eau pendant plusieurs minutes",
    "P352": "Laver abondamment à l'eau",
    "P353": "Rincer la peau à l'eau/se doucher",
    "P360": "Rincer immédiatement et abondamment avec de l'eau les vêtements contaminés et la peau avant de les enlever",
    "P361": "Enlever immédiatement tous les vêtements contaminés",
    "P362": "Enlever les vêtements contaminés",
    "P363": "Laver les vêtements contaminés avant réutilisation",
    "P370": "En cas d'incendie:",
    "P371": "En cas d'incendie important et de grandes quantités:",
    "P372": "Risque d'explosion en cas d'incendie",
    "P373": "NE PAS combattre l'incendie lorsque le feu atteint les explosifs",
    "P375": "Combattre l'incendie à distance à cause du risque d'explosion",
    "P376": "Obturer la fuite si cela peut se faire sans danger",
    "P377": "Fuite de gaz enflammé: ne pas éteindre, sauf s'il est possible d'obturer la fuite sans danger",
    "P378": "Utiliser... pour l'extinction",
    "P380": "Évacuer la zone",
    "P381": "En cas de fuite, éliminer toutes les sources d'ignition",
    "P390": "Absorber toute substance répandue pour éviter qu'elle puisse endommager les matériaux environnants",
    "P391": "Recueillir le produit répandu",
    "P401": "Stocker conformément à...",
    "P402": "Stocker dans un endroit sec",
    "P403": "Stocker dans un endroit bien ventilé",
    "P404": "Stocker dans un récipient fermé",
    "P405": "Garder sous clef",
    "P406": "Stocker dans un récipient résistant à la corrosion avec doublure intérieure résistante",
    "P407": "Maintenir un intervalle d'air entre les piles/palettes",
    "P410": "Protéger du rayonnement solaire",
    "P411": "Stocker à des températures ne dépassant pas... °C",
    "P412": "Ne pas exposer à des températures supérieures à 50 °C/122 °F",
    "P413": "Stocker les quantités en vrac de plus de... kg à des températures ne dépassant pas... °C",
    "P420": "Stocker à l'écart des autres matières",
    "P501": "Éliminer le contenu/récipient dans un point de collecte approprié",
    "P502": "Se reporter au fabricant ou fournisseur pour des informations concernant la récupération ou le recyclage",
}

# GHS pictogram descriptions
GHS_PICTOGRAMS = {
    "GHS01": "Bombe explosant (Explosif)",
    "GHS02": "Flamme (Inflammable)",
    "GHS03": "Flamme sur un cercle (Comburant)",
    "GHS04": "Bouteille à gaz (Gaz sous pression)",
    "GHS05": "Corrosion (Corrosif)",
    "GHS06": "Tête de mort (Toxicité aiguë)",
    "GHS07": "Point d'exclamation (Nocif/Irritant)",
    "GHS08": "Danger pour la santé (Danger grave pour la santé)",
    "GHS09": "Environnement (Danger pour l'environnement)",
}

# Section header patterns for French and English FDS
SECTION_PATTERNS = [
    # French patterns
    r"(?:RUBRIQUE|SECTION|Rubrique|Section)\s+(\d{1,2})\s*[:\.\-]",
    # Numbered patterns like "1." or "1 -"
    r"^(\d{1,2})\s*[\.\-]\s+(?:IDENTIFICATION|HAZARD|COMPOSITION|FIRST|FIRE|ACCIDENTAL|HANDLING|EXPOSURE|PHYSICAL|STABILITY|TOXICOLOGICAL|ECOLOGICAL|DISPOSAL|TRANSPORT|REGULATORY|OTHER)",
    r"^(\d{1,2})\s*[\.\-]\s+(?:IDENTIFICATION|DANGERS|COMPOSITION|PREMIERS|MESURES|MANIPULATION|CONTRÔLE|PROPRIÉTÉS|STABILITÉ|INFORMATIONS|CONSIDÉRATIONS|TRANSPORT|RÉGLEMENTATION|AUTRES)",
]


def extract_from_pdf(filepath):
    """Extract FDS data from a PDF file. Returns a dict matching the DB schema."""
    text = _extract_text(filepath)
    if not text or len(text.strip()) < 50:
        return {"product_name": "Extraction failed - no text found", "error": True}

    sections = _split_sections(text)
    full_text = text  # fallback for searching across all sections

    section1 = sections.get(1, "")
    section2 = sections.get(2, "")
    section3 = sections.get(3, "")
    section4 = sections.get(4, "")
    section7 = sections.get(7, "")

    # If section splitting didn't work well, search the full text
    search_text = section2 if section2 else full_text
    search_comp = section3 if section3 else full_text

    return {
        "product_name": _extract_product_name(section1, full_text),
        "manufacturer": _extract_manufacturer(section1, full_text),
        "supplier_info": _extract_supplier_info(section1, full_text),
        "cas_numbers": _extract_cas_numbers(search_comp),
        "ghs_pictograms": ",".join(_extract_ghs_pictograms(search_text)),
        "signal_word": _extract_signal_word(search_text),
        "hazard_statements": _extract_h_statements(search_text),
        "precautionary_statements": _extract_p_statements(search_text),
        "supplemental_info": _extract_supplemental_info(search_text),
        "ufi_code": _extract_ufi(section1 + " " + section2 if section1 or section2 else full_text),
        "first_aid": _extract_first_aid(section4, full_text),
        "storage_handling": _extract_storage(section7, full_text),
    }


def _extract_text(filepath):
    """Extract all text from PDF using pdfplumber."""
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _split_sections(text):
    """Split FDS text into numbered sections (1-16)."""
    sections = {}
    lines = text.split("\n")

    current_section = 0
    current_lines = []

    for line in lines:
        matched = False
        for pattern in SECTION_PATTERNS:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                # Save previous section
                if current_section > 0:
                    sections[current_section] = "\n".join(current_lines)
                try:
                    current_section = int(m.group(1))
                except (ValueError, IndexError):
                    continue
                current_lines = [line]
                matched = True
                break
        if not matched:
            current_lines.append(line)

    # Save last section
    if current_section > 0:
        sections[current_section] = "\n".join(current_lines)

    return sections


def _extract_product_name(section1, full_text):
    """Extract product name from Section 1."""
    text = section1 if section1 else full_text[:2000]

    # Look for common patterns
    patterns = [
        r"(?:Nom\s+(?:du\s+)?produit|Nom\s+commercial|Product\s+name|Trade\s+name)\s*[:\-]?\s*(.+)",
        r"(?:Désignation\s+commerciale|Identification\s+du\s+produit)\s*[:\-]?\s*(.+)",
        r"1\.1[.\s]*(?:Identificateur\s+de\s+produit|Product\s+identifier)\s*[:\-]?\s*(?:\n)?\s*(.+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            # Clean up: take only first line if multiline
            name = name.split("\n")[0].strip()
            if len(name) > 2:
                return name

    # Fallback: first non-empty line that isn't a header
    for line in text.split("\n")[:20]:
        line = line.strip()
        if len(line) > 3 and not re.match(r"^(SECTION|RUBRIQUE|FICHE|SAFETY|\d+\.)", line, re.IGNORECASE):
            return line

    return "Unknown product"


def _extract_manufacturer(section1, full_text):
    """Extract manufacturer name."""
    text = section1 if section1 else full_text[:3000]
    patterns = [
        r"(?:Fabricant|Manufacturer|Fournisseur|Supplier|Société|Company)\s*[:\-]?\s*(.+)",
        r"1\.3[.\s]*(?:Renseignements|Details)\s*[:\-]?\s*(?:\n)?\s*(.+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().split("\n")[0].strip()
    return ""


def _extract_supplier_info(section1, full_text):
    """Extract supplier contact info."""
    text = section1 if section1 else full_text[:3000]
    # Collect address, phone, email info
    info_parts = []

    # Phone
    phone = re.search(r"(?:Tél|Tel|Phone|Téléphone)\s*[:\.]?\s*([\d\s\+\-\.()]+)", text, re.IGNORECASE)
    if phone:
        info_parts.append("Tél: " + phone.group(1).strip())

    # Email
    email = re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", text)
    if email:
        info_parts.append("Email: " + email.group(0))

    # Address (very basic)
    addr = re.search(r"(?:Adresse|Address)\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    if addr:
        info_parts.append(addr.group(1).strip())

    return " | ".join(info_parts)


def _extract_cas_numbers(text):
    """Extract CAS numbers and associated substance names."""
    results = []
    cas_pattern = r"\b(\d{2,7}-\d{2}-\d)\b"

    for m in re.finditer(cas_pattern, text):
        cas = m.group(1)
        # Try to find the substance name near the CAS number
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 100)
        context = text[start:end]

        # Look for concentration/percentage nearby
        pct_match = re.search(r"(\d+[\.,]?\d*)\s*[-–]\s*(\d+[\.,]?\d*)\s*%", context)
        if not pct_match:
            pct_match = re.search(r"[<>≤≥]?\s*(\d+[\.,]?\d*)\s*%", context)

        percent = ""
        if pct_match:
            percent = pct_match.group(0).strip()

        entry = {"cas": cas, "name": "", "percent": percent}

        # Check if already added
        if not any(r["cas"] == cas for r in results):
            results.append(entry)

    return results


def _extract_ghs_pictograms(text):
    """Extract GHS pictogram codes."""
    pictograms = set()

    # Direct GHS code references
    for m in re.finditer(r"\bGHS0([1-9])\b", text, re.IGNORECASE):
        pictograms.add(f"GHS0{m.group(1)}")

    # SGH references (French variant)
    for m in re.finditer(r"\bSGH0([1-9])\b", text, re.IGNORECASE):
        pictograms.add(f"GHS0{m.group(1)}")

    # Pictogram image name references
    for m in re.finditer(r"(?:pictogramme|pictogram)[s]?\s*[:\-]?\s*(.*)", text, re.IGNORECASE):
        line = m.group(1)
        for code in re.findall(r"GHS0[1-9]|SGH0[1-9]", line, re.IGNORECASE):
            pictograms.add(code.upper().replace("SGH", "GHS"))

    return sorted(pictograms)


def _extract_signal_word(text):
    """Extract signal word (Danger/Warning/Avertissement)."""
    patterns = [
        r"(?:Mention\s+d'avertissement|Signal\s+word)\s*[:\-]?\s*(Danger|Warning|Avertissement)",
        r"\b(Danger|Avertissement)\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            word = m.group(1).strip().capitalize()
            if word == "Avertissement":
                word = "Avertissement"
            return word
    return ""


def _extract_h_statements(text):
    """Extract hazard statements (H-codes)."""
    results = []
    seen = set()

    # Match H-codes with optional text
    pattern = r"\b(H\d{3}[a-zA-Z]?(?:\s*\+\s*H\d{3}[a-zA-Z]?)*)\b\s*[-–:]?\s*([^\n]*)"
    for m in re.finditer(pattern, text):
        code = m.group(1).strip()
        desc = m.group(2).strip()

        # Clean up description
        if desc and len(desc) > 200:
            desc = desc[:200]

        # If no description found, use reference
        if not desc or len(desc) < 3:
            base_code = code.split("+")[0].strip()
            desc = H_STATEMENTS_FR.get(base_code, "")

        if code not in seen:
            seen.add(code)
            results.append({"code": code, "text": desc})

    return sorted(results, key=lambda x: x["code"])


def _extract_p_statements(text):
    """Extract precautionary statements (P-codes)."""
    results = []
    seen = set()

    # Match P-codes (including combined like P301+P310)
    pattern = r"\b(P\d{3}(?:\s*\+\s*P\d{3})*)\b\s*[-–:]?\s*([^\n]*)"
    for m in re.finditer(pattern, text):
        code = m.group(1).strip()
        # Normalize combined code spacing
        code = re.sub(r"\s*\+\s*", "+", code)
        desc = m.group(2).strip()

        if desc and len(desc) > 200:
            desc = desc[:200]

        if not desc or len(desc) < 3:
            # Try lookup for single codes
            base_code = code.split("+")[0].strip()
            desc = P_STATEMENTS_FR.get(base_code, "")

        if code not in seen:
            seen.add(code)
            results.append({"code": code, "text": desc})

    return sorted(results, key=lambda x: x["code"])


def _extract_supplemental_info(text):
    """Extract EUH statements and other supplemental info."""
    euh_statements = []
    for m in re.finditer(r"\b(EUH\d{3}[A-Za-z]?)\b\s*[-–:]?\s*([^\n]*)", text):
        code = m.group(1).strip()
        desc = m.group(2).strip()
        euh_statements.append(f"{code} - {desc}" if desc else code)
    return "\n".join(euh_statements)


def _extract_ufi(text):
    """Extract UFI (Unique Formula Identifier)."""
    # UFI format: XXXX-XXXX-XXXX-XXXX (alphanumeric groups)
    patterns = [
        r"UFI\s*[:\-]?\s*([A-Z0-9]{4}[\-\s][A-Z0-9]{4}[\-\s][A-Z0-9]{4}[\-\s][A-Z0-9]{4})",
        r"\b([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().upper().replace(" ", "-")
    return ""


def _extract_first_aid(section4, full_text):
    """Extract first aid measures."""
    text = section4 if section4 else ""
    if not text:
        # Try to find section 4 in full text
        m = re.search(
            r"(?:SECTION|RUBRIQUE)\s*4.*?(?=(?:SECTION|RUBRIQUE)\s*5|\Z)",
            full_text, re.IGNORECASE | re.DOTALL,
        )
        if m:
            text = m.group(0)

    if text:
        # Limit to reasonable length
        return text[:2000].strip()
    return ""


def _extract_storage(section7, full_text):
    """Extract handling and storage info."""
    text = section7 if section7 else ""
    if not text:
        m = re.search(
            r"(?:SECTION|RUBRIQUE)\s*7.*?(?=(?:SECTION|RUBRIQUE)\s*8|\Z)",
            full_text, re.IGNORECASE | re.DOTALL,
        )
        if m:
            text = m.group(0)

    if text:
        return text[:2000].strip()
    return ""

import os
import re
import easyocr

from pdf2image import convert_from_path


# =====================================================
# BI-RADS EXTRACTOR
# =====================================================

def extract_birads(text):

    text = text.upper()

    patterns = [
        r'BI[- ]?RADS\s*(?:CATEGORY)?\s*([0-6][A-C]?)',
        r'BIRADS\s*(?:CATEGORY)?\s*([0-6][A-C]?)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1)

    if "BENIGN FINDING" in text:
        return "2"

    return "Unknown"


# =====================================================
# FINDING EXTRACTOR
# =====================================================

def extract_findings(text):

    text_upper = text.upper()

    findings = {
        "breast_side": "Unknown",
        "lesion_type": "Unknown",
        "size": "Unknown",
        "location": "Unknown",
        "clock_position": "Unknown",
        "lymph_nodes": "Unknown",
        "axillary_region": "Unknown"
    }

    # Breast Side

    if "LEFT BREAST" in text_upper:
        findings["breast_side"] = "Left"

    elif "RIGHT BREAST" in text_upper:
        findings["breast_side"] = "Right"

    # Negative Findings

    negative_phrases = [
        "NO MASS",
        "NO DOMINANT MASS",
        "NO LESION",
        "NO SOLID MASS"
    ]

    for phrase in negative_phrases:

        if phrase in text_upper:
            findings["lesion_type"] = "None Detected"
            return findings

    # Lesion Types

    lesion_keywords = [
        "HYPOECHOIC LESION",
        "FIBROADENOMA",
        "SOLID MASS",
        "CYST",
        "MASS",
        "LESION"
    ]

    for keyword in lesion_keywords:

        if keyword in text_upper:
            findings["lesion_type"] = keyword.title()
            break

    # Lesion Size

    lesion_size_pattern = (
        r'LESION.*?'
        r'(\d+\.?\d*)\s*[Xx×]\s*'
        r'(\d+\.?\d*)'
        r'(?:\s*[Xx×]\s*(\d+\.?\d*))?'
        r'\s*(CM|MM)'
    )

    match = re.search(
        lesion_size_pattern,
        text_upper,
        re.DOTALL
    )

    if match:

        if match.group(3):

            findings["size"] = (
                f"{match.group(1)} x "
                f"{match.group(2)} x "
                f"{match.group(3)} "
                f"{match.group(4)}"
            )

        else:

            findings["size"] = (
                f"{match.group(1)} x "
                f"{match.group(2)} "
                f"{match.group(4)}"
            )

    else:

        size_patterns = [

            r'(\d+\.?\d*)\s*[Xx×]\s*(\d+\.?\d*)\s*[Xx×]\s*(\d+\.?\d*)\s*(CM|MM)',

            r'(\d+\.?\d*)\s*[Xx×]\s*(\d+\.?\d*)\s*(CM|MM)',

            r'(\d+\.?\d*)\s*BY\s*(\d+\.?\d*)\s*(CM|MM)'
        ]

        for pattern in size_patterns:

            match = re.search(pattern, text_upper)

            if match:

                if len(match.groups()) == 4:

                    findings["size"] = (
                        f"{match.group(1)} x "
                        f"{match.group(2)} x "
                        f"{match.group(3)} "
                        f"{match.group(4)}"
                    )

                else:

                    findings["size"] = (
                        f"{match.group(1)} x "
                        f"{match.group(2)} "
                        f"{match.group(3)}"
                    )

                break

    # Location

    location_patterns = [
        r'UPPER\s+OUTER\s+QUADRANT',
        r'UPPER\s+INNER\s+QUADRANT',
        r'LOWER\s+OUTER\s+QUADRANT',
        r'LOWER\s+INNER\s+QUADRANT',
        r'RETROAREOLAR'
    ]

    for pattern in location_patterns:

        match = re.search(pattern, text_upper)

        if match:
            findings["location"] = match.group(0).title()
            break

    # Clock Position

    clock_pattern = r"(\d{1,2})\s*O'?CLOCK"

    clock_match = re.search(
        clock_pattern,
        text_upper
    )

    if clock_match:

        findings["clock_position"] = (
            f"{clock_match.group(1)} o'clock"
        )

    # Lymph Nodes

    if "LYMPH NODE" in text_upper or "LYMPH NODES" in text_upper:

        findings["lymph_nodes"] = "Present"

        if "LEFT AXILLARY" in text_upper:
            findings["axillary_region"] = "Left"

        elif "RIGHT AXILLARY" in text_upper:
            findings["axillary_region"] = "Right"

    else:

        findings["lymph_nodes"] = "Not Mentioned"

    return findings


# =====================================================
# RECOMMENDATION EXTRACTOR
# =====================================================

def extract_recommendation(text):

    text_upper = text.upper()

    recommendations = []

    recommendation_patterns = [

        ("CORE NEEDLE BIOPSY", "Core Needle Biopsy"),
        ("BIOPSY", "Biopsy"),
        ("FOLLOW-UP ULTRASOUND", "Follow-up Ultrasound"),
        ("CLINICAL CORRELATION", "Clinical Correlation"),
        ("HISTOPATHOLOGICAL CORRELATION",
         "Histopathological Correlation"),
        ("TISSUE DIAGNOSIS",
         "Tissue Diagnosis Recommended")
    ]

    for keyword, label in recommendation_patterns:

        if keyword in text_upper:
            recommendations.append(label)

    return recommendations


# =====================================================
# RISK CLASSIFIER
# =====================================================

def classify_risk(birads):

    risk_map = {
        "0": "Incomplete",
        "1": "Negative",
        "2": "Benign",
        "3": "Probably Benign",
        "4": "Suspicious",
        "4A": "Low Suspicion",
        "4B": "Moderate Suspicion",
        "4C": "High Suspicion",
        "5": "Highly Suggestive of Malignancy",
        "6": "Known Malignancy"
    }

    return risk_map.get(
        birads,
        "Unknown"
    )


# =====================================================
# SUMMARY GENERATOR
# =====================================================

def generate_summary(
    findings,
    birads,
    risk_level,
    recommendations
):

    summary = (
        f"A {findings['lesion_type']} is present in the "
        f"{findings['breast_side']} breast, "
        f"{findings['location']}, "
        f"{findings['clock_position']} position, "
        f"measuring {findings['size']}. "
        f"BI-RADS Category {birads} "
        f"({risk_level}). "
    )

    if findings["lymph_nodes"] == "Present":

        summary += (
            f"Enlarged {findings['axillary_region']} "
            f"axillary lymph nodes are present. "
        )

    if recommendations:

        summary += (
            "Recommendations: "
            + ", ".join(recommendations)
            + "."
        )

    return summary


# =====================================================
# REPORT GENERATOR
# =====================================================

def generate_report(
    findings,
    birads,
    risk_level,
    recommendations,
    summary
):

    return {
        "breast_side": findings["breast_side"],
        "lesion_type": findings["lesion_type"],
        "size": findings["size"],
        "location": findings["location"],
        "clock_position": findings["clock_position"],
        "lymph_nodes": findings["lymph_nodes"],
        "axillary_region": findings["axillary_region"],
        "birads": birads,
        "risk_level": risk_level,
        "recommendations": recommendations,
        "summary": summary
    }


# =====================================================
# ULTRASOUND ANALYZER
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

POPPLER_PATH = os.path.join(
    BASE_DIR,
    "poppler",
    "poppler-26.07.0",
    "Library",
    "bin"
)

reader = easyocr.Reader(['en'])


def analyze_ultrasound(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    ocr_lines = []

    if extension in [
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    ]:

        ocr_lines = reader.readtext(
            file_path,
            detail=0
        )

    elif extension == ".pdf":

        pages = convert_from_path(
            file_path,
            poppler_path=POPPLER_PATH
        )

        for i, page in enumerate(pages):

            page_path = f"page_{i}.jpg"

            page.save(
                page_path,
                "JPEG"
            )

            page_text = reader.readtext(
                page_path,
                detail=0
            )

            ocr_lines.extend(page_text)

            os.remove(page_path)

    else:

        raise ValueError(
            "Unsupported file type"
        )

    clean_text = " ".join(ocr_lines)

    birads = extract_birads(
        clean_text
    )

    findings = extract_findings(
        clean_text
    )

    recommendations = (
        extract_recommendation(
            clean_text
        )
    )

    risk_level = classify_risk(
        birads
    )

    summary = generate_summary(
        findings,
        birads,
        risk_level,
        recommendations
    )

    report = generate_report(
        findings,
        birads,
        risk_level,
        recommendations,
        summary
    )

    return report
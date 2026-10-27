"""Name normalisation for ShellScope sanctions screening."""
from __future__ import annotations

import re
import unicodedata

# Legal-form words removed from the END of a name (whole words only).
LEGAL_SUFFIXES = {
    "LTD", "LIMITED", "PLC", "LLP", "LP", "LLC", "INC", "INCORPORATED", "CORP", "CORPORATION",
    "CO", "COMPANY", "CIC", "GMBH", "AG", "SA", "SARL", "SAS", "BV", "NV", "SPA", "SRL",
    "OOO", "AO", "PAO", "JSC", "PJSC", "OJSC", "ZAO", "FZE", "FZCO", "PTE", "PTY",
}


def normalise_name(name: str | None) -> str:
    """Return a cleaned, comparable version of a company or entity name.

    Steps: remove accents -> upper case -> '&' to AND -> punctuation to spaces ->
    collapse spaces -> join single letters (S A -> SA) -> drop legal suffixes and a
    dangling AND at the end -> drop a leading THE.
    """
    if name is None or name != name:          # None or NaN (NaN is never equal to itself)
        return ""
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    text = text.upper().replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = " ".join(text.split())
    text = re.sub(r"\b([A-Z]) (?=[A-Z]\b)", r"\1", text)
    words = text.split()
    while words and (words[-1] in LEGAL_SUFFIXES or words[-1] == "AND"):
        words.pop()
    while words and words[0] == "THE":
        words.pop(0)
    return " ".join(words)


if __name__ == "__main__":
    examples = {
        "Acme Trading Ltd.": "ACME TRADING",
        "Société Générale S.A.": "SOCIETE GENERALE",
        "Smith & Sons Limited": "SMITH AND SONS",
        "The Blue Ocean Co. Ltd": "BLUE OCEAN",
        "Limited Edition Books LLP": "LIMITED EDITION BOOKS",
    }
    for raw, expected in examples.items():
        got = normalise_name(raw)
        assert got == expected, f"{raw!r}: got {got!r}, expected {expected!r}"
    print(f"all {len(examples)} examples pass")
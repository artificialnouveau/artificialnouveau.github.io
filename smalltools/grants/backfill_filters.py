#!/usr/bin/env python3
"""Backfill the structured filter fields on grants.json entries.

Fields written (only when missing; existing values are never overwritten, so
hand corrections stick):

- eligibility: "open" | "residents" | "nationals" | "unknown"
    open      = anyone worldwide may apply
    residents = restricted by where you live (country, region, or city)
    nationals = restricted by citizenship/nationality
- attendance: "remote" | "hybrid" | "onsite" | "unknown"
- career: "any" | "emerging" | "established" | "unknown"
- ageCap: integer maximum age, or null when no age cap is stated

Classification is conservative regex matching over title + location +
description; anything ambiguous stays "unknown" (the site has an Unknown chip
for each of these filters). Duration buckets are derived client-side from the
freetext `duration` field, so no duration field is written here.

Run: python3 smalltools/grants/backfill_filters.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent


def text_of(g: dict) -> str:
    return " ".join(
        str(g.get(k) or "") for k in ("title", "location", "description")
    ).lower()


NATIONALS_PATTERNS = [
    r"\bnationals only\b",
    r"\bcitizens only\b",
    r"open (?:only )?to [a-z, ]{0,30}citizens\b",
    r"\bmust (?:be|hold)(?: a)? [a-z]{3,20} (?:citizen|national|nationality|passport)",
    r"\bapplicants must be of [a-z]{3,20} nationality",
    r"\bmust hold [a-z]{3,20} nationality",
    r"\b(?:restricted|open only) to citizens\b",
    r"\bcitizens (?:and|or) permanent residents of\b",
    r"\bcitizenship (?:is )?required\b",
]

RESIDENTS_PATTERNS = [
    r"\bresidents only\b",
    r"\bonly to [a-z-]{2,20}[- ]based\b",
    r"\b[a-z]{2,20}[- ]based (?:applicants|artists|candidates) only\b",
    r"\bmust (?:be )?(?:legally |officially |currently )?resid(?:e|ing|ent)\b",
    r"\bmust (?:be|currently be) (?:based|living|working) in\b",
    r"\bapplicants must be based in\b",
    r"\blegally residing in\b",
    r"\blegally resident in\b",
    r"\blegal residents? of\b",
    r"\bmust live\b",
    r"\blive, work and be officially registered\b",
    r"\bopen (?:only )?to (?:artists|applicants|candidates|those|people) (?:based|living|residing|resident) in\b",
    r"\bcreative europe countr",
    r"\bculture moves europe eligible countr",
    r"\beligible countries\b",
    r"\brestricted:",
    r"\bprovincial council; [a-z ]*residency typically required\b",
]

OPEN_PATTERNS = [
    r"\bopen internationally\b",
    r"\bopen worldwide\b",
    r"\bopen to (?:artists|applicants|all artists|creatives|all) worldwide\b",
    r"\bno nationality restriction\b",
    r"\bany nationality\b",
    r"\bopen to all nationalities\b",
    r"\bfrom all over the world\b",
    r"\banywhere in the world\b",
    r"\bworldwide submissions\b",
    r"\binternational submissions\b",
    r"\bopen to international\b",
    r"\bapplications (?:are )?accepted internationally\b",
    r"\bno geographic restriction\b",
    r"\binternationally open\b",
    r"\bopen to professional artists and collectives from anywhere\b",
]

REMOTE_PATTERNS = [
    r"\bfully remote\b",
    r"\bwork(?:ing)? remotely\b",
    r"\bremote[- ]friendly\b",
    r"\bonline residency\b",
    r"\bvirtual residency\b",
    r"\bweb residenc",
    r"\bremote residency\b",
    r"\bremote cohort\b",
    r"\bremote and self-directed\b",
    r"\bwork is remote\b",
    r"\bno in-person\b",
    r"\bno residency requirement\b",
    r"\bremote[,;] ",
    r"\bremote / ",
    r"\bonline programme\b",
    r"\bonline application\b.*\bno in-person\b",
    r"\bfully online\b",
]

ONSITE_PATTERNS = [
    r"\bin-person\b",
    r"\bin person\b",
    r"\bon-site\b",
    r"\bon site\b",
    r"\brelocat",
    r"\bresidential\b",
    r"\blive and work on",
    r"\bmust reside at\b",
    r"\bfull-time, on site\b",
    r"\bcampus residency\b",
    r"\baccommodation (?:is )?provided\b",
    r"\bhoused at\b",
]

HYBRID_PATTERNS = [
    r"\bhybrid\b",
]

CAREER_ANY_PATTERNS = [
    r"\ball career stages\b",
    r"\bany career stage\b",
    r"\bevery career stage\b",
    r"\bno specific level of experience\b",
    r"\bemerging (?:or|and|to) established\b",
    r"\bestablished (?:or|and) emerging\b",
    r"\ball experience levels\b",
    r"\bregardless of (?:career|experience)\b",
    r"\bemerging, mid-career and established\b",
]

CAREER_EMERGING_PATTERNS = [
    r"\bemerging (?:artist|talent|creator|maker|designer|curator|filmmaker|practitioner|writer)",
    r"\bearly[- ]career\b",
    r"\byoung (?:artist|creator|talent|professional)",
    r"\bnewcomer\b",
    r"\bdebut\b",
]

CAREER_ESTABLISHED_PATTERNS = [
    r"\bestablished (?:artist|practitioner|professional)s?\b",
    r"\bmid-career\b",
    r"\bat least \d+ years of professional\b",
    r"\bprofessional practice of at least\b",
    r"\bmid-career to seasoned\b",
    r"\bseasoned practitioner",
    r"\b\d+\+? years of (?:professional )?(?:artistic )?practice\b",
]

# "under 18" also appears in family top-ups ("children under 18") and film
# calls ("under 25 minutes"), so the bare "under N" pattern excludes unit words
# after the number and child contexts before it, and caps below 20 are ignored
# (a real applicant age cap is 20+; 18 is always a minimum age).
AGE_CAP_UNIT_GUARD = r"(?!\s*(?:km|kg|%|,\d|\.\d|minutes?|min\b|seconds?|hours?|days?|weeks?|months?|pages?|words?|mb|gb|euro|eur\b|usd|gbp|people|members|employees|years? of\b))"
AGE_CAP_PATTERNS = [
    r"\bunder (?:the age of )?(\d{2})\b" + AGE_CAP_UNIT_GUARD,
    r"\baged? (?:\d{1,2})\s*(?:-|–|to)\s*(\d{2})\b" + AGE_CAP_UNIT_GUARD,
    r"\bup to (\d{2}) years (?:old|of age)\b",
    r"\byounger than (\d{2})\b",
    r"\bmaximum age(?: of)? (\d{2})\b",
    r"\b(\d{2}) years old or younger\b",
    r"\bage limit(?: of| is)? (\d{2})\b",
]
AGE_CAP_CHILD_CONTEXT = r"(?:child(?:ren)?|kids?|minors?|dependants?|dependents?)[^.;]{0,30}under (?:the age of )?\d{2}"
# Age phrases about someone other than the applicant: a jury's age, or the
# beneficiary population an organisation serves.
AGE_CAP_OTHER_CONTEXT = r"(?:jur(?:y|ors)|audiences?|beneficiar\w*|communities|participants they serve|serving youth)[^.;]{0,80}aged? \d{1,2}"


def any_match(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def classify_eligibility(g: dict, text: str) -> str:
    if any_match(NATIONALS_PATTERNS, text):
        return "nationals"
    if any_match(RESIDENTS_PATTERNS, text):
        return "residents"
    if any_match(OPEN_PATTERNS, text):
        return "open"
    if g.get("region") in ("Worldwide", "Remote"):
        return "open"
    return "unknown"


def classify_attendance(g: dict, text: str, types_text: str) -> str:
    if any_match(HYBRID_PATTERNS, text):
        return "hybrid"
    r = any_match(REMOTE_PATTERNS, text) or g.get("region") == "Remote"
    o = any_match(ONSITE_PATTERNS, text)
    if r and o:
        return "hybrid"
    if r:
        return "remote"
    if o:
        return "onsite"
    if "residen" in types_text:
        # A residency with no online/virtual marker is on site.
        return "onsite"
    return "unknown"


def classify_career(text: str) -> str:
    if any_match(CAREER_ANY_PATTERNS, text):
        return "any"
    emerging = any_match(CAREER_EMERGING_PATTERNS, text)
    established = any_match(CAREER_ESTABLISHED_PATTERNS, text)
    if emerging and established:
        return "any"
    if emerging:
        return "emerging"
    if established:
        return "established"
    return "unknown"


def detect_age_cap(text: str) -> int | None:
    if re.search(r"\bno age (?:limit|cap|restriction)", text):
        return None
    # Strip "children under 18" style phrases so family top-ups never read as
    # caps, and age phrases about juries or beneficiary populations.
    text = re.sub(AGE_CAP_CHILD_CONTEXT, "", text)
    text = re.sub(AGE_CAP_OTHER_CONTEXT, "", text)
    caps = []
    for p in AGE_CAP_PATTERNS:
        for m in re.finditer(p, text):
            try:
                n = int(m.group(1))
            except (IndexError, ValueError):
                continue
            if 20 <= n <= 45:
                caps.append(n)
    return max(caps) if caps else None


def main() -> int:
    dry = "--dry-run" in sys.argv
    path = HERE / "grants.json"
    data = json.loads(path.read_text())
    stats = {k: Counter() for k in ("eligibility", "attendance", "career")}
    age_caps = 0
    touched = 0

    for g in data["grants"]:
        text = text_of(g)
        tags_text = " ".join(str(t) for t in (g.get("tags") or [])).lower()
        types_text = tags_text + " " + str(g.get("title") or "").lower()
        changed = False
        if not g.get("eligibility"):
            g["eligibility"] = classify_eligibility(g, text)
            changed = True
        if not g.get("attendance"):
            g["attendance"] = classify_attendance(g, text, types_text)
            changed = True
        if not g.get("career"):
            g["career"] = classify_career(text)
            changed = True
        if "ageCap" not in g:
            # Organisations do not have ages; any age phrase in an org-facing
            # call is about the people the organisation serves.
            g["ageCap"] = None if g.get("applicant") == "organizations" else detect_age_cap(text)
            changed = True
        if changed:
            touched += 1
        stats["eligibility"][g["eligibility"]] += 1
        stats["attendance"][g["attendance"]] += 1
        stats["career"][g["career"]] += 1
        if g.get("ageCap"):
            age_caps += 1

    for field, counter in stats.items():
        print(f"{field}: " + ", ".join(f"{k}={v}" for k, v in counter.most_common()))
    print(f"ageCap set on {age_caps} entries; touched {touched} of {len(data['grants'])}")

    if not dry:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

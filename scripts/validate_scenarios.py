#!/usr/bin/env python3
"""scripts/validate_scenarios.py — Validate that scenario YAML section paths exist in corpus.

For every scenario in data/scenarios/*.yaml, checks that every entry in
`gold_chunk_sections` refers to a heading that literally exists in one of the
Markdown files in data/corpus/.

This is the acceptance-criteria check required by the S0 brief:
  "All 7 scenario YAMLs parse and reference section paths that literally exist
   in the Markdown corpus."

Exit code: 0 if all scenarios pass, 1 if any fail.

Usage:
    python scripts/validate_scenarios.py

Approved dependencies: pyyaml (stdlib re, pathlib).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Heading extraction
# ---------------------------------------------------------------------------

# Matches ATX headings: optional leading whitespace, one or more #, space, text
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def _extract_headings(md_path: Path) -> set[str]:
    """Return the set of all heading texts from a Markdown file (stripped of markup)."""
    text = md_path.read_text(encoding="utf-8")
    headings: set[str] = set()
    for match in _HEADING_RE.finditer(text):
        # Strip inline bold/italic markup so "**DANGER:**" becomes "DANGER:"
        raw = match.group(1).strip()
        clean = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", raw)
        headings.add(clean.strip())
    return headings


def load_corpus_headings(corpus_dir: Path) -> dict[str, set[str]]:
    """Load headings from all Markdown files. Returns {filename: {heading_set}}."""
    all_headings: dict[str, set[str]] = {}
    for md_file in sorted(corpus_dir.glob("*.md")):
        all_headings[md_file.name] = _extract_headings(md_file)
    return all_headings


def all_headings_union(heading_map: dict[str, set[str]]) -> set[str]:
    """Return the union of all headings across all corpus files."""
    union: set[str] = set()
    for headings in heading_map.values():
        union |= headings
    return union


# ---------------------------------------------------------------------------
# Scenario validation
# ---------------------------------------------------------------------------

def validate_scenario(
    scenario_path: Path,
    all_headings: set[str],
    heading_map: dict[str, set[str]],
) -> list[str]:
    """Validate one scenario YAML.  Returns a list of error strings (empty = pass)."""
    errors: list[str] = []

    with open(scenario_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    # --- Required top-level keys ---
    required_keys = [
        "scenario_id", "description", "asset_id", "asset_class",
        "error_code", "input_snapshot", "expected_deviations",
        "gold_chunk_sections", "required_safety_strings",
        "expected_top_hypothesis", "expects_refusal",
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"  MISSING KEY: '{key}'")

    if errors:
        # Can't continue without required keys
        return errors

    scenario_id: str = data["scenario_id"]
    expects_refusal: bool = data["expects_refusal"]
    gold_sections: list[list[str]] = data["gold_chunk_sections"]

    # --- E-999 (refusal scenario) must have empty gold_chunk_sections ---
    if expects_refusal and gold_sections:
        errors.append(
            f"  LOGIC ERROR: expects_refusal=true but gold_chunk_sections is not empty: {gold_sections}"
        )

    # --- For non-refusal scenarios, each gold section path must exist in the corpus ---
    if not expects_refusal:
        for section_path in gold_sections:
            if not isinstance(section_path, list):
                errors.append(
                    f"  FORMAT ERROR: gold_chunk_sections entry is not a list: {section_path!r}"
                )
                continue
            for heading in section_path:
                if heading not in all_headings:
                    # Show which files were searched
                    searched = sorted(heading_map.keys())
                    errors.append(
                        f"  MISSING HEADING: '{heading}' not found in any of {searched}"
                    )

    # --- required_safety_strings must be substrings of some corpus file ---
    for safety_str in data.get("required_safety_strings", []):
        found_in: list[str] = []
        for md_name, _ in heading_map.items():
            corpus_dir = Path(__file__).parent.parent / "data" / "corpus"
            md_text = (corpus_dir / md_name).read_text(encoding="utf-8")
            # Also normalize markdown callout prefixes like "> **WARNING:**" -> "WARNING:"
            normalized_md = re.sub(r">\s*\*\*([A-Z]+):\*\*", r"\1:", md_text)
            normalized_md = re.sub(r"\*\*([A-Z]+):\*\*", r"\1:", normalized_md)
            if safety_str in md_text or safety_str in normalized_md:
                found_in.append(md_name)
        if not found_in:
            errors.append(
                f"  SAFETY STRING NOT FOUND verbatim in any corpus file:\n"
                f"    '{safety_str[:100]}...'"
                if len(safety_str) > 100 else
                f"  SAFETY STRING NOT FOUND verbatim in any corpus file:\n"
                f"    '{safety_str}'"
            )

    # --- input_snapshot must contain all 9 sensors ---
    snapshot = data.get("input_snapshot", {})
    expected_sensors = {
        "vibration_rms", "bearing_temp_de", "bearing_temp_nde", "motor_current",
        "discharge_pressure", "flow_rate", "oil_level_pct", "rpm", "suction_pressure",
    }
    missing_sensors = expected_sensors - set(snapshot.keys())
    if missing_sensors:
        errors.append(f"  MISSING SENSORS in input_snapshot: {sorted(missing_sensors)}")

    return errors


def main() -> None:
    project_root = Path(__file__).parent.parent
    corpus_dir   = project_root / "data" / "corpus"
    scenario_dir = project_root / "data" / "scenarios"

    if not corpus_dir.exists():
        print(f"ERROR: corpus directory not found: {corpus_dir}")
        sys.exit(1)

    # Load all corpus headings once
    heading_map  = load_corpus_headings(corpus_dir)
    all_headings = all_headings_union(heading_map)

    print(f"Loaded headings from {len(heading_map)} corpus files:")
    for fname, headings in heading_map.items():
        print(f"  {fname}: {len(headings)} headings")
    print(f"  Total unique headings: {len(all_headings)}")
    print()

    # Validate each scenario
    scenario_files = sorted(scenario_dir.glob("*.yaml"))
    if not scenario_files:
        print(f"ERROR: No scenario YAML files found in {scenario_dir}")
        sys.exit(1)

    print(f"Validating {len(scenario_files)} scenario files ...\n")
    all_passed = True

    for scenario_path in scenario_files:
        errors = validate_scenario(scenario_path, all_headings, heading_map)
        if errors:
            print(f"  FAIL  {scenario_path.name}")
            for err in errors:
                print(err)
            all_passed = False
        else:
            with open(scenario_path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            refusal_flag = "  [refusal]" if data.get("expects_refusal") else ""
            n_gold = len(data.get("gold_chunk_sections", []))
            n_safety = len(data.get("required_safety_strings", []))
            print(
                f"  PASS  {scenario_path.name}"
                f"  (gold_sections={n_gold}, safety_strings={n_safety}){refusal_flag}"
            )

    print()
    if all_passed:
        print("ALL SCENARIOS PASSED")
        sys.exit(0)
    else:
        print("ONE OR MORE SCENARIOS FAILED - see errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()

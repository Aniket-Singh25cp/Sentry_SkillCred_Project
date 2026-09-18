#!/usr/bin/env python3
"""scripts/generate_corpus.py — Convert Markdown corpus files to PDF.

Attempts weasyprint first (pure Python, pip-installable).
Falls back to pandoc via subprocess if weasyprint is unavailable.

Output: data/corpus/*.pdf  (one PDF per Markdown source)

Usage:
    python scripts/generate_corpus.py

Approved dependencies: markdown, weasyprint (optional), subprocess (stdlib).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CSS for PDF rendering — compact, print-friendly style sheet.
# Kept inline so the script is self-contained with no external asset files.
# ---------------------------------------------------------------------------

PRINT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,700;1,400&family=Source+Code+Pro:wght@400&display=swap');

@page {
    size: A4;
    margin: 20mm 22mm 22mm 22mm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        font-family: 'Source Serif 4', serif;
        color: #555;
    }
    @top-right {
        content: string(doctitle);
        font-size: 8pt;
        font-family: 'Source Serif 4', serif;
        color: #555;
    }
}

body {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1a1a1a;
    max-width: 100%;
}

h1 {
    font-size: 18pt;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 6pt;
    color: #002244;
    page-break-after: avoid;
    string-set: doctitle content();
}

h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #003366;
    margin-top: 16pt;
    margin-bottom: 4pt;
    border-bottom: 1pt solid #003366;
    padding-bottom: 2pt;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #004488;
    margin-top: 12pt;
    margin-bottom: 3pt;
    page-break-after: avoid;
}

h4 {
    font-size: 10.5pt;
    font-weight: 700;
    font-style: italic;
    color: #333;
    margin-top: 10pt;
    margin-bottom: 2pt;
    page-break-after: avoid;
}

p { margin: 0 0 7pt 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 10pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #003366;
    color: white;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: 700;
}

td {
    padding: 3pt 6pt;
    border: 0.5pt solid #aab;
    vertical-align: top;
}

tr:nth-child(even) td { background-color: #f0f4f8; }

blockquote {
    margin: 8pt 0 8pt 0;
    padding: 6pt 10pt;
    border-left: 4pt solid #cc0000;
    background-color: #fff5f5;
    page-break-inside: avoid;
}

blockquote p { margin: 0; }

/* Safety callout colour coding by signal word */
blockquote:has(strong:first-child) { border-left-color: #cc0000; }

code, pre {
    font-family: 'Source Code Pro', 'Courier New', monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 1pt 3pt;
    border-radius: 2pt;
}

pre {
    padding: 6pt 8pt;
    border: 0.5pt solid #ccc;
    overflow-x: auto;
    page-break-inside: avoid;
}

ol, ul {
    margin: 4pt 0 8pt 0;
    padding-left: 18pt;
}

li { margin-bottom: 3pt; }

hr {
    border: none;
    border-top: 1pt solid #ccc;
    margin: 14pt 0;
}

strong { font-weight: 700; }
em { font-style: italic; }
"""

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _md_to_html(md_path: Path) -> tuple[str, str]:
    """Convert a Markdown file to an HTML string. Returns (title, html_body)."""
    try:
        import markdown  # type: ignore[import-untyped]
    except ImportError:
        print("  ERROR: 'markdown' package not installed. Run: pip install markdown")
        sys.exit(1)

    md_text = md_path.read_text(encoding="utf-8")
    # Extract the first H1 heading as the document title
    title = md_path.stem
    for line in md_text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    html_body: str = markdown.markdown(
        md_text,
        extensions=["tables", "toc", "attr_list", "fenced_code"],
    )
    return title, html_body


def _render_weasyprint(html: str, out_pdf: Path) -> None:
    """Use WeasyPrint to write the PDF."""
    from weasyprint import HTML  # type: ignore[import-untyped]
    from weasyprint.text.fonts import FontConfiguration  # type: ignore[import-untyped]

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(str(out_pdf), font_config=font_config)


def _render_pandoc(md_path: Path, out_pdf: Path) -> None:
    """Fall back to pandoc via subprocess."""
    cmd = [
        "pandoc",
        str(md_path),
        "-o", str(out_pdf),
        "--pdf-engine=xelatex",
        "--variable", "geometry:a4paper,margin=20mm",
        "--variable", "fontsize=10.5pt",
        "--variable", "colorlinks=true",
        "--toc",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stderr:
            print(f"    pandoc stderr: {result.stderr.strip()}")
    except FileNotFoundError:
        raise RuntimeError("pandoc not found on PATH")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pandoc failed: {exc.stderr}") from exc


def _render_browser(full_html: str, out_pdf: Path) -> None:
    """Fall back to headless Edge/Chrome to print HTML to PDF."""
    import shutil
    # Candidate browser executables
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    browser_bin: str | None = None
    for c in candidates:
        if c.is_file():
            browser_bin = str(c)
            break

    if not browser_bin:
        for name in ["msedge", "edge", "chrome", "google-chrome", "chromium"]:
            found = shutil.which(name)
            if found:
                browser_bin = found
                break

    if not browser_bin:
        raise RuntimeError("No headless browser (Edge/Chrome) found on system")

    # Write temporary HTML file for browser to open
    temp_html = out_pdf.with_suffix(".temp.html")
    temp_html.write_text(full_html, encoding="utf-8")
    try:
        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf.resolve()}",
            temp_html.resolve().as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode != 0 or not out_pdf.exists():
            raise RuntimeError(f"Browser PDF export failed (code {res.returncode}): {res.stderr}")
    finally:
        if temp_html.exists():
            temp_html.unlink()


def convert_md_to_pdf(md_path: Path, out_pdf: Path) -> str:
    """Convert one Markdown file to PDF, trying weasyprint, then pandoc, then headless browser."""
    title, html_body = _md_to_html(md_path)
    full_html = HTML_TEMPLATE.format(title=title, css=PRINT_CSS, body=html_body)

    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    # 1. Try weasyprint first
    try:
        _render_weasyprint(full_html, out_pdf)
        return "weasyprint"
    except Exception:
        pass  # Fall through to pandoc or browser

    # 2. Try pandoc fallback
    try:
        _render_pandoc(md_path, out_pdf)
        return "pandoc"
    except Exception:
        pass  # Fall through to browser fallback

    # 3. Try browser fallback (Edge/Chrome headless)
    try:
        _render_browser(full_html, out_pdf)
        return "browser"
    except Exception as exc:
        print(f"  ERROR: All PDF renderers failed for {md_path.name}: {exc}")
        # Write HTML as fallback
        html_path = out_pdf.with_suffix(".html")
        html_path.write_text(full_html, encoding="utf-8")
        print(f"  Wrote HTML fallback -> {html_path}")
        return "html_only"


def main() -> None:
    project_root = Path(__file__).parent.parent
    corpus_dir = project_root / "data" / "corpus"

    md_files = sorted(corpus_dir.glob("*.md"))
    if not md_files:
        print(f"No Markdown files found in {corpus_dir}")
        sys.exit(1)

    print(f"generate_corpus.py - converting {len(md_files)} Markdown files to PDF ...")
    for md_path in md_files:
        out_pdf = md_path.with_suffix(".pdf")
        print(f"  Converting: {md_path.name} -> {out_pdf.name}")
        renderer = convert_md_to_pdf(md_path, out_pdf)
        if out_pdf.exists():
            size_kb = out_pdf.stat().st_size // 1024
            print(f"    OK [{renderer}] - {size_kb} kB")
        else:
            print(f"    WARN: {out_pdf.name} was not produced (see errors above)")

    print("Done.")


if __name__ == "__main__":
    main()

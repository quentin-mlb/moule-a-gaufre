import argparse
from pathlib import Path
import sys
from weasyprint import HTML, CSS

#!/usr/bin/env python3
"""
generate_pdf.py

Simple CLI that converts an HTML file (and optional CSS file) to PDF using WeasyPrint.

Usage:
    python generate_pdf.py input.html [--css style.css] [--output out.pdf]
"""


def main():
        parser = argparse.ArgumentParser(description="Generate PDF from HTML (+ optional CSS) using WeasyPrint.")
        parser.add_argument("html", type=Path, help="Path to the input HTML file.")
        parser.add_argument("--css", type=Path, help="Path to an optional CSS file.")
        parser.add_argument("--output", "-o", type=Path, help="Output PDF path. Defaults to input name with .pdf extension.")
        args = parser.parse_args()

        html_path = args.html
        css_path = args.css
        out_path = args.output or html_path.with_suffix(".pdf")

        if not html_path.exists():
                print(f"Error: HTML file not found: {html_path}", file=sys.stderr)
                sys.exit(2)
        if css_path and not css_path.exists():
                print(f"Error: CSS file not found: {css_path}", file=sys.stderr)
                sys.exit(2)

        try:
            pass
        except Exception as e:
                print("Error: could not import weasyprint. Install it with: pip install weasyprint", file=sys.stderr)
                sys.exit(1)

        try:
                html = HTML(filename=str(html_path))
                stylesheets = [CSS(filename=str(css_path))] if css_path else None
                html.write_pdf(target=str(out_path), stylesheets=stylesheets)
        except Exception as e:
                print(f"Failed to generate PDF: {e}", file=sys.stderr)
                sys.exit(3)

        print(f"PDF generated: {out_path}")

if __name__ == "__main__":
        main()
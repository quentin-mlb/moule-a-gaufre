#!/usr/bin/env python3
"""
generate_pdf.py

Can be used as a CLI or imported as a library.

Usage (CLI):
        python generate_pdf.py input.html [--css style.css] [--output out.pdf]

Library:
        from generate_pdf import generate_pdf
        pdf_path = generate_pdf("input.html", css="style.css", out="out.pdf")
"""

from pathlib import Path
import argparse
import sys
import logging
from typing import Optional, Union

__all__ = ["generate_pdf"]

PathLike = Union[str, Path]


def generate_pdf(html: PathLike, css: Optional[PathLike] = None, out: Optional[PathLike] = None) -> Path:
        """
        Generate a PDF from an HTML file (optionally with a CSS file) using WeasyPrint.

        Args:
                html: Path to the input HTML file.
                css: Optional path to a CSS file.
                out: Optional output PDF path. If None, uses input name with .pdf extension.

        Returns:
                Path to the generated PDF.

        Raises:
                FileNotFoundError: if html or css files are missing.
                RuntimeError: if weasyprint is not installed.
                Exception: for other errors raised during PDF generation.
        """
        html_path = Path(html)
        if not html_path.exists():
                raise FileNotFoundError(f"HTML file not found: {html_path}")

        css_path = Path(css) if css else None
        if css_path and not css_path.exists():
                raise FileNotFoundError(f"CSS file not found: {css_path}")

        out_path = Path(out) if out else html_path.with_suffix(".pdf")

        try:
                # Lazy import so module can be imported even if weasyprint isn't installed,
                # and so callers get a clear RuntimeError when they call the function.
                from weasyprint import HTML, CSS
        except ImportError as e:
                raise RuntimeError("weasyprint is not installed. Install it with: pip install weasyprint") from e

        stylesheets = [CSS(filename=str(css_path))] if css_path else None
        html_doc = HTML(filename=str(html_path))
        html_doc.write_pdf(target=str(out_path), stylesheets=stylesheets)

        return out_path


def _cli():
        parser = argparse.ArgumentParser(description="Generate PDF from HTML (+ optional CSS) using WeasyPrint.")
        parser.add_argument("html", type=Path, help="Path to the input HTML file.")
        parser.add_argument("--css", type=Path, help="Path to an optional CSS file.")
        parser.add_argument("--output", "-o", type=Path, help="Output PDF path. Defaults to input name with .pdf extension.")
        args = parser.parse_args()

        # Configure weasyprint logger for CLI use
        logger = logging.getLogger("weasyprint")
        logger.setLevel(logging.WARNING)
        if not logger.handlers:
                logger.addHandler(logging.StreamHandler())

        try:
                out_path = generate_pdf(args.html, css=args.css, out=args.output)
        except FileNotFoundError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(2)
        except RuntimeError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
                print(f"Failed to generate PDF: {e}", file=sys.stderr)
                sys.exit(3)

        print(f"PDF generated: {out_path}")


if __name__ == "__main__":
        _cli()
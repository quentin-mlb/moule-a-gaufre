from pathlib import Path
import argparse
import json
import sys
from typing import Optional, Union


"""
generate_html.py

Render a Jinja2 template with a JSON file (schema.org Recipe) and write HTML.
Usable as:
        - CLI: python generate_html.py -t template.html -j recipe.json -o out.html
        - Library: from generate_html import generate_html; html = generate_html("t.html", "r.json")
"""


def load_json(path: Union[str, Path]) -> object:
                path = Path(path)
                try:
                                with path.open("r", encoding="utf-8") as f:
                                                return json.load(f)
                except Exception as exc:
                                raise RuntimeError(f"Failed to read JSON '{path}': {exc}") from exc


def find_recipe(data: object) -> Optional[dict]:
                if isinstance(data, dict):
                                if data.get("@type") == "Recipe" or data.get("type") == "Recipe":
                                                return data
                                if "mainEntity" in data and isinstance(data["mainEntity"], dict) and data["mainEntity"].get("@type") == "Recipe":
                                                return data["mainEntity"]
                                if "@graph" in data and isinstance(data["@graph"], list):
                                                for item in data["@graph"]:
                                                                if isinstance(item, dict) and (item.get("@type") == "Recipe" or item.get("type") == "Recipe"):
                                                                                return item
                if isinstance(data, list):
                                for item in data:
                                                if isinstance(item, dict) and (item.get("@type") == "Recipe" or item.get("type") == "Recipe"):
                                                                return item
                return None


def render_template(template_path: Union[str, Path], context: dict) -> str:
                # Import jinja2 lazily so the module can be imported without Jinja2 installed.
                try:
                                from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
                except ImportError as exc:
                                raise RuntimeError("Jinja2 is required. Install with: pip install Jinja2") from exc

                template_path = Path(template_path)
                env = Environment(
                                loader=FileSystemLoader(str(template_path.parent or ".")),
                                autoescape=select_autoescape(["html", "htm", "xml"]),
                                undefined=StrictUndefined,
                )
                tpl = env.get_template(template_path.name)
                return tpl.render(context)


def generate_html(template: Union[str, Path], json_file: Union[str, Path]) -> str:
                """
                Render template with JSON and return rendered HTML as string.
                Raises RuntimeError on failures.
                """
                template_path = Path(template)
                json_path = Path(json_file)

                if not template_path.is_file():
                                raise RuntimeError(f"Template file not found: {template_path}")
                if not json_path.is_file():
                                raise RuntimeError(f"JSON file not found: {json_path}")

                data = load_json(json_path)
                recipe = find_recipe(data)
                context = {"recipe": recipe if recipe is not None else data}
                return render_template(template_path, context)


def write_output(path: Union[str, Path], content: str):
                path = Path(path)
                try:
                                path.parent.mkdir(parents=True, exist_ok=True)
                                with path.open("w", encoding="utf-8") as f:
                                                f.write(content)
                except Exception as exc:
                                raise RuntimeError(f"Failed to write output '{path}': {exc}") from exc


def main(argv=None):
                p = argparse.ArgumentParser(description="Render a Jinja2 template with a schema.org Recipe JSON.")
                p.add_argument("-t", "--template", required=True, help="Path to Jinja2 template file (HTML).")
                p.add_argument("-j", "--json", required=True, help="Path to JSON file containing a schema.org Recipe object.")
                p.add_argument("-o", "--output", help="Output HTML file path. Defaults to input json basename + .html")

                args = p.parse_args(argv)
                template_path = Path(args.template)
                json_path = Path(args.json)
                out_path = Path(args.output) if args.output else json_path.with_suffix(".html")

                try:
                                out_html = generate_html(template_path, json_path)
                except RuntimeError as exc:
                                msg = str(exc)
                                # Map common error messages to exit codes to preserve prior behavior
                                if "Jinja2 is required" in msg:
                                                print(msg, file=sys.stderr)
                                                sys.exit(2)
                                if msg.startswith("Failed to read JSON"):
                                                print(msg, file=sys.stderr)
                                                sys.exit(3)
                                if msg.startswith("Template file not found"):
                                                print(msg, file=sys.stderr)
                                                sys.exit(4)
                                if msg.startswith("JSON file not found"):
                                                print(msg, file=sys.stderr)
                                                sys.exit(5)
                                # Template/rendering errors
                                print(f"Template rendering error: {msg}", file=sys.stderr)
                                sys.exit(6)

                try:
                                write_output(out_path, out_html)
                except RuntimeError as exc:
                                print(str(exc), file=sys.stderr)
                                sys.exit(7)

                print(f"Wrote {out_path}")


if __name__ == "__main__":
                main()

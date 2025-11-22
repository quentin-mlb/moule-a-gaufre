from pathlib import Path
import argparse
import json
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

#!/usr/bin/env python3
"""
generate_html.py

Simple script to render a Jinja2 template with a JSON file (schema.org Recipe) and write HTML.
Usage (PowerShell):
    python .\\generate_html.py -t .\\template.html -j .\\recipe.json -o .\\out.html
"""

try:
    pass
except Exception as e:
    print("Error: Jinja2 is required. Install with: pip install Jinja2", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path):
        try:
                with path.open("r", encoding="utf-8") as f:
                        return json.load(f)
        except Exception as exc:
                print(f"Failed to read JSON '{path}': {exc}", file=sys.stderr)
                sys.exit(3)


def render_template(template_path: Path, context: dict):
        env = Environment(
                loader=FileSystemLoader(str(template_path.parent or ".")),
                autoescape=select_autoescape(["html", "htm", "xml"]),
                undefined=StrictUndefined,
        )
        tpl = env.get_template(template_path.name)
        print('debug',type(template_path.name))
        return tpl.render(context)


def main():
        p = argparse.ArgumentParser(description="Render a Jinja2 template with a schema.org Recipe JSON.")
        p.add_argument("-t", "--template", required=True, help="Path to Jinja2 template file (HTML).")
        p.add_argument("-j", "--json", required=True, help="Path to JSON file containing a schema.org Recipe object.")
        p.add_argument("-o", "--output", help="Output HTML file path. Defaults to input json basename + .html")

        args = p.parse_args()
        template_path = Path(args.template)
        json_path = Path(args.json)
        out_path = Path(args.output) if args.output else json_path.with_suffix(".html")

        if not template_path.is_file():
                print(f"Template file not found: {template_path}", file=sys.stderr)
                sys.exit(4)
        if not json_path.is_file():
                print(f"JSON file not found: {json_path}", file=sys.stderr)
                sys.exit(5)

        data = load_json(json_path)

        # If the JSON file wraps the recipe in a graph or has @graph, try to extract a Recipe object.
        recipe = None
        if isinstance(data, dict):
                # common places: top-level is the recipe, or in "@graph", or "mainEntity"
                if data.get("@type") == "Recipe" or data.get("type") == "Recipe":
                        recipe = data
                elif "mainEntity" in data and isinstance(data["mainEntity"], dict) and data["mainEntity"].get("@type") == "Recipe":
                        recipe = data["mainEntity"]
                elif "@graph" in data and isinstance(data["@graph"], list):
                        for item in data["@graph"]:
                                if isinstance(item, dict) and (item.get("@type") == "Recipe" or item.get("type") == "Recipe"):
                                        recipe = item
                                        break
        if recipe is None and isinstance(data, list):
                # maybe the JSON is a list of nodes; pick the first Recipe
                for item in data:
                        if isinstance(item, dict) and (item.get("@type") == "Recipe" or item.get("type") == "Recipe"):
                                recipe = item
                                break

        # Fallback: pass the entire JSON as "recipe"
        context = {"recipe": recipe}# if recipe is not None else data}
        
        print(context['recipe']['name'])

        try:
                out_html = render_template(template_path, context)
        except Exception as exc:
                print(f"Template rendering error: {exc}", file=sys.stderr)
                sys.exit(6)

        try:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8") as f:
                        f.write(out_html)
        except Exception as exc:
                print(f"Failed to write output '{out_path}': {exc}", file=sys.stderr)
                sys.exit(7)

        print(f"Wrote {out_path}")


if __name__ == "__main__":
        main()
"""CLI for notebook2api."""

import argparse
import sys
from pathlib import Path

from converter import NotebookParser, EndpointGenerator
from api_generator import APIGenerator


def convert(notebook_path: str, output_dir: str, framework: str = "fastapi"):
    """Convert a notebook to an API application."""
    notebook_path = Path(notebook_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse notebook
    parser = NotebookParser(str(notebook_path))
    cells = parser.parse()
    print(f"Parsed {len(cells)} cells from {notebook_path.name}")

    # Generate endpoints
    generator = EndpointGenerator(cells)
    endpoints = generator.generate_endpoints()
    print(f"Generated {len(endpoints)} endpoints:")
    for e in endpoints:
        print(f"  {e.method.upper()} {e.path} -> {e.function_name}()")

    # Generate API code
    api_gen = APIGenerator(
        title=f"{notebook_path.stem} API",
        framework=framework
    )
    code = api_gen.generate(endpoints)

    # Write output files
    main_file = output_dir / "main.py"
    main_file.write_text(code)
    print(f"Generated API: {main_file}")

    # Write requirements
    req_file = output_dir / "requirements.txt"
    if framework == "fastapi":
        req_file.write_text("fastapi==0.109.0\nuvicorn[standard]==0.27.0\npydantic==2.5.0\n")
    else:
        req_file.write_text("flask==3.0.0\nflask-cors==4.0.0\n")
    print(f"Generated requirements: {req_file}")

    print(f"\nDone! Run: cd {output_dir} && pip install -r requirements.txt && uvicorn main:app --reload")


def main():
    parser = argparse.ArgumentParser(description="notebook2api: Convert Jupyter notebooks to REST APIs")
    sub = parser.add_subparsers(dest="command")

    conv = sub.add_parser("convert", help="Convert a notebook to API")
    conv.add_argument("notebook", help="Path to .ipynb file")
    conv.add_argument("--output", "-o", default="./api", help="Output directory")
    conv.add_argument("--framework", "-f", choices=["fastapi", "flask"], default="fastapi", help="Web framework")
    conv.add_argument("--watch", "-w", action="store_true", help="Watch for changes")

    args = parser.parse_args()

    if args.command == "convert":
        try:
            convert(args.notebook, args.output, args.framework)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

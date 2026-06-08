"""Parse Jupyter notebooks and convert to API endpoints."""

import json
import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Cell:
    type: str  # "code" or "markdown"
    source: str
    line_start: int
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)


@dataclass
class Endpoint:
    path: str
    method: str
    function_name: str
    docstring: Optional[str] = None
    parameters: list[str] = field(default_factory=list)


class NotebookParser:
    """Parse a Jupyter notebook and extract code cells."""

    def __init__(self, notebook_path: str):
        self.path = Path(notebook_path)
        self.cells: list[Cell] = []

    def parse(self) -> list[Cell]:
        """Parse the notebook file."""
        with open(self.path) as f:
            nb = json.load(f)

        line_offset = 0
        for worksheet in nb.get("worksheets", [{}]):
            for cell in worksheet.get("cells", []):
                cell_type = cell.get("cell_type", "code")
                source = "".join(cell.get("source", []))
                lines = source.split("\n")
                cell_obj = Cell(
                    type=cell_type,
                    source=source,
                    line_start=line_offset,
                )
                if cell_type == "code":
                    cell_obj.functions = self._extract_functions(source)
                    cell_obj.classes = self._extract_classes(source)
                self.cells.append(cell_obj)
                line_offset += len(lines) + 1

        return self.cells

    def _extract_functions(self, source: str) -> list[str]:
        """Extract function names from source code."""
        try:
            tree = ast.parse(source)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except SyntaxError:
            return []

    def _extract_classes(self, source: str) -> list[str]:
        """Extract class names from source code."""
        try:
            tree = ast.parse(source)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except SyntaxError:
            return []


class EndpointGenerator:
    """Generate API endpoints from parsed notebook cells."""

    def __init__(self, cells: list[Cell]):
        self.cells = cells

    def generate_endpoints(self) -> list[Endpoint]:
        """Generate REST endpoints from notebook functions."""
        endpoints = []
        for cell in self.cells:
            if cell.type != "code":
                continue
            for fn_name in cell.functions:
                if fn_name.startswith("_"):
                    continue
                path = f"/{fn_name.replace('_', '-')}"
                endpoints.append(Endpoint(
                    path=path,
                    method="POST",
                    function_name=fn_name,
                    docstring=self._get_docstring(cell.source, fn_name),
                    parameters=self._get_parameters(cell.source, fn_name),
                ))
        return endpoints

    def _get_docstring(self, source: str, fn_name: str) -> Optional[str]:
        match = re.search(rf'def {fn_name}\([^)]*\):\s*"""(.*?)"""', source, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _get_parameters(self, source: str, fn_name: str) -> list[str]:
        match = re.search(rf'def {fn_name}\(([^)]*)\)', source)
        if match:
            args = match.group(1).replace("self,", "").replace("self", "")
            return [a.strip().split(":")[0].strip() for a in args.split(",") if a.strip()]
        return []

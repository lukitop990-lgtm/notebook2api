"""Generate FastAPI or Flask application from notebook endpoints."""

from typing import Optional


TEMPLATE_FASTAPI = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

{imports}

app = FastAPI(title="{title}", version="1.0.0")

{endpoint_classes}

{endpoints}

@app.get("/")
def root():
    return {{"message": "{title}", "version": "1.0.0", "endpoints": [{endpoint_list}]}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

TEMPLATE_FLASK = '''from flask import Flask, request, jsonify
import os

{imports}

app = Flask(__name__)

{endpoints}

@app.route("/")
def root():
    return jsonify({{"message": "{title}", "version": "1.0.0", "endpoints": [{endpoint_list}]}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''


class APIGenerator:
    """Generate API application code from endpoints."""

    def __init__(self, title: str = "Notebook API", framework: str = "fastapi"):
        self.title = title
        self.framework = framework.lower()

    def generate(self, endpoints: list) -> str:
        """Generate the full API application code."""
        endpoint_list = ", ".join(f'"{e.path}"' for e in endpoints)
        imports = self._generate_imports(endpoints)
        endpoint_classes = self._generate_endpoint_classes(endpoints)
        endpoint_handlers = self._generate_handlers(endpoints)

        template = TEMPLATE_FASTAPI if self.framework == "fastapi" else TEMPLATE_FLASK

        return template.format(
            title=self.title,
            endpoint_list=endpoint_list,
            imports=imports,
            endpoint_classes=endpoint_classes,
            endpoints=endpoint_handlers,
        )

    def _generate_imports(self, endpoints: list) -> str:
        if self.framework == "fastapi":
            return "from typing import Any, List\nfrom fastapi import FastAPI"
        return "from flask import Flask, request, jsonify"

    def _generate_endpoint_classes(self, endpoints: list) -> str:
        if self.framework != "fastapi":
            return ""
        lines = []
        for e in endpoints:
            params = ", ".join(f"{p}: Any" for p in e.parameters)
            lines.append(
                f'class {e.function_name.title().replace("-", "")}Request(BaseModel):\n'
                f'    {params}'
            )
        return "\n".join(lines) if lines else "# No request models needed"

    def _generate_handlers(self, endpoints: list) -> str:
        lines = []
        for e in endpoints:
            params = ", ".join(e.parameters)
            if self.framework == "fastapi":
                body_param = e.parameters[0] if e.parameters else "data: Any"
                lines.append(
                    f'@app.post("{e.path}")\n'
                    f'def {e.function_name}({body_param}):\n'
                    f'    """{e.docstring or f"Endpoint for {e.function_name}"}"""\n'
                    f'    return {{"result": {e.function_name}({params})}}'
                )
            else:
                lines.append(
                    f'@app.route("{e.path}", methods=["POST"])\n'
                    f'def {e.function_name}():\n'
                    f'    """{e.docstring or f"Endpoint for {e.function_name}"}"""\n'
                    f'    data = request.get_json() or {{}}\n'
                    f'    return jsonify({{"result": {e.function_name}(**data)}})'
                )
        return "\n\n".join(lines)

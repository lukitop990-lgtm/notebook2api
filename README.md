# notebook2api

Convert Jupyter notebooks to REST APIs with automatic endpoint generation and Docker support.

## Features

- Parse `.ipynb` files and extract code cells
- Auto-generate FastAPI/Flask endpoints from notebook cells
- Docker containerization out of the box
- Swagger/OpenAPI docs auto-generated
- Support for notebook with markdown cells as API documentation
- Environment variable injection for secrets

## Quick Start

```bash
pip install notebook2api
notebook2api convert my_notebook.ipynb --output ./api --framework fastapi
cd api && uvicorn main:app --reload
```

## API

Visit `http://localhost:8000/docs` for auto-generated Swagger UI.

## Example

```python
# my_notebook.ipynb cell:
# def predict(input_data):
#     model = load_model()
#     return model.predict(input_data)

# Generated API:
# POST /predict
# Body: { "input_data": [...] }
```

## License

MIT

# File Parser CRUD API with Progress Tracking

A FastAPI-based backend for uploading, parsing, and managing files (CSV, Excel, PDF) with progress tracking.

## Setup
1. Clone the repo: `git clone <your-repo-url>`
2. Create and activate virtual environment: `python -m venv venv`, `venv\Scripts\activate`
3. Install dependencies: `pip install fastapi uvicorn sqlalchemy pandas openpyxl pypdf`
4. Run the server: `uvicorn main:app --reload`
5. API available at `http://127.0.0.1:8000`

## API Endpoints
- **POST /files**: Upload a file.
  - Payload: Multipart form-data with `file` field.
  - Example: `curl.exe -X POST "http://127.0.0.1:8000/files" -F "file=@C:\Project\FP_PT\test.csv"`
  - Response: `{"file_id":"d627606536ad4ba588cde84caf65f729"}`
- **GET /files/{file_id}/progress**: Check upload/parsing progress.
  - Example: `curl.exe "http://127.0.0.1:8000/files/d627606536ad4ba588cde84caf65f729/progress"`
  - Response: `{"file_id":"d627606536ad4ba588cde84caf65f729","status":"ready","progress":100}`
- **GET /files/{file_id}**: Get parsed content.
  - Response: `[{"name":"Alice","age":30},...]`
- **GET /files**: List all files.
  - Response: `[{"id":"d627606536ad4ba588cde84caf65f729","filename":"test.csv",...}]`
- **DELETE /files/{file_id}**: Delete a file.
  - Response: `{"message":"File deleted"}`

## Testing
- Use cURL commands above or import `file_parser_api.json` into Postman.
- Test with CSV, Excel (.xlsx), and PDF files.

## Limitations
- Progress tracking uses in-memory storage (not persistent).
- Parsing delay is simulated (~10 seconds).

## Test Results
- CSV: Successfully uploaded, parsed, and retrieved: `[{"name":"Alice","age":30},...]`.
- PDF: Successfully extracted text: `[{"page":1,"text":"E-commerce Product..."},...]`.
- Excel: Successfully parsed: `[{"name":"Alice","age":30},...]`.
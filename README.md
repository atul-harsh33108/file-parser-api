# File Parser CRUD API with Progress Tracking

This project is a **FastAPI-based backend** designed to upload, parse, manage, and track the progress of file processing for CSV, Excel (`.xlsx`), and PDF files. It supports CRUD operations, stores file metadata in a SQLite database, and provides real-time progress updates via a WebSocket endpoint. The project includes unit tests, a Postman collection for API testing, and sample files for demonstration.

## Project Overview

The File Parser CRUD API allows users to:
- **Upload** files (CSV, Excel, PDF) via a RESTful API.
- **Track** upload and parsing progress in real-time using HTTP or WebSocket.
- **Retrieve** parsed content (e.g., tabular data for CSV/Excel, text for PDF).
- **List** all uploaded files with metadata.
- **Delete** files and their associated data.
- **Test** the API using included unit tests and a Postman collection.

### Features
- **Supported File Types**: CSV, Excel (`.xlsx`), PDF.
- **Database**: SQLite for storing file metadata and parsed content.
- **Progress Tracking**: In-memory tracking of upload and parsing progress.
- **Real-Time Updates**: WebSocket endpoint for live progress monitoring.
- **Testing**: Unit tests with `pytest` and a Postman collection for API testing.
- **Sample Files**: Included `test.csv`, `test.xlsx`, and `test.pdf` for demonstration.

## Prerequisites

Before setting up the project, ensure you have:
- **Python 3.8+** installed (tested with Python 3.13.3).
- **Git** installed for cloning the repository.
- **Postman** (optional, for testing the API with the provided collection).
- **Node.js** (optional, for testing WebSocket with `wscat`).
- A code editor (e.g., VS Code) for viewing/editing files.

## Setup Instructions

Follow these steps to set up and run the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/atul-harsh33108/file-parser-api.git
   cd file-parser-api
   ```

2. **Create and Activate a Virtual Environment**:
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - This isolates dependencies to avoid conflicts with other projects.

3. **Install Dependencies**:
   - Use the provided `requirements.txt` for all required packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Alternatively, install core dependencies manually:
     ```bash
     pip install fastapi uvicorn sqlalchemy pandas openpyxl pypdf httpx pytest
     ```
   - Dependencies include:
     - `fastapi`: For building the API.
     - `uvicorn`: ASGI server to run FastAPI.
     - `sqlalchemy`: For SQLite database operations.
     - `pandas`: For parsing CSV and Excel files.
     - `openpyxl`: For reading Excel (`.xlsx`) files.
     - `pypdf`: For extracting text from PDF files.
     - `httpx`: For unit testing with FastAPI’s test client.
     - `pytest`: For running unit tests.

4. **Run the Server**:
   - Start the FastAPI server with hot-reload for development:
     ```bash
     uvicorn main:app --reload
     ```
   - The API will be available at `http://127.0.0.1:8000`.

5. **Verify Setup**:
   - Open `http://127.0.0.1:8000/docs` in a browser to access the interactive FastAPI Swagger UI for testing endpoints.

## API Endpoints

The API provides the following endpoints for file management and progress tracking:

1. **POST /files**  
   - **Description**: Uploads a file (CSV, Excel, or PDF) for processing.
   - **Payload**: Multipart form-data with a `file` field containing the file.
   - **Example**:
     ```bash
     curl.exe -X POST "http://127.0.0.1:8000/files" -F "file=@C:\path\to\test.csv"
     ```
   - **Response**:
     ```json
     {"file_id":"d627606536ad4ba588cde84caf65f729"}
     ```
   - **Behavior**: Saves the file to the `uploads/` directory, stores metadata in SQLite, and starts parsing in the background.

2. **GET /files/{file_id}/progress**  
   - **Description**: Retrieves the upload or parsing progress for a specific file.
   - **Example**:
     ```bash
     curl.exe "http://127.0.0.1:8000/files/d627606536ad4ba588cde84caf65f729/progress"
     ```
   - **Response** (example when complete):
     ```json
     {"file_id":"d627606536ad4ba588cde84caf65f729","status":"ready","progress":100}
     ```
   - **Status Values**: `uploading`, `processing`, `ready`, `failed`.
   - **Progress**: Percentage (0–100) updated during upload and parsing.

3. **GET /files/{file_id}**  
   - **Description**: Retrieves the parsed content of a file.
   - **Example**:
     ```bash
     curl.exe "http://127.0.0.1:8000/files/d627606536ad4ba588cde84caf65f729"
     ```
   - **Response** (example for CSV/Excel):
     ```json
     [{"name":"Alice","age":30},{"name":"Bob","age":25},{"name":"Corinthian","age":255},{"name":"Dagath","age":40}]
     ```
   - **Response** (example for PDF):
     ```json
     [{"page":1,"text":"E-commerce Product..."},{"page":2,"text":"..."}]
     ```
   - **Behavior**: Returns parsed content only if the file status is `ready`; otherwise, returns a message indicating the file is still processing.

4. **GET /files**  
   - **Description**: Lists all uploaded files with their metadata.
   - **Example**:
     ```bash
     curl.exe "http://127.0.0.1:8000/files"
     ```
   - **Response**:
     ```json
     [{"id":"d627606536ad4ba588cde84caf65f729","filename":"test.csv","status":"ready","created_at":"2025-08-21T11:59:09.359205"}]
     ```
   - **Behavior**: Retrieves file metadata from the SQLite database.

5. **DELETE /files/{file_id}**  
   - **Description**: Deletes a file and its metadata.
   - **Example**:
     ```bash
     curl.exe -X DELETE "http://127.0.0.1:8000/files/d627606536ad4ba588cde84caf65f729"
     ```
   - **Response**:
     ```json
     {"message":"File deleted"}
     ```
   - **Behavior**: Removes the file from the `uploads/` directory and deletes its record from the database.

6. **WebSocket /ws/progress/{file_id}**  
   - **Description**: Provides real-time progress updates for a file’s upload and parsing.
   - **Connection**: `ws://127.0.0.1:8000/ws/progress/{file_id}`
   - **Example**:
     - Use Postman’s WebSocket client or install `wscat`:
       ```bash
       npm install -g wscat
       wscat -c ws://127.0.0.1:8000/ws/progress/d627606536ad4ba588cde84caf65f729
       ```
   - **Response**: Real-time JSON messages every ~1 second:
     ```json
     {"file_id":"d627606536ad4ba588cde84caf65f729","status":"uploading","progress":10}
     {"file_id":"d627606536ad4ba588cde84caf65f729","status":"processing","progress":20}
     ...
     {"file_id":"d627606536ad4ba588cde84caf65f729","status":"completed","progress":100}
     ```
   - **Behavior**: Streams progress updates until parsing completes, then closes the connection.

## Testing Instructions

### Unit Tests
- **Purpose**: Verify API functionality (upload, progress, content retrieval, listing, deletion).
- **Requirements**: `test.csv` and `test.xlsx` must be in the project root (`C:\Project\FP_PT`).
- **Run Tests**:
  ```bash
  cd C:\Project\FP_PT
  pytest
  ```
- **Expected Output**: 6 tests pass (CSV upload, Excel upload, progress, content, list, delete).
- **File**: `test_main.py` contains the test suite.

### Postman Testing
- **Purpose**: Test API endpoints interactively.
- **File**: `file_parser_api.json` (included in the repository).
- **Steps**:
  1. Open Postman and import `file_parser_api.json`.
  2. Set the `file_id` variable after uploading a file via `POST /files`.
  3. Test each endpoint:
     - Upload: Select `test.csv`, `test.xlsx`, or `test.pdf` in the `POST /files` request.
     - Progress: Use the `file_id` in `GET /files/{file_id}/progress`.
     - Content: Use `GET /files/{file_id}` after parsing completes.
     - List: Use `GET /files` to see all files.
     - Delete: Use `DELETE /files/{file_id}` to remove a file.
     - WebSocket: Connect to `ws://127.0.0.1:8000/ws/progress/{file_id}` in Postman’s WebSocket client.

### Manual Testing with cURL
- **Purpose**: Test endpoints via command line.
- **Examples** (run in the project directory):
  ```bash
  # Upload a file
  curl.exe -X POST "http://127.0.0.1:8000/files" -F "file=@test.xlsx"
  # Check progress (replace <file_id>)
  curl.exe "http://127.0.0.1:8000/files/<file_id>/progress"
  # Get parsed content (after ~10 seconds)
  curl.exe "http://127.0.0.1:8000/files/<file_id>"
  # List files
  curl.exe "http://127.0.0.1:8000/files"
  # Delete a file
  curl.exe -X DELETE "http://127.0.0.1:8000/files/<file_id>"
  ```

### Sample Files
- **Included**: `test.csv`, `test.xlsx`, `test.pdf` are provided in the repository.
- **Content**:
  - `test.csv` and `test.xlsx`:
    ```
    name,age
    Alice,30
    Bob,25
    Corinthian,255
    Dagath,40
    ```
  - `test.pdf`: Contains text about an "E-commerce Product Recommendation RAG" project.

## Test Results

The API was tested with the provided sample files:
- **CSV**: Successfully uploaded, parsed, and retrieved:
  ```json
  [{"name":"Alice","age":30},{"name":"Bob","age":25},{"name":"Corinthian","age":255},{"name":"Dagath","age":40}]
  ```
- **Excel**: Successfully uploaded, parsed, and retrieved:
  ```json
  [{"name":"Alice","age":30},{"name":"Bob","age":25},{"name":"Corinthian","age":255},{"name":"Dagath","age":40}]
  ```
- **PDF**: Successfully extracted text:
  ```json
  [{"page":1,"text":"E-commerce Product Recommendation RAG\nProblem Statement\n..."},{"page":2,"text":"..."}]
  ```
- **WebSocket**: Successfully provided real-time progress updates for uploads and parsing.

## Limitations

- **Progress Tracking**: Uses in-memory storage (`progress_data` dictionary), which is not persistent across server restarts.
- **Parsing Delay**: Simulated with a ~10-second delay to mimic processing time.
- **File Storage**: Files are stored in the `uploads/` directory, which is not cleaned up automatically (except on deletion).
- **Database**: Uses SQLite, suitable for development but not optimized for production-scale concurrency.

## Repository Structure

- `main.py`: Core FastAPI application with all endpoints and logic.
- `test_main.py`: Unit tests for the API.
- `file_parser_api.json`: Postman collection for API testing.
- `requirements.txt`: List of Python dependencies.
- `test.csv`, `test.xlsx`, `test.pdf`: Sample files for testing.
- `.gitignore`: Excludes `venv/`, `__pycache__`, `files.db`, `uploads/`, and other temporary files.

## Troubleshooting

- **ModuleNotFoundError**: Ensure all dependencies are installed (`pip install -r requirements.txt`).
- **File Not Found**: Verify `test.csv` and `test.xlsx` are in the project root for unit tests.
- **WebSocket Connection Issues**: Ensure the server is running and use the correct `file_id`.
- **Database Errors**: Delete `files.db` and restart the server to reset the SQLite database.
- **Excel Parsing Issues**: Ensure `openpyxl` is installed and `test.xlsx` is a valid Excel file.

## Submission Details

- **GitHub Repository**: [https://github.com/atul-harsh33108/file-parser-api](https://github.com/atul-harsh33108/file-parser-api)
- **Status**: Fully functional with all endpoints tested (CSV, Excel, PDF, WebSocket).
- **Documentation**: This `README.md` provides comprehensive setup, usage, and testing instructions.
- **Testing**: Unit tests (`pytest`) and Postman collection (`file_parser_api.json`) included.
- **Bonus Feature**: WebSocket endpoint for real-time progress updates.
- - **Maintainer**: Atul Harsh (GitHub: [atul-harsh33108](https://github.com/atul-harsh33108)).
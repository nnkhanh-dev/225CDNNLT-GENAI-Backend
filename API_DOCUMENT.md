# API DOCUMENT - Nhóm 3

Hệ thống cung cấp kiến trúc Microservices gồm 3 service chính được quản lý thông qua API Gateway (Nginx).

## Base URL & Gateway

API Gateway chạy trên port `8888` (theo `docker-compose.yml` proxy được bind ra `8888:80`).
Mọi request từ phía client cần gọi qua gateway này.

- **Base URL:** `http://<domain-or-ip>:8888`

Các đường dẫn (route) đã được gateway map:

- `/option/`: Định tuyến đến `OptionService`
- `/prompt/`: Định tuyến đến `GeneratePromptService`
- `/model/`: Định tuyến đến `Generate3DModelService`
- `/models/`: Truy cập các file static model (.glb) đã tạo

---

## 1. Option Service

**Prefix:** `/option`

Quản lý các tài nguyên cơ bản như Đồ vật (Object), Phong cách (Style), Tài liệu RAG (Document) và Upload file.

### 1.1. Health Check

- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "OptionService"
  }
  ```

### 1.2. Objects (Đồ vật)

- **Lấy danh sách đồ vật**
  - **Endpoint:** `GET /objects`
  - **Query:** `skip` (int, default=0), `limit` (int, default=100)
  - **Response:** Mảng các đối tượng `{"id": int, "name": string}`
- **Thêm đồ vật mới**
  - **Endpoint:** `POST /objects`
  - **Body (JSON):** `{"name": string}`
  - **Response:** Đối tượng vừa tạo.
- **Lấy thông tin chi tiết đồ vật**
  - **Endpoint:** `GET /objects/{id}`
- **Cập nhật đồ vật**
  - **Endpoint:** `PUT /objects/{id}`
  - **Body (JSON):** `{"name": string}`
- **Xóa đồ vật**
  - **Endpoint:** `DELETE /objects/{id}`

### 1.3. Styles (Phong cách)

- **Lấy danh sách phong cách**
  - **Endpoint:** `GET /styles`
  - **Query:** `skip`, `limit`
  - **Response:** Mảng các đối tượng `{"id": int, "name": string, "prompt": string}`
- **Thêm phong cách mới**
  - **Endpoint:** `POST /styles`
  - **Body (JSON):** `{"name": string, "prompt": string}`
- **Lấy thông tin phong cách**
  - **Endpoint:** `GET /styles/{id}`
- **Cập nhật phong cách**
  - **Endpoint:** `PUT /styles/{id}`
  - **Body (JSON):** `{"name": string, "prompt": string}`
- **Xóa phong cách**
  - **Endpoint:** `DELETE /styles/{id}`
- **Tự động sinh Prompt cho Style** (Dùng AI Agent)
  - **Endpoint:** `POST /styles/{id}/generate-prompt`
  - **Response:** Trả về prompt được hệ thống AI tự sinh dựa vào dữ liệu RAG và phong cách tương ứng.

### 1.4. Documents (Tài liệu RAG)

- **Lấy danh sách tài liệu**
  - **Endpoint:** `GET /documents`
  - **Query:** `skip`, `limit`
  - **Response:** Mảng các đối tượng `{"id": int, "name": string, "style": string, "document_path": string}`
- **Thêm tài liệu mới**
  - **Endpoint:** `POST /documents`
  - **Body (JSON):** `{"name": string, "style": string, "document_path": string}`
- **Lấy chi tiết tài liệu**
  - **Endpoint:** `GET /documents/{id}`
- **Cập nhật tài liệu**
  - **Endpoint:** `PUT /documents/{id}`
  - **Body (JSON):** `{"name": string, "style": string, "document_path": string}`
- **Xóa tài liệu**
  - **Endpoint:** `DELETE /documents/{id}`
- **Reindex tài liệu vào VectorDB**
  - **Endpoint:** `POST /documents/{id}/reindex`
  - **Response:** `{"success": true, "total_chunks": int}`

### 1.5. File Upload

- **Endpoint:** `POST /upload`
- **Body (FormData):** `file: (UploadFile)`
- **Response:**
  ```json
  {
    "filename": "string",
    "file_path": "string",
    "file_size": int
  }
  ```

---

## 2. Generate Prompt Service

**Prefix:** `/prompt`

Cung cấp các API liên quan đến thao tác với LLM, Langchain và ChromaDB.

### 2.1. Health Check

- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "GeneratePromptService",
    "uptime_seconds": float,
    "time": "datetime"
  }
  ```

### 2.2. Generate Prompt

- **Endpoint:** `POST /generate-prompt`
- **Body (JSON):**
  ```json
  {
    "style": "string"
  }
  ```
- **Response:**
  ```json
  {
    "prompt": "Nội dung prompt đã sinh ra"
  }
  ```

### 2.3. RAG Documents Indexing

- **Index Document**
  - **Endpoint:** `POST /index-document`
  - **Body (JSON):**
    ```json
    {
      "style": "string",
      "document-id": "string",
      "document-path": "string"
    }
    ```
  - **Response:** `{"success": true, "total_chunks": int}`
- **Delete Document**
  - **Endpoint:** `POST /delete-document`
  - **Body (JSON):**
    ```json
    {
      "document-id": "string"
    }
    ```
  - **Response:** `{"success": true, "deleted_chunks": int}`

---

## 3. Generate 3D Model Service

**Prefix:** `/model`

Tích hợp với các dịch vụ AI như Trellis và Tripo3D để biến Text hoặc Image thành 3D Model.

### 3.1. Health Check

- **Endpoint:** `GET /health`

### 3.2. Generate 3D từ Object và Style (Text-to-3D qua Trellis)

- **Endpoint:** `POST /generate`
- **Body (JSON):**
  ```json
  {
    "object": "Chair",
    "style": "Modern"
  }
  ```
- **Response:** Trả về kết quả từ Trellis API.

### 3.3. Generate 3D bằng Custom Prompt (Text-to-3D qua Trellis)

- **Endpoint:** `POST /generate_custom`
- **Body (JSON):**
  ```json
  {
    "description": "A 3d model of a modern chair..."
  }
  ```

### 3.4. Generate Object 3D từ Ảnh (Image-to-3D qua Tripo3D)

- **Endpoint:** `POST /generate_from_image`
- **Body (FormData):** `file: (UploadFile)`
- **Mô tả:** Sử dụng Vision LLM để thẩm định ảnh. Nếu là đồ vật hợp lệ, đẩy sang Tripo3D kèm hardcoded prompt (bỏ qua background) để sinh object độc lập.
- **Response:** JSON trả về từ Tripo3D API.

### 3.5. Generate Room 3D (Text-to-3D qua Tripo3D)

- **Endpoint:** `POST /generate_room_from_image`
- **Body (FormData):** `file: (UploadFile)`
- **Mô tả:** Chấp nhận đầu vào nhưng bỏ qua ảnh. Gọi Text-To-3D bằng hardcoded prompt miêu tả 1 sa bàn căn phòng trống để làm môi trường.
- **Response:** JSON trả về từ Tripo3D API.

---

## 4. Phân phối Static Models

**Prefix:** `/models`

Cung cấp quyền truy cập để tải về các file `.glb` đã tạo thành công và lưu trữ.

- **Endpoint:** `GET /models/{filename.glb}`
- **Response:** Binary File

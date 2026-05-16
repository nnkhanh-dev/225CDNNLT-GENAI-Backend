# Hệ thống thiết kế nội thất 3D
## Giới thiệu
Hệ thống microservice cho phép người dụng tạo ra nội thất 3D dưới định dạng .glb. Các phương thức tạo nội thất bao gồm:
- Chọn phong cách và đối tượng
- Nhập mô tả vể nội thất
- Nhập ảnh 2D của nội thất

Ngoài ra hệ thống còn hỗ trợ AI Agent tạo prompt cho các phong cách nội thất nếu người dùng không có kỹ năng tự viết prompt
## Kiến trúc
![High level design](/.doc/architecture.png)
## Công nghệ
- 3D generation: Trellis
- Image understanding: Vision
- AI agent framework: Langchain
- Database: Chroma, PostgreSQL
- Serving: FastAPI, Docker
## Hướng dẫn 
Bước 1: Clone source code   
<pre>git clone https://github.com/nnkhanh-dev/225CDNNLT-GENAI-Backend.git</pre>
Bước 2: Thêm .env vào các service
- Generate 3D model service  
<pre>API_KEY = ""  
INVOKE_URL = "https://ai.api.nvidia.com/v1/genai/microsoft/trellis"  
VISION_INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"</pre>
- Option service
<pre>
DATABASE_URL=postgresql+psycopg2://postgres:change_this_password@postgres:5432/optionsdb
</pre>
- Global
<pre>
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_this_password
POSTGRES_DB=optionsdb
</pre>
Bước 3: Chạy dự án
<pre>docker compose up -d --build</pre>
## Đóng góp
Hệ thống thiết kề nội thất 3D là đồ án môn học 225CDNNLT của nhóm 3. Các thành viên bao gồm:
- Team lead: Nguyễn Nhật Khánh 
- Backend: Nguyễn Đức Chinh 
- Frontend: Nguyễn Anh Hoàng
- Technical writer: Nguyễn Duy Khoa

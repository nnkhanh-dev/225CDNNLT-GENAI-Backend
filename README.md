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
## Đóng góp
Hệ thống thiết kề nội thất 3D là đồ án môn học 225CDNNLT của nhóm 3. Các thành viên bao gồm:
- Team lead: Nguyễn Nhật Khánh 
- Backend: Nguyễn Đức Chinh 
- Frontend: Nguyễn Anh Hoàng
- Technical writer: Nguyễn Duy Khoa

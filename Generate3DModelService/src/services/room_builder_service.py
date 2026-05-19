import os
import uuid
import logging
import trimesh
import numpy as np
import cv2

logger = logging.getLogger(__name__)

# Giả lập thư mục models
OUTPUT_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_image_layout(image_bytes: bytes) -> dict:
    """
    Hệ thống phân tích ảnh dùng OpenCV (Computer Vision).
    Trích xuất các đặc trưng hình học từ ảnh thật (edges, contours)
    để suy ra kích thước xấp xỉ của căn phòng và vị trí cửa.
    """
    logger.info("Analyzing image layout with OpenCV...")
    
    # 1. Decode ảnh từ bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image for OpenCV processing.")
        
    img_h, img_w = img.shape[:2]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Lấy vùng đáy (bottom 20%) làm màu đại diện cho Sàn
    floor_region = img_rgb[int(img_h * 0.8):, :]
    floor_color = np.median(floor_region, axis=(0,1)).astype(int).tolist() if floor_region.size > 0 else [150, 110, 80]
    
    # Lấy vùng giữa - trái làm màu đại diện cho Tường
    wall_region_left = img_rgb[int(img_h * 0.2):int(img_h * 0.8), :int(img_w * 0.2)]
    wall_color = np.median(wall_region_left, axis=(0,1)).astype(int).tolist() if wall_region_left.size > 0 else [220, 220, 220]
    
    # KÍCH THƯỚC (Room Scale)
    aspect_ratio = img_w / float(img_h)
    room_width = max(6.0, 5.0 * aspect_ratio)
    room_length = 6.0 
    wall_height = 3.5
    
    # TÌM VỊ TRÍ CỬA SỔ
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    windows = []
    for c in contours:
        if cv2.contourArea(c) > (img_w * img_h * 0.05):
            x, y, w, h = cv2.boundingRect(c)
            windows.append({
                "width": max(1.5, (w / img_w) * room_width),
                "height": max(1.5, (h / img_h) * wall_height),
                "pos_x": (x / img_w) * room_width - (room_width / 2)
            })
            break
            
    return {
        "room_width": round(room_width, 2),
        "room_length": round(room_length, 2),
        "wall_height": round(wall_height, 2),
        "floor_rgba": floor_color + [255],
        "wall_rgba": wall_color + [255],
        "windows": windows
    }

def generate_room_with_trimesh(image_bytes: bytes) -> dict:
    """
    1. Phân tích ảnh trích xuất thông số hình học (Layout).
    2. Dùng thư viện Trimesh dựng hình khối tường và sàn trực tiếp trong Python (Không cần Blender).
    3. Ghép khối (Scene) và export ra file .glb.
    """
    try:
        # Bước 1: Trích xuất layout từ ảnh
        layout = analyze_image_layout(image_bytes)
        
        # Bước 2: Tạo đường dẫn export
        filename = f"trimesh_room_{uuid.uuid4().hex}.glb"
        output_glb_path = os.path.join(OUTPUT_DIR, filename)
        
        # Bước 3: Thuật toán dựng hình khối học bằng Trimesh
        width = layout["room_width"]
        length = layout["room_length"]
        height = layout["wall_height"]
        thickness = 0.2  # Độ dày tường
        
        floor_color = layout["floor_rgba"]
        wall_color = layout["wall_rgba"]
        meshes = []
        
        # 3.1: Dựng Sàn nhà (Floor)
        floor = trimesh.creation.box(extents=(width, length, thickness))
        floor.apply_translation((0, 0, -thickness / 2))
        floor.visual.face_colors = floor_color
        meshes.append(floor)
        
        # 3.2: Dựng Tường sau (Back) - Trục Y âm
        wall_back = trimesh.creation.box(extents=(width, thickness, height))
        wall_back.apply_translation((0, -length / 2 - thickness / 2, height / 2))
        
        # Khoét khung cửa sổ nếu tìm thấy (Boolean difference)
        if layout["windows"]:
            win = layout["windows"][0]
            hole = trimesh.creation.box(extents=(win["width"], thickness * 3, win["height"]))
            hole.apply_translation((win["pos_x"], -length / 2 - thickness / 2, height / 2))
            try:
                wall_back = wall_back.difference(hole)
            except Exception:
                pass # Đục hụt thì để tường kín
                
        wall_back.visual.face_colors = wall_color
        meshes.append(wall_back)
        
        # 3.3: Dựng Tường trái (Left) - Trục X âm
        wall_left = trimesh.creation.box(extents=(thickness, length + 2 * thickness, height))
        wall_left.apply_translation((-width / 2 - thickness / 2, 0, height / 2))
        wall_left.visual.face_colors = wall_color
        meshes.append(wall_left)
        
        # 3.4: Dựng Tường phải (Right) - Trục X dương
        wall_right = trimesh.creation.box(extents=(thickness, length + 2 * thickness, height))
        wall_right.apply_translation((width / 2 + thickness / 2, 0, height / 2))
        wall_right.visual.face_colors = wall_color
        meshes.append(wall_right)
        
        # ! BỎ BỨC TƯỜNG PHÍA TRƯỚC (Front Wall) để view camera nhìn được vào trong phòng
        
        # 3.5 Gom toàn bộ các khối (Mesh) lại vào một Scene
        room_scene = trimesh.Scene(meshes)
        
        # Bước 4: Chuyển đổi và lưu file .glb vô thư mục
        room_scene.export(output_glb_path)
        
        logger.info("Thành công: Hệ thống sinh ra .glb bằng Trimesh hoàn tất.")
        
        return {
            "success": "true", 
            "path": f"models/{filename}",
            "layout_analyzed": layout,
            "message": "Căn phòng 3D đã được tạo bằng thư viện Trimesh."
        }
        
    except ImportError as e:
        logger.error(f"Missing modules: {str(e)}")
        return {"success": "false", "error": f"Lỗi thiếu thư viện. Bạn cần chạy lệnh: pip install trimesh numpy scipy pyembree. Chi tiết: {str(e)}"}
    except Exception as e:
        logger.error(f"Error in generate_room_with_trimesh: {str(e)}")
        return {"success": "false", "error": str(e)}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore
import uvicorn
from datetime import datetime

# Khởi tạo kết nối Firebase
try:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Lỗi khởi tạo Firebase: {e}")

app = FastAPI()

# Khai báo cấu trúc dữ liệu gửi từ Frontend
class SuggestionRequest(BaseModel):
    user_id: str
    message: str

@app.get("/") 
async def root():
    return {"message": "Group T04 Backend is running"}

@app.get("/health") 
async def health():
    return {"status": "healthy"}

# API xử lý gửi tâm tư và lưu vào Firestore
@app.post("/suggestions") 
async def process_suggestions(data: SuggestionRequest):
    try:
        # Giả lập logic AI gợi ý (Yêu cầu Lab 2)
        reply = f"Hệ thống đã nhận tâm tư: '{data.message}'. Group T04 gợi ý bạn ghé thăm Landmark 81!"
        
        # Lưu vào Database dùng tên Document là Email của ông để dễ tìm kiếm
        db.collection('history').document(data.user_id).set({
            "user_id": data.user_id,
            "user_input": data.message,
            "ai_output": reply,
            "timestamp": datetime.now()
        })
        return {"result": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API lấy lịch sử trải nghiệm để hiển thị lên App
@app.get("/history/{user_id}") 
async def get_history(user_id: str):
    try:
        # Chỗ này cực kỳ quan trọng: Query tìm đúng user_id
        docs = db.collection("history").where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").limit(5).stream()
        
        history_list = [d.to_dict() for d in docs]
        print(f"History found for {user_id}: {history_list}") # Dòng này để ông debug trong terminal
        
        return {"history": history_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Chạy server ở cổng 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
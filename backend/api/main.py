from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
import sys
import os

# 将 backend 目录加入 path 以便引入 crawler 配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crawler

app = FastAPI(title="Dance King API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = pymysql.connect(**crawler.DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/api/dance-halls")
def get_nearby_dance_halls(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    db: pymysql.connections.Connection = Depends(get_db)
):
    """获取附近的舞厅，按距离排序"""
    try:
        with db.cursor() as cursor:
            # ST_Distance_Sphere 计算距离 (单位: 米)
            sql = """
                SELECT 
                    id, name, province, city, address, open_status, hot,
                    morning_hours, afternoon_hours, evening_hours, ticket_price, moment_text,
                    ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) as distance_m
                FROM dance_halls
                ORDER BY distance_m ASC
                LIMIT 50
            """
            # MySQL 8.0 SRID 4326: POINT(latitude longitude)
            point_str = f"POINT({latitude} {longitude})"
            cursor.execute(sql, (point_str,))
            results = cursor.fetchall()
            
            # 格式化距离供前端展示
            for r in results:
                dist = r['distance_m']
                if dist is not None:
                    if dist < 1000:
                        r['distance_display'] = f"{int(dist)}m"
                    else:
                        r['distance_display'] = f"{dist/1000:.1f}km"
                else:
                    r['distance_display'] = "未知"
            return {"code": 200, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ClaimRequest(BaseModel):
    venue_name: str
    city: str
    address: str
    applicant_name: str
    contact_phone: str
    contact_wechat: str
    relationship: str

@app.post("/api/claims")
def submit_claim(claim: ClaimRequest, db: pymysql.connections.Connection = Depends(get_db)):
    """提交认领申请"""
    try:
        with db.cursor() as cursor:
            sql = """
                INSERT INTO claim_applications 
                (user_id, venue_name, city, address, applicant_name, contact_phone, contact_wechat, relationship, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)
            """
            cursor.execute(sql, (
                1, # 模拟的当前登录 user_id
                claim.venue_name, claim.city, claim.address, claim.applicant_name,
                claim.contact_phone, claim.contact_wechat, claim.relationship
            ))
            db.commit()
            return {"code": 200, "message": "认领申请提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/trigger-sync")
def admin_trigger_sync():
    """手动触发数据同步"""
    try:
        res = crawler.trigger_sync(is_manual=True)
        return {"code": 200, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

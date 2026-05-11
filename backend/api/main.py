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

def init_reports_table():
    try:
        conn = pymysql.connect(**crawler.DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dance_hall_reports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    venue_name VARCHAR(100),
                    report_text VARCHAR(255),
                    reporter_name VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Insert some initial demo reports if table is empty
            cursor.execute("SELECT COUNT(*) as cnt FROM dance_hall_reports")
            if cursor.fetchone()['cnt'] == 0:
                cursor.executemany("""
                    INSERT INTO dance_hall_reports (venue_name, report_text, reporter_name)
                    VALUES (%s, %s, %s)
                """, [
                    ("星海壹号", "05-01 星海壹号 下午 暂停营业", "悉达多"),
                    ("迪乐汇歌舞厅", "05-01 迪乐汇歌舞厅 晚场满场，气氛极佳！", "舞王"),
                    ("金卡罗", "05-01 金卡罗 临时停业，大家别跑空了", "匿名用户")
                ])
            conn.commit()
        conn.close()
    except Exception as e:
        print("Failed to initialize reports table:", e)

init_reports_table()

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
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(20, description="Items per page", ge=1, le=100),
    open_status: int = Query(None, description="Filter by open status"),
    hot: int = Query(None, description="Filter by hot status"),
    db: pymysql.connections.Connection = Depends(get_db)
):
    """获取附近的舞厅，按距离排序"""
    try:
        with db.cursor() as cursor:
            # 1. 自动识别用户所在城市 (基于数据库中最近的一个点)
            point_str = f"POINT({latitude} {longitude})"
            cursor.execute("""
                SELECT city, ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) as dist
                FROM dance_halls 
                ORDER BY dist ASC 
                LIMIT 1
            """, (point_str,))
            closest = cursor.fetchone()
            
            # 如果最近的点在 100km 以内，我们认为用户属于该城市
            # 如果超过 100km，则认为当前位置不在数据库覆盖范围内，不进行强制城市过滤
            user_city = closest['city'] if closest and closest['dist'] < 100000 else None

            # 2. 构建查询条件
            where_clauses = ["1=1"]
            # 注意：第一个参数是用于 SELECT 中计算距离的 point_str
            query_params = [] 

            if user_city:
                where_clauses.append("city = %s")
                query_params.append(user_city)
            
            if open_status is not None:
                where_clauses.append("open_status = %s")
                query_params.append(open_status)
                
            if hot is not None:
                where_clauses.append("hot = %s")
                query_params.append(hot)

            where_str = " AND ".join(where_clauses)
            
            sql = f"""
                SELECT 
                    id, name, province, city, address, open_status, hot, cover,
                    morning_hours, afternoon_hours, evening_hours, ticket_price, moment_text,
                    ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) as distance_m
                FROM dance_halls
                WHERE {where_str}
                ORDER BY distance_m ASC
                LIMIT %s OFFSET %s
            """
            offset = (page - 1) * page_size
            # 最终参数列表：[SELECT中的point_str, WHERE中的参数..., LIMIT, OFFSET]
            params_for_execute = [point_str] + query_params + [page_size, offset]
            cursor.execute(sql, params_for_execute)
            results = cursor.fetchall()
            
            for r in results:
                dist = r['distance_m']
                if dist is not None:
                    if dist < 1000:
                        r['distance_display'] = f"{int(dist)}m"
                    else:
                        r['distance_display'] = f"{dist/1000:.1f}km"
                else:
                    r['distance_display'] = "未知"
            
            return {
                "code": 200, 
                "data": results,
                "current_city": user_city,
                "msg": f"已自动限定在 {user_city} 范围内" if user_city else "全网搜索"
            }
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

@app.get("/api/dance-halls/{hall_id}")
def get_dance_hall_detail(
    hall_id: int,
    latitude: float = Query(None, description="User latitude"),
    longitude: float = Query(None, description="User longitude"),
    db: pymysql.connections.Connection = Depends(get_db)
):
    """获取指定舞厅的详情"""
    try:
        with db.cursor() as cursor:
            if latitude is not None and longitude is not None:
                sql = """
                    SELECT 
                        id, name, province, city, address, open_status, hot, cover,
                        morning_hours, afternoon_hours, evening_hours, ticket_price, moment_text,
                        longitude, latitude,
                        ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) as distance_m
                    FROM dance_halls
                    WHERE id = %s
                """
                point_str = f"POINT({latitude} {longitude})"
                cursor.execute(sql, (point_str, hall_id))
            else:
                sql = """
                    SELECT 
                        id, name, province, city, address, open_status, hot, cover,
                        morning_hours, afternoon_hours, evening_hours, ticket_price, moment_text,
                        longitude, latitude, NULL as distance_m
                    FROM dance_halls
                    WHERE id = %s
                """
                cursor.execute(sql, (hall_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Dance hall not found")
                
            dist = result.get('distance_m')
            if dist is not None:
                if dist < 1000:
                    result['distance_display'] = f"{int(dist)}m"
                else:
                    result['distance_display'] = f"{dist/1000:.1f}km"
            else:
                result['distance_display'] = "未知"
                
            return {"code": 200, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=12800, reload=True)

@app.get("/api/reports")
def get_reports(latitude: float = None, longitude: float = None, db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            city = None
            if latitude is not None and longitude is not None:
                cursor.execute(
                    "SELECT city FROM dance_halls ORDER BY ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) LIMIT 1",
                    (f"POINT({longitude} {latitude})",)
                )
                closest = cursor.fetchone()
                if closest:
                    city = closest['city']

            if city:
                cursor.execute(
                    "SELECT name, open_status, moment_text, DATE_FORMAT(updated_at, '%m-%d') as date FROM dance_halls WHERE city = %s AND DATE(updated_at) = CURDATE() ORDER BY updated_at DESC LIMIT 2",
                    (city,)
                )
            else:
                cursor.execute(
                    "SELECT name, open_status, moment_text, DATE_FORMAT(updated_at, '%m-%d') as date FROM dance_halls WHERE DATE(updated_at) = CURDATE() ORDER BY updated_at DESC LIMIT 2"
                )
            
            halls = cursor.fetchall()
            results = []
            for h in halls:
                text = ""
                if h.get('moment_text'):
                    text = f"{h['name']} 最新公告：{h['moment_text']}"
                else:
                    status_str = "正常营业" if h['open_status'] == 1 else "休息中"
                    text = f"{h['name']} 今日状态：{status_str}"
                results.append({
                    "date": h['date'] or "最新",
                    "text": text
                })
            
            if not results:
                results = [
                    {"date": "今天", "text": "本市今日暂无更多最新动态"}
                ]
            return {"code": 200, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReportCreate(BaseModel):
    venue_name: str
    report_text: str
    reporter_name: str

@app.post("/api/reports")
def create_report(report: ReportCreate, db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO dance_hall_reports (venue_name, report_text, reporter_name) VALUES (%s, %s, %s)",
                (report.venue_name, report.report_text, report.reporter_name)
            )
            db.commit()
            return {"code": 200, "message": "上报成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import pymysql
import sys
import os
import json

# 将 backend 目录加入 path 以便引入 crawler 配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crawler
from api.security import verify_sign, aes_encrypt

app = FastAPI(title="Dance King API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Sign verification + response encryption for mini-program API routes."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-API and admin routes
        if not path.startswith("/api/") or path.startswith("/api/admin/"):
            return await call_next(request)

        # Collect params (query params for GET, body for POST)
        params = dict(request.query_params)

        if request.method == "POST":
            body = await request.body()
            if body:
                try:
                    body_json = json.loads(body)
                    if isinstance(body_json, dict):
                        # Decrypt body if encrypted
                        if "_encrypted" in body_json:
                            from api.security import aes_decrypt
                            decrypted = aes_decrypt(body_json["_encrypted"])
                            body_json = json.loads(decrypted)
                        params.update({k: str(v) for k, v in body_json.items() if k != "_encrypted"})
                        # Store decrypted body for route handlers
                        request._body = json.dumps(body_json).encode()
                except (json.JSONDecodeError, Exception):
                    pass

        if not verify_sign(params):
            return JSONResponse(status_code=403, content={"code": 403, "msg": "签名验证失败"})

        response = await call_next(request)

        # Encrypt response body
        if response.status_code == 200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            try:
                resp_data = json.loads(body)
                encrypted = aes_encrypt(json.dumps(resp_data, ensure_ascii=False))
                return JSONResponse(content={"data": encrypted})
            except Exception:
                pass

        return response


app.add_middleware(SecurityMiddleware)

def init_system_config_table():
    try:
        conn = pymysql.connect(**crawler.DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key VARCHAR(50) PRIMARY KEY,
                    config_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Failed to initialize system_config table:", e)

init_system_config_table()

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

            user_city = closest['city'] if closest and closest['dist'] < 100000 else None

            # 2. 构建查询条件
            where_clauses = []
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

            where_str = " AND ".join(where_clauses) if where_clauses else "1=1"

            sql = f"""
                SELECT
                    id, name, province, city, address, open_status, hot, cover,
                    morning_hours, afternoon_hours, evening_hours, ticket_price, moment_text,
                    ST_Distance_Sphere(location, ST_GeomFromText(%s, 4326)) as distance_m
                FROM dance_halls
                WHERE {where_str}
                HAVING distance_m < 100000
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

@app.get("/api/config")
def get_config(db: pymysql.connections.Connection = Depends(get_db)):
    """获取系统配置（公开接口）"""
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT config_key, config_value FROM system_config")
            rows = cursor.fetchall()
            config = {row['config_key']: row['config_value'] for row in rows}
            return {"code": 200, "data": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ConfigItem(BaseModel):
    config_key: str
    config_value: str

@app.get("/api/admin/config")
def admin_get_config(db: pymysql.connections.Connection = Depends(get_db)):
    """获取系统配置（管理接口）"""
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT config_key, config_value FROM system_config")
            rows = cursor.fetchall()
            config = {row['config_key']: row['config_value'] for row in rows}
            return {"code": 200, "data": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/config")
def admin_set_config(item: ConfigItem, db: pymysql.connections.Connection = Depends(get_db)):
    """设置系统配置（管理接口）"""
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO system_config (config_key, config_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE config_value = %s",
                (item.config_key, item.config_value, item.config_value)
            )
            db.commit()
            return {"code": 200, "message": "配置已更新"}
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
                    (f"POINT({latitude} {longitude})",)
                )
                closest = cursor.fetchone()
                if closest:
                    city = closest['city']

            results = []

            # 1. 舞厅动态 (from dance_halls) — 只展示今天和昨天的公告
            if city:
                cursor.execute(
                    "SELECT name, open_status, moment_text, DATE_FORMAT(moment_updated_at, '%%m-%%d') as date FROM dance_halls WHERE city = %s AND moment_updated_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) ORDER BY moment_updated_at DESC LIMIT 3",
                    (city,)
                )
            else:
                cursor.execute(
                    "SELECT name, open_status, moment_text, DATE_FORMAT(moment_updated_at, '%%m-%%d') as date FROM dance_halls WHERE moment_updated_at >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) ORDER BY moment_updated_at DESC LIMIT 3",
                    ()
                )
            for h in cursor.fetchall():
                text = ""
                if h.get('moment_text'):
                    text = f"{h['name']}：{h['moment_text']}"
                else:
                    status_str = "正常营业" if h['open_status'] == 1 else "休息中"
                    text = f"{h['name']}：{status_str}"
                results.append({"date": h['date'] or "最新", "text": text})

            # 2. 用户上报 (from dance_hall_reports)
            if city:
                cursor.execute(
                    "SELECT venue_name, report_text, DATE_FORMAT(created_at, '%%m-%%d') as date FROM dance_hall_reports WHERE city = %s AND DATE(created_at) = CURDATE() ORDER BY created_at DESC LIMIT 3",
                    (city,)
                )
            else:
                cursor.execute(
                    "SELECT venue_name, report_text, DATE_FORMAT(created_at, '%%m-%%d') as date FROM dance_hall_reports WHERE DATE(created_at) = CURDATE() ORDER BY created_at DESC LIMIT 3",
                    ()
                )
            for r in cursor.fetchall():
                results.append({"date": r['date'] or "最新", "text": f"{r['venue_name']}：{r['report_text']}"})


            if not results:
                results = [
                    {"date": "今天", "text": "本市今日暂无更多最新动态"}
                ]
            return {"code": 200, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


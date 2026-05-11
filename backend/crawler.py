import requests
import json
import time
import pymysql

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')), 
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 舞图图的固定伪装头
HEADERS = {
    'Host': 'api.dancehallmap.com:59876',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254186b) XWEB/19481',
    'xweb_xhr': '1',
    'Content-Type': 'application/json',
    'Referer': 'https://servicewechat.com/wx9239d3944daed5bc/87/page-frame.html',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

BASE_URL = "https://api.dancehallmap.com:59876/api/dance-hall"

def fetch_overview(open_status=1):
    """获取指定状态的舞厅列表 (1:营业, 0:停业)"""
    url = f"{BASE_URL}/daily-overview?openStatus={open_status}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        if data.get('code') == 200:
            result = []
            # API returns a dict: {"CityName": [hall1, hall2], ...}
            for key, halls in data.get('data', {}).items():
                if isinstance(halls, list):
                    result.extend(halls)
            return result
        else:
            print(f"[Error] 获取 {open_status} 状态列表失败: {data}")
            return []
    except Exception as e:
        print(f"[Exception] 请求失败: {e}")
        return []

def fetch_detail(hall_id):
    """获取单个舞厅详细信息"""
    url = f"{BASE_URL}/detail/{hall_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        if data.get('code') == 200:
            return data.get('data', {})
        else:
            print(f"[Error] 获取详情 {hall_id} 失败: {data}")
            return None
    except Exception as e:
        print(f"[Exception] 详情请求失败 {hall_id}: {e}")
        return None

def sync_data(is_manual=False):
    """
    数据抓取与入库同步主逻辑
    """
    trigger_type = "手动触发" if is_manual else "定时任务触发"
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始同步数据 ({trigger_type})...")
    
    # 建立数据库连接
    connection = pymysql.connect(**DB_CONFIG)
    
    try:
        with connection.cursor() as cursor:
            # 1. 抓取所有舞厅
            open_halls = fetch_overview(open_status=1)
            for h in open_halls:
                h['derived_status'] = 1
                
            closed_halls = fetch_overview(open_status=0)
            for h in closed_halls:
                h['derived_status'] = 0
                
            all_halls = open_halls + closed_halls
            print(f" -> 接口共返回 {len(all_halls)} 个舞厅。")
            
            # 为了测试速度，如果是大量数据，这里需要控制频率，或者只抓取未入库的详情
            # MVP版本我们遍历所有的 ID 更新状态并入库
            success_count = 0
            
            for index, hall_overview in enumerate(all_halls):
                hall_id = hall_overview.get('id')
                status = hall_overview.get('derived_status', 0)
                
                # 获取详细信息
                detail = fetch_detail(hall_id)
                if not detail:
                    continue
                    
                # 准备入库字段
                name = detail.get('name', '')
                province = detail.get('province', '')
                city = detail.get('city', '')
                address = detail.get('address', '')
                longitude = detail.get('longitude', 0)
                latitude = detail.get('latitude', 0)
                hot = detail.get('hot', 0)
                
                morning_hours = detail.get('morningOpenCloseTime', '')
                afternoon_hours = detail.get('noonOpenCloseTime', '')
                evening_hours = detail.get('eveningOpenCloseTime', '')
                ticket_price = detail.get('ticket', '')
                moment_text = detail.get('moment', '')
                cover = detail.get('cover', '')
                
                # 插入或更新 SQL
                sql = """
                INSERT INTO `dance_halls` (
                    `id`, `name`, `province`, `city`, `address`, 
                    `longitude`, `latitude`, `location`,
                    `open_status`, `hot`, `cover`,
                    `morning_hours`, `afternoon_hours`, `evening_hours`,
                    `ticket_price`, `moment_text`
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, ST_GeomFromText(%s, 4326),
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    `name`=VALUES(`name`), `province`=VALUES(`province`), `city`=VALUES(`city`),
                    `address`=VALUES(`address`),
                    `longitude`=VALUES(`longitude`), `latitude`=VALUES(`latitude`),
                    `location`=VALUES(`location`),
                    `open_status`=VALUES(`open_status`), `hot`=VALUES(`hot`), `cover`=VALUES(`cover`),
                    `morning_hours`=VALUES(`morning_hours`), `afternoon_hours`=VALUES(`afternoon_hours`), `evening_hours`=VALUES(`evening_hours`),
                    `ticket_price`=VALUES(`ticket_price`), `moment_text`=VALUES(`moment_text`)
                """
                
                # MySQL 8.0 中 SRID 4326 的格式要求为 POINT(latitude longitude)
                point_str = f"POINT({latitude} {longitude})"
                
                try:
                    cursor.execute(sql, (
                        hall_id, name, province, city, address,
                        longitude, latitude, point_str,
                        status, hot, cover,
                        morning_hours, afternoon_hours, evening_hours,
                        ticket_price, moment_text
                    ))
                    success_count += 1
                    
                    if index > 0 and index % 10 == 0:
                        print(f" -> 已处理 {index}/{len(all_halls)} 个舞厅")
                        connection.commit()
                        
                except Exception as db_err:
                    print(f"[DB Error] 插入/更新 {hall_id} 失败: {db_err}")
                
                # 降低抓取频率防止风控
                time.sleep(0.5)

            connection.commit()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 成功更新 {success_count} 条记录到数据库。")
            return {"synced_count": success_count}
            
    finally:
        connection.close()

trigger_sync = sync_data

if __name__ == "__main__":
    sync_data(is_manual=True)


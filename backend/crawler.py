import requests
import json
import time
import hashlib
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

def generate_hall_id(source_id):
    """用原始 API ID + 固定字符串的 MD5 前12位 hex 转整数作为 ID"""
    raw = f"dance_king_{source_id}"
    hex_str = hashlib.md5(raw.encode()).hexdigest()[:12]
    return int(hex_str, 16)

def parse_moment_date(text):
    """从 moment_text 开头解析日期，返回 datetime 或 None"""
    if not text:
        return None
    import re
    from datetime import datetime
    year = datetime.now().year
    m = re.match(r'(\d{1,2})月(\d{1,2})日', text)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        try:
            d = datetime(year, month, day)
            if d.date() > datetime.now().date():
                d = datetime(year - 1, month, day)
            return d
        except ValueError:
            return None
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

            # 过滤垃圾数据（黑名单）
            SPAM_NAMES = ['全成都中高端商K可安排', '商务KTV']

            for index, hall_overview in enumerate(all_halls):
                source_id = hall_overview.get('id')
                status = hall_overview.get('derived_status', 0)

                # 获取详细信息
                detail = fetch_detail(source_id)
                if not detail:
                    continue

                # 准备入库字段
                name = detail.get('name', '')
                if name in SPAM_NAMES:
                    continue
                province = detail.get('province', '')
                city = detail.get('city', '')
                address = detail.get('address', '')

                # 用原始 API ID + 固定字符串生成自己的 ID
                hall_id = generate_hall_id(source_id)
                longitude = detail.get('longitude', 0)
                latitude = detail.get('latitude', 0)
                hot = detail.get('hot', 0)
                
                morning_hours = detail.get('morningOpenCloseTime', '')
                afternoon_hours = detail.get('noonOpenCloseTime', '')
                evening_hours = detail.get('eveningOpenCloseTime', '')
                ticket_price = detail.get('ticket', '')
                moment_text = detail.get('moment', '')
                # 过滤垃圾信息
                SPAM_KEYWORDS = ['商K可安排']
                for kw in SPAM_KEYWORDS:
                    if kw in moment_text:
                        moment_text = ''
                        break
                cover = detail.get('cover', '')

                # 计算 moment_updated_at
                if moment_text:
                    parsed = parse_moment_date(moment_text)
                    if parsed:
                        # 公告有日期 → 用解析出的日期
                        moment_updated_at = parsed
                    else:
                        # 公告没日期 → 先设 NULL，SQL 中按内容变化决定
                        moment_updated_at = None
                else:
                    # 没有公告 → 不动
                    moment_updated_at = None

                # 插入或更新 SQL
                sql = """
                INSERT INTO `dance_halls` (
                    `id`, `name`, `province`, `city`, `address`,
                    `longitude`, `latitude`, `location`,
                    `open_status`, `hot`, `cover`,
                    `morning_hours`, `afternoon_hours`, `evening_hours`,
                    `ticket_price`, `moment_text`, `moment_updated_at`
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, ST_GeomFromText(%s, 4326),
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    `name`=VALUES(`name`), `province`=IF(VALUES(`province`)='', `province`, VALUES(`province`)), `city`=IF(VALUES(`city`)='', `city`, VALUES(`city`)),
                    `address`=VALUES(`address`),
                    `longitude`=VALUES(`longitude`), `latitude`=VALUES(`latitude`),
                    `location`=VALUES(`location`),
                    `open_status`=VALUES(`open_status`), `hot`=VALUES(`hot`), `cover`=VALUES(`cover`),
                    `morning_hours`=VALUES(`morning_hours`), `afternoon_hours`=VALUES(`afternoon_hours`), `evening_hours`=VALUES(`evening_hours`),
                    `ticket_price`=VALUES(`ticket_price`), `moment_text`=VALUES(`moment_text`),
                    `moment_updated_at`=CASE
                        WHEN VALUES(`moment_text`) = '' THEN `moment_updated_at`
                        WHEN VALUES(`moment_updated_at`) IS NOT NULL THEN VALUES(`moment_updated_at`)
                        WHEN `moment_text` <> VALUES(`moment_text`) THEN NOW()
                        ELSE `moment_updated_at`
                    END
                """

                # MySQL 8.0 中 SRID 4326 的格式要求为 POINT(latitude longitude)
                point_str = f"POINT({latitude} {longitude})"

                try:
                    cursor.execute(sql, (
                        hall_id, name, province, city, address,
                        longitude, latitude, point_str,
                        status, hot, cover,
                        morning_hours, afternoon_hours, evening_hours,
                        ticket_price, moment_text, moment_updated_at
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

            # 自动补齐空 city/province 字段
            backfill_location_fields(cursor)
            connection.commit()

            return {"synced_count": success_count}
            
    finally:
        connection.close()

trigger_sync = sync_data

CITIES = [
    "北京市","天津市","上海市","重庆市",
    "成都市","杭州市","西安市","南京市","嘉兴市","郑州市","苏州市","长沙市",
    "武汉市","广州市","宁波市","无锡市","合肥市","福州市","济南市","青岛市",
    "大连市","沈阳市","昆明市","贵阳市","南宁市","太原市","石家庄市","哈尔滨市",
    "长春市","兰州市","呼和浩特市","乌鲁木齐市","海口市","厦门市","东莞市",
    "佛山市","温州市","绍兴市","金华市","台州市","湖州市","徐州市","常州市",
    "南通市","扬州市","镇江市","泰州市","盐城市","淮安市","连云港市","宿迁市",
    "惠州市","珠海市","中山市","江门市","汕头市","洛阳市","南阳市","保定市","邯郸市",
    "深圳市","泉州市","漳州市","烟台市","潍坊市","临沂市","济宁市","淄博市","威海市",
    "宜昌市","襄阳市","荆州市","株洲市","湘潭市","衡阳市","岳阳市","常德市",
    "绵阳市","德阳市","宜宾市","南充市","泸州市","达州市","乐山市","眉山市",
    "鞍山市","运城市","鸡西市","晋城市","山南市","阿克苏市","防城港市","钦州市","河池市",
    "贵港市","桂林市","柳州市","玉林市","北海市","银川市","马鞍山市","安庆市","阜阳市",
]

PROVINCES = [
    ("北京市", "北京"), ("天津市", "天津"), ("上海市", "上海"), ("重庆市", "重庆"),
    ("河北省", "河北"), ("山西省", "山西"), ("辽宁省", "辽宁"), ("吉林省", "吉林"),
    ("黑龙江省", "黑龙江"), ("江苏省", "江苏"), ("浙江省", "浙江"), ("安徽省", "安徽"),
    ("福建省", "福建"), ("江西省", "江西"), ("山东省", "山东"), ("河南省", "河南"),
    ("湖北省", "湖北"), ("湖南省", "湖南"), ("广东省", "广东"), ("海南省", "海南"),
    ("四川省", "四川"), ("贵州省", "贵州"), ("云南省", "云南"), ("陕西省", "陕西"),
    ("甘肃省", "甘肃"), ("青海省", "青海"), ("台湾省", "台湾"),
    ("内蒙古自治区", "内蒙古"), ("广西壮族自治区", "广西"), ("西藏自治区", "西藏"),
    ("宁夏回族自治区", "宁夏"), ("新疆维吾尔自治区", "新疆"),
]

# 直辖市 city -> province 映射
MUNICIPALITY_PROVINCE = {
    "北京市": "北京市", "天津市": "天津市", "上海市": "上海市", "重庆市": "重庆市",
}

import re

def extract_city(address):
    """从 address 中正则提取城市名（XX市/XX自治州）"""
    if not address:
        return ''
    # 匹配 "XX市"、"XX自治州"、"XX盟"、"XX地区"、"XX县"（兜底）
    m = re.search(r'([\u4e00-\u9fff]{2,6}(?:市|自治州|盟|地区))', address)
    if m:
        return m.group(1)
    return ''

def extract_province(address):
    """从 address 中正则提取省份名"""
    if not address:
        return ''
    m = re.search(r'([\u4e00-\u9fff]{2,6}(?:省|自治区|特别行政区))', address)
    if m:
        return m.group(1)
    # 直辖市
    m2 = re.search(r'((?:北京|天津|上海|重庆)市?)', address)
    if m2:
        name = m2.group(1)
        if not name.endswith('市'):
            name += '市'
        return name
    return ''

def backfill_city(cursor):
    cursor.execute("SELECT id, address FROM dance_halls WHERE city IS NULL OR city = ''")
    rows = cursor.fetchall()
    updated = 0
    for r in rows:
        city = extract_city(r['address'] or '')
        if city:
            cursor.execute("UPDATE dance_halls SET city = %s WHERE id = %s", (city, r['id']))
            updated += 1
    if updated > 0:
        print(f" -> 自动补齐 {updated} 条记录的 city 字段")

def normalize_province(province):
    """将短名(如'四川')标准化为全称(如'四川省')"""
    for prov_name, prov_short in PROVINCES:
        if province == prov_short or province == prov_name:
            return prov_name
    return province

def backfill_location_fields(cursor):
    """补齐并标准化 city 和 province 字段"""
    cursor.execute("SELECT id, address, city, province FROM dance_halls")
    rows = cursor.fetchall()
    city_updated = 0
    province_updated = 0
    for r in rows:
        addr = r['address'] or ''
        city = r['city'] or ''
        province = r['province'] or ''

        # 补齐 city：正则提取
        if not city:
            city = extract_city(addr)
            if city:
                city_updated += 1

        # 补齐 province：正则提取
        if not province:
            province = extract_province(addr)
            if not province:
                province = normalize_province(province)

        # 标准化 province（短名 -> 全称）
        if province:
            province = normalize_province(province)

        if city != (r['city'] or '') or province != (r['province'] or ''):
            cursor.execute("UPDATE dance_halls SET city = %s, province = %s WHERE id = %s", (city, province, r['id']))
            if city != (r['city'] or ''):
                city_updated += 1
            if province != (r['province'] or ''):
                province_updated += 1

    if city_updated > 0 or province_updated > 0:
        print(f" -> 自动补齐/标准化 {city_updated} 条 city, {province_updated} 条 province")

if __name__ == "__main__":
    sync_data(is_manual=True)


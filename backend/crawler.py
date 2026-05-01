import requests
import json
import time

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
            return data['data'].get('danceHallList', [])
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

def trigger_sync(is_manual=False):
    """
    触发数据同步 (此函数既可以被Crontab定时调用，也可以被前端管理后台的API手动触发)
    """
    trigger_type = "手动触发" if is_manual else "定时任务触发"
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始同步数据 ({trigger_type})...")
    
    # 1. 抓取所有营业舞厅
    open_halls = fetch_overview(open_status=1)
    print(f" -> 抓取到 {len(open_halls)} 个营业中的舞厅。")
    
    # 2. 抓取所有停业舞厅
    closed_halls = fetch_overview(open_status=0)
    print(f" -> 抓取到 {len(closed_halls)} 个停业的舞厅。")
    
    all_halls = open_halls + closed_halls
    
    # 在真实环境中，这里会执行如下逻辑：
    # 1. 将上面拉取到的ID与数据库对比，更新 status
    # 2. 如果发现有新ID，调用 fetch_detail(id) 并 INSERT 进数据库
    
    # 演示：抓取第一个舞厅的详情看看格式
    if all_halls:
        sample_id = all_halls[0].get('id')
        print(f" -> 正在获取样本舞厅ID ({sample_id}) 的详细数据...")
        detail = fetch_detail(sample_id)
        if detail:
            print(f" -> 详情获取成功: {detail.get('name')} | 票价: {detail.get('ticket')}")

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 同步任务执行完毕。\n")
    return {"status": "success", "synced_count": len(all_halls)}

if __name__ == "__main__":
    # 本地测试可以直接运行此脚本
    trigger_sync(is_manual=True)

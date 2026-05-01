from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def run_tests():
    print("--- 正在测试 API 接口 ---")
    
    # 1. 测试获取附近的舞厅 (假设用户在成都天府广场: 30.6586, 104.0648)
    print("\n1. 测试 GET /api/dance-halls")
    response = client.get("/api/dance-halls", params={"latitude": 30.6586, "longitude": 104.0648})
    assert response.status_code == 200
    data = response.json()
    print(f"-> Returns status code 200")
    print(f" -> 共返回了 {len(data['data'])} 家舞厅")
    if data['data']:
        first_hall = data['data'][0]
        print(f" -> 离我最近的一家: {first_hall['name']} | 距离: {first_hall['distance_display']}")
        
    # 2. 测试认领提交接口
    print("\n2. 测试 POST /api/claims")
    claim_payload = {
        "venue_name": "测试音乐酒吧",
        "city": "成都市",
        "address": "高新区天府大道1号",
        "applicant_name": "张老板",
        "contact_phone": "13800138000",
        "contact_wechat": "zhang_boss",
        "relationship": "老板"
    }
    response = client.post("/api/claims", json=claim_payload)
    assert response.status_code == 200
    print("-> Claim submitted successfully:", response.json())

    # 3. (可选) 测试同步接口
    # response = client.post("/api/admin/trigger-sync")
    # print("同步结果:", response.json())
    
    print("\n-> All API tests passed!")

if __name__ == "__main__":
    run_tests()

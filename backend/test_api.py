import requests

HEADERS = {
    'Host': 'api.dancehallmap.com:59876',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254186b) XWEB/19481',
    'xweb_xhr': '1',
    'Content-Type': 'application/json',
    'Referer': 'https://servicewechat.com/wx9239d3944daed5bc/87/page-frame.html',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

url = "https://api.dancehallmap.com:59876/api/dance-hall/daily-overview?openStatus=1"
response = requests.get(url, headers=HEADERS, verify=False)
print(response.status_code)
try:
    print(response.json())
except:
    print(response.text)

import json
import sys
import urllib.request

WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/2312a890-bed5-49d7-a327-49051b5e65ff"
LOG_FILE = "/var/log/happy-dance-crawler.log"

def send_alert(failed_at):
    # 读取最后20行日志
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            log_tail = "".join(lines[-20:])
    except Exception:
        log_tail = "无法读取日志文件"

    msg = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "ALERT 舞王爬虫执行失败"},
                "template": "red"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**时间:** {failed_at}"}},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**最近日志:**\n```\n{log_tail}\n```"}}
            ]
        }
    }
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(msg).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_alert(sys.argv[1] if len(sys.argv) > 1 else "unknown")

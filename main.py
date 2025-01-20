from app import app, run_bot
from uvicorn import run
from threading import Thread
import logging

# 创建一个自定义日志过滤器
class RequestFilter(logging.Filter):
    def filter(self, record):
        # 过滤掉 /healthy 路径的日志
        if "/hello" in record.getMessage():
            return False
        return True

# 配置日志
logger = logging.getLogger("uvicorn.access")
handler = logging.StreamHandler()
handler.addFilter(RequestFilter())  # 添加过滤器
logger.addHandler(handler)

def start_app():
    run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    # start_app()
    Thread(target=start_app, daemon=True).start()
    run_bot()

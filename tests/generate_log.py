import random
import time
from datetime import datetime, timedelta

# 配置
LOG_COUNT = 50000  # 生成日志行数
OUTPUT_FILE = "massive_app.log"
ERROR_FILE = "error_only.log"

# 模拟数据池
USERS = ["user_a", "admin", "guest", "system", "api_client_007"]
IPS = ["192.168.1.10", "10.0.0.5", "172.16.0.99", "203.0.113.5"]
ENDPOINTS = ["/api/v1/login", "/api/v1/orders", "/api/v1/products", "/health", "/api/v1/db/query"]

# 模拟错误信息
ERROR_MESSAGES = [
    "ConnectionRefusedError: [Errno 111] Connection refused",
    "java.lang.NullPointerException: Cannot invoke method on null object",
    "TimeoutError: The read operation timed out",
    "KeyError: 'user_id' not found in request payload",
    "DatabaseError: (psycopg2.OperationalError) could not connect to server",
    "OutOfMemoryError: Java heap space",
    "PermissionDenied: Access denied for user 'root'@'localhost'"
]


def generate_timestamp(base_time, offset_seconds):
    return (base_time + timedelta(seconds=offset_seconds)).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def generate_logs():
    print(f"🚀 正在生成 {LOG_COUNT} 行日志...")

    base_time = datetime.now() - timedelta(hours=5)  # 从5小时前开始

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_app, \
            open(ERROR_FILE, "w", encoding="utf-8") as f_err:

        for i in range(LOG_COUNT):
            # 1. 生成时间戳
            ts = generate_timestamp(base_time, i * 0.1)  # 每隔 0.1 秒一条

            # 2. 决定日志级别 (权重：INFO 70%, WARN 20%, ERROR 10%)
            rand_val = random.random()
            if rand_val > 0.90:
                level = "ERROR"
                msg = random.choice(ERROR_MESSAGES)
            elif rand_val > 0.70:
                level = "WARN"
                msg = f"High latency detected: {random.randint(500, 2000)}ms"
            else:
                level = "INFO"
                msg = f"Request processed successfully for {random.choice(USERS)}"

            # 3. 组装标准格式日志
            log_line = f"{ts} [{level}] [Thread-{random.randint(1, 10)}] - {msg}\n"

            # 4. 写入文件
            f_app.write(log_line)

            # 如果是错误日志，额外写入一个堆栈跟踪（模拟真实报错）
            if level == "ERROR":
                f_err.write(log_line)
                # 模拟堆栈
                stack_trace = f"    at com.example.service.{random.choice(ENDPOINTS).replace('/', '.')}(Unknown Source)\n"
                f_err.write(stack_trace)

    print(f"✅ 生成完毕！")
    print(f"   - 混合日志: {OUTPUT_FILE}")
    print(f"   - 错误日志: {ERROR_FILE}")


if __name__ == "__main__":
    generate_logs()
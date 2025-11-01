#!/usr/bin/env python3
"""使用Python内置http.server的简单认证服务器"""

import http.server
import socketserver
import json
import urllib.parse
from urllib.parse import parse_qs
import hashlib
import time

PORT = 8000

# 模拟用户数据库
USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "email": "admin@example.com",
        "full_name": "管理员"
    },
    "test": {
        "id": 2,
        "username": "test",
        "password": hashlib.sha256("test123".encode()).hexdigest(),
        "email": "test@example.com",
        "full_name": "测试用户"
    }
}

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "message": "悦恩人机共写平台 API",
                "status": "ok",
                "endpoints": {
                    "login": "POST /api/v1/auth/login",
                    "register": "POST /api/v1/auth/register",
                    "health": "GET /health"
                }
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"status": "healthy", "timestamp": int(time.time())}
            self.wfile.write(json.dumps(response).encode())

        else:
            super().do_GET()

    def do_POST(self):
        """处理POST请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data)
        except:
            self.send_error(400, "Invalid JSON")
            return

        # CORS headers
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        # 登录
        if self.path == "/api/v1/auth/login":
            username = data.get("username", "")
            password = data.get("password", "")

            user = USERS.get(username)
            if not user:
                response = {"error": True, "message": "用户不存在"}
                self.wfile.write(json.dumps(response).encode())
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user["password"] != password_hash:
                response = {"error": True, "message": "密码错误"}
                self.wfile.write(json.dumps(response).encode())
                return

            # 返回用户信息
            response = {
                "access_token": {"token": "demo_token", "expires": int(time.time()) + 3600},
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"]
                }
            }
            self.wfile.write(json.dumps(response).encode())

        # 注册
        elif self.path == "/api/v1/auth/register":
            username = data.get("username", "")
            password = data.get("password", "")

            if username in USERS:
                response = {"error": True, "message": "用户名已存在"}
                self.wfile.write(json.dumps(response).encode())
                return

            # 创建新用户
            user_id = len(USERS) + 1
            USERS[username] = {
                "id": user_id,
                "username": username,
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "email": data.get("email", ""),
                "full_name": data.get("full_name", "")
            }

            user = USERS[username]
            response = {
                "access_token": {"token": "demo_token", "expires": int(time.time()) + 3600},
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"]
                }
            }
            self.wfile.write(json.dumps(response).encode())

        else:
            response = {"error": True, "message": "API endpoint not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    print("="*60)
    print("悦恩人机共写平台 - 简化认证服务器")
    print("="*60)
    print(f"服务器地址: http://localhost:{PORT}")
    print("演示用户:")
    print("  1. 用户名: admin, 密码: admin123")
    print("  2. 用户名: test, 密码: test123")
    print("="*60)

    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        print(f"服务器启动在端口 {PORT}...")
        httpd.serve_forever()

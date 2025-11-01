"""
API文档生成器
自动生成API文档、测试用例和API规范
"""
import os
import json
import inspect
from typing import Dict, List, Any, Optional, Type, get_type_hints
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .config import settings


class APIDocumentationGenerator:
    """API文档生成器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.routes = []
        self.schemas = {}
        self.endpoints = {}
        
        # 收集所有路由
        self._collect_routes()
        
        # 收集所有模型
        self._collect_schemas()
    
    def _collect_routes(self):
        """收集所有路由"""
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                self.routes.append(route)
            elif isinstance(route, APIRouter):
                for sub_route in route.routes:
                    if isinstance(sub_route, APIRoute):
                        self.routes.append(sub_route)
    
    def _collect_schemas(self):
        """收集所有模型"""
        # 从路由中提取模型
        for route in self.routes:
            if hasattr(route, 'response_model') and route.response_model:
                self._add_schema(route.response_model)
            
            if hasattr(route, 'body_field') and route.body_field:
                field_info = route.body_field.field_info
                if hasattr(field_info, 'annotation'):
                    self._add_schema_from_annotation(field_info.annotation)
            
            # 从依赖中提取模型
            if hasattr(route, 'dependencies'):
                for dependency in route.dependencies:
                    if hasattr(dependency, 'call') and hasattr(dependency.call, '__annotations__'):
                        for param_name, param_type in dependency.call.__annotations__.items():
                            self._add_schema_from_annotation(param_type)
    
    def _add_schema(self, model: Type[BaseModel]):
        """添加模型到模式集合"""
        if model and issubclass(model, BaseModel):
            model_name = model.__name__
            if model_name not in self.schemas:
                self.schemas[model_name] = self._generate_schema(model)
    
    def _add_schema_from_annotation(self, annotation: Any):
        """从注解中添加模型"""
        # 处理泛型类型
        origin = getattr(annotation, '__origin__', None)
        args = getattr(annotation, '__args__', [])
        
        if origin is list and args:
            self._add_schema_from_annotation(args[0])
        elif origin is dict and len(args) >= 2:
            self._add_schema_from_annotation(args[1])
        elif hasattr(annotation, '__origin__') and hasattr(annotation, '__args__'):
            # 处理其他泛型类型
            for arg in annotation.__args__:
                self._add_schema_from_annotation(arg)
        elif inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            self._add_schema(annotation)
    
    def _generate_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """生成模型模式"""
        schema = model.schema()
        
        # 添加额外的元数据
        schema["x-model-name"] = model.__name__
        schema["x-module"] = model.__module__
        
        # 添加字段描述
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                # Pydantic v2 使用 model_fields 替代 __fields__
                field_info = model.model_fields.get(field_name)
                if field_info:
                    # Pydantic v2 中 field_info 直接包含描述和示例
                    if hasattr(field_info, 'description') and field_info.description:
                        field_schema["description"] = field_info.description
                    if hasattr(field_info, 'examples') and field_info.examples:
                        field_schema["example"] = field_info.examples[0] if isinstance(field_info.examples, list) else field_info.examples
        
        return schema
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        openapi_spec: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": self.app.title,
                "description": self.app.description,
                "version": self.app.version,
                "contact": {
                    "name": "悦恩人机共写平台团队",
                    "email": "support@yueen.com"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "开发环境"
                },
                {
                    "url": "https://api.yueen.com",
                    "description": "生产环境"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {}
            },
            "tags": []
        }
        
        # 添加路径
        for route in self.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                path = route.path
                methods = list(route.methods)
                
                # 为每个方法生成操作
                for method in methods:
                    if method in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                        operation = self._generate_operation(route, method)
                        
                        # 添加到路径
                        if path not in openapi_spec["paths"]:
                            openapi_spec["paths"][path] = {}
                        
                        openapi_spec["paths"][path][method.lower()] = operation
        
        # 添加模式
        openapi_spec["components"]["schemas"] = self.schemas
        
        # 添加标签
        tags = set()
        for route in self.routes:
            if hasattr(route, 'tags'):
                tags.update(route.tags)
        
        openapi_spec["tags"] = [{"name": tag} for tag in sorted(tags)]
        
        return openapi_spec
    
    def _generate_operation(self, route: APIRoute, method: str) -> Dict[str, Any]:
        """生成操作"""
        operation: Dict[str, Any] = {
            "operationId": f"{method.lower()}_{route.path.replace('/', '_').replace('{', '').replace('}', '')}",
            "summary": route.summary or f"{method} {route.path}",
            "description": route.description or "",
            "tags": route.tags or [],
            "responses": {}
        }
        
        # 添加参数
        if hasattr(route, 'dependant') and route.dependant:
            params = self._extract_parameters(route.dependant)
            if params:
                operation["parameters"] = params
        
        # 添加请求体
        if method in ["POST", "PUT", "PATCH"] and hasattr(route, 'body_field'):
            body_field = route.body_field
            if body_field:
                content_type = "application/json"
                schema_ref = {"$ref": f"#/components/schemas/{body_field.type_.__name__}"}
                
                operation["requestBody"] = {
                    "content": {
                        content_type: {
                            "schema": schema_ref
                        }
                    },
                    "required": True
                }
        
        # 添加响应
        if hasattr(route, 'response_model') and route.response_model:
            response_model_name = route.response_model.__name__
            schema_ref = {"$ref": f"#/components/schemas/{response_model_name}"}
            
            operation["responses"]["200"] = {
                "description": "成功响应",
                "content": {
                    "application/json": {
                        "schema": schema_ref
                    }
                }
            }
        
        # 添加错误响应
        operation["responses"]["400"] = {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
        
        operation["responses"]["401"] = {
            "description": "未授权",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
        
        operation["responses"]["403"] = {
            "description": "禁止访问",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
        
        operation["responses"]["404"] = {
            "description": "资源不存在",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
        
        operation["responses"]["500"] = {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
        
        return operation
    
    def _extract_parameters(self, dependant: Any) -> List[Dict[str, Any]]:
        """提取参数"""
        params = []
        
        # 这里简化处理，实际应该更复杂
        if hasattr(dependant, 'call') and hasattr(dependant.call, '__annotations__'):
            for param_name, param_type in dependant.call.__annotations__.items():
                param = {
                    "name": param_name,
                    "in": "query",
                    "required": True,
                    "schema": {"$ref": f"#/components/schemas/{param_type.__name__}"}
                }
                params.append(param)
        
        return params
    
    def generate_postman_collection(self) -> Dict[str, Any]:
        """生成Postman集合"""
        collection: Dict[str, Any] = {
            "info": {
                "name": f"{self.app.title} API",
                "description": self.app.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # 添加请求
        for route in self.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        item = self._generate_postman_item(route, method)
                        collection["item"].append(item)
        
        return collection
    
    def _generate_postman_item(self, route: APIRoute, method: str) -> Dict[str, Any]:
        """生成Postman项"""
        url: Dict[str, Any] = {
            "raw": "{{baseUrl}}" + route.path,
            "host": ["{{baseUrl}}"],
            "path": []
        }
        
        # 添加路径部分
        path_parts = route.path.split('/')
        for part in path_parts:
            if part:
                if part.startswith('{') and part.endswith('}'):
                    param_name = part[1:-1]
                    url["path"].append(f":{param_name}")
                else:
                    url["path"].append(part)
        
        # 替换路径参数
        for part in path_parts:
            if part.startswith('{') and part.endswith('}'):
                param_name = part[1:-1]
                url["raw"] = url["raw"].replace(part, "{{" + param_name + "}}")
        
        item: Dict[str, Any] = {
            "name": f"{method} {route.path}",
            "request": {
                "method": method,
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "url": url
            }
        }
        
        # 添加请求体
        if method in ["POST", "PUT", "PATCH"] and hasattr(route, 'body_field'):
            body_field = route.body_field
            if body_field:
                # 简化处理，实际应该更复杂
                item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps({
                        "example": "示例数据"
                    }),
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
        
        return item
    
    def save_documentation(self, output_dir: str = "docs/api"):
        """保存文档"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存OpenAPI规范
        openapi_spec = self.generate_openapi_spec()
        with open(os.path.join(output_dir, "openapi.json"), "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
        
        # 保存Postman集合
        postman_collection = self.generate_postman_collection()
        with open(os.path.join(output_dir, "postman_collection.json"), "w", encoding="utf-8") as f:
            json.dump(postman_collection, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown文档
        self._generate_markdown_docs(output_dir)
        
        # 生成HTML文档
        self._generate_html_docs(output_dir)
    
    def _generate_markdown_docs(self, output_dir: str):
        """生成Markdown文档"""
        openapi_spec = self.generate_openapi_spec()
        
        with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {openapi_spec['info']['title']}\n\n")
            f.write(f"{openapi_spec['info']['description']}\n\n")
            f.write("## API规范\n\n")
            f.write(f"版本: {openapi_spec['info']['version']}\n\n")
            
            # 添加服务器信息
            f.write("## 服务器\n\n")
            for server in openapi_spec.get("servers", []):
                f.write(f"- **{server['description']}**: {server['url']}\n")
            f.write("\n")
            
            # 添加标签
            f.write("## 标签\n\n")
            for tag in openapi_spec.get("tags", []):
                f.write(f"- {tag['name']}\n")
            f.write("\n")
            
            # 添加路径
            f.write("## 路径\n\n")
            for path, path_item in openapi_spec.get("paths", {}).items():
                f.write(f"### {path}\n\n")
                
                for method, operation in path_item.items():
                    f.write(f"#### {method.upper()} {operation.get('summary', '')}\n\n")
                    f.write(f"{operation.get('description', '')}\n\n")
                    
                    # 添加参数
                    if "parameters" in operation:
                        f.write("**参数:**\n\n")
                        f.write("| 名称 | 位置 | 类型 | 必需 | 描述 |\n")
                        f.write("|------|--------|------|--------|--------|\n")
                        
                        for param in operation["parameters"]:
                            param_name = param.get("name", "")
                            param_in = param.get("in", "")
                            param_required = param.get("required", False)
                            param_desc = param.get("description", "")
                            
                            f.write(f"| {param_name} | {param_in} | - | {'是' if param_required else '否'} | {param_desc} |\n")
                        f.write("\n")
                    
                    # 添加响应
                    if "responses" in operation:
                        f.write("**响应:**\n\n")
                        for status_code, response in operation["responses"].items():
                            f.write(f"- **{status_code}**: {response.get('description', '')}\n")
                        f.write("\n")
    
    def _generate_html_docs(self, output_dir: str):
        """生成HTML文档"""
        openapi_spec = self.generate_openapi_spec()
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css">
    <style>
        html {{ box-sizing: border-box; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        .swagger-ui .topbar {{ display: none; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: 'openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>
        """
        
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_template.format(title=openapi_spec["info"]["title"]))


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.routes = []
        
        # 收集所有路由
        self._collect_routes()
    
    def _collect_routes(self):
        """收集所有路由"""
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                self.routes.append(route)
            elif isinstance(route, APIRouter):
                for sub_route in route.routes:
                    if isinstance(sub_route, APIRoute):
                        self.routes.append(sub_route)
    
    def generate_test_cases(self, output_dir: str = "tests/api"):
        """生成测试用例"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成测试文件
        for route in self.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        test_file = self._generate_test_file(route, method)
                        
                        # 保存测试文件
                        file_name = f"test_{method.lower()}_{route.path.replace('/', '_').replace('{', '').replace('}', '')}.py"
                        file_path = os.path.join(output_dir, file_name)
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(test_file)
    
    def _generate_test_file(self, route: APIRoute, method: str) -> str:
        """生成测试文件"""
        path = route.path
        function_name = f"test_{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"
        
        # 生成测试代码
        test_code = f"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def {function_name}():
    \"\"\"\"测试 {method} {path}\"\"\"
    response = client.{method.lower()}(
        "{path}"
    )
    
    # 检查响应状态码
    assert response.status_code == 200
    
    # 检查响应内容
    # assert response.json() == {{}}
    
    print(f"测试通过: {method} {path}")


if __name__ == "__main__":
    {function_name}()
        """
        
        return test_code
    
    def generate_pytest_config(self, output_dir: str = "tests"):
        """生成pytest配置"""
        pytest_config = """
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
"""
        
        with open(os.path.join(output_dir, "pytest.ini"), "w", encoding="utf-8") as f:
            f.write(pytest_config)
        
        # 生成conftest.py
        conftest_content = """
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
"""
        
        with open(os.path.join(output_dir, "conftest.py"), "w", encoding="utf-8") as f:
            f.write(conftest_content)


# 创建全局实例
def generate_api_documentation(app: FastAPI, output_dir: str = "docs/api"):
    """生成API文档"""
    doc_generator = APIDocumentationGenerator(app)
    doc_generator.save_documentation(output_dir)
    print(f"API文档已生成到: {output_dir}")


def generate_test_cases(app: FastAPI, output_dir: str = "tests/api"):
    """生成测试用例"""
    test_generator = TestCaseGenerator(app)
    test_generator.generate_test_cases(output_dir)
    test_generator.generate_pytest_config(output_dir.replace("/api", ""))
    print(f"测试用例已生成到: {output_dir}")
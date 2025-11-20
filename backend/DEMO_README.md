# 企业文档生成端到端Demo

## 概述

本Demo演示了如何使用AI Section Framework生成三个企业环境管理文档：
- 环境风险评估报告
- 突发环境事件应急预案
- 应急资源调查报告

## 文件说明

### 核心文件

1. **sample_enterprise.json** - 示例企业数据
   - 包含完整的企业信息，覆盖所有26个AI段落的需求
   - 包括基本信息、生产工艺、环境信息、合规信息、应急资源等

2. **demo_generate_documents.py** - Demo主程序
   - 使用Mock AI服务生成文档
   - 避免真实AI调用，确保Demo稳定运行
   - 生成所有26个AI段落和三个HTML文档

3. **run_demo.sh** - 运行脚本
   - 提供简单的命令行界面
   - 自动检查环境和依赖
   - 显示执行结果和文件位置

### 输出文件

所有生成的文件保存在 `test_output/` 目录：

1. **risk_assessment_demo.html** - 环境风险评估报告
2. **emergency_plan_demo.html** - 突发环境事件应急预案
3. **resource_report_demo.html** - 应急资源调查报告
4. **ai_sections_demo.json** - 生成的AI段落信息

## 使用方法

### 方法1：使用运行脚本（推荐）

```bash
cd backend
chmod +x run_demo.sh
./run_demo.sh
```

### 方法2：直接运行Python脚本

```bash
cd backend
python3 demo_generate_documents.py
```

## 技术特点

### AI Section Framework
- 使用26个预定义的AI段落
- 每个段落都有专门的system prompt和user template
- 支持不同文档类型的段落过滤

### Mock AI服务
- 避免真实AI调用的成本和延迟
- 提供稳定的演示环境
- 包含所有26个段落的示例内容

### 文档生成
- 使用Jinja2模板引擎
- 支持复杂的条件渲染
- 生成完整的HTML格式文档

## 扩展使用

### 使用真实AI服务

要使用真实AI服务，可以修改 `demo_generate_documents.py`：

```python
# 注释掉Mock替换
# processor.call_llm = mock_call_llm
# processor.render_user_template = mock_render_user_template
# processor.postprocess_ai_output = mock_postprocess_ai_output
```

### 修改企业数据

编辑 `sample_enterprise.json` 文件，替换为真实的企业信息。

### 自定义AI段落

修改 `backend/app/prompts/config/ai_sections_complete.json` 文件，添加或修改AI段落配置。

## 依赖要求

- Python 3.7+
- Jinja2
- 项目依赖包（见requirements.txt）

## 故障排除

1. **权限错误**：确保运行脚本有执行权限
   ```bash
   chmod +x run_demo.sh
   ```

2. **Python路径错误**：确保在backend目录下运行
   ```bash
   cd backend
   python3 demo_generate_documents.py
   ```

3. **依赖缺失**：安装必要的Python包
   ```bash
   pip install -r requirements.txt
   ```

## 输出示例

成功运行后，您将看到类似以下的输出：

```
============================================================
企业文档生成Demo - 端到端演示
============================================================
✓ 成功加载企业数据：示例化工有限公司
✓ 文档生成器初始化成功

开始生成AI段落...
✓ 成功生成 26 个AI段落

生成的AI段落：
   1. enterprise_overview
   2. location_description
   ...
  26. conclusion

开始生成文档...
✓ 所有文档生成成功
✓ 风险评估报告已保存：test_output/risk_assessment_demo.html
✓ 应急预案已保存：test_output/emergency_plan_demo.html
✓ 应急资源调查报告已保存：test_output/resource_report_demo.html
✓ AI段落信息已保存：test_output/ai_sections_demo.json
```

## 查看结果

使用任何现代浏览器打开生成的HTML文件即可查看完整的文档：

- 风险评估报告：包含企业概况、环境风险识别、风险分析等
- 应急预案：包含应急组织、应急措施、应急处置卡等
- 应急资源调查报告：包含调查过程、差距分析、结论等

每个文档都包含了完整的目录结构、专业内容和格式化排版。
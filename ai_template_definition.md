🌿 环保应急预案 AI 共创模板定义文档

版本： v1.0
作者： 杨开迪
用途： 指导 AI（GLM）在逻辑层中实现基于模板和企业数据的应急预案自动生成系统。

一、文档设计目标

实现标准化模板与企业数据的动态融合；

让 AI 能理解哪些部分为固定八股文模板、哪些为动态生成部分；

支持模块化生成、富文本输出；

最终结果可编辑、可复核、可导出。

二、总体架构设计
模板定义（template schema）
        ↓
企业数据（enterprise data）
        ↓
AI 生成逻辑（prompt + template merge）
        ↓
富文本编辑器（Tiptap / Editor.js）
        ↓
导出（PDF / Word / Markdown）

三、模板层设计（Template Schema）

模板结构建议使用 JSON 文件或数据库存储。

模板示例（emergency_plan_template.json）
{
  "document_type": "突发环境事件应急预案",
  "sections": [
    {
      "id": "1",
      "title": "总则",
      "prompt": "生成应急预案的总则部分，包括编制目的、依据、原则等内容。",
      "variables": []
    },
    {
      "id": "2",
      "title": "企业概况",
      "prompt": "根据企业的基本信息生成企业概况内容。",
      "variables": ["enterprise_name", "industry_type", "address", "main_products", "employees_count"]
    },
    {
      "id": "3",
      "title": "环境风险分析",
      "prompt": "结合危险物质和周边环境信息生成风险识别与分级说明。",
      "variables": ["hazardous_materials", "storage_amounts", "surrounding_receptors"]
    },
    {
      "id": "4",
      "title": "应急组织机构及职责",
      "prompt": "根据组织结构数据生成指挥体系及职责说明。",
      "variables": ["emergency_team_structure"]
    },
    {
      "id": "5",
      "title": "应急资源与保障",
      "prompt": "生成企业内部应急物资、设备及外部支援单位的说明。",
      "variables": ["emergency_resources"]
    },
    {
      "id": "6",
      "title": "应急响应程序",
      "prompt": "生成各类突发事件的响应流程与防控措施。",
      "variables": ["incident_types", "response_steps"]
    },
    {
      "id": "7",
      "title": "信息报告与后期处置",
      "prompt": "生成事故报告程序与善后措施。",
      "variables": []
    },
    {
      "id": "8",
      "title": "附录",
      "prompt": "生成附录部分，包括表格、清单、联系方式等。",
      "variables": ["appendices"]
    }
  ]
}

四、企业数据结构（Enterprise Data Schema）

企业在前端填写的表单数据可结构化保存如下：

{
  "enterprise_info": {
    "enterprise_name": "云南生物制药有限公司",
    "industry_type": "化工制造",
    "address": "云南省昆明市盘龙区××工业园",
    "main_products": "医用乙醇、甲醇溶剂",
    "employees_count": 132
  },
  "hazardous_materials": [
    {"name": "甲醇", "max_storage_ton": 8.5, "threshold_ton": 10, "ratio": 0.85},
    {"name": "乙醇", "max_storage_ton": 5.0, "threshold_ton": 10, "ratio": 0.5}
  ],
  "surrounding_receptors": ["居民区", "水源地", "绿化带"],
  "emergency_team_structure": [
    {"role": "总指挥", "name": "张三", "contact": "138xxxx"},
    {"role": "副总指挥", "name": "李四", "contact": "137xxxx"}
  ],
  "emergency_resources": {
    "internal": [
      {"name": "防毒面具", "count": 30},
      {"name": "消防沙", "count": 10}
    ],
    "external": [
      {"unit": "消防大队", "contact": "119"},
      {"unit": "环保局应急办", "contact": "0871-xxxxxx"}
    ]
  },
  "incident_types": ["化学品泄漏", "火灾", "爆炸"],
  "response_steps": [
    "立即启动应急预案",
    "疏散人员并隔离区域",
    "通知应急指挥部",
    "采取防止污染扩散措施"
  ]
}

五、AI 生成逻辑（Prompt 示例）

AI 每生成一个章节，执行以下伪逻辑：

for section in template.sections:
    content = call_ai_model(
        prompt=section.prompt,
        variables=fill_from_enterprise_data(section.variables)
    )
    render_to_editor(section.title, content)

示例 Prompt
你是环保应急预案的专业撰写助手。
根据以下企业信息和模板内容，生成“环境风险分析”章节，语言应正式、符合《HJ941-2018》标准。

企业信息：
{enterprise_info}

危险化学品：
{hazardous_materials}

周边环境：
{surrounding_receptors}

请生成完整、专业的文字描述。

六、富文本编辑器结构

在前端编辑器中，为每个章节提供独立可编辑区：

左侧目录树（章节标题）

右侧富文本区（可显示AI生成文本）

工具栏包含：

✨ 重新生成本节

🪄 改写语气

📑 插入模板

💾 保存为版本

七、生成与导出

支持导出为 Markdown / Word / PDF；

支持 JSON Schema 回传（便于后续审校和修改记录）。

八、扩展与复用

未来可扩展：

环评报告模板（同样结构）

数据飞轮训练（AI不断优化模板生成效果）

行业专用模块（污水厂、制药厂、危险废物处理等）

✅ 总结

此模板定义文档旨在帮助 AI 和开发工程师理解应急预案的结构化生成机制。
模板内容固定，企业数据动态注入，AI负责拼接与润色。
最终结果由人类复核、编辑器修改，确保合规与专业性。
# AI Section Framework（可扩展架构规范 · V1）

> 面向对象：后端开发（GLM4.6）、Prompt 维护人、模板维护人
> 目标：用**声明式配置**驱动 26 个（及未来更多）AI 段落的生成与注入，不把逻辑写死在代码里。

---

## 1. 设计目标（Design Goals）

1. **可扩展**：AI 段落可以随时增加/删除/禁用，而不用改核心代码。
2. **可配置**：所有 AI 段落的 System Prompt、User Prompt 模板、字段依赖都写在配置文件里（`ai_sections.json`），而不是散落在代码中。
3. **可追踪**：每个 AI 段落有自己的 `version`、`document`、`description`，方便后续迭代。
4. **松耦合**：

   * Jinja 模板仅通过 `{{ ai_sections.xxx }}` 取值
   * 后端只管：加载配置 → 渲染 prompt → 调用模型 → 回填 `ai_sections`
5. **多模型兼容**：未来可以同时支持讯飞星火 / GPT / GLM 等，通过配置选择 `model`。

---

## 2. 配置文件：`ai_sections.json` 规范

### 2.1 文件位置（建议）

```text
backend/app/prompts/config/ai_sections.json
```

### 2.2 顶层结构

```jsonc
{
  "sections": {
    "<section_key>": {
      "...": "..."
    }
  }
}
```

* `section_key` 必须与 Jinja 模板中的变量名一致：
  `{{ ai_sections.enterprise_overview }}` → key = `"enterprise_overview"`

### 2.3 section 配置结构（标准版）

```jsonc
{
  "sections": {
    "enterprise_overview": {
      "enabled": true,
      "document": "risk_assessment",  // 所属文档：risk_assessment / emergency_plan / resource_report
      "description": "企业概况，总体性技术描述",
      "version": 1,
      "model": "xunfei_spark_v4",     // 可选：xunfei_spark_v4 / gpt_xxx / glm_xxx
      "fields": [
        "basic_info.company_name",
        "basic_info.industry_category",
        "basic_info.operation.production_status",
        "production_process.products",
        "production_process.raw_materials",
        "production_process.hazardous_chemicals",
        "environment_info.wastewater",
        "environment_info.waste_gas"
      ],
      "system_prompt": "（这里填入该段落专属的 System Prompt 文本）",
      "user_template": "（这里填入带 {字段占位符} 的 User Prompt 模板）"
    },

    "location_description": {
      "enabled": true,
      "document": "risk_assessment",
      "description": "地理位置及交通条件描述",
      "version": 1,
      "model": "xunfei_spark_v4",
      "fields": [
        "basic_info.address",
        "environment_info.nearby_receivers"
      ],
      "system_prompt": "...",
      "user_template": "..."
    }

    // ... 其余 24 个 section
  }
}
```

### 2.4 字段含义说明

* `enabled`:

  * `true`：该段落启用，参与生成
  * `false`：该段落暂时禁用（模板中变量可留空或用占位文本）

* `document`:

  * `"risk_assessment"`：环境风险评估报告
  * `"emergency_plan"`：突发环境事件应急预案
  * `"resource_report"`：应急资源调查报告

* `description`: 人类可读说明，方便后续维护。

* `version`: Prompt 配置版本号，后续改动时递增（1, 2, 3…）。

* `model`: 指定默认调用的模型标识，**实现时允许忽略**，先统一用星火。

* `fields`:

  * 仅用于提示/文档用途
  * 表示该 section 所依赖的 JSON 字段路径
  * 不强制校验，但可以用于调试和提示缺失字段

* `system_prompt`:

  * 为该段落专门优化的 System Prompt（已经在第二部分 A/B/C 里定义）

* `user_template`:

  * 模板字符串，内部使用 `{xxx}` 占位符
  * 运行时通过企业数据填充得到最终 user prompt
  * 占位符映射规则由后端实现（见下文 4）

---

## 3. 运行时整体流程（后端框架）

### 3.1 核心流程概览

1. 前端提交：`enterprise_data`（符合 `emergency_plan.json` Schema 的对象）
2. 后端加载 `ai_sections.json` → 得到全部 section 配置
3. 后端调用 `build_ai_sections(enterprise_data)`：

   * 遍历所有 `enabled=true` 的 sections
   * 用 `user_template` + `enterprise_data` → 渲染出 user prompt
   * 组合 `system_prompt` + `user_prompt` → 调用模型
   * 将结果存入 `ai_sections[section_key]`
4. 构造模板上下文：`ctx = {**enterprise_data, "ai_sections": ai_sections}`
5. 调用 Jinja 模板：

   * 风险评估：`template_risk_plan.jinja2`
   * 应急预案：`template_emergency_plan.jinja2`
   * 资源调查：`template_resource_investigation.jinja2`
6. 返回 3 段 HTML/Markdown/纯文本给前端预览/导出。

---

## 4. Prompt 渲染规范（user_template → 实际 prompt）

### 4.1 基础要求

* `user_template` 内使用 **花括号占位符**：`{basic_info.company_name}`
* 支持嵌套字段（对象）和列表（用预处理生成字符串）
* 对不存在或为 null 的字段：用安全描述或留空，由模板片段负责兜底

### 4.2 建议的渲染机制（伪代码）

```python
def render_user_template(template_str: str, enterprise_data: dict) -> str:
    """
    将 user_template 中的 {xxx.yyy} 占位符替换为 enterprise_data 中的实际值（转为字符串）。
    对于复杂结构（list/object），建议先用一个 helper 把它转成简要字符串。
    """
```

建议实现 `get_value_by_path(data, path: str)`：

```python
value = get_value_by_path(enterprise_data, "basic_info.company_name")
```

* `value` 为 `None` 时，返回空字符串 `""` 或字符串 `"（企业未提供相关信息）"` 由你决定。
* `list` 类型，可用一个 helper 按一定格式序列化，例如：

```python
def summarize_list(value):
    # 如产品列表、危化品列表等
    # 生成类似：“主要产品包括：xxx、yyy 等。”
```

GLM4.6 完全可以根据你前面那份字段规范写出这些 helper。

---

## 5. AI Section 生成流程（build_ai_sections）

### 5.1 建议函数签名

```python
def build_ai_sections(enterprise_data: dict, sections_config: dict) -> dict:
    """
    输入：
      - enterprise_data: 企业信息对象
      - sections_config: 从 ai_sections.json 中读取的 "sections" 字典

    输出：
      - ai_sections: { section_key: generated_text }
    """
```

### 5.2 伪代码逻辑

```python
def build_ai_sections(enterprise_data, sections_config):
    ai_sections = {}

    for key, cfg in sections_config.items():
        if not cfg.get("enabled", True):
            # 可以选择写空字符串或占位提醒
            ai_sections[key] = ""
            continue

        system_prompt = cfg.get("system_prompt", "")
        user_template = cfg.get("user_template", "")

        user_prompt = render_user_template(user_template, enterprise_data)

        # TODO: 调用讯飞星火（此处可先用 mock/stub）
        generated = call_llm(
            model=cfg.get("model", "xunfei_spark_v4"),
            system=system_prompt,
            user=user_prompt
        )

        ai_sections[key] = postprocess_ai_output(generated)

    return ai_sections
```

> `postprocess_ai_output` 可用于去掉首尾空行、过滤非法字符等。

---

## 6. 模板解析机制（Template Introspection，可选但推荐）

目标：自动检查模板中出现了哪些 `ai_sections.xxx`，与配置文件对比，给出诊断信息（缺少配置 / 配置未使用）。

### 6.1 实现思路

* 用简单正则扫描模版文本：

  * 模式：`{{\s*ai_sections\.([a-zA-Z0-9_]+)\s*}}`
* 收集所有出现的 section_key 列表
* 与 `ai_sections.json` 中的 key 集合做对比：

```python
used_in_templates = {...}   # 来自 jinja 模板扫描
defined_in_config = set(sections_config.keys())

missing_in_config = used_in_templates - defined_in_config
unused_in_template = defined_in_config - used_in_templates
```

### 6.2 诊断用例

* 如果 `missing_in_config` 非空：

  * 说明模板中有 AI 段落未在配置中定义 → 应提醒开发者补齐配置或删除变量。

* 如果 `unused_in_template` 非空：

  * 说明配置中有 AI 段落未被任何模板使用 → 可以选择以后清理或保留。

可以把这做成一个命令行工具或单元测试，比如：

```bash
python -m backend.app.prompts.check_ai_sections
```

---

## 7. 文档生成 API 设计（建议）

### 7.1 统一生成接口

```http
POST /api/docs/generate_all
```

* Body: `enterprise_data` JSON
* 逻辑：

  * 加载 `ai_sections.json`
  * `ai_sections = build_ai_sections(enterprise_data, sections_config)`
  * 渲染 3 个模板
* 返回：

```json
{
  "risk_report": "<html or markdown>",
  "emergency_plan": "<html or markdown>",
  "resource_report": "<html or markdown>",
  "ai_sections_used": ["enterprise_overview", "water_environment_impact", ...]
}
```

### 7.2 单段调试接口（可选）

```http
POST /api/docs/generate_section
```

* Body:

```json
{
  "section_key": "air_environment_impact",
  "enterprise_data": { ... }
}
```

* 用于调试单个段落效果。

---

## 8. Prompt 版本管理（version）

### 8.1 简单策略（推荐）

* `version` 字段手动维护，修改某段 prompt 时，`version += 1`
* 可以在日志中记录：

  * section_key
  * version
  * 调用时间
  * 模型返回文本长度等

### 8.2 后续可扩展

未来你可以：

* 新建 `ai_sections_v2.json`，并在配置中选择使用不同版本
* 或者在配置中增加 `prompt_profile` 概念（例如 `default` / `expert` / `simple`）

---

## 9. 新增 / 删除 AI 段落的流程

### 9.1 新增一个段落（例如 `climate_risk`）

1. 在 Jinja 模板中插入：
   `{{ ai_sections.climate_risk }}`
2. 在 `ai_sections.json` 中增加：

```jsonc
"climate_risk": {
  "enabled": true,
  "document": "risk_assessment",
  "description": "气候相关环境风险分析",
  "version": 1,
  "model": "xunfei_spark_v4",
  "fields": ["basic_info.address", "..."],
  "system_prompt": "（新段落的 system prompt）",
  "user_template": "（新段落的 user_template）"
}
```

3. 运行模板检查工具（如有）：

   * 确认模板与配置匹配
4. 无需修改核心代码，框架自动生效。

### 9.2 删除 / 暂停某个段落

* 若只是暂时不用：

  * 将 `enabled` 设置为 `false`
* 若彻底不用：

  1. 从模板中删除 `{{ ai_sections.xxx }}`
  2. 从 `ai_sections.json` 中删除对应配置
  3. 运行检查工具确保无遗留引用

---

## 10. 多模型 / 多风格扩展（预留）

当前你使用的是 **风格 B（专家评审型）**，未来如果你需要：

* 客户展示版（简化语气）
* 内部风险排查版（更技术）

可以在 `ai_sections.json` 中扩展：

```jsonc
"enterprise_overview": {
  "profiles": {
    "expert_review": {
      "model": "xunfei_spark_v4",
      "system_prompt": "...",
      "user_template": "..."
    },
    "client_friendly": {
      "model": "gpt_4o",
      "system_prompt": "...",
      "user_template": "..."
    }
  }
}
```

当前 V1 可以先不实现 `profiles`，但架构已为其预留空间。



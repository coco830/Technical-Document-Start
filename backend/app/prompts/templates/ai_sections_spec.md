# AI段落插槽规范

本文档定义了三个Jinja2模板中所有AI段落插槽的含义、用途和参考字段路径，用于指导AI生成内容。

## 1. 环境风险评估报告 (template_risk_plan.jinja2)

### 1.1 企业概况
- **插槽名称**: `ai_sections.enterprise_overview`
- **用途**: 根据企业基本情况，生成企业概况描述
- **参考字段**: 
  - `enterprise_name` - 企业名称
  - `enterprise_info.establishment_date` - 企业成立时间
  - `enterprise_info.environmental_investment` - 环保投资
  - `enterprise_info.main_construction` - 主要建设内容
  - `enterprise_info.production_capacity` - 主要生产能力
  - `products` - 主要产品列表
  - `enterprise_info.work_system` - 工作制度

### 1.2 地理位置及交通
- **插槽名称**: `ai_sections.location_description`
- **用途**: 描述企业地理位置及周边交通情况
- **参考字段**:
  - `enterprise_name` - 企业名称
  - `longitude` - 经度
  - `latitude` - 纬度
  - `enterprise_info.address` - 企业地址
  - `enterprise_info.transportation` - 交通情况

### 1.3 地形地貌
- **插槽名称**: `ai_sections.terrain_description`
- **用途**: 描述企业所在区域的地形地貌特征
- **参考字段**:
  - `enterprise_info.terrain` - 地形地貌信息
  - `enterprise_info.topography` - 地形特征

### 1.4 气象条件
- **插槽名称**: `ai_sections.weather_description`
- **用途**: 描述企业所在区域的气象条件
- **参考字段**:
  - `enterprise_info.climate` - 气候条件
  - `enterprise_info.meteorology` - 气象信息

### 1.5 水文
- **插槽名称**: `ai_sections.hydrology_description`
- **用途**: 描述企业所在区域的水文情况
- **参考字段**:
  - `enterprise_info.hydrology` - 水文信息
  - `water_receptors` - 水环境受体信息

### 1.6 生产工艺
- **插槽名称**: `ai_sections.production_process_description`
- **用途**: 描述企业主要生产工艺流程
- **参考字段**:
  - `enterprise_info.production_process` - 生产工艺描述
  - `raw_materials` - 原材料信息
  - `products` - 产品信息
  - `main_equipment` - 主要设备信息

### 1.7 安全生产管理
- **插槽名称**: `ai_sections.safety_management_description`
- **用途**: 描述企业安全生产管理情况
- **参考字段**:
  - `enterprise_info.safety_management` - 安全生产管理情况
  - `emergency_materials` - 应急物资信息

### 1.8 水环境影响分析
- **插槽名称**: `ai_sections.water_environment_impact`
- **用途**: 分析企业对水环境的影响
- **参考字段**:
  - `enterprise_name` - 企业名称
  - `pollutant_emissions` - 污染物排放信息
  - `wastewater_management` - 废水管理信息
  - `water_receptors` - 水环境受体信息

### 1.9 大气环境影响分析
- **插槽名称**: `ai_sections.air_environment_impact`
- **用途**: 分析企业对大气环境的影响
- **参考字段**:
  - `pollutant_emissions` - 污染物排放信息
  - `air_receptors` - 大气环境受体信息

### 1.10 噪声环境影响分析
- **插槽名称**: `ai_sections.noise_environment_impact`
- **用途**: 分析企业噪声对环境的影响
- **参考字段**:
  - `pollutant_emissions` - 污染物排放信息
  - `main_equipment` - 主要设备信息

### 1.11 固体废物影响分析
- **插槽名称**: `ai_sections.solid_waste_impact`
- **用途**: 分析企业固体废物对环境的影响
- **参考字段**:
  - `pollutant_emissions` - 污染物排放信息
  - `waste_management` - 废物管理信息

### 1.12 风险管理结论
- **插槽名称**: `ai_sections.risk_management_conclusion`
- **用途**: 总结企业环境风险管理制度和应急资源情况
- **参考字段**:
  - `hazardous_materials` - 危险物质信息
  - `emergency_materials` - 应急物资信息
  - `risk_level` - 风险等级

### 1.13 长期计划
- **插槽名称**: `ai_sections.long_term_plan`
- **用途**: 制定企业环境风险防控长期计划
- **参考字段**:
  - `risk_level` - 风险等级
  - `enterprise_info.training_programs` - 培训计划

### 1.14 中期计划
- **插槽名称**: `ai_sections.medium_term_plan`
- **用途**: 制定企业环境风险防控中期计划
- **参考字段**:
  - `enterprise_info.environmental_factors` - 环境因素
  - `emergency_materials` - 应急物资信息

### 1.15 短期计划
- **插槽名称**: `ai_sections.short_term_plan`
- **用途**: 制定企业环境风险防控短期计划
- **参考字段**:
  - `emergency_materials` - 应急物资信息
  - `wastewater_management` - 废水管理信息

## 2. 突发环境事件应急预案 (template_emergency_plan.jinja2)

### 2.1 企业概况
- **插槽名称**: `ai_sections.enterprise_overview`
- **用途**: 根据企业基本情况，生成企业概况描述
- **参考字段**: 
  - `enterprise_name` - 企业名称
  - `enterprise_info.establishment_date` - 企业成立时间
  - `enterprise_info.environmental_investment` - 环保投资
  - `enterprise_info.main_construction` - 主要建设内容
  - `enterprise_info.production_capacity` - 主要生产能力
  - `products` - 主要产品列表
  - `enterprise_info.work_system` - 工作制度

### 2.2 地理位置及交通
- **插槽名称**: `ai_sections.location_description`
- **用途**: 描述企业地理位置及周边交通情况
- **参考字段**:
  - `enterprise_name` - 企业名称
  - `longitude` - 经度
  - `latitude` - 纬度
  - `enterprise_info.address` - 企业地址
  - `enterprise_info.transportation` - 交通情况

### 2.3 地形地貌
- **插槽名称**: `ai_sections.terrain_description`
- **用途**: 描述企业所在区域的地形地貌特征
- **参考字段**:
  - `enterprise_info.terrain` - 地形地貌信息
  - `enterprise_info.topography` - 地形特征

### 2.4 气象条件
- **插槽名称**: `ai_sections.weather_description`
- **用途**: 描述企业所在区域的气象条件
- **参考字段**:
  - `enterprise_info.climate` - 气候条件
  - `enterprise_info.meteorology` - 气象信息

### 2.5 水文
- **插槽名称**: `ai_sections.hydrology_description`
- **用途**: 描述企业所在区域的水文情况
- **参考字段**:
  - `enterprise_info.hydrology` - 水文信息
  - `water_receptors` - 水环境受体信息

### 2.6 企业环保工作情况
- **插槽名称**: `ai_sections.environmental_work`
- **用途**: 描述企业环保手续情况
- **参考字段**:
  - `enterprise_info.environmental_procedures` - 环保手续
  - `enterprise_info.eia_approval` - 环评批复
  - `enterprise_info.acceptance` - 验收情况
  - `enterprise_info.historical_emergency_plan` - 历史应急预案
  - `enterprise_info.discharge_permit` - 排污许可证

### 2.7 企业建设布置情况
- **插槽名称**: `ai_sections.construction_layout`
- **用途**: 描述企业平面布置情况
- **参考字段**:
  - `enterprise_info.layout` - 平面布置情况
  - `enterprise_info.construction` - 建设情况

### 2.8 生产工艺
- **插槽名称**: `ai_sections.production_process_description`
- **用途**: 描述企业主要生产工艺流程
- **参考字段**:
  - `enterprise_info.production_process` - 生产工艺描述
  - `raw_materials` - 原材料信息
  - `products` - 产品信息
  - `main_equipment` - 主要设备信息

### 2.9 环境风险源防范措施
- **插槽名称**: `ai_sections.risk_prevention_measures`
- **用途**: 根据企业可能发生的突发环境事件，提出各事件的防范措施
- **参考字段**:
  - `hazardous_materials` - 危险物质信息
  - `incident_scenarios` - 事故情景
  - `risk_identification_list` - 风险辨识清单
  - `risk_prevention_list` - 风险防范措施清单

### 2.10 突发环境事件现场应急措施
- **插槽名称**: `ai_sections.emergency_response_measures`
- **用途**: 根据企业可能发生的突发环境事件，提出各事件的应急处置措施
- **参考字段**:
  - `incident_scenarios` - 事故情景
  - `emergency_materials` - 应急物资信息
  - `emergency_teams` - 应急队伍信息

### 2.11 事故类型应急处置卡
- **插槽名称**: `ai_sections.incident_response_card`
- **用途**: 生成完整的应急处置卡内容
- **参考字段**:
  - `incident_type` - 事故类型
  - `incident_description` - 事故描述
  - `incident_consequence_analysis` - 危害及后果分析
  - `emergency_materials_for_incident` - 应急物资
  - `incident_response_measures` - 处置措施
  - `incident_response_precautions` - 应急处置注意事项
  - `internal_emergency_contacts` - 内部应急联系电话
  - `fire_police` - 火警/匪警
  - `env_bureau` - 生态环境局
  - `surrounding_units` - 周边联防单位

## 3. 应急资源调查报告 (template_resource_investigation.jinja2)

### 3.1 调查过程
- **插槽名称**: `ai_sections.investigation_process`
- **用途**: 描述应急资源调查的过程和方法
- **参考字段**:
  - `investigation_start_date` - 调查开始时间
  - `investigation_end_date` - 调查结束时间
  - `investigation_baseline_date` - 调查基准时间
  - `investigation_leader` - 调查负责人
  - `investigation_contact` - 调查联系人

### 3.2 差距分析1
- **插槽名称**: `ai_sections.gap_analysis_1`
- **用途**: 分析企业应急资源差距，主要针对救援队伍力量
- **参考字段**:
  - `emergency_teams` - 应急队伍信息
  - `enterprise_info.staff_count` - 企业员工数量

### 3.3 差距分析2
- **插槽名称**: `ai_sections.gap_analysis_2`
- **用途**: 分析企业应急资源差距，主要针对救援装备
- **参考字段**:
  - `emergency_materials` - 应急物资信息
  - `resource_match` - 资源匹配情况

### 3.4 差距分析3
- **插槽名称**: `ai_sections.gap_analysis_3`
- **用途**: 分析企业应急资源差距，主要针对救援知识
- **参考字段**:
  - `emergency_teams` - 应急队伍信息
  - `enterprise_info.training_records` - 培训记录

### 3.5 差距分析4
- **插槽名称**: `ai_sections.gap_analysis_4`
- **用途**: 分析企业应急资源差距，主要针对应急演练
- **参考字段**:
  - `drill_records` - 演练记录
  - `enterprise_info.emergency_drills` - 应急演练情况

### 3.6 结论
- **插槽名称**: `ai_sections.conclusion`
- **用途**: 总结企业应急资源调查结论
- **参考字段**:
  - `enterprise_name` - 企业名称
  - `hazardous_materials` - 危险物质信息
  - `emergency_materials` - 应急物资信息
  - `emergency_teams` - 应急队伍信息
  - `resource_match` - 资源匹配情况

## 使用说明

1. 在生成文档时，系统会为每个AI插槽调用AI服务生成相应内容
2. AI生成内容时应参考指定的字段路径，确保内容与企业实际情况相符
3. AI生成的内容应保持专业、准确、简洁的风格
4. 对于没有提供数据的字段，AI应基于行业常识生成合理内容
5. 所有AI生成的内容应与模板的整体风格保持一致
-- 更新企业基本信息字段
-- 添加新字段
ALTER TABLE enterprise_info ADD COLUMN legal_representative VARCHAR(100) COMMENT '法定代表人';
ALTER TABLE enterprise_info ADD COLUMN fax VARCHAR(50) COMMENT '传真';
ALTER TABLE enterprise_info ADD COLUMN email VARCHAR(100) COMMENT '电子邮箱';

-- 重命名字段
ALTER TABLE enterprise_info CHANGE COLUMN contact_person legal_representative_old VARCHAR(100) COMMENT '旧联系人字段';
ALTER TABLE enterprise_info CHANGE COLUMN phone contact_phone_old VARCHAR(50) COMMENT '旧联系电话字段';
ALTER TABLE enterprise_info CHANGE COLUMN description overview_old TEXT COMMENT '旧企业简介字段';

-- 删除不需要的字段
ALTER TABLE enterprise_info DROP COLUMN employee_count;
ALTER TABLE enterprise_info DROP COLUMN main_products;
ALTER TABLE enterprise_info DROP COLUMN annual_output;
ALTER TABLE enterprise_info DROP COLUMN legal_representative_old;
ALTER TABLE enterprise_info DROP COLUMN contact_phone_old;
ALTER TABLE enterprise_info DROP COLUMN overview_old;
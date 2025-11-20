{{ basic_info.company_name or "某某公司" }}突发环境事件应急预案
专家评审意见采纳情况表
====================================================

<table border="1" cellspacing="0" cellpadding="6">
    <thead>
        <tr>
            <th width="5%">序号</th>
            <th width="35%">专家评审意见</th>
            <th width="20%">修改情况（已修改/部分采纳/未采纳）</th>
            <th width="40%">具体修改内容说明</th>
        </tr>
    </thead>
    <tbody>
        {% if compliance_info.expert_comments %}
            {% for c in compliance_info.expert_comments %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ c.comment_text or "—" }}</td>
                <td>{{ c.status or "—" }}</td>
                <td>{{ c.modify_detail or "—" }}</td>
            </tr>
            {% endfor %}
        {% else %}
            <tr><td colspan="4">企业未提供专家意见，暂无法生成采纳情况表。</td></tr>
        {% endif %}
    </tbody>
</table>

说明：  
1. 本表用于展示预案编制过程中对专家意见的整改落实情况。  
2. 需与专家签字页及评分表一并归档。  

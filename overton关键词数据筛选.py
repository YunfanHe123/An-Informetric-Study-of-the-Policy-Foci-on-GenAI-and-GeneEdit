import csv
import re


def process_keywords(keyword_str):
    # 分割关键词并去除空白字符
    keywords = [k.strip() for k in keyword_str.split(';')]

    # 定义SDG匹配模式（不区分大小写）
    sdg_pattern = re.compile(r'^sdg \d+:', re.IGNORECASE)

    processed = []
    for kw in keywords:
        # 过滤符合SDG模式的关键词
        if not sdg_pattern.match(kw):
            # 统一转小写后加入结果列表
            processed.append(kw.lower())

    return '; '.join(processed)


# 读取CSV文件
with open('E:\hhh.csv', 'r', newline='', encoding='gbk') as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)
    fieldnames = reader.fieldnames

# 处理keywords字段
for row in rows:
    if 'keywords' in row:
        row['keywords'] = process_keywords(row['keywords'])

# 写入新的CSV文件
with open('E:\processed.csv', 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
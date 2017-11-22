#!/usr/bin/python3

import pymysql
from kafka import KafkaProducer
import msgpack

# 打开数据库连接
db = pymysql.connect("localhost", "root", "19830602", "frontera_category2")
producer = KafkaProducer(bootstrap_servers='10.0.6.65:9092', value_serializer=msgpack.dumps)

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 查询语句
sql = "select PATH_BY_ID from amazon_category where HAS_CHILDREN = 0 and SITE = 'US'"
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        data = row[0].split(',')
        url = 'https://www.amazon.com/s?rh='
        for j in data:
            url += 'n:' + j + ','
        # 分类url
        print(url[:-1])
        # print("https://www.amazon.com/s?rh=n:%s,n:!%s,n:%s,n:%s" % (data[0],data[1],data[2],data[3]))
        # data = "https://www.amazon.com/s?rh=n:"+data[0]+",n:!"+data[1]+",n:"+data[2]+",n:"+data[3]
        producer.send('scrapy-categories2', ['a', str.encode(url[:-1])] )
except:
    print("Error: unable to fetch data")

# 关闭数据库连接
db.close()

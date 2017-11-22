#!/usr/bin/python3

import pymysql
from kafka import KafkaProducer
import msgpack

# 打开数据库连接
db = pymysql.connect("localhost", "root", "19830602", "amazon_category")
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=msgpack.dumps)

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 查询语句
sql = "SELECT PATH_BY_ID FROM amazon_category where LEVEL = '%d'" % (3)
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        data = row[0].split(',')
        print("https://www.amazon.com/s?rh=n:%s,n:!%s,n:%s,n:%s" % (data[0],data[1],data[2],data[3]))
        data = "https://www.amazon.com/s?rh=n:"+data[0]+",n:!"+data[1]+",n:"+data[2]+",n:"+data[3]
        producer.send('scrapy-categories2', ['a', str.encode(data)] )
except:
    print("Error: unable to fetch data")

# 关闭数据库连接
db.close()

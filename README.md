# distributed crawler.

## 运行环境

1. 安装python3.6.2
2. virtualenv创建虚拟环境
3. pip3 install -r requirements.txt

## mysql建表

详见`frontera.sql`, `frontera_category.sql`, `frontera_keyword.sql`

## influxdb安装

```bash
cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF
```

```bash
sudo yum install influxdb
```

```bash
influxdb
create database crawlerstats;
create user admin with password 'admin' with all privileges
grant all privileges to admin
vim /etc/influxdb/influxdb.conf 修改[http]中的auth-enabled = true
sudo service influxdb start
```


## kafka topic, 括号是分区数, *是没要求 

### TSCProductUrls

* scrapy-categories (*)  # 分类的输出topic, 这里是输入
* frontier-done-category (1)  # 禁止发送数据到这个topic
* frontier-todo-category (3)  # 分区数量决定爬虫数量, 根据实际调整; 禁止发送数据到这个topic
* frontier-seeds (*)  # product的输入topic

### productBaseInfo

* frontier-seeds (*)  # 同上 , 这个topic同时接入竞品监控的url
* frontier-done (1)  # 禁止发送数据到这个topic
* frontier-todo (3)  # 分区数量决定爬虫数量, 根据实际调整; 禁止发送数据到这个topic
* scrapy-items (*)  # product的输出topic

### keyword

* frontier-seeds-keyword(*)  # 接别的组发的keyword消息
* frontier-done-keyword(1)  # 禁止发送数据到这个topic
* frontier-toto-keyword(3)  # 分区数量决定爬虫数量, 根据实际情况调整; 禁止发送数据到这个topic
* scrapy-items-keyword(*)  # keyword爬虫的产出topic, 别的组来消费

## 各个模块相关topic消息格式

**以下topic消息使用msgpack序列化**

* scrapy-categories & frontier-seeds

```
['a', 'url']
```

列表第一个元素, 'a'表示新增, 'd'表示删除
列表第二个元素url是消息的url
列表第三个元素置为'0'即可, 表示优先级

* frontier-seeds-keyword

```
['a', 'asin', ['keyword1', 'keyword2'...], 'uuid']
```

列表第一个元素, 'a'表示新增, 'd'表示删除
列表第二个元素是asin
列表第三个元素是一个列表, 每个元素是一个keyword
列表第四个元素是uuid, 表示该消息的请求方, 会传回结果

* 竞品: frontier-seeds-competing

```bash
['a', 'asin']
```

* 模拟下单: scrapy-simulatecart, 注意了, 2017-10-18修改模拟下单也要接竞品topic

```bash
['a', 'asin']
```

## 各组件启动命令

** 修改3个workersettings配置为实际配置, 包括mysql以及kafka

### TSCProductUrls

#### 启动TSCProductUrls服务器

```bash
python -m frontera.worker.db --config amazon.frontier.category_workersettings
```

#### 启动TSCProductUrls爬虫

```bash
scrapy crawl TSCProductUrls -L INFO -s FRONTERA_SETTINGS=amazon.frontier.category_spider_settings -s SPIDER_PARTITION_ID=0
scrapy crawl TSCProductUrls -L INFO -s FRONTERA_SETTINGS=amazon.frontier.category_spider_settings -s SPIDER_PARTITION_ID=1
scrapy crawl TSCProductUrls -L INFO -s FRONTERA_SETTINGS=amazon.frontier.category_spider_settings -s SPIDER_PARTITION_ID=2
```

### productBaseInfo

#### 启动productBaseInfo服务器

```bash
python -m frontera.worker.db --config amazon.frontier.workersettings
```

#### 启动productBaseInfo爬虫

```bash
scrapy crawl productBaseInfo -L INFO -s FRONTERA_SETTINGS=amazon.frontier.spider_settings -s SPIDER_PARTITION_ID=0
scrapy crawl productBaseInfo -L INFO -s FRONTERA_SETTINGS=amazon.frontier.spider_settings -s SPIDER_PARTITION_ID=1
scrapy crawl productBaseInfo -L INFO -s FRONTERA_SETTINGS=amazon.frontier.spider_settings -s SPIDER_PARTITION_ID=2
```

### keyWordsProducts

#### 启动keyWordsProducts服务器

```bash
python -m frontera.worker.db --config amazon.frontier.keyword_workersettings
```

#### 启动keyWordsProducts爬虫

```bash
scrapy crawl keyWordsProducts -L INFO -s FRONTERA_SETTINGS=amazon.frontier.keyword_spider_settings -s SPIDER_PARTITION_ID=0
scrapy crawl keyWordsProducts -L INFO -s FRONTERA_SETTINGS=amazon.frontier.keyword_spider_settings -s SPIDER_PARTITION_ID=1
scrapy crawl keyWordsProducts -L INFO -s FRONTERA_SETTINGS=amazon.frontier.keyword_spider_settings -s SPIDER_PARTITION_ID=2
```

## 修改frontera内容

* mysql增加两个表, 扩展revisiting backend功能
* 扩展revisiting backend, 实现: 1. 出错重试; 2. yield出来的Request能够按照正确的时间间隔重爬
* 扩展revisiting queue, 实现: 1. 竞品监控时无人监控的商品停止爬取; 
* 新增middleware, 轮询kafka收消息后写入种子表, 同步向集群生成Request

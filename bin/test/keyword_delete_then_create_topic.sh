#!/bin/bash

while true; do
    read -p "sure?" yn
    case $yn in
        [Yy]* ) 
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-done-keyword;
#           kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-seeds-keyword;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-todo-keyword;
#            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic scrapy-items-keyword;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-done-keyword --replication-factor 1 --partitions 1;
#           kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-seeds-keyword --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-todo-keyword --replication-factor 1 --partitions 3;
#            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic scrapy-items-keyword --replication-factor 1 --partitions 3;
            break;;
        [Nn]* ) exit;;
        * ) echo 'y? n?';;
    esac
done

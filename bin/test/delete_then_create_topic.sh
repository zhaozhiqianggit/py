#!/bin/bash

while true; do
    read -p "sure?" yn
    case $yn in
        [Yy]* ) 
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-done;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-done-category;
           kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-seeds;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-todo;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-todo-category;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic scrapy-categories2;
#            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic scrapy-items-bsr;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-done --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-done-category --replication-factor 1 --partitions 1;
           kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-seeds --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-todo --replication-factor 1 --partitions 3;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-todo-category --replication-factor 1 --partitions 3;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic scrapy-categories2 --replication-factor 1 --partitions 1;
#            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic scrapy-items-bsr --replication-factor 1 --partitions 3;
            break;;
        [Nn]* ) exit;;
        * ) echo 'y? n?';;
    esac
done

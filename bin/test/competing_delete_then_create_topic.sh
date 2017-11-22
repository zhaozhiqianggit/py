#!/bin/bash

while true; do
    read -p "sure?" yn
    case $yn in
        [Yy]* ) 
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-done-competing;
#            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-seeds-competing;
            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic frontier-todo-competing;
#            kafka-topics --zookeeper 192.168.30.159:2181 --delete --topic scrapy-items-competing;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-done-competing --replication-factor 1 --partitions 1;
#            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-seeds-competing --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic frontier-todo-competing --replication-factor 1 --partitions 3;
#            kafka-topics --zookeeper 192.168.30.159:2181 --create --topic scrapy-items-competing --replication-factor 1 --partitions 3;
            break;;
        [Nn]* ) exit;;
        * ) echo 'y? n?';;
    esac
done

#!/bin/bash

while true; do
    read -p "sure?" yn
    case $yn in
        [Yy]* ) 
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-done-simulatecart2;
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-todo-simulatecart2;
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-seeds-competing;
            kafka-topics --zookeeper localhost:2181 --delete --topic scrapy-items-competing-simulatecart;
            kafka-topics --zookeeper localhost:2181 --delete --topic error-seeds;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-done-simulatecart2 --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-todo-simulatecart2 --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-seeds-competing --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic scrapy-items-competing-simulatecart --replication-factor 1 --partitions 3;
            kafka-topics --zookeeper localhost:2181 --create --topic error-seeds --replication-factor 1 --partitions 1;
            break;;
        [Nn]* ) exit;;
        * ) echo 'y? n?';;
    esac
done

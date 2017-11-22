#!/bin/bash

while true; do
    read -p "sure?" yn
    case $yn in
        [Yy]* ) 
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-done-simulatecart-bsr;
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-todo-simulatecart-bsr;
            kafka-topics --zookeeper localhost:2181 --delete --topic frontier-seeds-simulatecart-bsr;
            kafka-topics --zookeeper localhost:2181 --delete --topic scrapy-items-bsr-simulatecart;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-done-simulatecart-bsr --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-todo-simulatecart-bsr --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic frontier-seeds-simulatecart-bsr --replication-factor 1 --partitions 1;
            kafka-topics --zookeeper localhost:2181 --create --topic scrapy-items-bsr-simulatecart --replication-factor 1 --partitions 3;
            break;;
        [Nn]* ) exit;;
        * ) echo 'y? n?';;
    esac
done

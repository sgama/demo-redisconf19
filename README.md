# demo-redisconf19

# Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Launch containers](#containers)
4. [Bloom Filters in Redis with RedisBloom](#bloomfilters)
5. [Timeseries in Redis with RedisTimeSeries](#timeseries)
6. [RedisGears](#redisgears)
7. [An interesting use case I learned about](#interestingusecase)

---

## Introduction
This repository holds all the necessary source code and template files to run the following tutorials.

Following along the tutorial on your own machine will require you to bring up the docker-compose stack.

---
### Prerequisites

MacOS or Linux operating systems are preferred. cAdvisor and Nodeexporter is not compatible with Windows. You may still run through the demo with Windows, but any will not be able to see container level metrics through Grafana.

- [Docker + docker-compose](https://www.google.com)
- [Python3](https://www.python.org/downloads/)

---
### Launch containers

Bring up the docker-compose stack:
`> docker-compose up -d`

A compiled version of Redis has been uploaded to DockerHub for this demo, however if you want to build your custom version of Redis locally, you can run:
`> docker-compose -f docker-compose.build.yml up -d`

This may take a minute or two while the images are pulled and started.
Verify the containers are up and running either with:
`> docker ps -a`
or visiting the containers individually:

| Service        | URL           |
|----------------|---------------|
|Grafana|[http://localhost:3000](http://localhost:3000)|
|Prometheus|[http://localhost:9090](http://localhost:9090)|
|Cadvisor|[http://localhost:8080](http://localhost:8080)|
|Nodexporter|[http://localhost:9100](http://localhost:9100)|

You may find the following dashboard interesting: [http://localhost:3000/d/redisdashboard/redis?orgId=1&refresh=5s](http://localhost:3000/d/redisdashboard/redis?orgId=1&refresh=5s)


Redis:
```
> docker exec -it db-redis sh
# whoami
root
# redis-cli
127.0.0.1:6379> ping
PONG
```
---

## Bloom Filters in Redis with RedisBloom

### What are bloom filters

If you want the indepth explanation of Bloom Filters, I'll direct you to the Wiki entry: [https://en.wikipedia.org/wiki/Bloom_filter](https://en.wikipedia.org/wiki/Bloom_filter)

But for the purposes of this demo, [a Bloom Filter is a probabilistic data structure which provides an efficient way to verify that an entry is certainly not in a set](https://redislabs.com/blog/rebloom-bloom-filter-datatype-redis/). We will also be using the [Redis Bloom](https://oss.redislabs.com/redisbloom/) module for this demo.

### Use Cases
- URL Shorteners
- Cache Filtering
- Counting Filters

### Caveat

It is important that we size our bloom filters appropriately for our use cases. 

Further in the tutorial, we will use the following website to calculate the parameters of our bloom filters:
[https://hur.st/bloomfilter/](https://hur.st/bloomfilter/)

Without going into too much detail of how bloom filters work internally, this calculator calculates the most efficient parameters such that the error rate and bloom filter size required is minimized.

Note: Hyperloglog is a probablistic datastructure that is included by Redis by default. It could also be used in place of Bloom Filters on the OSS versions of Redis such as AWS Elasticache and GCP Memorystore.

### Demo

This demo will be an extension of a Counting Filter.

Let us say we wanted to count all the unique visitors on a website, where each visitor has a unique ID and we wanted the ability to query if a certain visitor has visited the website as to avoid double counting.

The most obvious solution would be to create an enormous set in which all the IDs exist. In Redis, such a data structure would be a Sorted Set. However, this solution would not scale to millions or even billions of unique visitors.

Let's start:

```
> docker exec -it db-redis sh
# whoami
root
# redis-cli
127.0.0.1:6379>
```

Let's assume we want to store 10 items with an error rate of 0.0001, so we'll reserve it and start adding entries.
Redis will return 1 if a new element has been added and 0 if it wasn't new to the filter.

```
127.0.0.1:6379> BF.RESERVE bloomTest 0.0001 10
OK
127.0.0.1:6379> BF.MADD bloomTest elem1 elem2 elem3 elem4 elem5 elem6 elem7 elem8
1) (integer) 1
2) (integer) 1
3) (integer) 1
4) (integer) 1
5) (integer) 1
6) (integer) 1
7) (integer) 1
8) (integer) 1
127.0.0.1:6379> BF.ADD bloomTest elem7
(integer) 0
127.0.0.1:6379> BF.MADD bloomTest elem9 elem10 elem11
1) (integer) 1
2) (integer) 1
3) (integer) 1
127.0.0.1:6379> BF.MADD bloomTest elem12 elem13 elem14 elem 15
1) (integer) 1
2) (integer) 1
3) (integer) 1
4) (integer) 1
5) (integer) 1
127.0.0.1:6379> BF.MADD bloomTest elem16 elem 17 elem18
1) (integer) 1
2) (integer) 0
3) (integer) 1
4) (integer) 1
```

You'll notice that we were able to add 16 elements until the bloom filter failed on us. That's because the error rate goes up quite rapidly once you exceed your desired capacity.


## Timeseries in Redis with RedisTimeSeries

### What is a Timeseries Dataset
Time Series data is sequential data. Analysis of this data is often reduced to running aggregration queries to reduce processing overhead and to extract intelligence in real time. We can use [RedisTimeseries](https://oss.redislabs.com/redistimeseries/) to help us achieve this.

### Use Cases
- Stock ticker data
- IoT sensor data
- Fleet management (vehicle id, timestamp, GPS coordinates, average speed)
- Requiring a database where other RDBMS are too heavy

### Note
- In Redis, if you do not set a retention policy, Redis may use LRU to determine when to clean up old items

### Demo
Within the scripts folder run
`> python .\populateTimeSeries.py --sensor-id=10`

Then exec into Redis:
```
> docker exec -it db-redis sh
# date +%s
1554591979
# redis-cli
127.0.0.1:6379> TS.RANGE temperature:10 1554591900 1554591979
...
...
...
127.0.0.1:6379> TS.RANGE temperature:10 1554591900 1554591979 AGGREGATION SUM 10
...
127.0.0.1:6379> TS.RANGE temperature:10 1554591900 1554591979 AGGREGATION AVG 10
```

## RedisGears

### What are RedisGears

Officially according to the documentation, [RedisGears](https://oss.redislabs.com/redisgears/) is a Dynamic execution framework for your Redis Data.

Unofficially, it's a neat way to add map/reduce/filter functionality with a built-in Python interpreter.
Unfortunately this means that any map reduce functions are single-threaded due to the Python Global Interpreter Lock. That also means processing may not be the fastest.

### Use Cases
TBD. But let's go over the topics off the top of my head.

### Demo

The following script can be used to try out the following RedisGears.

`> python .\populateRandomData.py`

Within the redis-cli, you can run these following commands:

| Use Case        | Command         |
|----------------|---------------|
|List all keys|`RG.PYEXECUTE "GearsBuilder().map(lambda x: x['key']).run()"`|
|Delete all keys|`RG.PYEXECUTE "GearsBuilder().map(lambda x: x['key']).foreach(lambda x: execute('del', x)).count().run()"`|
|Count number of keys|`RG.PYEXECUTE "GearsBuilder().count().run()"`|
|Count keys with string value greater than 50|`RG.PYEXECUTE "GearsBuilder().map(lambda x: {'key':x['key'], 'value': 0 if int(x['value']) < 50 else 100}).countby(lambda x: x['value']).collect().run()"`|
|Get the average of these keys|`RG.PYEXECUTE "GearsBuilder().map(lambda x:int(x['value'])).avg().run()"`|
|Aggregate over the keys to get the total sum|`RG.PYEXECUTE "GearsBuilder().map(lambda x:int(x['value'])).aggregate(0, lambda r, x: x + r, lambda r, x: x + r).run()"`|
|Delete all keys prefixed with city|`RG.PYEXECUTE "GearsBuilder().map(lambda x: x['key']).foreach(lambda x: execute('del', x)).count().run('city:*')"`|
|Delete all keys added in the future|`RG.PYEXECUTE "GearsBuilder().foreach(lambda x: execute('del', x['key'])).register()"`|

Unfortunately, we currently cannot delete an existing gear, so the last command effectively makes Redis useless.

This feature is expected soon though: [https://github.com/RedisLabsModules/RedisGears/issues/44](https://github.com/RedisLabsModules/RedisGears/issues/44)

To revert any gears you have created. Restart all your services:
```
docker-compose down && docker system prune -f && docker volume prune -f && docker-compose up -d
```

## An interesting use case I learned about

### Training multiple machine learning models at the same time

In traditional machine learning pipelines, data sits on a disk/database and is pulled into memory and used on demand while training. In the case of LSTM Neural Networks, you often take a linear sequence of data and turn it into batches of sequential sliding windows. These batches are often stored in variables in memory and rebuilt every time a new model is created.

But what if you wanted to create multiple models at the same time on separate machines to see its performance with the most up-to-date data as soon as possible?

The simple solution would be to share this data across all servers and have them build the training batches on demand. This solution while correct, has a lot of repeated, redundent steps of building the batches of sequential sliding windows. This is where Redis fits into our picture.

Instead of building the batches multiple times and storing it in variables within the machine learning pipeline. We can build the batches separately, store them in Redis and have each of the machine learning models pull from Redis as each batch is needed during both the training and evaluation phases. This way, reading off disk is only done once. Data can be discarded from memory as soon as it is consumed and can be fetched from Redis the next time it is needed.
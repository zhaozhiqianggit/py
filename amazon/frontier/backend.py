#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from calendar import timegm
from datetime import timedelta, datetime
from urllib.parse import unquote_plus

from frontera import Request
from frontera.contrib.backends.sqlalchemy.revisiting import Backend, RevisitingQueueModel, RevisitingQueue
from frontera.core.components import States
from sqlalchemy import desc, or_

from .models import SeedsModel, KeywordSeedsModel, SimulateCartSeedsModel, CompetingSeedsModel, \
    BSRSimulateCartSeedsModel

__author__ = "sunwei"
logger = logging.getLogger("custom_backend")


def utcnow_timestamp():
    d = datetime.utcnow()
    return timegm(d.timetuple())


class CustomBackend(Backend):
    component_name = 'Custom Backend'
    seeds_model = SeedsModel

    def _create_queue(self, settings):
        self.interval = settings.get("SQLALCHEMYBACKEND_REVISIT_INTERVAL")
        assert isinstance(self.interval, timedelta)
        self.interval = self.interval.total_seconds()
        return CustomRevisitingQueue(self.session_cls, RevisitingQueueModel, self.seeds_model,
                                     settings.get('SPIDER_FEED_PARTITIONS'))

    def request_error(self, request, error):
        logger.warning("error happen, %s", error)
        logger.warning('error request, %s', request.url)
        logger.warning(f'error request meta: {request.meta}')
        super(CustomBackend, self).request_error(request, error)
        self._custom_schedule(request, self.seeds_model)

    def _custom_schedule(self, request, model):
        '''封装一下, 供page_crawled和request_error调用
        1. 将种子放回队列
        2. 不能重复
        3. 非种子url不放队列'''
        is_seed = False
        is_revisit = False
        session = self.session_cls()
        try:
            is_seed = session.query(model.url).filter(model.url == unquote_plus(request.url)).first()
            logger.warning(f'is_seed:{is_seed}')
            if is_seed:
                is_revisit = session.query(RevisitingQueueModel).filter(RevisitingQueueModel.url
                                                                        == unquote_plus(request.url)).first()
                logger.warning(f'is_revisit:{is_revisit}')
        except Exception as exc:
            logger.exception(exc)
        session.close()
        if is_seed and not is_revisit:
            logger.warning('schedule')
            self._schedule([request])

    def page_crawled(self, response):
        response.meta[b'state'] = States.CRAWLED
        self.states.update_cache(response)
        self.metadata.page_crawled(response)
        self.states.set_states(response.request)
        self._custom_schedule(response.request, self.seeds_model)
        self.states.update_cache(response.request)

    def _schedule(self, requests):
        batch = []
        for request in requests:
            logger.warning(f"request.url:{request.url}, state:{request.meta[b'state']}")
            if request.meta[b'state'] in [States.NOT_CRAWLED]:
                request.meta[b'crawl_at'] = utcnow_timestamp()
            elif request.meta[b'state'] in [States.CRAWLED, States.ERROR]:
                # request.meta[b'crawl_at'] = utcnow_timestamp() + self.interval
                # 第二次迭代yield出来的request马上执行
                if request.meta.get(b'scrapy_callback', None):
                    request.meta[b'crawl_at'] = utcnow_timestamp()
                else:
                    request.meta[b'crawl_at'] = utcnow_timestamp() + self.interval
            else:
                continue  # QUEUED
            batch.append((request.meta[b'fingerprint'], self._get_score(request), request, True))
        self.queue.schedule(batch)
        self.metadata.update_score(batch)
        self.queue_size += len(batch)


class BSRSimulateCartBackend(CustomBackend):
    component_name = 'simulatecart backend bsr'
    seeds_model = BSRSimulateCartSeedsModel


class SimulateCartBackend(CustomBackend):
    component_name = 'simulatecart backend'
    seeds_model = SimulateCartSeedsModel


class KeywordBackend(CustomBackend):
    component_name = 'keyword backend'
    seeds_model = KeywordSeedsModel


class CompetingBackend(CustomBackend):
    component_name = 'competing backend'
    seeds_model = CompetingSeedsModel


class CustomRevisitingQueue(RevisitingQueue):
    def __init__(self, session_cls, queue_cls, seeds_cls, partitions):
        self.seeds_model = seeds_cls
        super(CustomRevisitingQueue, self).__init__(session_cls, queue_cls, partitions)

    def get_next_requests(self, max_n_requests, partition_id, **kwargs):
        results = []
        try:
            for item in self.session.query(self.queue_model). \
                    join(self.seeds_model, self.queue_model.url == self.seeds_model.url, isouter=True). \
                    filter(or_(self.seeds_model.ref_no > 0, self.seeds_model.ref_no.is_(None))). \
                    filter(self.queue_model.crawl_at <= utcnow_timestamp()). \
                    filter(self.queue_model.partition_id == partition_id). \
                    order_by(desc(self.seeds_model.ts)). \
                    limit(max_n_requests):
                method = 'GET' if not item.method else item.method
                results.append(Request(item.url, method=method, meta=item.meta, headers=item.headers,
                                       cookies=item.cookies))
                self.session.delete(item)
            self.session.commit()
        except Exception as exc:
            self.logger.exception(exc)
            self.session.rollback()
        return results

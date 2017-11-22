#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from calendar import timegm
from datetime import datetime
from traceback import format_tb

from frontera import Request
from frontera.contrib.messagebus.kafkabus import Consumer
from frontera.contrib.middlewares.fingerprint import BaseFingerprintMiddleware

from frontera.core.components import Middleware
from msgpack import unpackb
from twisted.internet import task
import logging

from w3lib.url import canonicalize_url

from .models import SeedsModel, KeywordSeedsModel, SimulateCartSeedsModel, CompetingSeedsModel, \
    BSRSimulateCartSeedsModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json
from urllib.parse import unquote_plus

logger = logging.getLogger(__name__)

def utcnow_timestamp():
    d = datetime.utcnow()
    return timegm(d.timetuple())

class CustomConsumer(Consumer):
    def _start_looping_call(self, interval=3):
        super(CustomConsumer, self)._start_looping_call(interval)


class CustomUrlFingerprintMiddleware(BaseFingerprintMiddleware):
    """
    This :class:`Middleware <frontera.core.components.Middleware>` will add a ``fingerprint`` field for every
    :attr:`Request.meta <frontera.core.models.Request.meta>` and
    :attr:`Response.meta <frontera.core.models.Response.meta>` if is activated.

    Fingerprint will be calculated from object ``URL``, using the function defined in
    :setting:`URL_FINGERPRINT_FUNCTION` setting.
    You can write your own fingerprint calculation function and use by changing this setting.
    The fingerprint must be bytes.

    An example for a :class:`Request <frontera.core.models.Request>` object::

        >>> request.url
        'http//www.scrapinghub.com:8080'

        >>> request.meta['fingerprint']
        '60d846bc2969e9706829d5f1690f11dafb70ed18'

    """

    component_name = 'Custom URL Fingerprint Middleware'
    fingerprint_function_name = 'URL_FINGERPRINT_FUNCTION'

    def _get_fingerprint(self, url):
        return self.fingerprint_function(canonicalize_url(url))

    def _add_fingerprint(self, obj):
        obj.meta[b'fingerprint'] = self._get_fingerprint(obj.url+
                                                         obj.meta.get('asin','') +
                                                         obj.meta.get('uuid','')
                                                         )
        if b'redirect_urls' in obj.meta:
            obj.meta[b'redirect_fingerprints'] = [self._get_fingerprint(url) for url in obj.meta[b'redirect_urls']]
        return obj


class SeedsMiddleware(Middleware):
    component_name = 'Seeds Middleware'

    @classmethod
    def from_manager(cls, manager):
        return cls(manager)

    def __init__(self, manager):
        # logger.warning(type(manager))
        self.manager = manager
        settings = manager.settings
        self.loopInterval = settings.get('LOOPINTERVAL', 30)
        engine = settings.get('SQLALCHEMYBACKEND_ENGINE')
        engine_echo = settings.get('SQLALCHEMYBACKEND_ENGINE_ECHO', False)
        self.engine = create_engine(engine, echo=engine_echo)
        self.db_session = sessionmaker(bind=self.engine)

    def frontier_start(self):
        def errback(failure):
            logger.exception(failure.value)
            if failure.frames:
                logger.critical(str("").join(format_tb(failure.getTracebackObject())))
            self.task.start(self.loopInterval).addErrback(errback)
        self.task = task.LoopingCall(self._sync, self.manager)
        self.task.start(self.loopInterval, False).addErrback(errback)

        self.task_seeds = task.LoopingCall(self._seeds_consume,
                                           CustomConsumer(self.manager.settings.get('KAFKA_LOCATION'),
                                                    self.manager.settings.get('SEEDS_TOPIC'),
                                                    self.manager.settings.get('SEEDS_GROUP'),
                                                    None))
        self.task_seeds.start(self.manager.settings.get('SEEDS_INTERVAL', 5), False)

    def _seeds_consume(self, c):
        logger.info("消费Kafka seeds topic")
        for m in c.get_messages(timeout=1.0, count=100):
            try:
                msg = unpackb(m, encoding='utf-8')
            except Exception as e:
                logger.error("Decoding error: %s", e)
                continue
            else:
                try:
                    logger.info("m:{}, msg:{}".format(m, msg))
                    optype = msg[0].upper()
                    url = msg[1]
                    logger.info("optype:{}, url:{}".format(optype, url))
                    if optype not in ['A', 'D']:
                        logger.warning("invalid optype, %s", optype)
                        continue
                except Exception as e:
                    logger.error(e)
                    continue
                session = self.db_session()
                seeds = session.query(SeedsModel).filter(SeedsModel.url
                                                         == unquote_plus(url)).first()
                try:
                    if seeds:
                        logger.info("已有相同的url在seed表, %s", url)
                        if optype == 'A':
                            seeds.ref_no += 1
                            seeds.ts = utcnow_timestamp()
                        elif optype == 'D':
                            seeds.ref_no -= 1
                    else:
                        logger.info("seed表没有该url: %s", url)
                        if optype == 'A':
                            s = SeedsModel(url=url, ref_no=1,status=0, ts=utcnow_timestamp())
                            session.add(s)
                    session.commit()
                except Exception as e:
                    logger.error("kafka msg process error: %s", e)
                    session.rollback()
                session.close()

    def _sync(self, manager):
        logger.info("同步种子库...")
        session = self.db_session()
        seeds = session.query(SeedsModel).filter(SeedsModel.status == 0)
        # logger.info(seeds.all())
        urls = [x.url for x in seeds.all()]
        if urls:
            try:
                manager.add_seeds([Request(url=url) for url in urls])
                seeds.update({"status": 1})
                session.commit()
            except Exception as e:
                logger.exception(e)
                session.rollback()
        session.close()

    def frontier_stop(self):
        if self.task and self.task.running:
            self.task.stop()

        if self.task_seeds and self.task_seeds.running:
            self.task_seeds.stop()

    def page_crawled(self, response):
        logger.info("SeedsMiddleware -> page_crawled:")
        logger.info(response.url)
        return response

    def add_seeds(self, seeds):
        logger.info("SeedsMiddleware -> add_seeds")
        return seeds

    def links_extracted(self, request, links):
        logger.info("SeedsMiddleware -> links_extracted")
        return request

    def request_error(self, request, error):
        logger.info("SeedsMiddleware -> request_error")
        return request


class SimulateCartSeedsMiddleware(SeedsMiddleware):
    component_name = 'simulate cart middleware'

    def _seeds_consume(self, c):
        logger.info("消费simulate cart kafka seeds topic")
        for m in c.get_messages(timeout=1.0, count=10):
            try:
                # msg = unpackb(m, encoding='utf-8')
                msg = json.loads(m.decode('utf-8'))
            except Exception as e:
                logger.error("Decoding error: %s", e)
                continue
            else:
                try:
                    logger.info("m:{}, msg:{}".format(m, msg))
                    optype = msg[0].upper()
                    asin = msg[1]
                    url = f'https://www.amazon.com/gp/aws/cart/add.html?ASIN.1={asin}&Quantity.1=999&add=add'
                    logger.info(f"optype:{optype}, asin:{asin}, url:{url}")
                    if optype not in ['A', 'D']:
                        logger.warning("invalid optype, %s", optype)
                        continue
                    if not asin:
                        logger.warning("invalid asin, %s", asin)
                        continue
                except Exception as e:
                    logger.error(e)
                    continue
                session = self.db_session()
                seeds = session.query(SimulateCartSeedsModel).filter(SimulateCartSeedsModel.url
                                                                     == unquote_plus(url)).first()
                try:
                    if seeds:
                        logger.info("已有相同的url在seed表, %s", url)
                        if optype == 'A':
                            seeds.ref_no += 1
                            seeds.ts = utcnow_timestamp()
                        elif optype == 'D':
                            seeds.ref_no -= 1
                    else:
                        logger.info("seed表没有该url: %s", url)
                        if optype == 'A':
                            s = SimulateCartSeedsModel(url=url, ref_no=1,status=0, asin=asin, ts=utcnow_timestamp())
                            session.add(s)
                    session.commit()
                except Exception as e:
                    logger.error("kafka msg process error: %s", e)
                    session.rollback()
                session.close()

    def _sync(self, manager):
        logger.info("同步SimulateCart种子库...")
        session = self.db_session()
        seeds = session.query(SimulateCartSeedsModel).filter(SimulateCartSeedsModel.status == 0)
        # logger.info(seeds.all())
        if seeds.all():
            try:
                manager.add_seeds([Request(url=x.url,meta={b'scrapy_meta': {'cookiejar':x.asin, 'saveCookies':1}}) for x in seeds])
                seeds.update({'status': 1})
                session.commit()
            except Exception as e:
                logger.exception(e)
                session.rollback()
        session.close()


class BSRSimulateCartSeedsMiddleware(SeedsMiddleware):
    component_name = 'simulate cart middleware bsr'

    def _seeds_consume(self, c):
        logger.info("消费bsr simulate cart kafka seeds topic")
        for m in c.get_messages(timeout=1.0, count=10):
            try:
                msg = json.loads(m.decode('utf-8'))
            except Exception as e:
                logger.error("Decoding error: %s", e)
                continue
            else:
                try:
                    logger.info("m:{}, msg:{}".format(m, msg))
                    optype = msg[0].upper()
                    asin = msg[1]
                    url = f'https://www.amazon.com/gp/aws/cart/add.html?ASIN.1={asin}&Quantity.1=999&add=add'
                    logger.info(f"optype:{optype}, asin:{asin}, url:{url}")
                    if optype not in ['A', 'D']:
                        logger.warning("invalid optype, %s", optype)
                        continue
                    if not asin:
                        logger.warning("invalid asin, %s", asin)
                        continue
                except Exception as e:
                    logger.error(e)
                    continue
                session = self.db_session()
                seeds = session.query(BSRSimulateCartSeedsModel).filter(BSRSimulateCartSeedsModel.url
                                                                        == unquote_plus(url)).first()
                try:
                    if seeds:
                        logger.info("已有相同的url在seed表, %s", url)
                        if optype == 'A':
                            seeds.ref_no += 1
                            seeds.ts = utcnow_timestamp()
                        elif optype == 'D':
                            seeds.ref_no -= 1
                    else:
                        logger.info("seed表没有该url: %s", url)
                        if optype == 'A':
                            s = BSRSimulateCartSeedsModel(url=url, ref_no=1, status=0, asin=asin, ts=utcnow_timestamp())
                            session.add(s)
                    session.commit()
                except Exception as e:
                    logger.error("kafka msg process error: %s", e)
                    session.rollback()
                session.close()

    def _sync(self, manager):
        logger.info("同步SimulateCart种子库...")
        session = self.db_session()
        seeds = session.query(BSRSimulateCartSeedsModel).filter(BSRSimulateCartSeedsModel.status == 0)
        # logger.info(seeds.all())
        if seeds.all():
            try:
                # 注意了, 这个meta 不要动
                manager.add_seeds([Request(url=x.url, meta={b'scrapy_meta': {'cookiejar': x.asin, 'saveCookies': 1}}) for x in seeds])
                seeds.update({'status': 1})
                session.commit()
            except Exception as e:
                logger.exception(e)
                session.rollback()
        session.close()


class KeyWordSeedsMiddleware(SeedsMiddleware):
    component_name = 'Keyword Middleware'

    def _seeds_consume(self, c):
        logger.info("消费Kafka key words seeds topic")
        for m in c.get_messages(timeout=1.0, count=100):
            try:
                msg = json.loads(m.decode('utf-8'))
            except Exception as e:
                logger.error("Decoding error: %s", e)
                continue
            else:
                try:
                    logger.info("m:{}, msg:{}".format(m, msg))
                    optype = msg[0].upper()
                    asin = msg[1]
                    keywords = msg[2]
                    uuid = msg[3]
                    logger.info(f"asin:{asin}, keywords:{keywords}, optype:{optype}, uuid:{uuid}")
                    # urls = [f'https://www.amazon.com/s/field-keywords={x}' for x in keywords]
                    if optype not in ['A', 'D']:
                        logger.warning("invalid optype, %s", optype)
                        continue
                    if not uuid:
                        logger.warning("uuid is empty")
                        continue
                    if not keywords:
                        logger.warning('keywords is empty')
                        continue
                    if not asin:
                        logger.warning("invalid asin, %s", asin)
                        continue
                    keywords_clean = True
                    for keyword in keywords:
                        if not keyword:
                            logger.warning(f'{keyword} is empty')
                            keywords_clean = False
                    if not keywords_clean:
                        continue
                except Exception as e:
                    logger.error(e)
                    continue
                session = self.db_session()
                try:
                    # for url in urls:
                    for keyword in keywords:
                        url = f'https://www.amazon.com/s/field-keywords={keyword}'
                        seed = session.query(KeywordSeedsModel).filter(KeywordSeedsModel.url
                                                                       == unquote_plus(url)). \
                            filter(KeywordSeedsModel.asin == asin). \
                            filter(KeywordSeedsModel.uuid == uuid).first()
                        if seed:
                            logger.info("已有相同的url,asin在seed表, %s, %s" % (url,asin))
                            if optype == 'A':
                                seed.ref_no += 1
                                seed.ts = utcnow_timestamp()
                            elif optype == 'D':
                                seed.ref_no -= 1
                        else:
                            logger.info("keyword seed表没有该url: %s, %s, %s" % (url, asin, uuid))
                            if optype == 'A':
                                s = KeywordSeedsModel(url=url, ref_no=1, status=0, asin=asin,
                                                      uuid=uuid, keyword=keyword, ts=utcnow_timestamp())
                                session.add(s)
                    session.commit()
                except Exception as e:
                    logger.error("kafka msg process error: %s", e)
                    session.rollback()
                session.close()

    def _sync(self, manager):
        logger.info("同步种子库...")
        session = self.db_session()
        seeds = session.query(KeywordSeedsModel).filter(KeywordSeedsModel.status == 0)
        # logger.info(seeds.all())
        if seeds.all():
            try:
                manager.add_seeds([Request(url=x.url,meta={b'scrapy_meta':{'asin':x.asin, 'uuid':x.uuid,
                                                           'keyword': x.keyword}}) for x in seeds])
                seeds.update({'status': 1})
                session.commit()
            except Exception as e:
                logger.exception(e)
                session.rollback()
        session.close()


class CompetingSeedsMiddleware(SeedsMiddleware):
    component_name = 'Competing Middleware'

    def _seeds_consume(self, c):
        logger.info("消费Kafka Competing seeds topic")
        for m in c.get_messages(timeout=1.0, count=100):
            try:
                msg = json.loads(m.decode('utf-8'))
            except Exception as e:
                logger.error("Decoding error: %s", e)
                continue
            else:
                try:
                    logger.info(f"m:{m}, msg:{msg}")
                    optype = msg[0].upper()
                    asin = msg[1]
                    logger.info(f"asin:{asin}, optype:{optype}")
                    if optype not in ['A', 'D']:
                        logger.warning("invalid optype, %s", optype)
                        continue
                    if not asin:
                        logger.warning("invalid asin, %s", asin)
                        continue
                except Exception as e:
                    logger.exception(e)
                    continue
                session = self.db_session()
                try:
                    url = f'https://www.amazon.com/dp/{asin}'
                    seed = session.query(CompetingSeedsModel).filter(CompetingSeedsModel.url
                                                                    == unquote_plus(url)).first()
                    if seed:
                        logger.info(f"已有相同的url在seed表, {url}")
                        if optype == 'A':
                            seed.ref_no += 1
                            seed.ts = utcnow_timestamp()
                        elif optype == 'D':
                            seed.ref_no -= 1
                    else:
                        logger.info(f"competing seed表没有该url:{url}")
                        if optype == 'A':
                            s = CompetingSeedsModel(url=url, ref_no=1, status=0, asin=asin, ts=utcnow_timestamp())
                            session.add(s)
                    session.commit()
                except Exception as e:
                    logger.error("kafka msg process error: %s", e)
                    session.rollback()
                session.close()

    def _sync(self, manager):
        logger.info("同步种子库...")
        session = self.db_session()
        seeds = session.query(CompetingSeedsModel).filter(CompetingSeedsModel.status == 0)
        # logger.info(seeds.all())
        if seeds.all():
            try:
                manager.add_seeds([Request(url=x.url) for x in seeds])
                seeds.update({'status': 1})
                session.commit()
            except Exception as e:
                logger.exception(e)
                session.rollback()
        session.close()

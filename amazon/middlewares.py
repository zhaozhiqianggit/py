# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging

import scrapy
from frontera.contrib.scrapy.middlewares.schedulers import SchedulerSpiderMiddleware, SchedulerDownloaderMiddleware
from scrapy import signals

import random

from scrapy.downloadermiddlewares.cookies import CookiesMiddleware
from scrapy.exceptions import NotConfigured, IgnoreRequest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from amazon.exceptions import RemoteServerCannotBeAccessed, OrderError, ProxyNotConfigured, CartSpiderError, \
    StatusCodeError
from .useragent import agents
from selenium import webdriver
from scrapy.http import HtmlResponse
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import requests
from requests.auth import HTTPBasicAuth
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import redis
import pickle
from scrapy.http.cookies import CookieJar
logger = logging.getLogger(__name__)



class CustomCookiesMiddleware(CookiesMiddleware):

    def __init__(self, r,debug=False):
        self.r = r
        self.debug = debug

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('COOKIES_ENABLED')\
                or not crawler.settings.get('COOKIES_REDIS'):
            raise NotConfigured
        host, port, db = crawler.settings.get('COOKIES_REDIS').split(':')
        r=redis.StrictRedis(host=host, port=port, db=db)
        m = cls(r,crawler.settings.getbool('COOKIES_DEBUG'))
        crawler.signals.connect(m.spider_closed, signal=signals.spider_closed)
        return m

    def spider_closed(self):

        pass

    def process_request(self, request, spider):
        if request.meta.get('dont_merge_cookies', False):
            return
        cookiejarkey = request.meta.get("cookiejar")
        cookiebyte=self.r.get('amazon-cookies:{}'.format(cookiejarkey))
        if cookiebyte:
            logger.info("CCM request-> get Cookies from redis,and make request")
            cookieObject = pickle.loads(cookiebyte)
            jar=cookieObject
            cookies = self._get_request_cookies(jar, request)
            for cookie in cookies:
                jar.set_cookie_if_ok(cookie, request)
            # logger.info(f'jar:{jar._cookies}')
            # set Cookie header
            request.headers.pop('Cookie', None)
            jar.add_cookie_header(request)
            self._debug_cookie(request, spider)
        else:
            logger.info("CCM request->first time Cookies none.")

    def process_response(self, request, response, spider):

        if request.meta.get('dont_merge_cookies', False):
            return response

        # extract cookies from Set-Cookie and drop invalid/expired cookies

        cookiejarkey = request.meta.get("cookiejar")
        jar=CookieJar()
        cookiebyte = self.r.get('amazon-cookies:{}'.format(cookiejarkey))
        if cookiebyte:
            logger.info("CCM response-> get Cookies from redis,and merge it")
            cookieObject = pickle.loads(cookiebyte)
            jar = cookieObject
        jar.extract_cookies(response, request)
        self._debug_set_cookie(response, spider)

        saveCookies = request.meta.get("saveCookies")

        if saveCookies:
            logger.info('CCM response->save Cookies to redis')
            self.r.set('amazon-cookies:{}'.format(cookiejarkey), pickle.dumps(jar))

        deleteCookies = request.meta.get("deleteCookies")
        if deleteCookies:
            logger.info(f'CCM response-> pop jar,delete Cookies!!')
            self.r.delete('amazon-cookies:{}'.format(cookiejarkey))
        return response



class CustomSchedulerSpiderMiddleware(SchedulerSpiderMiddleware):
    def process_spider_exception(self, response, exception, spider):
        logger.warning(f'CSSM -> response.url:{response.url}')
        return self.scheduler.process_exception(response.request, exception, spider)

    def process_spider_output(self, response, result, spider):
        logger.warning(f'CSSM -> process_spider_output:{response.url}')
        try:
            return self.scheduler.process_spider_output(response, result, spider)
        except Exception:
            logger.warning(f'CSSM -> process_spider_output -> exception')


class CustomSchedulerDownloaderMiddleware(SchedulerDownloaderMiddleware):
    def process_response(self, request, response, spider):
        logger.warning(f'CSDM -> response.status: {response.status}, url: {response.url}, '
                       f'code:{self.crawler.settings.get("RETRY_HTTP_CODES")}')
        if response.status in self.crawler.settings.get('RETRY_HTTP_CODES', []):
            self.process_exception(request, StatusCodeError(response.status), spider)
            raise IgnoreRequest()
        return response

    def process_exception(self, request, exception, spider):
        logger.warning(f'CSDM -> process_exception, url:{request.url}')
        return self.scheduler.process_exception(request, exception, spider)

class RotateUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = random.choice(agents)
        request.headers["User-Agent"] = ua

class RotateUserAgentDisableCrawleraCookiesMiddleware(object):
    def process_request(self, request, spider):
        # request.headers["X-Crawlera-Cookies"] = "disable"
        if request.meta.get('UserAgent'):
            request.headers["User-Agent"] = request.meta.get('UserAgent')
            spider.logger.info('---------------')
            request.headers["X-Crawlera-Cookies"] = "disable"
        else:
            ua = random.choice(agents)
            request.headers["User-Agent"] = ua
        spider.logger.info(f'User-Agent:{request.headers["User-Agent"]}')

class SetVPSPorxyMiddlewares(object):
    # 必须配置
    to_obtain_ip_address = ''
    to_obtain_ip_address_user = ''
    to_obtain_ip_address_pwd = ''

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS'):  # 获取代理ip地址
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS'))

        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS_USER'):  # 获取代理ip用户名
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address_user = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS_USER'))

        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS_PWD'):  # 获取代理ip认真密码
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address_pwd = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS_PWD'))

        m = cls()
        return m

    def process_request(self, request, spider):
        #获取代理ip设置头信息
        try:
            result = requests.get(self.to_obtain_ip_address,
                                  auth=(self.to_obtain_ip_address_user, self.to_obtain_ip_address_pwd)).text
            currentAddr = result.split("##")[0]
            version = result.split("##")[1]
        except:
            raise RemoteServerCannotBeAccessed()
        spider.logger.info(f'proxy ip address is :{currentAddr}')
        request.meta['proxy'] = currentAddr
        # request.meta['proxy'] = '127.0.0.1:8888'



# class DisableCrawleraCookies(object):
#     def process_request(self, request, spider):
#         request.headers["X-Crawlera-Cookies"] = "disable"


class AmazonSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PhantomJSMiddleware(object):
    # currentAddr=''
    # version=''
    obtain_ip_retries_default = 5
    selenium_page_waiting_time_default = 5
    selenium_time_out=selenium_page_waiting_time_default+60+60
    #选配
    obtain_ip_retries=obtain_ip_retries_default
    selenium_page_waiting_time=selenium_page_waiting_time_default

    #必须配置
    to_obtain_ip_address=''
    to_obtain_ip_address_user=''
    to_obtain_ip_address_pwd=''

    def __init__(self, currentAddr, version):
        self.currentAddr = currentAddr
        self.version = version

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.settings.getint('OBTAIN_IP_RETRIES'):#拨号后获取ip的重试次数,等待时间指数增加
            cls.obtain_ip_retries=int(crawler.settings.getbool('OBTAIN_IP_RETRIES'))
            if cls.obtain_ip_retries<1:
                cls.obtain_ip_retries=cls.obtain_ip_retries_default

        if crawler.settings.getint('SELENIUM_PAGE_WAITING_TIME'):  # 模拟器加载压面，等待时间和超时时间
            cls.selenium_page_waiting_time = int(crawler.settings.getbool('SELENIUM_PAGE_WAITING_TIME'))
            if cls.selenium_page_waiting_time < 1:
                cls.selenium_page_waiting_time = cls.selenium_page_waiting_time_default
        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS'):  # 获取代理ip地址
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS'))

        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS_USER'):  # 获取代理ip用户名
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address_user = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS_USER'))

        if not crawler.settings.get('TO_OBTAIN_IP_ADDRESS_PWD'):  # 获取代理ip认真密码
            raise ProxyNotConfigured()
        else:
            cls.to_obtain_ip_address_pwd = str(crawler.settings.get('TO_OBTAIN_IP_ADDRESS_PWD'))

        try:
            result = requests.get(cls.to_obtain_ip_address,
                                  auth=(cls.to_obtain_ip_address_user, cls.to_obtain_ip_address_pwd)).text
            print('init:' + result)
            currentAddr = result.split("##")[0]
            version = result.split("##")[1]
        except:
            raise RemoteServerCannotBeAccessed()

        # cls.currentAddr = '111.226.188.203:8889'
        # currentAddr = '{}:53127'.format(currentAddr.split(":")[0])
        # version = version
        m = cls(currentAddr, version)
        crawler.signals.connect(m.spider_closed, signal=signals.spider_closed)
        return m

    def spider_closed(self):
        # currentAddr = ''
        # version = ''
        pass

    def process_request(self, request, spider):
        driver= None
        try:
            spider.logger.info("process_request phantom")
            spider.logger.info("request:{}".format(request))
            spider.logger.info("request.meta:{}".format(request.meta))
            # if request.meta.get('PhantomJS'):
            if request.meta.get(b'frontier_request').meta.get('PhantomJS', False):

                spider.logger.info("currentAddr:{}".format(self.currentAddr))
                #获取代理ip
                if request.meta.get('currentAddr'):
                    self.currentAddr=request.meta.get('currentAddr')

                dcap = dict(DesiredCapabilities.PHANTOMJS)
                service_args = [
                    '--proxy=' + self.currentAddr,
                    #'--proxy=127.0.0.1:8888',
                    '--ignore-ssl-errors=true',
                    '--load-images=false',
                    '--disk-cache=true',
                    # '--disk-cache-path=/Users/hanyi/Documents/app/cache'
                    # '--disk-cache-path=/Users/sunwei/Documents/workspace-xbn/xbn-distributed-crawler/cache'
                    '--disk-cache-path=/opt/cache'
                ]  # 默认为http代理，可以指定proxy type

                ua=random.choice(agents)
                spider.logger.info('User-Agent: %s' % ua)
                headers = {
                    'User-Agent': ua
                }
                for key, value in headers.items():
                    capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
                    dcap[capability_key] = value

                driver = webdriver.PhantomJS(service_args=service_args,
                                             desired_capabilities=dcap)  # driver = webdriver.Firefox(proxy=proxy)
                driver.set_page_load_timeout(self.selenium_time_out)
                driver.set_script_timeout(self.selenium_time_out)
                driver.get(request.url)

                driver.save_screenshot('111.png')

                try:
                    spider.logger.info('waitting for element ......')
                    element = WebDriverWait(driver, self.selenium_page_waiting_time).until(#等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行，主要是判断增值服务
                        EC.presence_of_element_located((By.XPATH, '//*[@id="availability"]/span'))
                    )

                    flag = driver.find_element_by_xpath('//*[@id="availability"]/span').text == 'Currently unavailable.'
                    if flag:
                        driver.quit()
                        url = request.url
                        split = url.split('/')
                        request.meta['asin'] = split[5]
                        request.meta['flag'] = True
                        return HtmlResponse('https://www.amazon.com/gp/cart/view.html/ref=nav_cart', encoding='utf-8',body='')
                except:
                    flag = False
                    spider.logger.info('无库存提示信息')


                #必须有的流程，点击购物车。
                try:
                    spider.logger.info('waitting for element ......')
                    elem_sub = WebDriverWait(driver, self.selenium_page_waiting_time).until(
                        # 等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行。
                        EC.presence_of_element_located((By.XPATH, '//*[@id="add-to-cart-button"]'))
                    )
                    elem_sub.click()
                except:
                    flag = False

                    driver.save_screenshot('222.png')
                    spider.logger.info('无点击购物车按钮')

                #增值服务处理
                handles = driver.window_handles
                driver.switch_to.window(window_name=handles[0])
                try:
                    spider.logger.info('waitting for element ......')
                    click5 = WebDriverWait(driver, self.selenium_page_waiting_time).until(#等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行，
                        EC.presence_of_element_located((By.XPATH, '//*[@id="siNoCoverage-announce"]'))
                    )
                    click5.click()

                except:
                    spider.logger.info('无增值服务')
                #跳转购物车页面
                driver.get('https://www.amazon.com/gp/cart/view.html/ref=nav_cart')


                #点击购物车数量输入框
                try:
                    spider.logger.info('waitting for element ......')
                    click6 = WebDriverWait(driver, self.selenium_page_waiting_time).until(#等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行
                        EC.presence_of_element_located((By.XPATH, '//*[starts-with(@id,"a-autoid-") and @data-action="a-dropdown-button"]'))
                    )
                    click6.click()

                except:
                    driver.save_screenshot('333.png')
                    spider.logger.info('购物车商品数量输入框无法点击')

                # 修改购物车数量
                try:
                    spider.logger.info('waitting for element ......')
                    click7 = WebDriverWait(driver, self.selenium_page_waiting_time).until(
                        # 等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="dropdown1_9"]'))
                    )
                    click7.click()

                except:
                    driver.save_screenshot('444.png')
                    spider.logger.info('无法点击1-9')

                # 修改购物车数量
                try:
                    spider.logger.info('waitting for element ......')
                    input = WebDriverWait(driver, self.selenium_page_waiting_time).until(
                        # 等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="activeCartViewForm"]/div[2]/div/div[4]/div/div[3]/div/div/input'))
                    )
                    input.send_keys('999')

                except:
                    driver.save_screenshot('555.png')
                    spider.logger.info('无法输入999')
                # 修改购物车数量
                try:
                    spider.logger.info('waitting for element ......')
                    click8 = WebDriverWait(driver, self.selenium_page_waiting_time).until(
                        # 等待是否出现这个元素，如果有就点击关闭，如果没有。就继续执行
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[starts-with(@id,"a-autoid-") and @data-action="update"]'))
                    )
                    click8.click()
                except:
                    spider.logger.info('无法更新999')
                    raise CartSpiderError
                try:
                    spider.logger.info('waitting for element ......')
                    element = WebDriverWait(driver, self.selenium_page_waiting_time).until_not(#等待15秒，如果15秒内完成判断，直接跳过。
                        EC.presence_of_element_located((By.XPATH, '//*[starts-with(@id,"a-autoid-") and @data-action="update"]'))
                        # lambda driver: driver.find_element_by_xpath("id('activeCartViewForm')/div[2]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]")
                    )
                    content = driver.page_source.encode('utf-8')

                    driver.save_screenshot('666.png')
                    #driver.save_screenshot('333.png')
                except:
                    driver.save_screenshot('666.png')
                    #driver.save_screenshot('123.png')
                    content = driver.page_source.encode('utf-8')
                return HtmlResponse('https://www.amazon.com/gp/cart/view.html/ref=nav_cart', encoding='utf-8',body=content)
            else:
                return request
        finally:
            if driver:
                driver.quit()

    def process_exception(self,request, exception, spider):

        if isinstance(exception, CartSpiderError):
            # 不拨号
            spider.logger.info('———————————CartSpiderError———————————')
            spider.crawler.stats.inc_value('error_count')
            errors = spider.crawler.stats.get_value('errors', [])
            error_msg = {'middlewares': 'PhantomJSMiddleware', 'error_str': str(exception), 'url': request.url}
            errors.append(error_msg)
            spider.crawler.stats.set_value('errors', errors)
            return request
        else:
            spider.logger.warning(f'exception: {str(exception)}')
            spider.logger.exception(exception)

            #如果发现缓存的ip和服务器获取的ip不一致，使用服务器ip不去拨号。
            addr = (self.currentAddr.split(':'))[0]
            spider.logger.info('local ip address is:' + addr)
            retries = 1
            flag=True
            while retries <= self.obtain_ip_retries:
                spider.logger.info(f'dial-upDetection..... time:{retries}')
                serverIpInfo = requests.get(self.to_obtain_ip_address,
                                    auth=(self.to_obtain_ip_address_user, self.to_obtain_ip_address_pwd)).text
                spider.logger.info(f'server address :{serverIpInfo}')
                serverIp = (serverIpInfo.split(':'))[0]
                if not serverIp == addr:
                    self.currentAddr = (serverIpInfo.split('##'))[0]
                    self.version = (serverIpInfo.split('##'))[1]
                    flag =False
                    break
                time.sleep(2 * retries)
                retries = retries + 1
            if flag:
                spider.logger.info('process_exception execute!! get new ip adderss')


                url = 'http://' + addr + ':5000/pppoe' + '/' + self.version
                spider.logger.info('retry pppoe url is:' + url)
                try:
                    requests.get(url, auth=(self.to_obtain_ip_address_user, self.to_obtain_ip_address_pwd), timeout=5).text
                except:
                    spider.logger.info('Can Not to Access ：' + url)


                spider.crawler.stats.inc_value('error_count')
                errors = spider.crawler.stats.get_value('errors', [])
                error_msg = {'middlewares': 'PhantomJSMiddleware', 'error_str': 'adsl re dial', 'url': request.url}
                errors.append(error_msg)
                spider.crawler.stats.set_value('errors', errors)

                retries = 1
                while retries <= self.obtain_ip_retries:
                    spider.logger.info('getting new address ,doing .....')
                    text = requests.get(self.to_obtain_ip_address,
                                        auth=(self.to_obtain_ip_address_user, self.to_obtain_ip_address_pwd)).text
                    spider.logger.info('current address :' + text)
                    subtext = (text.split(':'))[0]
                    if not subtext == addr:
                        spider.logger.info('getting new address ,done :' + text)
                        # request.meta['currentAddr'] = (text.split('##'))[0]
                        self.currentAddr = (text.split('##'))[0]
                        self.version = (text.split('##'))[1]
                        break
                    time.sleep(2 * retries)
                    retries = retries + 1
            # return request
            if '?' not in request.url: #url 中不包含参数
                newurl = '{}?{}{}'.format(request.url, '_ts=',int(time.time()))  # 防止url 被拦截器拦截而导致请求遗漏
            else: # url中包含参数
                if '?_ts=' in request.url: #只包含时间戳参数
                    newurl = '{}?{}{}'.format(request.url[:request.url.index('?_ts=', 1)], '_ts=', int(time.time()))
                elif '&_ts=' in request.url:
                    newurl = '{}{}{}'.format(request.url[:request.url.index('&_ts=', 1)], '&_ts=', int(time.time()))
                else:
                    newurl = '{}{}{}'.format(request.url, '&_ts=', int(time.time()))  # 防止url 被拦截器拦截而导致请求遗漏
            # if '?' not in request.url:
            #     newurl='{}?{}'.format(request.url, int(time.time()))  #防止url 被拦截器拦截而导致请求遗漏
            # else:
            #     newurl = '{}?{}'.format(request.url[:request.url.index('?', 1)], int(time.time()))
            return request.replace(url=newurl)

        # def f(a):
        #     ...:
        #     if '?' not in a:
        #         ...:
        #         return '{}?{}'.format(a, int(time.time()))
        #     ...:     else:
        #     ...:
        #     return '{}?{}'.format(a[:a.index('?', 1)], int(time.time()))

        # retries=1
        # while retries<=self.obtain_ip_retries:
        #     spider.logger.info('getting new address ,doing .....')
        #     text = requests.get(self.to_obtain_ip_address,auth=(self.to_obtain_ip_address_user, self.to_obtain_ip_address_pwd)).text
        #     spider.logger.info('current address :'+text)
        #     subtext=(text.split(':'))[0]
        #     if not subtext == addr:
        #         spider.logger.info('getting new address ,done :' + text)
        #         request.meta['currentAddr']=(text.split('##'))[0]
        #         self.version=(text.split('##'))[1]
        #         break
        #     time.sleep(2*retries)
        #     if retries == self.obtain_ip_retries:
        #         spider.logger.info('adsl dial up service error!!')
        #         #发送钉钉消息
        #         errors = spider.crawler.stats.get_value('errors', [])
        #         error_msg = {'middlewares': 'PhantomJSMiddleware', 'error_str': 'Maximum Retries Not Get New ProxyIp', 'url': request.url}
        #         errors.append(error_msg)
        #         spider.crawler.stats.set_value('errors', errors)
        #         return request #请求错误就不再继续请求。
        #         #抛出异常，可能由于adsl拨号服务器异常，导致无法更换ip导致ip总是相同的。需要进行重试次数调节，或者坚持adsl服务器异常。
        #     retries=retries+1
        # newurl=request.url+'?'+str(time.time())#防止url 被拦截器拦截而导致请求遗漏
        # item ={}
        # item['url']=request.url
        # yield item
        # return request.replace(url=newurl)

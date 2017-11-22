class RemoteServerCannotBeAccessed(Exception):
    def __init__(self, reason='Fixed Ip Servers Can not Access,Unable To Get ProxyIp'):
        self.reason = reason

class OrderError(Exception): #middlewares顺序错误，user-agent应该放在phantomjs-middlewares 前面
    def __init__(self, reason='Middleware Configuration Sequence error ，Must Be Afte rUseragent'):
        self.reason = reason

class ProxyNotConfigured(Exception):
    def __init__(self, reason='Get ProxyIp Related Configuration Is Not Specified,Please Modify setting.py'):
        self.reason = reason

class CartSpiderError(Exception):
    def __init__(self, reason='this asin error'):
        self.reason = reason

class StatusCodeError(Exception):
    def __init__(self, status_code, reason='status code is illegal'):
        self.reason = reason
        self.status_code = status_code

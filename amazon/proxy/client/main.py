# -*- coding: utf-8 -*-
# Created by hanyi at 2017年09月29日
# adsl拨号服务
from flask import request, Flask, Response
from .config import *
from functools import wraps
import subprocess

def check_auth(username, password):
    if NEED_AUTH:
        return username == AUTH_USER and password == AUTH_PASSWORD
    else:
        return True


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


app = Flask(__name__)




@app.route('/pppoe/<version>', methods=['GET'])
#@requires_auth
def pppoe(version):
    remoteversion=0
    localversion = 0
    if version:
        remoteversion = version
    with open('version', 'r') as f:
        local = f.read().strip()
        f.close()
        if local:
            localversion=local
        else:
            localversion=0
        if remoteversion<localversion:
            return 'Has Launched Dial'
    with open('version', 'w') as f:
            localversion = localversion + 1
            f.write(str(localversion))
            f.close()
    try:
        print('start !!!')
        subprocess.Popen(["./request.sh","./request.conf","./version"])
    except:
        print('error !!!')
        subprocess.Popen(["./request.sh", "./request.conf", "./version"])
    else:
        print("pppoe sucess!!")
    return '200'
if __name__ == '__main__':
    subprocess.Popen(["./request.sh", "./request.conf", "./version"])
    app.run(host='0.0.0.0', port=PORT)



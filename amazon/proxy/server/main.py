from flask import request, Flask, Response
from .config import *
from functools import wraps

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


@app.route('/record/<key>/<version>', methods=['GET'])
def record(key,version):
    if key == KEY:
        ip = request.remote_addr

        with open('version', 'w') as f:
            f.write(version)
            f.close()

        with open('ip', 'w') as f:
            f.write(ip)
            f.close()
        return ip + '\n'
    else:
        return 'Invalid Key'

@app.route('/', methods=['GET'])
@requires_auth
def proxy():
    version=""
    with open('version', 'r') as f:
        version = f.read().strip()
        f.close()
    with open('ip', 'r') as f:
        ip = f.read().strip()
        f.close()
        if ip:
            return ip + ':' + str(PROXY_PORT) +'##' + version
    return '0'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)



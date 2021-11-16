from dbAccess import JSONEncoder
from dbEntry import userAC, orderAC
from emailSender import verifyCode, notifyOrder
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from order import alipay, orderVIP, orderCustom
import settings
import traceback
from waitress import serve

app = Flask(__name__)
app.config.from_object('configure')
CORS(app)


@app.route('/')
def helloWorld():
    return '<h1>一二三木头人</h1>'


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/register: {data}')
        try:
            # Check
            if userAC.isUsernameRepeat(data['name']):
                status = 'nameRegistered'
            elif userAC.isEmailRepeat(data['email']):
                status = 'emailRegistered'
            else:
                userAC.createUser(data)
                status = 'registerSuccess'
        except Exception:
            status = ''
            traceback.print_exc()
        return jsonify({'status': status})
    return jsonify({'status': ''})


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/login: {data}')
        try:
            # Check
            if userAC.matchLogIn(data):
                info = userAC.updateLogTime(data['name'], data['type'])
                status = 'logInSuccess'
            else:
                info = ''
                status = 'logInMismatch'
        except Exception:
            info = ''
            status = ''
            traceback.print_exc()
        return jsonify({'status': status, 'info': info})
    return jsonify({'status': '', 'info': ''})


@app.route('/cookieLogin', methods=['POST'])
def cookieLogin():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/cookieLogin: {data}')
        try:
            # Check
            if userAC.cookieLogIn(data):
                info = userAC.updateLogTime(data['username'], 'name')
                status = 'cookieValid'
            else:
                info = ''
                status = 'cookieInvalid'
        except Exception:
            info = ''
            status = ''
            traceback.print_exc()
        return jsonify({'status': status, 'info': info})
    return jsonify({'status': '', 'info': ''})


@app.route('/forget', methods=['POST'])
def forget():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/forget: {data}')
        try:
            # Check
            if not userAC.isEmailRepeat(data['email']):
                status = 'notRegistered'
            elif userAC.forgetPassword(data['email'], data['pwd']):
                status = 'findSuccess'
            else:
                status = 'findFailure'
        except Exception:
            status = ''
            traceback.print_exc()
        return jsonify({'status': status})
    return jsonify({'status': ''})


@app.route('/email', methods=['POST'])
def email():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/email: {data}')
        try:
            # Check
            if data['type'] == 'reg':
                status = 'hasRegistered' if userAC.isEmailRepeat(
                    data['email']) else 'emailSuccess'
            elif data['type'] == 'find':
                status = 'emailSuccess' if userAC.isEmailRepeat(
                    data['email']) else 'notRegistered'
            else:
                status = ''
            # Send
            if status == 'emailSuccess':
                verifyCode(data)
        except Exception:
            status = ''
            traceback.print_exc()
        return jsonify({'status': status})
    return jsonify({'status': ''})


@app.route('/order', methods=['POST'])
def order():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/order: {data}')
        try:
            # Check
            orderId = str(orderAC.createOrder(data))
            data['orderId'] = orderId
            # Send
            if data['type'] == 'vip':
                jump = orderVIP(data)
            elif data['type'] == 'analysis':
                jump = orderCustom(data)
            else:
                jump = ''
            # Jump
            if jump:
                status = 'orderSuccess'
            else:
                status = ''
        except Exception:
            jump = ''
            status = ''
            traceback.print_exc()
        return jsonify({'status': status, 'jump': jump, 'orderId': orderId})
    return jsonify({'status': '', 'jump': '', 'orderId': ''})


@app.route('/paid', methods=['POST'])
def paid():
    if request.method == 'POST':
        data = request.form.to_dict()
        print(f'/paid: {data}')
        try:
            # Verify
            signature = data.pop('sign')
            success = alipay.verify(data, signature)
            if success and data['trade_status'] in ('TRADE_SUCCESS',
                                                    'TRADE_FINISHED'):
                print(f'/{data["out_trade_no"]} trade succeed')
                orderRes = orderAC.updateOrder(data)
                userRes = userAC.updateVIP(orderRes)
                data['email'] = userRes['email']
                data['payment_method'] = '支付宝'
                notifyOrder(data)
                status = 'tradeSuccess'
            else:
                print(f'/{data["out_trade_no"]} trade failed')
                status = 'tradeFailure'
        except Exception:
            status = ''
            traceback.print_exc()
        return jsonify({'status': status})
    return jsonify({'status': ''})


@app.route('/confirmPaid', methods=['POST'])
def confirmPaid():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/confirmPaid: {data}')
        try:
            # Check
            if orderAC.confirmOrder(data):
                info = userAC.searchUserId(data['userId'])
                info = json.dumps(info, cls=JSONEncoder)
                status = 'paidSuccess'
            else:
                info = ''
                status = 'paidFailure'
        except Exception:
            status = ''
            traceback.print_exc()
        return jsonify({'status': status, 'info': info})
    return jsonify({'status': '', 'info': info})


@app.route('/findOrder', methods=['POST'])
def findOrder():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        print(f'/findOrder: {data}')
        try:
            # Fetch
            res = orderAC.searchUserOrder(data['_id'])
            status = 'findSuccess'
        except Exception:
            res = ''
            status = ''
            traceback.print_exc()
        return jsonify({'status': status, 'res': res})
    return jsonify({'status': '', 'res': ''})


if __name__ == "__main__":
    port = settings.flaskPort
    print(f'Flask started at port {port}')
    serve(app, host="0.0.0.0", port=port)

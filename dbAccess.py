from bson.objectid import ObjectId
from datetime import date, datetime, timedelta
import hashlib
import json
import pymongo
from pymongo import ReturnDocument
import random
import string


class DBAccess:
    def __init__(self, **kwargs):
        strClient = f'mongodb://{kwargs["user"]}:{kwargs["pwd"]}@{kwargs["host"]}:{kwargs["port"]}'
        self.dbClient = pymongo.MongoClient(strClient)
        self.db = self.dbClient[kwargs['dbName']]
        self.doc = self.db[kwargs['docName']]

    def insert(self, data):
        res = self.doc.insert_one(data)
        return res.inserted_id

    def search(self, query, pageCnt=0, pageSize=10):
        res = self.doc.find(query).skip(pageSize * pageCnt).limit(pageSize)
        return res

    def searchId(self, _id):
        res = self.doc.find_one(
            {'_id': _id if isinstance(_id, ObjectId) else ObjectId(_id)})
        return res

    def searchIdList(self, idList):
        res = []
        for _id in idList:
            res.append(self.searchId(_id))
        return res

    def __del__(self):
        self.dbClient.close()
        print('Mongodb connection closed')


class UserAccess(DBAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def searchUserId(self, _id):
        res = self.doc.find_one(
            {'_id': _id if isinstance(_id, ObjectId) else ObjectId(_id)},
            {'salt': 0})
        return res

    def searchUsername(self, data):
        res = self.search({'username': data})
        return res

    def searchEmail(self, data):
        res = self.search({'email': data})
        return res

    def isUsernameRepeat(self, data):
        return True if self.searchUsername(data).count() else False

    def isEmailRepeat(self, data):
        return True if self.searchEmail(data).count() else False

    def createUser(self, struct):
        salt = ''.join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(16))
        pwd = getMd5(struct['pwd'] + salt)
        res = self.insert({
            'username': struct['name'],
            'password': pwd,
            'salt': salt,
            'email': struct['email'],
            'phone': None,
            'register_time': datetime.now(),
            'last_login_time': None,
            'vip_level': 'basic',
            'vip_effect_time': None,
            'vip_expire_time': None,
            'avatar': None,
            'birthday': None,
            'role': 'personal',
            'state': 'valid',
        })
        return res

    def matchLogIn(self, struct):
        try:
            if struct['type'] == 'name':
                res = self.searchUsername(struct['name'])[0]
                return getMd5(struct['pwd'] + res['salt']) == res['password']
            elif struct['type'] == 'email':
                res = self.searchEmail(struct['name'])[0]
                return getMd5(struct['pwd'] + res['salt']) == res['password']
            else:
                return False
        except Exception:
            return False

    def cookieLogIn(self, struct):
        try:
            res = self.searchUsername(struct['username'])[0]
            return struct['password'] == res['password']
        except Exception:
            return False

    def updateLogTime(self, data, src):
        # Check
        if src == 'email':
            query = {'email': data}
            entry = self.searchEmail(data)[0]
        else:
            query = {'username': data}
            entry = self.searchUsername(data)[0]
        nowTime = datetime.now()
        lastLoginTime = {'last_login_time': nowTime}
        vipExpired = {
            'vip_level': 'basic',
            'vip_effect_time': None,
            'vip_expire_time': None,
        } if (bool(entry['vip_expire_time'])
              and entry['vip_expire_time'] < nowTime) else {}
        newVal = {'$set': {**lastLoginTime, **vipExpired}}
        # Update
        res = self.doc.find_one_and_update(
            query,
            newVal,
            projection={
                'salt': 0,
            },
            return_document=ReturnDocument.AFTER)
        res = json.dumps(res, cls=JSONEncoder)
        return res

    def forgetPassword(self, email, pwd):
        salt = ''.join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(16))
        newPwd = getMd5(pwd + salt)
        query = {'email': email}
        newVal = {'$set': {'password': newPwd, 'salt': salt}}
        res = self.doc.update_one(query, newVal)
        return res.modified_count

    def updateVIP(self, struct):
        userRes = self.searchId(struct['user_id'])
        nowTime = datetime.now()
        # Effect
        isExpired = (not userRes['vip_expire_time']) or (
            userRes['vip_expire_time'] < nowTime)
        effectTime = nowTime if isExpired else userRes['vip_effect_time']
        # Expire
        levelPeriod = {'month': 30, 'season': 90, 'year': 365}
        deltaTime = timedelta(days=levelPeriod[struct['order_level']])
        expireTime = (nowTime + deltaTime) if isExpired else (
            userRes['vip_expire_time'] + deltaTime)
        # Update
        query = {'_id': ObjectId(struct['user_id'])}
        newVal = {
            '$set': {
                'vip_level': struct['order_level'],
                'vip_effect_time': effectTime,
                'vip_expire_time': expireTime,
            }
        }
        res = self.doc.find_one_and_update(
            query,
            newVal,
            projection={
                'salt': 0,
            },
            return_document=ReturnDocument.AFTER)
        # res = json.dumps(res, cls=JSONEncoder)
        return res


class OrderAccess(DBAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def searchUserOrder(self, data):
        res = self.search({'user_id': data})
        return [json.dumps(r, cls=JSONEncoder) for r in res]

    def createOrder(self, struct):
        res = self.insert({
            'user_id': struct['userId'],
            'order_create_time': datetime.now(),
            'order_finish_time': None,
            'order_amount': struct['amount'],
            'order_discount': struct['discount'],
            'payment_amount': None,
            'payment_method': struct['method'],
            'order_level': struct['level'],
            'order_renew': struct['renew'],
            'order_status': 'undone',
            'after_status': None,
        })
        return res

    def updateOrder(self, struct):
        query = {'_id': ObjectId(struct['out_trade_no'])}
        newVal = {
            '$set': {
                'order_create_time':
                datetime.strptime(struct['gmt_create'], '%Y-%m-%d %H:%M:%S'),
                'order_finish_time':
                datetime.strptime(struct['gmt_payment'], '%Y-%m-%d %H:%M:%S'),
                'payment_amount':
                float(struct['total_amount']),
                'order_status':
                'paid',
                'after_status':
                'normal',
            }
        }
        res = self.doc.find_one_and_update(
            query,
            newVal,
            projection={
                '_id': 0,
            },
            return_document=ReturnDocument.AFTER)
        # res = json.dumps(res, cls=JSONEncoder)
        return res

    def confirmOrder(self, struct):
        return self.doc.find({
            '_id': ObjectId(struct['orderId']),
            'user_id': struct['userId'],
            'order_status': 'paid',
        }).count()


class AnalysisAccess(DBAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def searchUserAnalysis(self, data):
        res = self.search({'user_id': data})
        return [json.dumps(r, cls=JSONEncoder) for r in res]

    def createAnalysis(self, struct):
        res = self.insert({
            'user_id': struct['userId'],
            'order_id': struct['userId'],
            'custom_effect_time': None,
            'custom_expire_time': None,
            'status': 'inactive',
        })
        return res


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)


def getMd5(pwd):
    return hashlib.md5(pwd.encode('utf-8')).hexdigest()

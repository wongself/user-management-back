from alipay import AliPay
from alipay.utils import AliPayConfig
import settings

app_private_key_string = open('ali/ali_private_key.pem').read()
alipay_public_key_string = open('ali/ali_public_key.pem').read()

alipay = AliPay(
    appid='8364872364872364827374',  # 发起请求的应用ID
    app_notify_url=None,  # 默认回调url
    app_private_key_string=app_private_key_string,
    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_string=alipay_public_key_string,
    sign_type='RSA2',  # RSA 或者 RSA2
    debug=False,  # 默认False
    verbose=False,  # 输出调试数据
    config=AliPayConfig(timeout=10)  # 可选, 请求超时时间
)


def orderVIP(data):
    levelSubject = {'month': '月付', 'season': '季付', 'year': '年付'}
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=data['orderId'],  # 唯一订单号
        total_amount=data['amount'],  # 订单金额
        subject='一二三木头人' + levelSubject[data['level']] + 'VIP会员订单',  # 订单说明
        return_url='https://example.com',  # 支付成功跳转地址
        notify_url='http://' + settings.flaskHost + ':' +
        str(settings.flaskPort) + '/paid'  # 异步通知地址（私有地址无效）
    )
    return alipayJump(order_string)


def orderCustom(data):
    levelSubject = {
        'analysis_one': '企业定制化木头人分析报告（一个月）',
        'analysis_two': '企业定制化木头人分析报告（两个月）',
        'analysis_three': '企业定制化木头人分析报告（三个月）',
    }
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=data['orderId'],  # 唯一订单号
        total_amount=data['amount'],  # 订单金额
        subject='一二三木头人' + levelSubject[data['level']],  # 订单说明
        return_url='https://example.com',  # 支付成功跳转地址
        notify_url='http://' + settings.flaskHost + ':' +
        str(settings.flaskPort) + '/paid'  # 异步通知地址（私有地址无效）
    )
    return alipayJump(order_string)


# 电脑网站支付，部署时需要切换为https://openapi.alipay.com/gateway.do? + s
def alipayJump(s):
    # return 'https://openapi.alipay.com/gateway.do?' + s
    return 'https://openapi.alipaydev.com/gateway.do?' + s  # 沙箱环境跳转测试

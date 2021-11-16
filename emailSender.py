from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

fromAddr = 'mutouren@289736128736.com'  # 发送者邮箱地址
password = 'ioufokchdsjgcjsdahbcjshdfvhgsadcvhgasc'  # 发送者邮箱SMTP授权码


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def verifyCode(data):
    msg = MIMEText(
        f"""
        <html><body>
        <p style="font-size: 20px;">尊敬的用户：您好！</p>
        <p>请在验证码输入框中输入：<span style="color: #009688; font-size: 20px;">{data['code']}</span>，以完成操作。</p>
        <p>此操作可能会修改您的密码、绑定邮箱或其他重要信息。如非本人操作，请及时登录并修改密码以保证帐户安全。</p>
        <p>工作人员不会向你索取此验证码，请勿泄漏！</p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.5rem 0 0.25rem;">此为系统邮件，请勿回复。</p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.25rem 0;">请保管好您的邮箱，避免账号被他人盗用。</p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.25rem 0;">一二三木头人团队</p>
        </body></html>
        """, 'html', 'utf-8')
    msg['From'] = _format_addr(f'一二三木头人 <{fromAddr}>')
    msg['To'] = _format_addr(f'一二三木头人用户 <{data["email"]}>')
    msg['Subject'] = Header(f'一二三木头人 - 您的邮箱验证码为 {data["code"]}',
                            'utf-8').encode()
    sendEmail(data, msg)


def notifyOrder(data):
    msg = MIMEText(
        f"""
        <html><body>
        <p style="font-size: 20px;">尊敬的用户：您好！</p>
        <p>一二三木头人已收到您的订单，订单号为<span style="color: #009688;">{data["out_trade_no"]}</span>，商品内容为<span style="color: #009688;">{data["subject"]}</span>，支付金额为<span style="color: #009688;">RMB${data["total_amount"]}</span>，支付时间为<span style="color: #009688;">{data["gmt_payment"]}</span>。</p>
        <p>您选择的是{data["payment_method"]}支付，订单信息以“个人中心 - 我的订单”页面显示为准，您也可以随时进入该页面对订单进行查看等操作。 </p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.5rem 0 0.25rem;">此为系统邮件，请勿回复。</p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.25rem 0;">请保管好您的邮箱，避免账号被他人盗用。</p>
        <p style="color: #7d8591; font-size: 12px; margin: 0.25rem 0;">一二三木头人团队</p>
        </body></html>
        """, 'html', 'utf-8')
    msg['From'] = _format_addr(f'一二三木头人 <{fromAddr}>')
    msg['To'] = _format_addr(f'一二三木头人用户 <{data["email"]}>')
    msg['Subject'] = Header(f'一二三木头人已收到您的订单【{data["out_trade_no"]}】',
                            'utf-8').encode()
    sendEmail(data, msg)


def sendEmail(data, msg):
    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    # server.set_debuglevel(1)
    server.login(fromAddr, password)
    server.sendmail(fromAddr, [data['email']], msg.as_string())
    server.quit()

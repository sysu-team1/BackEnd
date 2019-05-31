# -*- coding:utf-8 -*-
import smtplib, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
import secret_key, constants, random


def send_email(rcptto, username=secret_key.USERNAME, password=secret_key.PASSWORD, replyto=secret_key.REPLYTO):
    '''发送邮件
    参数：
        username 表示控制台创建的发件人地址
        password 表示发件人密码
        replyto 表示回复地址
        rcptto 表示收件人地址
        input:rcptto 收件人
        output:code 验证码
    example：
    code = utils.send_email(rcptto='653128964@qq.com')
    print(code)
    '''

    # 生成6位验证码
    code = generate_verification_code()
    # 构建alternative结构
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header('验证码').encode()
    msg['From'] = '%s <%s>' % (Header('闲余翻身').encode(), username)
    msg['To'] = rcptto
    msg['Reply-to'] = replyto
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate() 
    # 构建alternative的text/html部分
    html_file = open('./tools/templates/email.html','r',encoding="utf-8")
    html_text = html_file.read().format(rcptto=rcptto, code=code) + '<style type="text/css">.qmbox style, .qmbox script, .qmbox head, .qmbox link, .qmbox meta {display: none !important;}</style></div></div><!-- --><style>#mailContentContainer .txt {height:auto;}</style>  </div>'
    texthtml = MIMEText(html_text, _subtype='html', _charset='UTF-8')
    msg.attach(texthtml)
    # 发送邮件
    try:
        client = smtplib.SMTP_SSL(host='smtp.gmail.com')
        client.connect('smtpdm.aliyun.com', 465)
        # 开启DEBUG模式
        client.set_debuglevel(0)
        client.login(username, password)
        client.sendmail(username, rcptto, msg.as_string())
        client.quit()
        print('邮件发送成功！')
    except Exception as e:
        print('邮件发送异常, ', str(e))
    return code


def generate_verification_code():
    '''生成6位验证码
    参数：
        input:None
        output: code
    '''
    return ''.join(random.sample(constants.code_element_list, 6))


def model_repr(obj, pattern: str, orders):
    ''' 返回制定的样式

    参数：
        obj：从数据库中查询的结果
        pattern：模式字符串
        orders：需要的属性的顺序
    '''
    temp = []
    for order in orders:
        temp.append('"{}"'.format(order))
        attr = getattr(obj, order)
        if attr is None:
            attr = '""'
        elif isinstance(attr, (str)):
            attr = '"{}"'.format(attr)
        else:
            attr = str(attr)
        temp.append(attr)
    return pattern % tuple(temp)


def make_pattern(orders_len: int):
    '''用于获取指定长度的匹配字符串
    
    参数：
        orders_len: 指定属性的列表的长度
    '''
    if orders_len <= 0:
        raise AttributeError('orders_len can not be less than 1')
    pattern = r'{'
    for _ in range(orders_len - 1):
        pattern += '%s: %s, '
    pattern += r'%s: %s}'
    return pattern

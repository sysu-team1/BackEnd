# -*- coding:utf-8 -*-
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
import random
import secret_key


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



# 利用random生成6为验证码
# code_element_list 存储随机验证码的生成元素
code_element_list = []
# 添加0-9数字
for i in range(10):
    code_element_list.append(str(i))
# 添加A-Z数字
for i in range(65, 91):
    code_element_list.append(chr(i))
# 添加a-z数字
for i in range(97, 123):
    code_element_list.append(chr(i))


def generate_verification_code():
    '''生成6位验证码
    参数：
        input:None
        output: code
    '''
    return ''.join(random.sample(code_element_list, 6))
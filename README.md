<!-- TOC -->

- [闲余翻身 后台部署文档](#闲余翻身-后台部署文档)
    - [一、部署架构图](#一部署架构图)
        - [服务器图](#服务器图)
        - [文件目录](#文件目录)
    - [二、部署流程](#二部署流程)
        - [1. 服务器后台环境配置](#1-服务器后台环境配置)
            - [1.1 服务器系统环境](#11-服务器系统环境)
            - [1.2 宝塔面板 安装](#12-宝塔面板-安装)
            - [1.3 LNMP环境的安装](#13-lnmp环境的安装)
            - [1.4 SMTP邮件推送服务器](#14-smtp邮件推送服务器)
        - [2. 服务器程序配置运行](#2-服务器程序配置运行)
            - [2.1 拉取后台源代码](#21-拉取后台源代码)
            - [2.2 创建secret.py文件](#22-创建secretpy文件)
            - [2.3 修改app.py文件](#23-修改apppy文件)
            - [2.4 数据库的配置](#24-数据库的配置)
            - [2.5 一键运行](#25-一键运行)
            - [2.6 预装载数据](#26-预装载数据)
    - [三、常见问题解决方法](#三常见问题解决方法)
        - [1. 查看数据库内部状态使用](#1-查看数据库内部状态使用)
        - [2、需要重建数据可](#2需要重建数据可)
        - [3、数据库中无数据](#3数据库中无数据)
        - [4、Python版本不正确](#4python版本不正确)
        - [5、一切正常但是就是连接不上](#5一切正常但是就是连接不上)
        - [其他不确定错误](#其他不确定错误)

<!-- /TOC -->

# 闲余翻身 后台部署文档

项目的后端实现
- python3.7 Flask
- MySQL

## 一、部署架构图

### 服务器图

![1561308502316](assets/1561308502316.png)

### 文件目录

```
│  app.py					主程序入口
│  config.py				flask与MySQL配置
│  constants.py				常量文件
│  README.md				文档
│  requirements.txt			记录所有依赖包及其精确的版本号，以便新环境部署。
│  secret_key.py			邮件服务器的密钥
│  
├─assets					文档图片文件夹
│      
├─db						数据库操作文件夹
│  │  Accept.py				Accept表
│  │  Answer.py				Answer表
│  │  DbHelper.py			集成的数据库操作文件
│  │  Organization.py		Organization表
│  │  prepare.py			预处理函数文件
│  │  Problem.py			Problem表
│  │  Student.py			Student表
│  │  Task.py				Task表
│  │  test.py				数据库测试文件
│  │  __init__.py
│  │  
│  └─__pycache__			pyc中间文件夹
│          
├─images					用户上传的文件夹
│      
├─responses					响应函数
│  │  my.py					个人信息文件
│  │  task.py				任务相关操作文件
│  │  user.py				用户操作文件
│  │  __init__.py
│  │  测试样例.md
│  │  
│  └─__pycache__			pyc中间文件夹
│          
├─tools
│  │  utils.py				工具类
│  │  
│  ├─templates
│  │      email.html		邮件模板
│  │      
│  └─__pycache__			pyc中间文件夹
│        
└─__pycache__				pyc中间文件夹
```

## 二、部署流程

### 1. 服务器后台环境配置

#### 1.1 服务器系统环境

- 阿里云 CentOS 7.3

#### 1.2 宝塔面板 安装

- [官方安装文档](http://docs.bt.cn/443922)

安装之后根据安装提示的url以及用户名密码成功登陆宝塔面板就说明安装成功

- 安装成功之后开放端口5000，用于数据的传输

#### 1.3 LNMP环境的安装

- [官方文档](http://docs.bt.cn/424212)
- MySQL版本选择5.7

```mysql
刚装完的mysql默认实没有密码的
mysql -u root -p
即可成功登陆，提示welcome to the mysql monitor! 的字样即表示登陆成功
退出之后输入
mysqladmin -u root -p password
根据提示进行重置
```

#### 1.4 SMTP邮件推送服务器

- 使用的是阿里云的邮件推送功能

[阿里云-如何在DNS服务器上配置域名](<https://help.aliyun.com/knowledge_detail/39397.html>)

- 创建发信地址的发送地址以及密钥

### 2. 服务器程序配置运行

#### 2.1 拉取后台源代码

```
git clone https://github.com/sysu-team1/BackEnd.git
```

#### 2.2 创建secret.py文件

- 该文件放在与app.py同个目录下

内容大致如下：

```python
# 发件人地址，通过控制台创建的发件人地址
USERNAME = '发件人地址'
# 发件人密码，通过控制台创建的发件人密码
PASSWORD = '发件人密码'
# 自定义的回复地址
REPLYTO = ''
```

#### 2.3 修改app.py文件

main函数修改为如下

```python
if __name__ == "__main__":
	uploaded_photos = UploadSet('photos')
	configure_uploads(app, uploaded_photos)
	enter_event_and_run_scheduler()
	app.run(debug=True, host='0.0.0.0', port=5000, threaded = True)
```

#### 2.4 数据库的配置

```mysql
mysql的root账号密码是mysql
创建数据库test2
mysql -u root -p mysql
create database money;
exit;
```

#### 2.5 一键运行

```python
python -m pip install -r requirements.txt
python app.py
```

看到下面的信息表示运行成功

![1560345550416](assets/1560345550416.png)

#### 2.6 预装载数据

```python
在浏览器输入 ip + 端口 + '/initial/'即可
```



## 三、常见问题解决方法

### 1. 查看数据库内部状态使用

- 通过面板上的phpMyAdmin可以进行查看

![1560346717283](assets/1560346717283.png)

![1560346754997](assets/1560346754997.png)

### 2、需要重建数据可

- 跟上面一样，支持手动删除与创建

### 3、数据库中无数据

- 请再次尝试使用api导入初始数据

### 4、Python版本不正确

- 从宝塔面板左侧栏的软件商店中查询安装**Python项目管理器**，通过项目管理器的设置安装Python3.7

```python
# 查看已经安装的python版本
pyenv versions
# 切换python版本
pyenv global 3.7.2
```

### 5、一切正常但是就是连接不上

- 检查宝塔面板中以及阿里云控制台是否有设置5000端口自定义开放

### 其他不确定错误

1. 请检查系统环境配置是否与本仓库部署环境一致

- python3.7.2
- requirements.txt

2. 简单查看后台测试文档
3. Email 联系仓库维护者 [mj-love-life](<https://github.com/mj-love-life>)
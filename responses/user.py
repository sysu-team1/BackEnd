'''test
用于引用utils.py中的函数
'''
import sys
import os
sys.path.append('./../')
from tools import utils
from db import db_helper, app, model_repr
from threading import Timer, Thread, Lock
import time
import collections
import sched
codes = collections.OrderedDict()
s = sched.scheduler(time.time, time.sleep) # 用来定时删除过期验证码的调度器
scheduler_lock = Lock()
is_scheduler_running = False # 判定调度器是否正在运行

# 测试场合
# time_limit = 60 * 0.2
# 实际场合
time_limit = 60 * 5


def register_(email, password, student_id, sex, collage, grade, name, validate_code):
	res = {}
	if(email not in codes):
		res = {'error': 1, 'error_message': '未获取验证码或验证码过期'}
	elif(codes[email][0] != validate_code):
		res = {'error': 1, 'error_message': '验证码错误'}
	else:
		'''
		判断邮箱是否被注册
		'''
		error_code, error_message, openid = db_helper.sign_up_true(email, password, student_id, sex, collage, grade, name)
		if(error_code == 0):
			try:
				codes.pop(email)
			except Exception as e:
				print('Error:', e)
			res = {'error': str(error_code), 'error_message': error_message, 'data': {'openid': str(openid)}}
		else:
			res = {'error': str(error_code), 'error_message': error_message, 'data': {'openid': str(openid)}}
	return str(res)


def get_verification_code_(email):
	'''
	通过邮箱获取验证码，
	验证码在一定时间内有效，超过这个期限则会自动删除
	'''
	global is_scheduler_running
	res = {}
	# 验证码还未过期的情况
	if(email in codes):
		res	= {'error': 1, 'error_message': '原验证码未过期'}
		print(str(res))
	# 正常情况
	else:
		''' 
		# 测试生成验证码（不发送邮件）
		# 	code = utils.generate_verification_code()
		发送邮件并生成验证码
			code = utils.send_email(rcptto=email)
		'''
		# code = '11111' # 生成验证码并发送至邮箱
		code = utils.send_email(rcptto=email)
		if code == -1:
			return str({'error': 1, 'error_message': '验证码发送失败'})
		codes[email] = (code, time.time()) # 在本地记录验证码值
		print('生成的验证码', codes[email])
		# print(is_scheduler_running)
		if(not is_scheduler_running): # 若调度器不在运行
			enter_event_and_run_scheduler()
		res	= {'error': 0, 'error_message': '验证码已发送'}
	return str(res)


def delete_invalid_codes():
	'''
	删除本地保存的过期（无效）的验证码。
	OrderedDict按照插入的顺序排序，所以先创建验证码的一定在前面，从前面遍历删除直至遇到未过期的验证码为止
	'''
	global is_scheduler_running
	for k in list(codes):
		if(time.time() - codes[k][1] < time_limit):
			break 
		if(k in codes):
			try:
				print('删除的验证码：', codes.pop(k))
			except Exception as e:
				print('Error:', e)
	if(len(codes) > 0 and s.empty()): # 若还有验证码，且调度队列为空，则继续将delete_invalid_codes加入调度器
		s.enter(time_limit, 0, delete_invalid_codes)
	else:
		is_scheduler_running = False
		if(len(codes) > 0 and not is_scheduler_running): # 应对线程安全，此时可能有验证码加入，但调度器并未开启
			enter_event_and_run_scheduler()


def enter_event_and_run_scheduler():
	scheduler_lock.acquire()
	global is_scheduler_running
	if(not is_scheduler_running):
		is_scheduler_running = True
		if(s.empty()):
			s.enter(2, 0, delete_invalid_codes)
			t = Thread(target = s.run)
			t.start()
	scheduler_lock.release()


def update_(form):
	'''更新用户信息
        可以传递的属性有password/student_id/sex/collage/grade/name/edu_bg/signature
    input:
        openid
        attrs
        (old_password:)
    output:
        error
        data:
            msg: 旧密码错误/修改成功/修改异常/ 不存在该学生/组织 / 邮箱不可修改
    '''
	openid = int(form['openid'])
	success = True
	msg = "更改成功"
	for item in form.items():
		if(item[0] == 'openid' or item[0] == 'old_password'):
			continue
		if(item[0] == 'password'):
			target = db_helper.query_student(openid) if openid >= app.config['SPLIT_STU_ORG'] else db_helper.query_oraganization(openid)
			if target == None:
				return str({'error': 1, "data": {'msg': '不存在该学生或组织'}})
			if('old_password' not in form):
				return str({"error": 1, "data": {"msg": '请输入旧密码'}})
			if target.password == form['old_password']:
				success, msg = db_helper.update_student_or_organization(openid, item[0], item[1])
				if(not success):
					return str({"error": 1, "data": {"msg": msg}})
			else:
				return str({'error': 1, "data": {'msg': '旧密码错误'}})
		else:
			success, msg = db_helper.update_student_or_organization(openid, item[0], item[1])
			if(not success):
				return str({"error": 1, "data": {"msg": msg}})
	return str({"error": 0, "data": {"msg": "更改成功"}})



# def printf():
# 	print(s.empty())
# 	print('test')
# 	print(s.empty())


# test
'''
if __name__ == '__main__':
	enter_event_and_run_scheduler()
	s.enter(time_limit, 0, printf)
	print(s.empty())
	s.run()
	print(s.empty())


	# 测试获取、保存、删除验证码
	# time_limit = 60 * 0.1
	get_verification_code_('11.qq.com')
	get_verification_code_('11.qq.com') # 测试原验证码未过期

	# 删除时没有过期的验证码的情况
	delete_invalid_codes() 
	print('ok1')
	time.sleep(5)
	delete_invalid_codes()
	print('ok2')

	# 删除过期验证码的情况
	time.sleep(2)
	delete_invalid_codes()
	print('ok3')

	# 获取新的 
	get_verification_code_('2')
	print(codes)

	# 输出结果：
	# 生成的验证码 ('11111', 1559045170.948554)
	# {'error': 1, 'data': {'msg': '原验证码未过期'}}
	# ok1
	# ok2
	# 删除的验证码： ('11111', 1559045170.948554)
	# ok3
	# 生成的验证码 ('11111', 1559045177.9637892)
	# OrderedDict([('2', ('11111', 1559045177.9637892))])
'''
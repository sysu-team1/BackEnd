from threading import Timer, Thread
import time
import collections
import sched

codes = collections.OrderedDict()
s = sched.scheduler(time.time, time.sleep) # 用来定时删除过期验证码的调度器
is_scheduler_running = False
time_limit = 60 * 0.2


def login_():
	return "login_"


def register_(email, password, validate_code, name, student_id, grade, major, sex):
	res = {}
	if(email not in codes):
		res = {'error': 1, 'data': {'msg': '未获取验证码或验证码过期'}}
	elif(code[email][0] != validate_code):
		res = {'error': 1, 'data': {'msg': '验证码错误'}}
	else:
		# To Do数据库操作
		if(True):
			res = {'error': 0, 'data': {'msg': '注册成功'}}
		elif:
			res = {'error': 1, 'data': {'msg': '该邮箱已注册'}}
	return str(res)


def get_verification_code_(email):
	'''
	通过邮箱获取验证码，
	验证码在一定时间内有效，超过这个期限则会自动删除
	'''
	res = {}
	# 验证码还未过期的情况
	if(email in codes):
		res	= {'error': 1, 'data': {'msg': '原验证码未过期'}}
		print(str(res));
	# 正常情况
	else:
		code = '11111' # 生成验证码并发送至邮箱
		codes[email] = (code, time.time()) # 在本地记录验证码值
		print('生成的验证码', codes[email])
		if(not is_scheduler_running):
			enter_event_and_run_scheduler()
		res	= {'error': 0, 'data': {'msg': '验证码已发送'}}
	return str(res)


def delete_invalid_codes():
	'''
	删除本地保存的过期（无效）的验证码。
	OrderedDict按照插入的顺序排序，所以先创建验证码的一定在前面，从前面遍历删除直至遇到未过期的验证码为止
	'''
	for k in list(codes):
		if(time.time() - codes[k][1] < time_limit):
			break
		print('删除的验证码：', codes.pop(k))
	if(len(codes) > 0 and s.empty()): # 若还有验证码，且调度队列为空，则继续将delete_invalid_codes加入调度器
		s.enter(time_limit, 0, delete_invalid_codes)
	else:
		is_scheduler_running = False


def enter_event_and_run_scheduler():
	is_scheduler_running = True
	if not s.empty():
		return
	s.enter(time_limit, 0, delete_invalid_codes)
	t = Thread(target = s.run)
	t.start()

# def printf():
# 	print(s.empty())
# 	print('test')
# 	print(s.empty())


# # test
# if __name__ == '__main__':
# 	enter_event_and_run_scheduler()
	# s.enter(time_limit, 0, printf)
	# print(s.empty())
	# s.run()
	# print(s.empty())

	'''
	测试获取、保存、删除验证码
	time_limit = 60 * 0.1
	'''
	# get_verification_code_('11.qq.com')
	# get_verification_code_('11.qq.com') # 测试原验证码未过期

	# # 删除时没有过期的验证码的情况
	# delete_invalid_codes() 
	# print('ok1')
	# time.sleep(5)
	# delete_invalid_codes()
	# print('ok2')

	# # 删除过期验证码的情况
	# time.sleep(2)
	# delete_invalid_codes()
	# print('ok3')

	# # 获取新的 
	# get_verification_code_('2')
	# print(codes)

	# # 输出结果：
	# # 生成的验证码 ('11111', 1559045170.948554)
	# # {'error': 1, 'data': {'msg': '原验证码未过期'}}
	# # ok1
	# # ok2
	# # 删除的验证码： ('11111', 1559045170.948554)
	# # ok3
	# # 生成的验证码 ('11111', 1559045177.9637892)
	# # OrderedDict([('2', ('11111', 1559045177.9637892))])
	

# d = collections.OrderedDict()
# d['qq.com'] = ('sdfsdf', time.time())
# d['qq2.com'] = ('dfdf', time.time())
# d['wqeqq.com'] = ('sdfsdf', time.time())

# print(d)

# for k, v in d.items():
# 	print(k, v)

# for k in d:
# 	print(k)

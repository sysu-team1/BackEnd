# from tools import utils
# code = utils.send_email(rcptto='653128964@qq.com')
# print(code)

# ---------- test db ----------
from db import db_helper, app, model_repr
from config import make_pattern
from tools import utils
from flask import Flask, request, json
# from responses.manage_users import register_, get_verification_code_, enter_event_and_run_scheduler
# from responses.get_tasks import get_tasks_by_
from responses import register_, get_verification_code_, enter_event_and_run_scheduler, get_tasks_by_


@app.route('/')
def test():
    # --------- 尝试定制返回格式
    # orders = ['email', 'password']
    # return model_repr(db_helper.query_student(openid=1000000), make_pattern(len(orders)), orders)
    # --------- 尝试获取10个task
    tasks = db_helper.get_task()
    tasks = '{"tasks": [' + ','.join([str(task) for task in tasks]) + ']}'
    return tasks
    # --------- 尝试获取1个student
    # return str(db_helper.query_student(openid=1000000))


@app.route('/user/login/', methods=['GET', 'POST'])
def login():
	'''
	详情请见db_helper.sign_in_true
	'''
	error_code, error_message, openid = db_helper.sign_in_true(request.form['type'], request.form['email'], request.form['password'])
	res = '{"error": ' + str(error_code) + ',' + '"error_message":"'+ error_message + '",' + '"data": {"openid":"' + str(openid) + '"}}'
	return res


@app.route('/user/register/', methods=['POST'])
def register():
	print(request)
	return register_(request.form['email'], request.form['password'], request.form['student_id'],
					request.form['sex'], request.form['collage'], 
					request.form['grade'], request.form['name'],
					request.form['validate_code'])


@app.route('/user/get_verification_code/', methods=['POST'])
def get_verification_code():
	# 生成验证码并发送至邮箱
	# print(request.get_json())
	# data = request.get_json()
	# print(data['email'])
	return get_verification_code_(request.form['email'])


@app.route('/tasks/search/', methods=['GET'])
def get_tasks_by():
	return get_tasks_by_(request.args)


if __name__ == "__main__":
    enter_event_and_run_scheduler()
    app.run(debug=True)

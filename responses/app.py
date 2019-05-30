import sys
import os
sys.path.append('./../')
from tools import utils
from db import db_helper, app, model_repr

from flask import Flask, request, json
from manage_users import register_, get_verification_code_, enter_event_and_run_scheduler
from get_tasks import get_tasks_by_


app = Flask(__name__)


@app.route('/user/login/', methods=['GET', 'POST'])
def login():
	'''
	详情请见db_helper.sign_in_true
	'''
	error_code, error_message, openid = db_helper.sign_in_true(request.form['type'], request.form['email'], request.form['password'])
	res = '{"error": ' + str(error_code) + ',' + '"error_message":'+ error_message + ',' + '"data": {"openid":' + str(openid) + '}}'
	return res


@app.route('/user/register/', methods=['POST'])
def register():
	print('email' + request.form['email'])
	# print('password' + request.form['password'])
	# print('validate_code' + request.form['validate_code'])
	# print('name' + request.form['name'])
	# print('student_id' + request.form['student_id'])
	# print('grade' + request.form['grade'])
	# print('major' + request.form['major'])
	# print('sex' + request.form['sex'])
	return register_(request.form['email'], request.form['password'], 
					request.form['validate_code'], request.form['name'], 
					request.form['student_id'], request.form['grade'],
					request.form['major'], request.form['sex'])


@app.route('/user/get_verification_code/', methods=['POST'])
def get_verification_code():
	# 生成验证码并发送至邮箱
	return get_verification_code_(request.form['email'])


@app.route('/tasks/search_by/', methods=['GET'])
def get_tasks_by():
	return get_tasks_by_(request.args)


if __name__ == "__main__":
	enter_event_and_run_scheduler()
	app.run(debug=True)
	
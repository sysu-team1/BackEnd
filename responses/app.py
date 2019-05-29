from flask import Flask, request, json
from login_or_register import login_, register_, get_verification_code_, enter_event_and_run_scheduler

app = Flask(__name__)

@app.route('/user/login/', methods=['GET', 'POST'])
def login():
	return login_()

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

@app.route('/user/get_verification_code', methods=['POST'])
def get_verification_code():
	# 生成验证码并发送至邮箱
	return get_verification_code_(request.form['email'])


if __name__ == "__main__":
	enter_event_and_run_scheduler()
	app.run(debug=True)
	
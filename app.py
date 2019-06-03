# from tools import utils
# code = utils.send_email(rcptto='653128964@qq.com')
# print(code)

# ---------- test db ----------
from db import db_helper, app, model_repr
from config import make_pattern, UPLOADED_PHOTOS_DEST
from tools import utils
from flask import Flask, request, json
# from responses.manage_users import register_, get_verification_code_, enter_event_and_run_scheduler
# from responses.get_tasks import get_tasks_by_
from responses import register_, get_verification_code_, enter_event_and_run_scheduler, get_tasks_by_, create_task_
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

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


@app.route('/tast/create/', methods=['POST'])
def create_task():
	# TODO 添加问卷的创建
	# 参数：
    #     publish_id, 发布人id ，也就是open_id
    #     limit_time, ddl
    #     limit_num, 限制人数数量
    #     title, task标题
    #     content, 内容（如果tag为'w问卷'，则内容为问卷的内容）
    #     tag, 标签
	#output：还没有做好
	new_task = db_helper.create_task(request.form['open_id'], request.form['limit_time'], request.form['limit_num'], request.form['title'], request.form['content'], request.form['tag'])
	task_id = new_task.id
	# new_task.image_path =
	if 'photo' not in request.files:
		print('No file part')
		return str({'code': -1, 'filename': '', 'msg': 'No file part'})
	photo = request.files['photo']
	# if user does not select file, browser also submit a empty part without filename
	if photo.filename == '':
		print('No selected file')
		return str({'code': -1, 'filename': '', 'msg': 'No selected file'})
	else:
		try:
			filename = UPLOADED_PHOTOS_DEST + str(task_id) + '.png'
			photo.save(filename)
			new_task.image_path = filename
			print(new_task)
			db_helper.commit()
			return str({'code': 0, 'filename': filename})
		except Exception as e:
			print('upload file exception: %s' % e)
			return str({'code': -1, 'filename': '', 'msg': 'Error occurred'})
	return create_task_(request.form)


if __name__ == "__main__":
	uploaded_photos = UploadSet('photos')
	configure_uploads(app, uploaded_photos)
	enter_event_and_run_scheduler()
	app.run(debug=True)

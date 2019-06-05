# from tools import utils
# code = utils.send_email(rcptto='653128964@qq.com')
# print(code)

# ---------- test db ----------
from db import db_helper, app, model_repr, Task
from config import make_pattern, UPLOADED_PHOTOS_DEST
from tools import utils
from flask import Flask, request, json, url_for, Response
# from responses.manage_users import register_, get_verification_code_, enter_event_and_run_scheduler
# from responses.get_tasks import get_tasks_by_
from responses import register_, get_verification_code_, enter_event_and_run_scheduler, get_tasks_by_, create_task_
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from tools.utils import generate_verification_code

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


@app.route('/tasks/create/', methods=['POST'])
def create_task():
	''' 任务的创建
	参数：
		publish_id, 发布人id ，也就是open_id
		limit_time, ddl
		limit_num, 限制人数数量
		title, task标题
		content, 内容（如果tag为'问卷'，则内容为问卷的内容）
		tag, 标签
		reward
	output： 
	"error": 0/1,
	"data": {
		"msg": "余额不足/创建成功/'没有图片上传'/'创建成功'/'图片上传失败'",
	}
	'''
	print(request.files)
	problem_content = '' if request.form['tag'] != '问卷' else request.form['problem_content']
	error, new_task = db_helper.create_task(int(request.form['openid']), request.form['limit_time'], request.form['limit_num'], request.form['title'], request.form['content'], request.form['tag'], request.form['reward'], problem_content)
	if error == 1:
		return str({'error': 1, "data": {'msg': '余额不足'}})
	task_id = new_task.id
	# return str({'error': 0, "data": {'msg': '创建成功', 'task_id': str(task_id)}})
	# 暂时找不到text与file同时上传的方法，先留着
	if 'photo' not in request.files:
		print('No file part')
		return str({'error': 1, "data": {'msg': '没有图片上传'}})
	photo = request.files['photo']
	# if user does not select file, browser also submit a empty part without filename
	if photo.filename == '':
		print('No selected file')
		return str({'error': 1, "data": {'msg': '没有图片上传'}})
	else:
		try:
			# 为了保证安全性，添加一个随机数（此处使用邮箱验证码的函数）
			photo.filename = generate_verification_code() + '-' + str(task_id) + '.png'
			uploaded_photos.save(photo)
			new_task.image_path = uploaded_photos.url(photo.filename)
			db_helper.commit()
			return str({'error': 0, "data": {'msg': '创建成功'}})
		except Exception as e:
			print('upload file exception: %s' % e)
			return str({'error': 1, "data": {'msg': '图片上传失败'}})


@app.route('/tasks/upload_photo/<task_id>', methods=['POST', 'GET'])
def upload_photo(task_id):
	''' 任务图片上传(前端只能够上传数据或者文件，不能够同时)
	参数：
        task_id，
		photo，图片
	output： 
	"error": 0/1,
	"data": {
		"msg": '没有图片上传'/'创建成功'/'图片上传失败'
	}
	图片上传失败：任务回滚
	'''
	task_id = int(task_id)
	task = db_helper.session.query(Task).filter(Task.id == task_id).one_or_none()
	if 'photo' not in request.files:
		print('No file part')
		Task.query.filter(Task.id == task_id).delete()
		db_helper.commit()
		return str({'error': 1, "data": {'msg': '没有图片上传'}})
	photo = request.files['photo']
	# if user does not select file, browser also submit a empty part without filename
	if photo.filename == '':
		print('No selected file')
		Task.query.filter(Task.id == task_id).delete()
		db_helper.commit()
		return str({'error': 1, "data": {'msg': '没有图片上传'}})
	else:
		try:
			# 为了保证安全性，添加一个随机数（此处使用邮箱验证码的函数）
			photo.filename = generate_verification_code() + '-' + str(task_id) + '.png'
			uploaded_photos.save(photo)
			task.image_path = uploaded_photos.url(photo.filename)
			db_helper.commit()
			return str({'error': 0, "data": {'msg': '创建成功'}})
		except Exception as e:
			print('upload file exception: %s' % e)
			Task.query.filter(Task.id == task_id).delete()
			db_helper.commit()
			return str({'error': 1, "data": {'msg': '图片上传失败'}})


@app.route("/_uploads/photos/<image_path>")
def index(image_path):
	'''
	利用图片url用于显示
	'''
	with open(UPLOADED_PHOTOS_DEST + image_path, 'rb') as f:
		image = f.read()
	pic_url = Response(image, mimetype="image/jpeg")
	return pic_url


@app.route("/add_cash/<open_id>", methods=['POST'])
def add_cash(open_id):
	# 用于充钱的
	add_cash_num = request.form['money']
	error, msg = db_helper.charge(int(open_id), int(add_cash_num))
	error = 1 if error == False else 0
	msg = '充钱成功' if error == 0 else '充钱失败'
	return str({'error': error, "data": {'msg': msg}})


@app.route("/my/<open_id>", methods=['GET'])
def get_self_information(open_id):
	# 获取用户个人信息
	# TODO 还没有写完
	print(db_helper.query_student(open_id))
	return 'hhh'


@app.route("/get_problem/<task_id>", methods=['GET'])
def get_problem(task_id):
	'''
	获取问卷的信息
	'''
	return str({'error': 0, "data": {'problem_content': db_helper.get_all_problems(int(task_id))}})


@app.route("/post_answer/", methods=['POST'])
def post_answer():
	'''
	提交问卷答案
	需要task_id, open_id, answer_content，使用^进行切分
	'''
	
	task_id = request.form['task_id']
	answer_content = request.form['answer']
	open_id = request.form['open_id']
	db_helper.post_answer(task_id, answer_content, open_id)
	return str({'error': 0, "data": {'msg': '提交成功'}})


@app.route("/get_answer/<task_id>", methods=['GET'])
def get_answer(task_id):
	# TODO 获取问卷的所有答案
	pass


if __name__ == "__main__":
	uploaded_photos = UploadSet('photos')
	configure_uploads(app, uploaded_photos)
	enter_event_and_run_scheduler()
	app.run(debug=True, use_reloader=False)

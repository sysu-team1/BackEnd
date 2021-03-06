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
from responses import register_, get_verification_code_, enter_event_and_run_scheduler, get_tasks_by_, create_task_, accept_task_, update_, get_recipients_
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from tools.utils import generate_verification_code
import os


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


@app.route('/user/update/', methods=['POST'])
def update():
	return update_(request.form)

@app.route('/tasks/search/', methods=['GET'])
def get_tasks_by():
	return get_tasks_by_(request.args)


@app.route('/tasks/create/', methods=['POST'])
def create_task():
	''' 任务的创建
	参数：
		publish_id, 发布人id ，也就是openid
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
	# TODO 注释掉
	print(request.files)
	problem_content = ''
	if request.form['tag'] == '问卷':
		problem_content = request.form['problem_content']
		if '' == problem_content or ' ' == problem_content:
			return str({'error': 1, "data": {'msg': '请创建问卷或重新选择类型'}})
		if '$#' in problem_content or '##' in problem_content or '^$' in problem_content or '#^' in problem_content or problem_content[-1:] == '#':
			return str({'error': 1, "data": {'msg': '请将问卷填写完整'}})
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
			return str({'error': 0, "data": {'msg': '创建成功,已扣除{}鱼币'.format(int(request.form['limit_num']) * int(request.form['reward']))}})
		except Exception as e:
			print('upload file exception: %s' % e)
			return str({'error': 1, "data": {'msg': '图片上传失败'}})


@app.route('/tasks/accept/', methods=['POST'])
def accept_task():
	return accept_task_(request.form)

@app.route('/tasks/get_recipients/', methods=['GET'])
def get_recipients():
	return get_recipients_(request.args)

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


@app.route("/temp/upload/<openid>", methods=['POST']) 
def upload_temp_image(openid):
	openid = int(openid)
	filenames = os.listdir("./images")
	for filename in filenames:
		temp = filename.split('--')
		if len(temp) < 2:
			continue
		if temp[1] == str(openid) + '.png':
			os.remove('./images/' + filename)
			print('删除重复文件')
			break
	photo = request.files['photo']
	if photo.filename == '':
		print('No selected file')
		return str({'error': 1, "data": {'msg': '没有图片上传', 'url':""}})
	else:
		try:
			photo.filename = generate_verification_code() + '--' + str(openid) + '.png'
			uploaded_photos.save(photo)
			image_path = uploaded_photos.url(photo.filename)
			return str({'error': 0, "data": {'msg': '创建成功', 'url': image_path}})
		except Exception as e:
			print('upload file exception: %s' % e)
			return str({'error': 1, "data": {'msg': '图片上传失败', 'url':""}})


@app.route("/add_cash/<openid>", methods=['POST'])
def add_cash(openid):
	# 用于充钱的
	add_cash_num = request.form['money']
	error, msg = db_helper.charge(int(openid), int(add_cash_num))
	error = 1 if error == False else 0
	msg = '充钱成功' if error == 0 else '充钱失败'
	return str({'error': error, "data": {'msg': msg}})


@app.route("/my/", methods=['GET'])
def get_self_information():
	''' 获取用户个人信息

	需要的字段：
		openid:
		cash: 1表示只获取cash信息，0表示获取全部
	'''
	try:
		args = request.args
		id = int(args.get('openid'))
		cash = int(args.get('cash'))
		if id < 1000000:
			org = db_helper.query_oraganization(id)
			orders = ['email', 'name', 'cash'] if cash == 0 else ['cash']
			patterns = make_pattern(len(orders))
			info = model_repr(org, patterns, orders)
		else:
			stu = db_helper.query_student(id)
			orders = ['email', 'student_id', 'name', 'sex', 'collage', 'grade', 'edu_bg', 'cash'] if cash == 0 else ['cash']
			patterns = make_pattern(len(orders))
			info = model_repr(stu, patterns, orders)
		return str({'error': 0, 'data': None})[:-5] + info + '}'
	except Exception:
		return str({'error': 1, 'data': {'msg': '不存在该账号'}})


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
	需要task_id, openid, answer_content，使用#进行切分
	'''
	
	task_id = request.form['task_id']
	answer_content = request.form['answer']
	openid = request.form['openid']
	try:
		cash = db_helper.post_answer(task_id, answer_content, openid)
		return str({'error': 0, "data": {'msg': '提交成功, 获取{}鱼币'.format(cash)}})
	except Exception as e:
		return str({'error': 1, "data": {'msg': str(e)}})


@app.route("/finish_task/", methods=['POST'])
def finish_task():
	'''
	完成任务（除了问卷以外的类型的任务
	需要task_id, openid
	return:
		error
		data
			msg: '还没有接受该任务'/'任务完成, 已获取{}鱼币'/'发生异常: %s'
	'''
	error, msg = db_helper.finish_task(int(request.form['openid']), int(request.form['task_id']))
	error = 0 if error == True else 1
	return str({'error': error, "data": {'msg': msg}})


@app.route("/get_answer/", methods=['GET'])
def get_answer():
	'''获取问卷的所有答案或者部分问卷的答案
	需要： 
	all:表示是否是所有的答案, 是为1，否为0
	task_id
	openid: 可有可无，当all为1的时候不需要有
	'''
	args = request.args
	all = int(args.get('all'))
	if all == 0:
		error, answers = db_helper.get_answers(int(args.get('openid')), int(args.get('task_id')))
		error = 0 if error == True else 1
		if error == 1:
			return str({'error': 1, "data": {'msg': answers}})
		else:
			return str({'error': 0, "data": {'msg': '获取成功', 'answers': answers}})
	else:
		answers = db_helper.get_all_answers(int(args.get('task_id')))
		return str({'error': 0, "data": {'msg': '获取成功', 'answers': answers}})

@app.route("/initial/", methods=['GET'])
def initial_():
	'''初始化数据库
	'''
	try:
		stus, orgs = db_helper.initial_data()
		return str({'error' : 0, 'data': {'stus': str(stus), 'orgs': str(orgs)}})
	except Exception:
		return str({'error' : 1})


if __name__ == "__main__":
	uploaded_photos = UploadSet('photos')
	configure_uploads(app, uploaded_photos)
	enter_event_and_run_scheduler()
	app.run(debug=True, use_reloader=False)

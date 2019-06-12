from db import db_helper, app, model_repr
from datetime import datetime

# publisher_id  = 'publisher_id'
# accepter_id = 'accepter_id'
# tag = 'tag'
# text = 'text'

def get_tasks_by_(args):
	# global publisher_id, accepter_id, tag, text
	msg = '获取成功'
	tasks = []
	last_accept_time_res = None
	if('task_id' in args):
		tasks.append(db_helper.get_task_by_id(int(args.get('task_id'))))
	elif('publisher_id' in args):
		if(args.get('status') == 'all'):
			tasks = db_helper.get_all_publish_tasks(int(args.get('publisher_id')), last_id = int(args.get('last_id')))
		elif(args.get('status') == 'ongoing'):
			tasks = db_helper.get_ongoing_publish_tasks(int(args.get('publisher_id')), last_id = int(args.get('last_id')))
		elif(args.get('status') == 'finished'):
			tasks = db_helper.get_finished_publish_tasks(int(args.get('publisher_id')), last_id = int(args.get('last_id')))
	elif('accepter_id' in args):
		last_accept_time = args.get('last_accept_time')
		dt = None
		if(last_accept_time != ''):
			dt = datetime.strptime(args.get('last_accept_time'), "%Y-%m-%d %H:%M:%S")
		if(args.get('status') == 'all'):
			tasks, last_accept_time_res = db_helper.get_all_accept_tasks(int(args.get('accepter_id')), last_accept_time = dt)
		elif(args.get('status') == 'ongoing'):
			tasks, last_accept_time_res = db_helper.get_ongoing_accept_tasks(int(args.get('accepter_id')), last_accept_time = dt)
		elif(args.get('status') == 'finished'):
			tasks, last_accept_time_res = db_helper.get_finished_accept_tasks(int(args.get('accepter_id')), last_accept_time = dt)
		elif(args.get('status') == 'complete'):
			tasks, last_accept_time_res = db_helper.get_complete_accept_tasks(int(args.get('accepter_id')), last_accept_time = dt)
		if(last_accept_time_res != None):
			msg = last_accept_time_res.strftime("%Y-%m-%d %H:%M:%S")
	elif('tag' in args):
		tasks = db_helper.get_task_by_tag(args.get('tag'), last_id = int(args.get('last_id')))
	elif('text' in args):
		tasks = db_helper.get_task_by_text(str(args.get('text')), last_id = int(args.get('last_id')))
	else:
		tasks = db_helper.get_task(last_id = int(args.get('last_id')))
	tasks_str = '[' + ','.join([str(task) for task in tasks]) + ']'
	res = "{\"error\": 0, \"data\": {\"msg\": \"" + msg + "\", \"tasks\": " + tasks_str + "}}"
	return res

def accept_task_(form):
	success, msg = db_helper.accept_task(int(form['accepter_id']), int(form['task_id']))
	res = {'error': 0, 'data': {'msg': msg}}
	if(not success):
		res = {'error': 1, 'data': {'msg': msg}}
	return str(res)

def create_task_(form):
	pass
	# db_helper.create_task(self, publish_id, limit_time, limit_num, title, content, tag, reward, problem_content='')

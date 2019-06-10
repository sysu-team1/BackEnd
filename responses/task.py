from db import db_helper, app, model_repr

publisher_id  = 'publisher_id'
accepter_id = 'accepter_id'
tag = 'tag'
text = 'text'

def get_tasks_by_(args):
	global publisher_id, accepter_id, tag, text
	if('last_id' not in args):
		return str({'error': 1, "data": {'msg': '参数错误'}})
	tasks = []
	if(publisher_id in args):
		tasks = db_helper.get_publish_tasks(int(args.get(publisher_id)), last_id = int(args.get('last_id')))
		print(tasks)
	elif(accepter_id in args):
		tasks = db_helper.get_accept_tasks(int(args.get(accepter_id)), last_id = int(args.get('last_id')))
	elif(tag in args):
		tasks = db_helper.get_task_by_tag(int(args.get(tag)), last_id = int(args.get('last_id')))
	elif(text in args):
		tasks = db_helper.get_task_by_text(int(args.get(text)), last_id = int(args.get('last_id')))
	else:
		tasks = db_helper.get_task(last_id = int(args.get('last_id')))
	tasks_str = '[' + ','.join([str(task) for task in tasks]) + ']'
	res = "{'error': 0, 'data': {'msg': '获取成功', 'tasks': " + tasks_str + "}}"
	return res

def create_task_(form):
	pass
	# db_helper.create_task(self, publish_id, limit_time, limit_num, title, content, tag, reward, problem_content='')

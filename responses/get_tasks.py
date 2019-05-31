from db import db_helper, app, model_repr

published_id = 'published_id'
accepter_id = 'accepter_id'
tag = 'tag'
text = 'text'

def get_tasks_by_(args):
	res = {}
	if(time_stamp in args):
		db_helper.get_task(last_id = args.get('last_id'))
	elif(published_id in args):
		tasks = db_helper.get_publish_tasks(args.get(published_id), last_id = args.get('last_id'))
	elif(accepter_id in args):
		tasks = db_helper.get_accept_tasks(args.get(accepter_id), last_id = args.get('last_id'))
	elif(tag in args):
		tasks = db_helper.get_task_by_tag(args.get(tag), last_id = args.get('last_id'))
	elif(text in args):
		tasks = db_helper.get_task_by_text(args.get(text), last_id = args.get('last_id'))
		tasks_str = '[' + ','.join([str(task) for task in tasks]) + ']'
	res = "{'error': 0, 'data': {'msg': '获取成功', 'tasks': " + tasks_str + "}}"
	return str(res)
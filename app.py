# from tools import utils  # ModuleNotFoundError: No module named 'secret_key'
# code = utils.send_email(rcptto='653128964@qq.com')
# print(code)

# ---------- test db ----------
from db import db_helper, app, model_repr
from config import make_pattern

@app.route('/')
def test():
    # --------- 尝试定制返回格式
    # orders = ['email', 'password']
    # return model_repr(db_helper.query_student(openid=1000000), make_pattern(len(orders)), orders)
    # --------- 尝试获取10个task
    tasks = db_helper.search_task_by_time()
    tasks = '{"tasks": [' + ','.join([str(task) for task in tasks]) + ']}'
    return tasks
    # --------- 尝试获取1个student
    # return str(db_helper.query_student(openid=1000000))


if __name__ == "__main__":
    app.run(debug=True)

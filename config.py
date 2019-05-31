from tools.utils import make_pattern


# 主机的MySQL账号:密码:端口号/数据库
# SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:mysql@localhost:3306/test2'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:960919AB@localhost:3308/test2'
# 是否输出
SQLALCHEMY_ECHO = False

# student attr list
STUDENT_JSON_ATTR_ORDER = [
    'openid', 'email', 'password', 'student_id', 'sex', 'collage', 'grade', 'edu_bg', 'tag', 'signature']
STUDENT_JSON_PATTERN = make_pattern(len(STUDENT_JSON_ATTR_ORDER))

# organization attr list
ORGANIZATION_JSON_ATTR_ORDER = ['openid', 'email', 'password', 'description']
ORGANIZATION_JSON_PATTERN = make_pattern(len(ORGANIZATION_JSON_ATTR_ORDER))

# task attr list
TASK_JSON_ATTR_ORDER = [
    'id', 'publish_id', 'publish_time', 'limit_time', 'limit_num', 'accept_num', 'title', 'content', 'tag']
TASK_JSON_PATTERN = make_pattern(len(TASK_JSON_ATTR_ORDER))

# accept task attr list
ACCEPT_JSON_ATTR_ORDER = [
    'id', 'tag', 'accept_id', 'task_id', 'accept_time', 'finish_time']
ACCEPT_JSON_PATTERN = make_pattern(len(ACCEPT_JSON_ATTR_ORDER))

# problem attr list 问卷
PROBLEM_JSON_ATTR_ORDER = ['id', 'task_id', 'description', 'all_answers']
PROBLEM_JSON_PATTERN = make_pattern(len(PROBLEM_JSON_ATTR_ORDER))

# answer sttr list
ANSWER_JSON_ATTR_ORDER = ['accept_id', 'problem_id', 'answer']
ANSWER_JSON_PATTERN = make_pattern(len(ANSWER_JSON_ATTR_ORDER))

SPLIT_STU_ORG = 1000000  # student与orgnization间的openid切割
SPLIT_ANSWER = '#'  # answer的切割符
DROP_ALL = False  # 表示每次重启/启动时是否删除原有表
UPDATE_ADD_NUM = 10  # 一次更新获取的值

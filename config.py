def make_pattern(orders_len: int):
    '''用于获取指定长度的匹配字符串
    
    参数：
        orders_len: 指定属性的列表的长度
    '''
    if orders_len <= 0:
        raise AttributeError('orders_len can not be less than 1')
    pattern = r'{'
    for _ in range(orders_len - 1):
        pattern += '%s: %s, '
    pattern += r'%s: %s}'
    return pattern


# 主机的MySQL账号:密码:端口号/数据库
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:mysql@localhost:3306/test2'
# 是否输出
SQLALCHEMY_ECHO = False

# student attr list
STUDENT_JSON_ATTR_ORDER = [
    'openid', 'email', 'password', 'sex', 'collage', 'grade', 'edu_bg', 'tag', 'signature']
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

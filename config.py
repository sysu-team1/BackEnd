def make_pattern(orders_len: int):
    if orders_len <= 0:
        raise AttributeError('orders_len can not be less than 1')
    pattern = r'{'
    for _ in range(orders_len - 1):
        pattern += '%s: %s, '
    pattern += r'%s: %s}'
    return pattern


SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:960919AB@localhost:3308/test2'
SQLALCHEMY_ECHO = False

STUDENT_JSON_ATTR_ORDER = [
    'openid', 'email', 'password', 'sex', 'collage', 'grade', 'edu_bg', 'tag', 'signature']
STUDENT_JSON_PATTERN = make_pattern(len(STUDENT_JSON_ATTR_ORDER))

ORGANIZATION_JSON_ATTR_ORDER = ['openid', 'email', 'password', 'description']
ORGANIZATION_JSON_PATTERN = make_pattern(len(ORGANIZATION_JSON_ATTR_ORDER))

TASK_JSON_ATTR_ORDER = [
    'id', 'publish_id', 'publish_time', 'limit_time', 'limit_num', 'accept_num', 'title', 'content', 'tag']
TASK_JSON_PATTERN = make_pattern(len(TASK_JSON_ATTR_ORDER))

ACCEPT_JSON_ATTR_ORDER = [
    'id', 'tag', 'accept_id', 'task_id', 'accept_time', 'finish_time']
ACCEPT_JSON_PATTERN = make_pattern(len(ACCEPT_JSON_ATTR_ORDER))

PROBLEM_JSON_ATTR_ORDER = ['id', 'task_id', 'description', 'all_answers']
PROBLEM_JSON_PATTERN = make_pattern(len(PROBLEM_JSON_ATTR_ORDER))

ANSWER_JSON_ATTR_ORDER = ['accept_id', 'problem_id', 'answer']
ANSWER_JSON_PATTERN = make_pattern(len(ANSWER_JSON_ATTR_ORDER))

SPLIT_STU_ORG = 1000000
SPLIT_ANSWER = '#'

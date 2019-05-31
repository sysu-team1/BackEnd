import datetime
import random
import time

from config import make_pattern

from .prepare import model_repr
from .Accept import Accept, random_accepts
from .Answer import Answer
from .Organization import Organization, random_orgs
from .prepare import ALL_TAGS, QUESTIONNAIRE_INDEX, app, db
from .Problem import Problem
from .Student import Student, random_stus
from .Task import Task, random_tasks

update_add_num = app.config['UPDATE_ADD_NUM']

class DBHelper:
    '''
    1. 添加用户/组织/任务/accept
    2. 得到用户/组织(主要用于注册与登陆)
    3. 删除用户/组织/任务/accept
    4. 更新用户/组织/任务/accept
    5. 得到用户发布的任务(有limit与offset)
    6. 得到用户接受的任务(有limit与offset)
    7. 根据任务id查找任务接受者
    8. 根据任务id查找任务发布者
    9. 搜索任务(根据内容/标题/tag/发布时间)
    '''

    def __init__(self, db, drop_all=False):
        self.db = db
        self.session = db.session
        if drop_all:
            self.db.drop_all()
        self.db.create_all()
        self.db.engine.execute('alter table {} auto_increment = {}'.format(
            Student.__tablename__, app.config['SPLIT_STU_ORG']))

    def commit(self):
        '''更新提交'''
        self.session.commit()

    def save(self, data):
        '''保存一个数据'''
        self.session.add(data)
        self.commit()

    def save_all(self, datas):
        '''保存批量数据'''
        for data in datas:
            self.save(data)

    def delete(self, data):
        '''删除一个数据，分三种情况
        1. 如果删除的是Problem，表示发布者在修改问卷，需要删除关联的所有回答
        2. 如果删除的是Student或者Organization，那么它们接受的任务和发布的任务都要删除
        3. 如果删除的是Task，需要删除关联的所有任务接受
            1. 如果是问卷，还要删除所有的Problem与对应的Answer
        '''
        # if isinstance(data, Problem):
        #     Answer.query.filter(Answer.problem_id == data.id).delete()
        # elif isinstance(data, (Student, Organization)):
        #     Accept.query.filter(Accept.accept_id == data.openid).delete()
        #     tasks = Task.query.filter(Task.publish_id == data.openid)
        #     for task in tasks:
        #         self.delete(task)
        # elif isinstance(data, Task):
        #     if data.tag.find(ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1:
        #         Answer.query.filter(Answer.task_id == data.id).delete()
        #         Problem.query.filter(Problem.task_id == data.id).delete()
        #     Accept.query.filter(Accept.task_id == data.id).delete()
        if isinstance(data, (Student, Organization)):
            Task.query.filter(Task.publish_id == data.openid).delete()
        self.session.delete(data)
        self.commit()

    def delete_all(self, datas):
        '''删除批量数据'''
        for data in datas:
            self.delete(data)

    def sign_in_true(self, type, email, password):
        '''登陆验证功能
        input: 
            type: stu org
            email, password
        output: error_code, error_message, openid
            error_code为1表示出错
            error_message:
                not exist
                password not right
        '''
        # 查找学生中是否存在这个账号
        # if type == 'stu':
        #     stu = Student.query.filter(Student.email == email).one_or_none()
        #     if stu is not None:
        #         if password == stu.password:
        #             return 0, '', stu.openid
        #         return 1, 'password not right', ''
        # elif type == 'org':
        #     org = Organization.query.filter(Organization.email == email).one_or_none()
        #     if org is not None:  
        #         if org.password == password:
        #             return 0, '', org.openid
        #         return 1, 'password not right', ''
        # # 未注册
        # return 1, 'not exist', '', 
        target = Student.query.filter(Student.email == email).one_or_none(
        ) if type == 'stu' else Organization.query.filter(Organization.email == email).one_or_none()
        if target is not None:
            if target.password == password:
                return 0, '', target.openid
            return 1, 'password not right', ''
        return 1, 'not exist', ''

    def sign_up_true(self, email, password, student_id, sex, collage, grade, edu_bg):
        '''验证邮箱是否已被注册
            如果未注册，则插入数据库并反馈信息
            如果注册，则反馈失败信息


            暂时没有使用的字段
            tag: '与任务相关的标签'
            signature: '用户签名'
        input: email, password, sex, collage, grade, edu_bg
            grade: '入学年级'
            edu_bg: '学历'
        output:error_code, error_message, openid
            error_code为1表示出错
            error_message: 
                'already exist'
                ''
            openid
        '''
        stu = Student.query.filter(Student.email == email).one_or_none()
        if stu is not None:
            return 1, 'already exist', None
        # 插入数据库
        stu = Student(email=email, password=password, student_id=student_id, sex=sex, collage=collage, grade=grade, edu_bg=edu_bg)
        self.save(stu)
        self.commit()
        return 0, "", stu.openid

    def query_student(self, openid, get_all=False):
        ''' 根据openid查找student，get_publish指定是否获取该student发布的任务与接受的任务 '''
        if get_all:
            stu = Student.query.options(db.joinedload(Student.accepts)).filter(
                Student.openid == openid).one_or_none()
            if stu is not None:
                stu.tasks = self.get_publish_tasks(stu.openid)
        else:
            stu = Student.query.filter(Student.openid == openid).one_or_none()
        return stu

    def query_oraganization(self, openid, get_all=False):
        '''根据openid查找oraganization，get_all指定是否同时获取该organization发布的任务'''
        org = self.session.query(Organization).filter(
            Organization.openid == openid).one_or_none()
        if get_all:
            org.tasks = self.get_publish_tasks(org.openid)
        return org

    def has_accept(self, accept_id, task_id):
        '''根据accept_id与task.id查询是否已经接受该任务了'''
        return Accept.query.filter(Accept.accept_id == accept_id, Accept.task_id == task_id).one_or_none() is not None

    def get_publish_tasks(self, openid, sort=True, last_id=-1, start=0, length=update_add_num):
        '''根据openid查找发布的任务  
        Args:
            openid:
            start: 开始获取任务的位置
            length: 获取任务的数量
            sort: 表示是否安装publish_time排序
        '''
        query = Task.query.filter(Task.publish_id == openid)
        if last_id != -1:
            query = query.filter(Task.id < last_id)
        if sort:
            query = query.order_by(Task.id.desc())
        return query.offset(start).limit(length).all()

    def get_accept_tasks(self, openid, sort=True, last_id=-1, start=0, length=update_add_num):
        '''根据openid查找接受的任务  
        Args:
            openid:
            start: 开始获取任务的位置
            length: 获取任务的数量
            sort: 表示是否安装accept_time排序
        '''
        query = self.session.query(Task).join(Accept).filter(
            Accept.accept_id == openid).filter(Accept.task_id == Task.id)
        if last_id != -1:
            query = query.filter(Task.id < last_id)
        if sort:
            query = query.order_by(Accept.accept_time.desc())
        return query.offset(start).limit(length).all()

    def get_recipient(self, id_or_task, start=0, length=update_add_num):
        '''根据task_id或者task查找接受任务者  
        Args:
            task_id:
            start: 获取接受者的开始位置
            length: 获取接受者的长度
        Tips:
            可以直接通过 **task.accepts** 获取接受，然后通过 **accept.student** 来获取接受者，但不按照时间排序
        '''
        # return self.session.query(Student).join(Accept).filter(Accept.task_id == task_id, Accept.accept_id == Student.openid).offset(start).limit(length).all()
        if isinstance(id_or_task, int):
            id_or_task = Task.query.filter(Task.id == id_or_task).one_or_none()
            if id_or_task is None:
                return None
        task = id_or_task
        accepts = task.accepts[start : length]
        return [accept.student for accept in accepts]

    def get_publisher(self, id_or_task):
        '''根据task_id或者task找到任务发布者'''
        if isinstance(id_or_task, int):
            task = self.session.query(
                Task).filter(Task.id == id_or_task).one()
        else:
            task = id_or_task
        if task.publisher is not None:
            return task.publisher
        if task.publish_id < app.config['SPLIT_STU_ORG']:
            task.publisher = Organization.query.filter(Organization.openid == task.publish_id).one()
        else:
            task.publisher = Student.query.filter(Student.openid == task.publish_id).one()
        return task.publisher

    def get_all_answers(self, id_or_task):
        ''' 根据问卷id或者问卷获取所有的答案  
        Return:
            [problem1.answers, problem2.answers, ...]
        Tips:
            其实可以自己根据 **task.problems** 和 **problem.answers** 来获取
        '''
        all_answers = []
        if isinstance(id_or_task, int):
            task = Task.query.filter(Task.id == id_or_task).one_or_none()
        else:
            task = id_or_task
        if task is None or task.tag.find(ALL_TAGS[QUESTIONNAIRE_INDEX]) == -1:
            return all_answers
        for problem in task.problems:
            all_answers.append(problem.answers)
        return all_answers

    def get_task(self, sort=True, last_id=-1, get_publisher=True, start=0, length=update_add_num):
        '''搜索Task  
        参数:
            sort: 表示是否按照时间排序
            get_publisher: 表示是否获取任务发布者
            last_id: 表示上次刷新时最后返回的任务的id
            start: 表示获取任务的开始位置
            length: 表示获取任务的数量
        '''
        query = Task.query
        return self._get_task(query, sort, last_id, get_publisher, start, length)

    def get_task_by_text(self, search_text, sort=True, last_id=-1, get_publisher=True, start=0, length=update_add_num):
        '''根据内容和标题搜索Task  
        参数:
            search_text: 表示用于搜索的文本
            sort: 表示是否按照时间排序
            last_id: 表示上次刷新时最后返回的任务的id
            get_publisher: 表示是否获取任务发布者
            start: 表示获取任务的开始位置
            length: 表示获取任务的数量
        '''
        query = Task.query.filter(self.db.text(
            "match (title, content) against (:text)")).params(text=search_text)
        return self._get_task(query, sort, last_id, get_publisher, start, length)

    def get_task_by_tag(self, search_tag, sort=True, last_id=-1, get_publisher=True, start=0, length=update_add_num):
        '''根据tag搜索Task  
        参数:
            search_tag: 表示用于搜索的tag
            sort: 表示是否按照时间排序
            last_id: 表示上次刷新时最后返回的任务的id
            get_publisher: 表示是否获取任务发布者
            start: 表示获取任务的开始位置
            length: 表示获取任务的数量
        '''
        query = Task.query.filter(Task.tag.match(search_tag))
        return self._get_task(query, sort, last_id, get_publisher, start, length)

    def _get_task(self, query, sort=True, last_id=-1, get_publisher=True, start=0, length=update_add_num):
        '''搜索Task  
        参数:
            query: 用于查询任务
            sort: 表示是否按照时间排序
            get_publisher: 表示是否获取任务发布者
            last_id: 表示上次刷新时最后返回的任务的id
            start: 表示获取任务的开始位置
            length: 表示获取任务的数量
        '''
        if last_id != -1:
            query = query.filter(Task.id < last_id)
        if sort:
            query = query.order_by(Task.id.desc())
        tasks = query.offset(start).limit(length).all()
        if tasks is not None and get_publisher:
            for task in tasks:
                self.get_publisher(task)
        return tasks

    def charge(self, openid, money_num):
        '''充钱  
        Args:
            openid: 学生或者组织的id
            money_num: 充的钱的数量
        Return:
            bool: 表示是否成功
            mess: 失败的原因，如果成功则为空
        '''
        if money_num <= 0:
            return False, 'money can not be less than or equals zero.'
        try:
            target = Student.query.filter(Student.openid == openid).with_for_update().one_or_none(
            ) if openid >= app.config['SPLIT_STU_ORG'] else Organization.query.filter(Organization.openid == openid).with_for_update().one_or_none()
            target_money = target.cash + money_num
            target.cash = target_money
            self.commit()
            return True, ''
        except Exception as e:
            self.session.rollback()
            return False, str(e)
        # if target.cash == target_money:
        #     return True
        # self.rollback()
        # return False

    def carry_over(self, source_id, target_id, money_num):
        '''转账，从source_id处转到target_id处，转移money_num个币  
        Args:
            source_id: 币来源
            target_id: 币去处
            money_num: 币数量
        Return:
            bool: 表示是否成功
            mess: 失败的原因，如果成功则为空
        '''
        if money_num <= 0:
            return False, 'money can not be less than or equals zero.'
        try:
            source = Student.query.filter(Student.openid == source_id).with_for_update().one_or_none(
            ) if source_id >= app.config['SPLIT_STU_ORG'] else Organization.query.filter(Organization.openid == source_id).with_for_update().one_or_none()
            if money_num > source.cash:
                return False, 'not enough money'
            target = Student.query.filter(Student.openid == target_id).with_for_update().one_or_none()
            source.cash -= money_num
            target.cash += money_num
            self.commit()
            return True, ''
        except Exception as e:
            self.rollback()
            return False, str(e)

    def cash_in(self, openid, money_num):
        '''套现  
        Args:
            openid: 学生或者组织的id
            money_num: 套现的钱的数量
        '''
        raise NotImplementedError('暂不支持套现')


db_helper = DBHelper(db, drop_all=app.config['DROP_ALL'])


# @classmethod
# def get_tasks(self):
#     if self._tasks is None:
#         self._tasks = db_helper.get_publish_tasks(self.openid)
#     return self._tasks
#
#
# @classmethod
# def get_publisher(self):
#     if self._publisher is None:
#         self._publisher = db_helper.get_publisher_by_task_id(self.id)
#     return self._publisher
#
#
# Student.get_tasks = get_tasks
# Organization.get_tasks = get_tasks
# Task.get_publisher = get_publisher
# 真的只是类方法， self是Student/Organization，而不是它们的实例

# Student.get_tasks = lambda openid: db_helper.get_publish_tasks(openid)  # 无限递归


def test_json():
    print(Student(openid=1000000, email='email1', password='password1'))
    print(Organization(openid=2, email='email2', password='password2'))
    print(Task(id=1, publish_id=2, publish_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), limit_num=10,
               title='title1', content='word1, word2', tag='tag1 tag2'))
    print(Problem(id=1, task_id=1, description='desc1',
                  all_answers='answer1;answer2;answer3'))
    print(Accept(accept_id=1000000, task_id=1, accept_time=datetime.datetime.now(),
                 finish_time='2020-01-01 00:00:00'))  # TODO now()
    print(Answer(accept_id=1, problem_id=1, answer='answer1'))


def test_normal_crud():
    stus = random_stus(100)
    db_helper.save_all(stus)
    db_helper.commit()
    print('---------- 随机查询10位幸运学生(可能重复)')
    for _ in range(10):
        print(db_helper.query_student(openid=random.choice(stus).openid))

    orgs = random_orgs(10)
    db_helper.save_all(orgs)
    db_helper.commit()
    print('---------- 随机查询3个幸运组织(可能重复)')
    for _ in range(3):
        print(db_helper.query_oraganization(openid=random.choice(orgs).openid))

    tasks = random_tasks(50, orgs, stus, db_helper)
    print('---------- 查找某些任务的发布者(可能重复)')
    sample_tasks = random.sample(tasks, 10)
    for task in sample_tasks:
        print(task.id, task.publish_id, db_helper.get_publisher(task))
    print('---------- 根据时间查询10个幸运任务')
    query_tasks_by_time = db_helper.search_task_by_time()
    for task in query_tasks_by_time:
        print(task)
    print('---------- 根据时间与tag查询10个幸运任务')
    query_tasks_by_tag = db_helper.search_task_by_tag(search_tag='tag1')
    for task in query_tasks_by_tag:
        print(task)
    print('---------- 根据时间与text查询10个幸运任务')
    query_tasks_by_content = db_helper.search_task_by_text(search_text='word1')
    for task in query_tasks_by_content:
        print(task)
    print('---------- 查找某些表单')
    form_tasks = list(filter(lambda task: task.tag.find(
        ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1, tasks))
    sample_form_tasks = random.sample(form_tasks, min(10, len(form_tasks)))
    for task in sample_form_tasks:
        print(task)
        for problem in task.problems:
            print('\t', problem)
            # random_tasks 中没有将 problems 赋给 task ，但这里自动获取了，因为 relationship
    # 直接在 mysql 命令行中检查:
    # select * from tasks where publish_id not in (select openid from students union select openid from organizations);  -- 检查 publish_id 是否合法
    # select * from tasks where publish_time != '2000-01-01 00:00:00' and publish_time >= now(); -- 检查 publish_time 是否合法
    # select * from tasks where limit_time != '2000-01-01 00:00:00' and limit_time <= publish_time; -- 检查 limit_time 是否合法
    # select * from tasks where limit_num != -1 and limit_num < 1; -- 检查 limit_num 是否合法
    # select * from tasks where accept_num < 0 or accept_num > limit_num; -- 检查 accept_num 是否合法

    accepts = random_accepts(300, tasks, stus, db_helper)
    print('---------- 查找这些任务的接收者(可能重复)')
    sample_accepts = random.sample(accepts, 10)
    for accept in sample_accepts:
        print(accept, accept.student)
    print('---------- 查找某些表单的接受')
    form_accepts = list(filter(lambda accept: accept.tag.find(
        ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1, accepts))
    sample_form_accepts = random.sample(
        form_accepts, min(10, len(form_accepts)))
    for accept in sample_form_accepts:
        print(accept)
        for answer in accept.answers:
            print('\t', answer)
    # 直接走 mysql 命令行中检查:
    # select * from accepts where accept_id not in (select openid from students); -- 检查 accept_id 是否合法
    # select * from accepts where task_id not in (select id from tasks); -- 检查 task_id 是否合法
    # select * from accepts where accept_time ??? -- 检查 accept_time 是否合法
    # select * from accepts where finish_time ??? -- 检查 finish_time 是否合法

    # 检查 problem TODO
    # 检查 answer TODO


""" def test_none():
    print('---------- stu._tasks && stu.get_tasks')
    stu = Student.query.filter(Student.openid == 1000000).one_or_none()
    print(stu, stu._tasks, stu.get_tasks()[0], sep='\n')
    print('---------- org._tasks && org.get_tasks')
    org = Organization.query.filter(Organization.openid == 1).one_or_none()
    print(org, org._tasks, org.get_tasks()[0], sep='\n')
    print('---------- task._publisher && task.get_publisher')
    task = Task.query.filter(Task.id == 1).one_or_none()
    print(task, task._publisher, task.get_publisher(), sep='\n')
    print('---------- test')
    print(stu._tasks[0], org._tasks[0], task._publisher, sep='\n') """


def test_time():
    print('---------- 根据时间加载最新10条')
    orders = ['id', 'publish_time']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task()
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据时间加载后10条')
        tasks = db_helper.get_task(last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    print('---------- 根据tag加载最新10条')
    orders = ['id', 'publish_time', 'tag']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task_by_tag(ALL_TAGS[QUESTIONNAIRE_INDEX])
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据tag加载后10条')
        tasks = db_helper.get_task_by_tag(ALL_TAGS[QUESTIONNAIRE_INDEX], last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    print('---------- 根据text加载最新10条')
    orders = ['id', 'publish_time', 'title', 'content']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task_by_text('word2')
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据text加载后10条')
        tasks = db_helper.get_task_by_text('word2', last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    print('---------- 加载组织6发布的最新4条任务')
    orders = ['id', 'publish_time']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_publish_tasks(openid=6, length=4)
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == 4:
        last_id = tasks[-1].id
        print('---------- 加载组织6发布的后4条任务')
        tasks = db_helper.get_publish_tasks(openid=6, last_id=last_id, length=4)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > 4:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')


if __name__ == "__main__":
    # test_json()
    # test_normal_crud()
    # test_none()
    # task = Task.query.filter(Task.id == 3).one_or_none()
    # print(task.accepts)
    test_time()

# 测试使用
# test_normal_crud()

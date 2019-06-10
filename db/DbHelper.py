<<<<<<< HEAD
from .test import test_json, test_normal_crud, test_time, test_create_student_and_organization, test_accetp_and_publish
=======

from .test import test_json, test_normal_crud, test_time, test_create_student_and_organization
>>>>>>> 31d46760eefea817bfa43ec206aa257da495f0d2
from .Accept import Accept
from .Organization import Organization
from .prepare import ALL_TAGS, QUESTIONNAIRE_INDEX, app, db, DEFAULT_TIME
from .Student import Student
from .Task import Task
from .Problem import Problem
from .Answer import Answer
from datetime import datetime

update_add_num = app.config['UPDATE_ADD_NUM']
default_datetime = datetime.strptime(DEFAULT_TIME, "%Y-%m-%d %H:%M:%S")

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

    10. 报酬系统
    11. 任务完成
    '''

    def __init__(self, db, drop_all=False):
        ''' 初始化  
        Args:
            db: SQLAlchemy 是要被封装的对象
            drop_all: bool 表明是否要放弃所有的表，重新创建
        '''
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
        '''保存一个数据  
        Args:
            data: 必须是 Student/Organization/Task/Accept/Problem/Answer 中实例，作为被保存在数据库的对象
        '''
        self.session.add(data)
        self.commit()

    def save_all(self, datas):
        '''保存批量数据  
        Args:
            datas: 必须是可遍历的对象，成员对象必须是 Student/Organization/Task/Accept/Problem/Answer 的实例，作为被保存在数据库的对象
        '''
        for data in datas:
            self.save(data)

    def delete(self, data):
        '''删除一个数据，分三种情况
        1. 如果删除的是Problem，表示发布者在修改问卷，需要删除关联的所有回答
        2. 如果删除的是Student或者Organization，那么它们接受的任务和发布的任务都要删除
        3. 如果删除的是Task，需要删除关联的所有任务接受
            1. 如果是问卷，还要删除所有的Problem与对应的Answer
        Args:
            data: 必须是 Student/Organization/Task/Accept/Problem/Answer 中实例
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
        '''删除批量数据  
        Args:
            datas: 必须是可遍历的对象，成员对象必须是 Student/Organization/Task/Accept/Problem/Answer 的实例
        '''
        for data in datas:
            self.delete(data)

    def sign_in_true(self, type, email, password):
        '''登陆验证功能
        input: 
            type: str 用户类型，可选值为'stu'和'org'
            email: str
            password: str
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
        ) if type == 'student' else Organization.query.filter(Organization.email == email).one_or_none()
        if target is not None:
            if target.password == password:
                return 0, '', target.openid
            return 1, '密码错误', ''
        return 1, '账号不存在', ''

    def sign_up_true(self, email, password, student_id, sex, collage, grade, name):
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
        stu = Student(email=email, password=password, student_id=student_id, sex=sex, collage=collage, grade=grade, name=name)
        self.save(stu)
        self.commit()
        return 0, "", stu.openid

    def create_task(self, publish_id, limit_time, limit_num, title, content, tag, reward, problem_content=''):
        '''创建任务

        参数：
        publish_id, 发布人id ，也就是open_id
        limit_time, ddl
        limit_num, 限制人数数量
        title, task标题
        content, 内容（如果tag为'w问卷'，则内容为问卷的内容）
        tag, 标签
        reward, 报酬
        problem_content, 问卷信息, 默认为空
        输出参数：
        error
        task
        '''
        # 判断发布人是否有足够的钱财进行发布任务
        target = Student.query.filter(Student.openid == publish_id).one_or_none(
        ) if publish_id >= 100000 else Organization.query.filter(Organization.openid == publish_id).one_or_none()
        if int(target.cash) < int(limit_num) * int(reward):
            return 1, -1
        task = Task(publish_id=publish_id, publish_time=datetime.now(), limit_time=limit_time,
                    limit_num=limit_num, title=title, content=content, tag=tag, reward=reward)
        self.save(task)
        if tag == '问卷':
            # 使用^作为problem的切分，使用$作为题目与答案的切分，使用#作为答案的切分
            problems_list = problem_content.split("^")
            problems = []
            for problems_list_element in problems_list:
                problems_list_element = problems_list_element.split("$")
                description = problems_list_element[0]
                all_answers = problems_list_element[1]
                problem = Problem(task_id = task.id, description=description, all_answers=all_answers)
                problems.append(problem)
            self.save_all(problems)
            self.commit()
        self.commit()
        return 0, task

    def query_student(self, openid: int, get_all: bool=False):
        '''根据openid查找student，get_publish指定是否获取该student发布的任务与接受的任务  
        Args:
            openid: int
            get_all: bool 表示是否同时获取该学生"发布"和"接受"的任务
        '''
        if get_all:
            stu = Student.query.options(db.joinedload(Student.accepts)).filter(
                Student.openid == openid).one_or_none()
            if stu is not None:
                stu.tasks = self.get_publish_tasks(stu.openid)
        else:
            stu = Student.query.filter(Student.openid == openid).one_or_none()
        return stu

    def query_oraganization(self, openid: int, get_all: bool=False):
        '''根据openid查找oraganization，get_all指定是否同时获取该organization发布的任务  
        Args:
            openid: int
            get_all: bool 表示是否同时获取该组织"发布"的任务
        '''
        org = self.session.query(Organization).filter(
            Organization.openid == openid).one_or_none()
        if get_all:
            org.tasks = self.get_publish_tasks(org.openid)
        return org

    def has_accept(self, accept_id: int, task_id: int):
        '''根据accept_id与task.id查询是否已经接受该任务了
        Args:
            accept_id: int
            task_id: int
        '''
        return Accept.query.filter(Accept.accept_id == accept_id, Accept.task_id == task_id).one_or_none() is not None

    def get_all_publish_tasks(self, openid: int, sort: bool=True, last_id: int=-1, start: int=0, length: int=update_add_num):
        '''根据openid查找所有发布的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置
            length: int 获取任务的数量
            sort: bool 表示是否安装publish_time排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
        '''
        query = Task.query.filter(Task.publish_id == openid)
        return self._get_publish_tasks(query, sort, last_id, start, length)

    def get_ongoing_publish_tasks(self, openid: int, sort: bool = True, last_id: int = -1, start: int = 0, length: int = update_add_num):
        '''根据openid查找进行中的发布的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置
            length: int 获取任务的数量
            sort: bool 表示是否安装publish_time排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
        '''
        now = datetime.now()
        query = Task.query.filter(Task.publish_id == openid, Task.limit_time > now)
        return self._get_publish_tasks(query, sort, last_id, start, length)

    def get_finished_publish_tasks(self, openid: int, sort: bool=True, last_id: int=-1, start: int=0, length: int=update_add_num):
        '''根据openid查找已完成的发布的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置
            length: int 获取任务的数量
            sort: bool 表示是否安装publish_time排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
        '''
        now = datetime.now()
        query = Task.query.filter(Task.publish_id == openid, Task.limit_time <= now)
        return self._get_publish_tasks(query, sort, last_id, start, length)

    def _get_publish_tasks(self, query, sort: bool=True, last_id: int=-1, start: int=0, length: int=update_add_num):
        '''查找发布的任务  
        Args:
            query: 用于查找任务的query
            start: int 开始获取任务的位置
            length: int 获取任务的数量
            sort: bool 表示是否安装publish_time排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
        '''
        if last_id != -1:
            query = query.filter(Task.id < last_id)
        if sort:
            query = query.order_by(Task.id.desc())
        return query.offset(start).limit(length).all()

    def get_all_accept_tasks(self, openid: int, sort: bool=True, last_accept_time: datetime=None, start: int=0, length: int=update_add_num):
        '''根据openid查找所有接受的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置 @deperated
            length: int 获取任务的数量
            sort: bool 表示是否安装accept_time排序
            last_accept_time: datetime 表示上次获取的任务列表的最后的一个item的accept_time，以此作为后续数据请求的"标识"
        Return:
            tasks: 任务列表
            last_accept_time: 最后一个item的accept_time，注意如果tasks为空，则last_accept_time是传入的last_accept_time
        '''
        query = self.session.query(Task).join(Accept).filter(
            Accept.accept_id == openid, Accept.task_id == Task.id)
        return self._get_accept_tasks(query, openid, sort, last_accept_time, start, length)

    def get_ongoing_accept_tasks(self, openid: int, sort: bool = True, last_accept_time: datetime=None, start: int = 0, length: int = update_add_num):
        '''根据openid查找进行中的接受了的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置 @deperated
            length: int 获取任务的数量
            sort: bool 表示是否安装accept_time排序
            last_accept_time: datetime 表示上次获取的任务列表的最后的一个item的accept_time，以此作为后续数据请求的"标识"
        Return:
            tasks: 任务列表
            last_accept_time: 最后一个item的accept_time，注意如果tasks为空，则last_accept_time是传入的last_accept_time
        '''
        now = datetime.now()
        query = self.session.query(Task).join(Accept).filter(
            Accept.accept_id == openid, Accept.task_id == Task.id,
            Accept.finish_time == default_datetime, Task.limit_time > now)
        return self._get_accept_tasks(query, openid, sort, last_accept_time, start, length)

    def get_finished_accept_tasks(self, openid: int, sort: bool = True, last_accept_time: datetime = None, start: int = 0, length: int = update_add_num):
        '''根据openid查找已完成的接受了的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置 @deperated
            length: int 获取任务的数量
            sort: bool 表示是否安装accept_time排序
            last_accept_time: datetime 表示上次获取的任务列表的最后的一个item的accept_time，以此作为后续数据请求的"标识"
        Return:
            tasks: 任务列表
            last_accept_time: 最后一个item的accept_time，注意如果tasks为空，则last_accept_time是传入的last_accept_time
        '''
        query = self.session.query(Task).join(Accept).filter(
            Accept.accept_id == openid, Accept.task_id == Task.id,
            Accept.finish_time != default_datetime, Accept.finish_time < Task.limit_time)
        return self._get_accept_tasks(query, openid, sort, last_accept_time, start, length)

    def get_complete_accept_tasks(self, openid: int, sort: bool = True, last_accept_time: datetime=None, start: int = 0, length: int = update_add_num):
        '''根据openid查找结束了的接受了的任务  
        Args:
            openid: int
            start: int 开始获取任务的位置 @deperated
            length: int 获取任务的数量
            sort: bool 表示是否安装accept_time排序
            last_accept_time: datetime 表示上次获取的任务列表的最后的一个item的accept_time，以此作为后续数据请求的"标识"
        Return:
            tasks: 任务列表
            last_accept_time: 最后一个item的accept_time，注意如果tasks为空，则last_accept_time是传入的last_accept_time
        '''
        now = datetime.now()
        query = self.session.query(Task).join(Accept).filter(
            Accept.accept_id == openid, Accept.task_id == Task.id,
            Accept.finish_time == default_datetime, Task.limit_time <= now)
        return self._get_accept_tasks(query, openid, sort, last_accept_time, start, length)

    def _get_accept_tasks(self, query, openid: int, sort: bool = True, last_accept_time: datetime=None, start: int = 0, length: int = update_add_num):
        '''查找接受的任务  
        Args:
            query: 查找任务的query
            openid: int
            start: int 开始获取任务的位置 @deperated
            length: int 获取任务的数量
            sort: bool 表示是否安装accept_time排序
            last_accept_time: datetime 表示上次获取的任务列表的最后的一个item的accept_time，以此作为后续数据请求的"标识"
        Return:
            tasks: 任务列表
            last_accept_time: 最后一个item的accept_time，注意如果tasks为空，则last_accept_time是传入的last_accept_time
        '''
        if last_accept_time is not None:
            query = query.filter(Accept.accept_time < last_accept_time)
        if sort:
            query = query.order_by(Accept.accept_time.desc())
        tasks = query.offset(start).limit(length).all()
        if tasks is not None and len(tasks) > 0:
            accept = Accept.query.filter(
                Accept.accept_id == openid, Accept.task_id == tasks[-1].id).one_or_none()
            if accept is not None:
                last_accept_time = accept.accept_time
        return tasks, last_accept_time

    def get_recipient(self, id_or_task, start: int=0, length: int=update_add_num):
        '''根据task_id或者task查找接受任务者  
        Args:
            id_or_task: int/Task 任务的id或者该任务
            start: int 获取接受者的开始位置
            length: int 获取接受者的长度
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
        '''根据task_id或者task找到任务发布者  
        Args:
            id_or_task: int/Task 任务的id或者该任务
        '''
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

    def get_all_problems(self, task_id: int):
        '''根据task_id获取对应的所有问题
        Args:
            task_id: int
        '''
        all_problems = Problem.query.filter(Problem.task_id == task_id)
        problem_content = ''
        for problem in all_problems:
            # 使用^作为problem的切分，使用$作为题目与答案的切分，使用#作为答案的切分
            if problem_content != "":
                problem_content += '^'
            problem_content += (problem.description + "$" + problem.all_answers)
        print(problem_content)
        return problem_content

    def post_answer(self, task_id: int, answer_content: str, open_id: int):
        '''
        提交问卷答案
        '''
        # TODO 逻辑上的一些问题 比如填完之后进行转账？还有limit_num减少
        answer_list = answer_content.split('^')
        all_problems = Problem.query.filter(Problem.task_id == task_id)
        i = 0
        answers = []
        for problem in all_problems:
            answers.append(Answer(accept_id=int(open_id), problem_id=problem.id, answer=int(answer_list[i])))
            i += 1
        print(answers)
        self.save_all(answers)
        self.commit()

    def get_all_answers(self, id_or_task):
        ''' 根据问卷id或者问卷获取所有的答案  
        Args:
            id_or_task: int/Task
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

    def get_task_by_id(self, task_id):
        ''' 根据任务id返回任务
        Args:
            task_id: int 任务id
        Return:
            task: Task 任务
        '''
        return Task.query.filter(Task.id == task_id).one_or_none()

    def get_task(self, accept_id: int=-1, sort: bool=True, last_id: int=-1, get_publisher: bool=True, start: int=0, length: int=update_add_num, screen_time: bool=True, screen_num: bool=True):
        '''搜索Task  
        Args:
            sort: bool 表示是否按照时间排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
            get_publisher: bool 表示是否获取任务发布者
            start: int 表示获取任务的开始位置
            length: int 表示获取任务的数量
            screen_time: bool 表示是否过滤掉时间过期了的任务
            screen_num: bool 表示是否过滤掉完成数量上满足了的任务
        Return:
            task_list: [Task] 任务列表
        '''
        query = Task.query
        return self._get_task(query, accept_id, sort, last_id, get_publisher, start, length, screen_time, screen_num)

    def get_task_by_text(self, search_text: str, accept_id: int=-1, sort: bool=True, last_id: int=-1, get_publisher: bool=True, start: int=0, length: int=update_add_num, screen_time: bool=True, screen_num: bool=True):
        '''根据内容和标题搜索Task  
        Args:
            search_text: str 表示用于搜索的文本
            sort: bool 表示是否按照时间排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
            get_publisher: bool 表示是否获取任务发布者
            start: int 表示获取任务的开始位置
            length: int 表示获取任务的数量
            screen_time: bool 表示是否过滤掉时间过期了的任务
            screen_num: bool 表示是否过滤掉完成数量上满足了的任务
        Return:
            task_list: [Task] 任务列表
        '''
        query = Task.query.filter(self.db.text(
            "match (title, content) against (:text)")).params(text=search_text)
        return self._get_task(query, accept_id, sort, last_id, get_publisher, start, length, screen_time, screen_num)

    def get_task_by_tag(self, search_tag: str, accept_id: int=-1, sort: bool=True, last_id: int=-1, get_publisher: bool=True, start: int=0, length: int=update_add_num, screen_time: bool=True, screen_num: bool=True):
        '''根据tag搜索Task  
        Args:
            search_tag: str 表示用于搜索的tag
            sort: bool 表示是否按照时间排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
            get_publisher: bool 表示是否获取任务发布者
            start: int 表示获取任务的开始位置
            length: int 表示获取任务的数量
            screen_time: bool 表示是否过滤掉时间过期了的任务
            screen_num: bool 表示是否过滤掉完成数量上满足了的任务
        Return:
            task_list: [Task] 任务列表
        '''
        query = Task.query.filter(Task.tag.match(search_tag))
        return self._get_task(query, accept_id, sort, last_id, get_publisher, start, length, screen_time, screen_num)

    def _get_task(self, query, accept_id: int=-1, sort: bool=True, last_id: int=-1, get_publisher: bool=True, start: int=0, length: int=update_add_num, screen_time: bool=True, screen_num: bool=True):
        '''搜索Task  
        Args:
            query: Task.query 用于查询任务的query
            sort: bool 表示是否按照时间排序
            last_id: int 表示上次获取的任务列表的最后的一个item的id，以此作为后续数据请求的"标识"
            get_publisher: bool 表示是否获取任务发布者
            start: int 表示获取任务的开始位置
            length: int 表示获取任务的数量
            screen_time: bool 表示是否过滤掉时间过期了的任务
            screen_num: bool 表示是否过滤掉完成数量上满足了的任务
            accept_id: int 表示是否过滤掉已经接受的任务
        Return:
            task_list: [Task] 任务列表
        '''
        if last_id != -1:
            query = query.filter(Task.id < last_id)
        if accept_id != -1:
            query = query.join(Accept).filter(Accept.task_id == Task.id, Accept.accept_id != accept_id)
        if screen_time:
            now = datetime.now()
            query = query.filter(Task.limit_time > now)
        if screen_num:
            query = query.filter(Task.limit_num > Task.accept_num)
        if sort:
            query = query.order_by(Task.id.desc())
        tasks = query.offset(start).limit(length).all()
        if tasks is not None and get_publisher:
            for task in tasks:
                self.get_publisher(task)
        return tasks

    def accept_task(self, accept_id :int, task_id: int):
        ''' 接受任务  
        Args:
            accept_id: int 接收者id
            task_id: int 任务id
        Return:
            flag: bool 表示是否结束成功，比如已经接受过了，则不可接受，或者是task不存在
            msg: str 表示失败原因
        '''
        task = Task.query.filter(Task.id == task_id).one_or_none()
        if task is None:
            return False, 'No such task.'
        stu = Student.query.filter(Student.openid == accept_id).one_or_none()
        if stu is None:
            return False, 'No such student.'
        accept = Accept.query.filter(Accept.task_id == task_id, Accept.accept_id == accept_id).one_or_none()
        if accept is not None:
            return False, 'Has been accepted.'
        self.save(Accept(tag=task.tag, accept_id=accept_id, task_id=task.id, accept_time=datetime.now(), finish_time=DEFAULT_TIME))
        return True, 'Accept successfully.'

    def finish_task(self, openid: int, task_id: int):
        '''完成任务  
        Args:
            openid: int 完整者的id
            task_id: int 任务id
        Return:
            flag: bool 表示是否成功
            msg: str 表示出错信息
        '''
        try:
            # with self.session.begin():
            accept = Accept.query.filter(Accept.accept_id == openid, Accept.task_id == task_id).with_for_update().one_or_none()
            if accept is None:
                return False, 'No such student ? No such task ? Or the student has not accepted this task!'
            task = Task.query.filter(Task.id == task_id).with_for_update().one_or_none()
            flag, msg = self.carry_over(task.publish_id, openid, task.reward)
            if not flag:
                return False, msg
            task.accept_num = task.accept_num + 1
            accept.finish_time = datetime.now()
            # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 这个太浪费时间了，要调用三个方法
            self.commit()
            return True, ''
        except Exception as e:
            self.session.rollback()
            return False, str(e)

    def charge(self, openid: int, money_num: int):
        '''充钱  
        Args:
            openid: int 学生或者组织的id
            money_num: int 充的钱的数量
        Return:
            flag: bool 表示是否成功
            msg: str 失败的原因，如果成功则为空
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

    def carry_over(self, source_id: int, target_id: int, money_num: int):
        '''转账，从source_id处转到target_id处，转移money_num个币  
        Args:
            source_id: int 币来源
            target_id: int 币去处
            money_num: int 币数量
        Return:
            flag: bool 表示是否成功
            msg: str 失败的原因，如果成功则为空
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

    def cash_in(self, openid: int, money_num: int):
        '''套现  
        Args:
            openid: int 学生或者组织的id
            money_num: int 套现的钱的数量
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

if __name__ == "__main__":
    test_json()
    test_normal_crud(db_helper)
    test_time(db_helper, update_add_num)
    # test_none()
    # task = Task.query.filter(Task.id == 3).one_or_none()
    # print(task.accepts)

# 测试使用
if app.config['ADD_RANDOM_SAMPLE']:
    test_normal_crud(db_helper)
# test_normal_crud(db_helper)
# test_create_student_and_organization(db_helper)
test_accetp_and_publish(db_helper, update_add_num)

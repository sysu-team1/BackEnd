from .test import test_json, test_normal_crud, test_time
from .Accept import Accept
from .Organization import Organization
from .prepare import ALL_TAGS, QUESTIONNAIRE_INDEX, app, db
from .Student import Student
from .Task import Task
from .Problem import Problem
import time

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

    10. 报酬系统
    11. 任务完成
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

    def create_task(self, publish_id, limit_time, limit_num, title, content, tag):
        '''创建任务

        参数：
        publish_id, 发布人id ，也就是open_id
        limit_time, ddl
        limit_num, 限制人数数量
        title, task标题
        content, 内容（如果tag为'w问卷'，则内容为问卷的内容）
        tag, 标签

        输出参数：
        task
        '''
        task = Task(publish_id=publish_id, publish_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 
                        limit_time=limit_time, limit_num=limit_num, title=title, content=content, tag=tag)
        self.save(task)
        if tag == '问卷':
            # 使用^作为problem的切分，使用$作为题目与答案的切分，使用#作为答案的切分
            problems_list = content.split("^")
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
        return task

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

    def finish_task(self, openid, task_id):
        '''完成任务  
        Args:
            openid: 完整者的id
            task_id: 任务id
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
            accept.finish_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            self.commit()
            return True, ''
        except Exception as e:
            self.session.rollback()
            return False, str(e)

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

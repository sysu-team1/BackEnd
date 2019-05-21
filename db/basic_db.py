from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:960919AB@localhost:3308/test2'
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)

SEX = ['unknown', 'male', 'female']
EDUBG = ['undergraduate', 'masterofscience', 'doctor']
DEFAULT_TIME = '2000-01-01 00:00:00'


class Student(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `students` (
        `openid` varchar(20) NOT NULL COMMENT '用户的唯一标识符',
        `email` varchar(20) NOT NULL COMMENT '学校邮箱',
        `password` varchar(20) NOT NULL COMMENT '密码',
        `sex` enum('unknown','male','female') DEFAULT 'unknown' COMMENT '用户性别',
        `collage` varchar(20) DEFAULT '' COMMENT '学院',
        `grade` char(4) NOT NULL DEFAULT '2016' COMMENT '入学年级',
        `edu_bg` enum('undergraduate','masterofscience','doctor') DEFAULT 'undergraduate' COMMENT '学历',
        `tag` varchar(20) DEFAULT '' COMMENT '与任务相关的标签',
        `signature` char(100) DEFAULT '' COMMENT '用户签名',
        PRIMARY KEY (`openid`),
        FULLTEXT KEY `stu_tag` (`tag`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        accepts: 表示接收的任务
        tasks: 表示发布的任务
    兴趣小组 TODO
    '''

    __tablename__ = 'students'

    openid = db.Column('openid', db.VARCHAR(
        20), nullable=False, comment='用户的唯一标识符')
    email = db.Column('email', db.VARCHAR(
        20), nullable=False, comment='学校邮箱')
    password = db.Column('password', db.VARCHAR(
        20), nullable=False, comment='密码')
    sex = db.Column('sex', db.Enum(
        *SEX), server_default=SEX[0], comment='用户性别')  # default的话是在插入时才有的
    collage = db.Column('collage', db.VARCHAR(
        20), server_default='', comment='学院')
    grade = db.Column('grade', db.CHAR(
        4), nullable=False, server_default='2016', comment='入学年级')
    edu_bg = db.Column('edu_bg', db.Enum(
        *EDUBG), server_default=EDUBG[0], comment='学历')
    tag = db.Column('tag', db.VARCHAR(
        20), server_default='', comment='与任务相关的标签')
    signature = db.Column('signature', db.CHAR(
        100), server_default='', comment='用户签名')

    __table_args__ = (
        db.PrimaryKeyConstraint('openid'),
        db.Index('stu_tag', 'tag', mysql_prefix='FULLTEXT'),
    )

    accepts = db.relationship(
        'Accept', back_populates='student', cascade='delete')
    tasks = None

    def __repr__(self):
        return '<Student(email={}, password={}, sex={}, collage={}, grade={}, edu_bg={}, tag={}, signature={})>'.format(
            self.email, self.password, self.sex, self.collage, self.grade, self.edu_bg, self.tag, self.signature)


class Organization(db.Model):
    '''
    ```sql
    CREATE TABLE `organizations` (
        `email` varchar(20) NOT NULL COMMENT '学校邮箱',
        `openid` varchar(20) NOT NULL COMMENT '组织的唯一标识符',
        `password` varchar(20) NOT NULL COMMENT '密码',
        `description` varchar(100) DEFAULT '' COMMENT '组织描述',
        PRIMARY KEY (`openid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        task: 表示发布的任务
    '''

    __tablename__ = 'organizations'

    email = db.Column('email', db.VARCHAR(
        20), nullable=False, comment='学校邮箱')
    openid = db.Column('openid', db.VARCHAR(
        20), nullable=False, comment='组织的唯一标识符')
    password = db.Column('password', db.VARCHAR(
        20), nullable=False, comment='密码')
    description = db.Column('description', db.VARCHAR(
        100), server_default='', comment='组织描述')

    __table_args__ = (
        db.PrimaryKeyConstraint('openid'),
    )

    tasks = None

    def __repr__(self):
        return '<Organization(email={}, password={}, description={})>'.format(
            self.email, self.password, self.description)


class Task(db.Model):
    '''
    ```sql
    CREATE TABLE `tasks` (
        `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '任务id',
        `publish_id` varchar(20) NOT NULL COMMENT '发布者id',
        `publish_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
        `limit_time` timestamp NULL DEFAULT '2000-01-01 00:00:00' COMMENT '限时',
        `limit_num` int(11) DEFAULT '-1' COMMENT '任务可接受人数',
        `accept_num` int(11) DEFAULT '0' COMMENT '任务已接受人数',
        `title` varchar(20) NOT NULL COMMENT '发布任务标题',
        `content` varchar(300) NOT NULL COMMENT '发布任务内容',
        `tag` varchar(30) DEFAULT NULL COMMENT '任务tag',
        PRIMARY KEY (`id`),
        KEY `publish` (`publish_id`,`id`),
        FULLTEXT KEY `task_tag` (`tag`),
        FULLTEXT KEY `task_text` (`title`,`content`)
    ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        accepts: 表示接受任务者
        publisher: 表示发布任务者
    '''

    __tablename__ = 'tasks'

    id = db.Column(
        'id', db.Integer, autoincrement=True, nullable=False, comment='任务id', primary_key=True)
    publish_id = db.Column('publish_id', db.VARCHAR(
        20), nullable=False, comment='发布者id')
    publish_time = db.Column(
        'publish_time', db.TIMESTAMP, server_default=db.func.now(), comment='发布时间')
    limit_time = db.Column(
        'limit_time', db.TIMESTAMP, server_default=DEFAULT_TIME, comment='限时')
    limit_num = db.Column(
        'limit_num', db.Integer, server_default='-1', comment='任务可接受人数')
    accept_num = db.Column(
        'accept_num', db.Integer, server_default='0', comment='任务已接受人数')
    title = db.Column('title', db.VARCHAR(
        20), nullable=False, comment='发布任务标题')
    content = db.Column('content', db.VARCHAR(
        300), nullable=False, comment='发布任务内容')
    tag = db.Column('tag', db.VARCHAR(30), comment='任务tag')

    __table_args__ = (
        db.Index('publish', 'publish_id', 'id'),
        db.Index('task_tag', 'tag', mysql_prefix='FULLTEXT'),
        db.Index('task_text', 'title', 'content', mysql_prefix='FULLTEXT'),
    )

    publisher = None
    accepts = db.relationship(
        'Accept', back_populates='task', cascade='delete')

    def __repr__(self):
        return '<Task(publish_id={}, publish_time={}, limit_time={}, limit_num={}, accept_num={}, content={}, tag={})>'.format(
            self.publish_id, self.publish_time, self.limit_time, self.limit_num, self.accept_num, self.content, self.tag)


class Accept(db.Model):
    '''
    ```sql
    CREATE TABLE `accepts` (
        `accept_id` varchar(20) NOT NULL COMMENT '接受者id',
        `task_id` int(11) NOT NULL COMMENT '任务id',
        `accept_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '接受时间',
        `finish_time` timestamp NULL DEFAULT '2000-01-01 00:00:00' COMMENT '完成时间',
        PRIMARY KEY (`accept_id`,`task_id`),
        KEY `task` (`task_id`),
        CONSTRAINT `accepts_ibfk_1` FOREIGN KEY (`accept_id`) REFERENCES `students` (`openid`) ON DELETE CASCADE,
        CONSTRAINT `accepts_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        task: 任务
        student: 接受者
    '''

    __tablename__ = 'accepts'

    accept_id = db.Column('accept_id', db.VARCHAR(20), db.ForeignKey(
        'students.openid', ondelete='cascade'), nullable=False, comment='接受者id')
    task_id = db.Column('task_id', db.Integer, db.ForeignKey(
        'tasks.id', ondelete='cascade'), nullable=False, comment='任务id')
    accept_time = db.Column(
        'accept_time', db.TIMESTAMP, server_default=db.func.now(), comment='接受时间')
    finish_time = db.Column(
        'finish_time', db.TIMESTAMP, server_default=DEFAULT_TIME, comment='完成时间')

    task = db.relationship('Task', back_populates='accepts')
    student = db.relationship('Student', back_populates='accepts')

    __table_args__ = (
        db.PrimaryKeyConstraint('accept_id', 'task_id'),
        db.Index('task', 'task_id'),
    )

    def __repr__(self):
        return '<Accept(accept_id={}, task_id={}, accept_time={}, finish_time={})>'.format(
            self.accept_id, self.task_id, self.accept_time, self.finish_time)


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
    9. 搜索任务(根据内容/标题/tag)
    '''

    def __init__(self, db):
        self.db = db
        self.session = self.db.session

    def commit(self):
        '''更新提交'''
        self.session.commit()

    def save(self, data):
        '''保存一个数据'''
        self.session.add(data)

    def save_all(self, datas):
        '''保存批量数据'''
        self.session.add_all(datas)

    def delete(self, data):
        '''删除一个数据'''
        if isinstance(data, (Student, Organization)):
            Accept.query.filter(Accept.accept_id == data.openid).delete()
            Task.query.filter(Task.publish_id == data.openid).delete()
        if isinstance(data, Task):
            Accept.query.filter(Accept.task_id == data.id).delete()
        self.session.delete(data)

    def delete_all(self, datas):
        '''删除批量数据'''
        for data in datas:
            self.delete(data)

    def query_student(self, openid, get_all=False):
        '''根据openid查找student'''
        if get_all:
            stu = Student.query.options(db.joinedload(Student.accepts)).filter(
                Student.openid == openid).one_or_none()
            stu.tasks = self.get_publish_tasks(stu.openid)
        else:
            stu = Student.query.filter(Student.openid == openid).one_or_none()
        return stu

    def query_oraganization(self, openid, get_all=False):
        '''根据openid查找oraganization'''
        org = self.session.query(Organization).filter(
            Organization.openid == openid).one_or_none()
        if get_all:
            org.tasks = self.get_publish_tasks(org.openid)
        return org

    def get_publish_tasks(self, openid, start=0, length=10):
        '''根据openid查找发布的任务'''
        return Task.query.filter(Task.publish_id == openid).offset(start).limit(length).all()

    def get_accept_tasks(self, openid, start=0, length=10):
        '''根据openid查找接受的任务'''
        return self.session.query(Task).join(Accept).filter(Accept.accept_id == openid).filter(Accept.task_id == Task.id).offset(start).limit(length).all()

    def get_recipient(self, task_id, start=0, length=10):
        '''根据task_id查找接受任务者'''
        return self.session.query(Student).join(Accept).filter(Accept.task_id == task_id).filter(Accept.accept_id == Student.openid).offset(start).limit(length).all()

    def get_publisher(self, task_id):
        '''根据task_id找到任务发布者'''
        publish_id = self.session.query(
            Task.publish_id).filter(Task.id == task_id).one()
        if publish_id.endswith('_o'):
            return Organization.query.filter(Organization.openid == publish_id).one()
        return Student.query.filter(Student.openid == publish_id).one()

    def search_task_by_text(self, search_text, start=0, length=10):
        '''根据内容和标题搜索Task'''
        return Task.query.filter(self.db.text("match (title, content) against (:text)")).params(text=search_text).offset(start).limit(length).all()

    def search_task_by_tag(self, search_tag, start=0, length=10):
        '''根据tag搜索Task'''
        return Task.query.filter(Task.tag.match(search_tag)).offset(start).limit(length).all()


db.drop_all()
db.create_all()
db_helper = DBHelper(db)

db_helper.save_all([
    Student(email='email1@qq.com', openid='openid1', password='password1'),
    Student(email='email2@qq.com', openid='openid2', password='password2'),
    Student(email='email3@qq.com', openid='openid3', password='password3'),
    Student(email='email4@qq.com', openid='openid4', password='password4'),
])
db_helper.save_all([
    Organization(email='email1@qq.com',
                 openid='openid1_o', password='password1'),
    Organization(email='email2@qq.com',
                 openid='openid2_o', password='password2'),
])
db_helper.save_all([
    Task(publish_id='openid1_o', title='title1',
         content='word1 word2 word3 word4 word5', tag='tag1 tag2'),
    Task(publish_id='openid1_o', title='title2',
         content='word1 word2 word6 word7 word8', tag='tag2 tag3 tag4'),
    Task(publish_id='openid1', title='title2',
         content='word1 word2 word6 word7 word8', tag='tag2 tag3 tag4'),
    Task(publish_id='openid2_o', title='title2',
         content='word1 word2 word6 word7 word8', tag='tag2 tag3 tag4'),
    Task(publish_id='openid2', title='title2',
         content='word1 word2 word6 word7 word8', tag='tag2 tag3 tag4'),
])
db_helper.save_all([
    Accept(accept_id='openid1', task_id=1),
    Accept(accept_id='openid3', task_id=1),
    Accept(accept_id='openid4', task_id=1),
    Accept(accept_id='openid2', task_id=2),
    Accept(accept_id='openid3', task_id=2),
    Accept(accept_id='openid4', task_id=2),
    Accept(accept_id='openid1', task_id=2),
])
db_helper.commit()

print(db.session.query(Accept).count(), db.session.query(Task).count())
stu = db_helper.query_student('openid1')
org = db_helper.query_oraganization('openid1_o')
print(db_helper.get_publish_tasks(org.openid))
print(db_helper.get_accept_tasks(stu.openid))
db_helper.delete(stu)
print(db.session.query(Accept).count(), db.session.query(Task).count())

print(db_helper.search_task_by_text('word1'))
print(db_helper.search_task_by_text('word5'))
print(db_helper.search_task_by_tag('tag2'))
print(db_helper.search_task_by_tag('tag4'))

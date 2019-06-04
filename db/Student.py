import copy
import random

from .prepare import app, db, model_repr, SEX, EDUBG, ALL_TAGS


class Student(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `students` (
        `openid` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户的唯一标识符',
        `email` varchar(40) NOT NULL COMMENT '学校邮箱',
        `password` varchar(20) NOT NULL COMMENT '密码',
        `student_id` varchar(10) NOT NULL DEFAULT '' COMMENT '学号',
        `name` varchar(100) DEFAULT '' COMMENT '名称',
        `sex` enum('unknown','male','female') DEFAULT 'unknown' COMMENT '用户性别',
        `collage` varchar(20) DEFAULT '' COMMENT '学院',
        `grade` int(11) NOT NULL DEFAULT '2016' COMMENT '入学年级',
        `edu_bg` enum('undergraduate','masterofscience','doctor') DEFAULT 'undergraduate' COMMENT '学历',
        `tag` varchar(100) DEFAULT '' COMMENT '与任务相关的标签',
        `signature` varchar(300) DEFAULT '' COMMENT '用户签名',
        `cash` int(11) DEFAULT '0' COMMENT '拥有的币',
        PRIMARY KEY (`openid`),
        FULLTEXT KEY `stu_tag` (`tag`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1000000 DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        accepts: 表示接收的任务
        tasks: 表示发布的任务
    '''

    __tablename__ = 'students'

    openid = db.Column('openid', db.Integer(
    ), autoincrement=True, nullable=False, comment='用户的唯一标识符')
    email = db.Column('email', db.VARCHAR(
        40), nullable=False, comment='学校邮箱')
    password = db.Column('password', db.VARCHAR(
        20), nullable=False, comment='密码')
    student_id = db.Column('student_id', db.VARCHAR(
        10), nullable=False, server_default='', comment='学号')
    name = db.Column('name', db.VARCHAR(
        100), server_default='', comment='名称')
    sex = db.Column('sex', db.Enum(
        *SEX), server_default=SEX[0], comment='用户性别')  # default的话是在插入时才有的
    collage = db.Column('collage', db.VARCHAR(
        20), server_default='', comment='学院')
    grade = db.Column('grade', db.Integer(
    ), nullable=False, server_default='2016', comment='入学年级')
    edu_bg = db.Column('edu_bg', db.Enum(
        *EDUBG), server_default=EDUBG[0], comment='学历')
    tag = db.Column('tag', db.VARCHAR(
        100), server_default='', comment='与任务相关的标签')
    signature = db.Column('signature', db.VARCHAR(
        300), server_default='', comment='用户签名')
    cash = db.Column('cash', db.Integer(), server_default='0', comment='拥有的币')

    __table_args__ = (
        db.PrimaryKeyConstraint('openid'),
        db.Index('stu_tag', 'tag', mysql_prefix='FULLTEXT'),
    )

    accepts = db.relationship(
        'Accept', back_populates='student', cascade='delete')
    tasks = None
    # _tasks = None
    # get_tasks = None

    # get_tasks = None
    # def __getattribute__(self, name):
    #     if name == 'tasks' and self.task is None and Student.get_tasks is not None:  # 无限递归
    #         self.tasks = Student.get_tasks(self.openid)
    #     return super(Student, self).__getattribute__(name)

    def __repr__(self):
        # return '<Student(email={}, password={}, sex={}, collage={}, grade={}, edu_bg={}, tag={}, signature={})>'.format(
        #     self.email, self.password, self.sex, self.collage, self.grade, self.edu_bg, self.tag, self.signature)
        # return model_repr(self, config.STUDENT_JSON_PATTERN, config.STUDENT_JSON_ATTR_ORDER)
        return model_repr(self, app.config['STUDENT_JSON_PATTERN'], app.config['STUDENT_JSON_ATTR_ORDER'])


def random_stus(num):
    rand_collages = ['药学院', '数据科学与计算机学院', '法学院', '心理学院', '哲学院', '医学院']
    tag_len = len(ALL_TAGS)
    stus = []
    for i in range(num):
        sex = random.choice(SEX)
        edu_bg = random.choice(EDUBG)
        collage = random.choice(rand_collages)
        grade = 2019 - random.randint(0, 10)
        rnum = random.randint(0, tag_len)
        tag = []
        all_tags = copy.deepcopy(ALL_TAGS)
        while len(tag) < rnum:
            index = random.randint(0, len(all_tags) - 1)
            tag.append(all_tags[index])
            all_tags.pop(index)
        tag = ','.join(tag)
        start, length = random.randint(1, 20), random.randint(10, 15)
        signature = ' '.join(['word{}'.format(
            j) for j in range(start, start + length)])
        cash = random.randint(10, 5000)
        stus.append(Student(email='email{}@qq.com'.format(i), password='pass{}'.format(
            i), student_id="16340{:0>3d}".format(i), name="16340{:0>3d}".format(i), sex=sex, collage=collage, grade=grade, edu_bg=edu_bg, tag=tag, signature=signature, cash=cash))
    return stus

import copy
import random

from .prepare import app, db, model_repr, DEFAULT_TIME, ALL_TAGS, QUESTIONNAIRE_INDEX
from .Problem import random_problems


class Task(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `tasks` (
        `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '任务id',
        `publish_id` int(11) NOT NULL COMMENT '发布者id',
        `publish_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
        `limit_time` timestamp NULL DEFAULT '2000-01-01 00:00:00' COMMENT '限时',
        `limit_num` int(11) DEFAULT '-1' COMMENT '任务可接受人数',
        `accept_num` int(11) DEFAULT '0' COMMENT '任务已接受人数',
        `title` varchar(50) NOT NULL COMMENT '发布任务标题',
        `content` varchar(300) NOT NULL COMMENT '发布任务内容',
        `tag` varchar(30) DEFAULT NULL COMMENT '任务tag',
        PRIMARY KEY (`id`),
        KEY `publish` (`publish_id`,`publish_time`),
        FULLTEXT KEY `task_text` (`title`,`content`),
        FULLTEXT KEY `task_tag` (`tag`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        accepts: 表示接受任务者
        publisher: 表示发布任务者
        problems: 表示问题
        answers: 表示回复
    '''

    __tablename__ = 'tasks'

    id = db.Column('id', db.Integer(
    ), autoincrement=True, nullable=False, comment='任务id', primary_key=True)
    publish_id = db.Column('publish_id', db.Integer(
    ), nullable=False, comment='发布者id')
    publish_time = db.Column(
        'publish_time', db.TIMESTAMP, server_default=db.func.now(), comment='发布时间')
    limit_time = db.Column(
        'limit_time', db.TIMESTAMP, server_default=DEFAULT_TIME, comment='限时')
    limit_num = db.Column(
        'limit_num', db.Integer, server_default='-1', comment='任务可接受人数')
    accept_num = db.Column(
        'accept_num', db.Integer, server_default='0', comment='任务已接受人数')
    title = db.Column('title', db.VARCHAR(
        50), nullable=False, comment='发布任务标题')
    content = db.Column('content', db.VARCHAR(
        300), nullable=False, comment='发布任务内容')
    tag = db.Column('tag', db.VARCHAR(30), comment='任务tag')

    __table_args__ = (
        db.Index('publish', 'publish_id', 'publish_time'),
        db.Index('task_tag', 'tag', mysql_prefix='FULLTEXT'),
        db.Index('task_text', 'title', 'content', mysql_prefix='FULLTEXT'),
    )

    # answers = db.relationship(
    #     'Answer', back_populates='task', cascade='delete')
    accepts = db.relationship(
        'Accept', back_populates='task', cascade='delete')
    problems = db.relationship(
        'Problem', back_populates='task', cascade='delete')
    publisher = None
    # _publisher = None
    # get_publisher = None

    def __repr__(self):
        # return '<Task(publish_id={}, publish_time={}, limit_time={}, limit_num={}, accept_num={}, content={}, tag={})>'.format(
        #     self.publish_id, self.publish_time, self.limit_time, self.limit_num, self.accept_num, self.content, self.tag)
        # return model_repr(self, config.TASK_JSON_PATTERN, config.TASK_JSON_ATTR_ORDER)
        return model_repr(self, app.config['TASK_JSON_PATTERN'], app.config['TASK_JSON_ATTR_ORDER'])


def random_tasks(num, orgs, stus, db_helper):
    tag_len = len(ALL_TAGS)
    tasks = []
    for i in range(num):
        publish_id = random.choice(stus).openid if random.random(
        ) < 0.33 else random.choice(orgs).openid
        start, length = random.randint(0, 10), random.randint(3, 5)
        title = ' '.join(['word{}'.format(
            j)for j in range(start, start + length)])
        start, length = random.randint(0, 10), random.randint(10, 30)
        content = ' '.join(['word{}'.format(
            j)for j in range(start, start + length)])
        tag = []
        all_tags = copy.deepcopy(ALL_TAGS)
        rnum = random.randint(0, tag_len)
        while len(tag) < rnum:
            index = random.randint(0, len(all_tags) - 1)
            tag.append(all_tags[index])
            all_tags.pop(index)
        tag = ','.join(tag)
        publish_time = db.func.now()
        limit_time = DEFAULT_TIME if random.random() < 0.5 else db.func.date_add(
            publish_time, db.text('interval {} hour'.format(random.randint(10, 120))))
        task = Task(publish_id=publish_id, publish_time=publish_time, limit_time=limit_time,
                    limit_num=random.randint(10, 50), title=title, content=content, tag=tag)
        tasks.append(task)
        db_helper.save(task)
        db_helper.commit()
        # -----------------
        if task.tag.find(ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1:
            # task.problems = random_problems(random.randint(5, 10), task)
            random_problems(random.randint(5, 10), task, db_helper)
        # -----------------
    return tasks

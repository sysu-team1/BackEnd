import datetime
import random

from prepare import app, db, model_repr, DEFAULT_TIME, ALL_TAGS, QUESTIONNAIRE_INDEX
from Answer import random_answers

class Accept(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `accepts` (
        `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '接受id',
        `tag` varchar(30) DEFAULT NULL COMMENT '任务tag',
        `accept_id` int(11) NOT NULL COMMENT '接受者id',
        `task_id` int(11) NOT NULL COMMENT '任务id',
        `accept_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '接受时间',
        `finish_time` timestamp NULL DEFAULT '2000-01-01 00:00:00' COMMENT '完成时间',
        PRIMARY KEY (`id`),
        KEY `task` (`task_id`,`finish_time`),
        KEY `accept` (`accept_id`,`finish_time`),
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

    id = db.Column('id', db.Integer(
    ), autoincrement=True, primary_key=True, comment='接受id')
    tag = db.Column('tag', db.VARCHAR(30), comment='任务tag')
    accept_id = db.Column('accept_id', db.Integer, db.ForeignKey(
        'students.openid', ondelete='cascade'), nullable=False, comment='接受者id')
    task_id = db.Column('task_id', db.Integer, db.ForeignKey(
        'tasks.id', ondelete='cascade'), nullable=False, comment='任务id')
    accept_time = db.Column(
        'accept_time', db.TIMESTAMP, server_default=db.func.now(), comment='接受时间')
    finish_time = db.Column(
        'finish_time', db.TIMESTAMP, server_default=DEFAULT_TIME, comment='完成时间')

    student = db.relationship('Student', back_populates='accepts')
    task = db.relationship('Task', back_populates='accepts')
    answers = db.relationship(
        'Answer', back_populates='accept', cascade='delete')

    __table_args__ = (
        db.Index('accept', 'accept_id', 'finish_time'),
        db.Index('task', 'task_id', 'finish_time'),
    )

    def __repr__(self):
        # return '<Accept(accept_id={}, task_id={}, accept_time={}, finish_time={})>'.format(
        #     self.accept_id, self.task_id, self.accept_time, self.finish_time)
        # return model_repr(self, config.ACCEPT_JSON_PATTERN, config.ACCEPT_JSON_ATTR_ORDER)
        return model_repr(self, app.config['ACCEPT_JSON_PATTERN'], app.config['ACCEPT_JSON_ATTR_ORDER'])


def random_accepts(num, tasks, stus, db_helper):
    accepts = []
    stu_num = len(stus)
    task_num = len(tasks)
    for i in range(num):
        accept_time = datetime.datetime.now()
        task = random.choice(tasks)
        while task.accept_num >= stu_num or \
            task.limit_time != DEFAULT_TIME and task.limit_time <= accept_time or \
                task.limit_num != -1 and task.limit_num <= task.accept_num:
            task = random.choice(tasks)
        accept_id = random.choice(stus).openid
        while db_helper.has_accept(accept_id, task.id):
            accept_id = random.choice(stus).openid
        if random.random() < 0.5:
            if task.limit_time == DEFAULT_TIME:
                # finish_time = db.func.date_add(accept_time, db.text(
                #     'interval {} hour'.format(random.randint(10, 240))))
                finish_time = accept_time + \
                    datetime.timedelta(hours=random.randint(10, 240))
            else:
                # finish_time = db.func.date_add(accept_time, db.text(
                #     'interval {} second'.format(random.randint(1800, 864000))))
                finish_time = accept_time + \
                    datetime.timedelta(seconds=random.randint(1800, 86400))
                while finish_time > task.limit_time:
                    finish_time = accept_time + \
                        datetime.timedelta(seconds=random.randint(1800, 86400))
        else:
            finish_time = DEFAULT_TIME
        accept = Accept(tag=task.tag, accept_id=accept_id, task_id=task.id,
                        accept_time=accept_time, finish_time=finish_time)
        task.accept_num += 1
        accepts.append(accept)
        db_helper.save(accept)
        db_helper.commit()
        # ----------
        if accept.tag.find(ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1:
            random_answers(accept.id, task.problems, db_helper)
        # ----------
    return accepts

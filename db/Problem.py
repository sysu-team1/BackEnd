import random

from .prepare import app, db, model_repr


class Problem(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `problems` (
        `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '问题id',
        `task_id` int(11) NOT NULL COMMENT '关联的任务的id',
        `description` varchar(100) DEFAULT '' COMMENT '问题描述',
        `all_answers` varchar(100) DEFAULT '' COMMENT '问题答案',
        PRIMARY KEY (`id`),
        KEY `task_id` (`task_id`),
        CONSTRAINT `problems_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        task: 任务
        answers: 所有回答
    '''

    __tablename__ = 'problems'

    id = db.Column('id', db.Integer(
    ), nullable=False, autoincrement=True, comment='问题id')
    task_id = db.Column('task_id', db.Integer, db.ForeignKey(
        'tasks.id', ondelete='cascade'), nullable=False, comment='关联的任务的id')
    description = db.Column('description', db.VARCHAR(
        100), server_default='', comment='问题描述')
    all_answers = db.Column('all_answers', db.VARCHAR(
        100), server_default='', comment='问题答案')

    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
    )

    task = db.relationship('Task', back_populates='problems')
    answers = db.relationship(
        'Answer', back_populates='problem', cascade='delete')

    def __repr__(self):
        return model_repr(self, app.config['PROBLEM_JSON_PATTERN'], app.config['PROBLEM_JSON_ATTR_ORDER'])


def random_problems(num, task, db_helper):
    problems = []
    for i in range(num):
        length = random.randint(3, 10)
        all_answers = '#'.join(['answer{}'.format(j) for j in range(length)])
        problem = Problem(task_id=task.id, description='descriptin{}'.format(
            i), all_answers=all_answers)
        problems.append(problem)
    db_helper.save_all(problems)
    db_helper.commit()
    return problems

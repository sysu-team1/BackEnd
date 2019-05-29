import random

from .prepare import app, db, model_repr

class Answer(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `answers` (
        `accept_id` int(11) NOT NULL COMMENT '接受id',
        `problem_id` int(11) NOT NULL COMMENT '问题id',
        `answer` int(11) NOT NULL DEFAULT '-1' COMMENT '具体答案的选项',
        PRIMARY KEY (`accept_id`,`problem_id`),
        KEY `problem_index` (`problem_id`),
        CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`accept_id`) REFERENCES `accepts` (`id`) ON DELETE CASCADE,
        CONSTRAINT `answers_ibfk_2` FOREIGN KEY (`problem_id`) REFERENCES `problems` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基本属性
        problem: 关联的问题
        task: 关联的任务
    '''

    __tablename__ = 'answers'

    accept_id = db.Column('accept_id', db.Integer, db.ForeignKey(
        'accepts.id', ondelete='cascade'), nullable=False, comment='接受id')
    problem_id = db.Column('problem_id', db.Integer, db.ForeignKey(
        'problems.id', ondelete='cascade'), nullable=False, comment='问题id')
    # answer_id = db.Column('answer_id', db.Integer, db.ForeignKey(
    #     'answers.openid', ondelete='cascade'), nullable=False, comment='回答者id')
    # task_id = db.Column('task_id', db.Integer, db.ForeignKey(
    #     'tasks.id', ondelete='cascade'), nullable=False, comment='任务id')
    answer = db.Column('answer', db.Integer(
    ), nullable=False, server_default='-1', comment='具体答案的选项')

    accept = db.relationship('Accept', back_populates='answers')
    problem = db.relationship('Problem', back_populates='answers')
    # task = db.relationship('Task', back_populates='answers')
    # student = db.relationship('Student', back_populates='answers')

    __table_args__ = (
        db.PrimaryKeyConstraint('accept_id', 'problem_id'),
        db.Index('problem_index', 'problem_id'),
    )

    def __repr__(self):
        return model_repr(self, app.config['ANSWER_JSON_PATTERN'], app.config['ANSWER_JSON_ATTR_ORDER'])


def random_answers(accept_id, problems, db_helper):
    answers = []
    for problem in problems:
        int_answer = random.randint(
            0, len(problem.all_answers.split(sep=app.config['SPLIT_ANSWER'])) - 1)
        answers.append(Answer(
            accept_id=accept_id, problem_id=problem.id, answer=int_answer))
    db_helper.save_all(answers)
    db_helper.commit()
    return answers

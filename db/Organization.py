import random

from .prepare import app, db, model_repr


class Organization(db.Model):
    '''
    使用的sql语句:
    ```sql
    CREATE TABLE `organizations` (
        `openid` int(11) NOT NULL AUTO_INCREMENT COMMENT '组织的唯一标识符',
        `email` varchar(20) NOT NULL COMMENT '学校邮箱',
        `password` varchar(20) NOT NULL COMMENT '密码',
        `description` varchar(300) DEFAULT '' COMMENT '组织描述',
        PRIMARY KEY (`openid`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```
    属性:
        基础属性
        task: 表示发布的任务
    '''

    __tablename__ = 'organizations'

    openid = db.Column('openid', db.Integer(
    ), autoincrement=True, nullable=False, comment='组织的唯一标识符')
    email = db.Column('email', db.VARCHAR(
        40), nullable=False, comment='学校邮箱')
    password = db.Column('password', db.VARCHAR(
        20), nullable=False, comment='密码')
    name = db.Column('name', db.VARCHAR(
        100), server_default='', comment='名称')
    description = db.Column('description', db.VARCHAR(
        300), server_default='', comment='组织描述')
    cash = db.Column('cash', db.Integer(), server_default='0', comment='拥有的币')

    __table_args__ = (
        db.PrimaryKeyConstraint('openid'),
    )

    tasks = None
    # _tasks = None
    # get_tasks = None

    def __repr__(self):
        # return '<Organization(email={}, password={}, description={})>'.format(
        #     self.email, self.password, self.description)
        return model_repr(self, app.config['ORGANIZATION_JSON_PATTERN'], app.config['ORGANIZATION_JSON_ATTR_ORDER'])


def random_orgs(num):
    orgs = []
    for i in range(num):
        start, length = random.randint(1, 20), random.randint(10, 15)
        description = ' '.join(['word{}'.format(
            j) for j in range(start, start + length)])
        orgs.append(Organization(email='email{}@qq.com'.format(i), password='pass{}'.format(
            i), description=description))
    return orgs

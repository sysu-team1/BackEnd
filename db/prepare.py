# 兴趣小组 TODO
# 报酬系统 TODO

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = SQLAlchemy(app)

SEX = ['unknown', 'male', 'female']
EDUBG = ['undergraduate', 'masterofscience', 'doctor']
DEFAULT_TIME = '2000-01-01 00:00:00'
ALL_TAGS = ['questionnaire', 'take out', 'others']
QUESTIONNAIRE_INDEX = 0
SPLIT_STU_ORG = 1000000
SPLIT_ANSWER = '#'


def model_repr(obj, pattern: str, orders):
    temp = []
    for order in orders:
        temp.append('"{}"'.format(order))
        attr = getattr(obj, order)
        if attr is None:
            attr = '""'
        elif isinstance(attr, (str)):
            attr = '"{}"'.format(attr)
        else:
            attr = str(attr)
        temp.append(attr)
    return pattern % tuple(temp)

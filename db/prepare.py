from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from tools.utils import model_repr

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = SQLAlchemy(app)

SEX = ['未知', '男', '女']
EDUBG = ['本科', '硕士', '博士']
DEFAULT_TIME = '2000-01-01 00:00:00'
ALL_TAGS = ['问卷', '取快递', '其他']
QUESTIONNAIRE_INDEX = 0
SPLIT_STU_ORG = 1000000
SPLIT_ANSWER = '#'

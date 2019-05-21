from data_flask_sqlalchemy import db, db_helper, Student, Organization, Task, Accept, app


@app.route('/')
def hello_world():
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

    html = "There are {} accepts, ".format(db.session.query(Accept).count())
    html += "and there are {} tasks total.<br>".format(db.session.query(Task).count())

    stu = db_helper.query_student('openid1')
    org = db_helper.query_oraganization('openid1_o')
    html += "组织openid1_o发布的任务: {}.<br>".format(
        ', '.join(map(str, db_helper.get_publish_tasks(org.openid))))
    html += "学生openid1接收到任务: {}.<br>".format(
        db_helper.get_accept_tasks(stu.openid)[0].content)
    # 为什么content可以显示，但是上面的join就不行了？？？

    db_helper.delete(stu)
    html += "删除学生openid1后<br>"

    html += "There are {} accepts, ".format(db.session.query(Accept).count())
    html += "and there are {} tasks total.<br>".format(db.session.query(Task).count())

    html += "根据单词(word1)查询到的任务: {}.<br>".format(db_helper.search_task_by_text('word1'))
    html += "根据单词(word5)查询到的任务: {}.<br>".format(db_helper.search_task_by_text('word5'))
    html += "根据标签(tag2)查询到的任务: {}.<br>".format(db_helper.search_task_by_tag('tag2'))
    html += "根据标签(tag4)查询到的任务: {}.<br>".format(db_helper.search_task_by_tag('tag4'))
    return html


if __name__ == "__main__":
    app.run(port=5000, debug=True)

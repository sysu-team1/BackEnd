from config import make_pattern

from .Accept import Accept, random_accepts
from .Answer import Answer
from .Organization import Organization, random_orgs
from .prepare import ALL_TAGS, QUESTIONNAIRE_INDEX, model_repr
from .Problem import Problem
from .Student import Student, random_stus
from .Task import Task, random_tasks


def test_json():
    import time
    import datetime
    print(Student(openid=1000000, email='email1', password='password1'))
    print(Organization(openid=2, email='email2', password='password2'))
    print(Task(id=1, publish_id=2, publish_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), limit_num=10,
               title='title1', content='word1, word2', tag='tag1 tag2'))
    print(Problem(id=1, task_id=1, description='desc1',
                  all_answers='answer1;answer2;answer3'))
    print(Accept(accept_id=1000000, task_id=1, accept_time=datetime.datetime.now(),
                 finish_time='2020-01-01 00:00:00'))  # TODO now()
    print(Answer(accept_id=1, problem_id=1, answer='answer1'))


def test_normal_crud(db_helper):
    import random
    stus = random_stus(100)
    db_helper.save_all(stus)
    db_helper.commit()
    print('---------- 随机查询10位幸运学生(可能重复)')
    for _ in range(10):
        print(db_helper.query_student(openid=random.choice(stus).openid))

    orgs = random_orgs(10)
    db_helper.save_all(orgs)
    db_helper.commit()
    print('---------- 随机查询3个幸运组织(可能重复)')
    for _ in range(3):
        print(db_helper.query_oraganization(openid=random.choice(orgs).openid))

    tasks = random_tasks(50, orgs, stus, db_helper)
    print('---------- 查找某些任务的发布者(可能重复)')
    sample_tasks = random.sample(tasks, 10)
    for task in sample_tasks:
        print(task.id, task.publish_id, db_helper.get_publisher(task))
    print('---------- 根据时间查询10个幸运任务')
    query_tasks_by_time = db_helper.get_task()
    for task in query_tasks_by_time:
        print(task)
    print('---------- 根据时间与tag查询10个幸运任务')
    query_tasks_by_tag = db_helper.get_task_by_tag(search_tag='tag1')
    for task in query_tasks_by_tag:
        print(task)
    print('---------- 根据时间与text查询10个幸运任务')
    query_tasks_by_content = db_helper.get_task_by_text(search_text='word1')
    for task in query_tasks_by_content:
        print(task)
    print('---------- 查找某些表单')
    form_tasks = list(filter(lambda task: task.tag.find(
        ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1, tasks))
    sample_form_tasks = random.sample(form_tasks, min(10, len(form_tasks)))
    for task in sample_form_tasks:
        print(task)
        for problem in task.problems:
            print('\t', problem)
            # random_tasks 中没有将 problems 赋给 task ，但这里自动获取了，因为 relationship
    # 直接在 mysql 命令行中检查:
    # select * from tasks where publish_id not in (select openid from students union select openid from organizations);  -- 检查 publish_id 是否合法
    # select * from tasks where publish_time != '2000-01-01 00:00:00' and publish_time >= now(); -- 检查 publish_time 是否合法
    # select * from tasks where limit_time != '2000-01-01 00:00:00' and limit_time <= publish_time; -- 检查 limit_time 是否合法
    # select * from tasks where limit_num != -1 and limit_num < 1; -- 检查 limit_num 是否合法
    # select * from tasks where accept_num < 0 or accept_num > limit_num; -- 检查 accept_num 是否合法

    accepts = random_accepts(300, tasks, stus, db_helper)
    print('---------- 查找这些任务的接收者(可能重复)')
    sample_accepts = random.sample(accepts, 10)
    for accept in sample_accepts:
        print(accept, accept.student)
    print('---------- 查找某些表单的接受')
    form_accepts = list(filter(lambda accept: accept.tag.find(
        ALL_TAGS[QUESTIONNAIRE_INDEX]) != -1, accepts))
    sample_form_accepts = random.sample(
        form_accepts, min(10, len(form_accepts)))
    for accept in sample_form_accepts:
        print(accept)
        for answer in accept.answers:
            print('\t', answer)
    # 直接走 mysql 命令行中检查:
    # select * from accepts where accept_id not in (select openid from students); -- 检查 accept_id 是否合法
    # select * from accepts where task_id not in (select id from tasks); -- 检查 task_id 是否合法
    # select * from accepts where accept_time ??? -- 检查 accept_time 是否合法
    # select * from accepts where finish_time ??? -- 检查 finish_time 是否合法

    # 检查 problem TODO
    # 检查 answer TODO


""" def test_none():
    print('---------- stu._tasks && stu.get_tasks')
    stu = Student.query.filter(Student.openid == 1000000).one_or_none()
    print(stu, stu._tasks, stu.get_tasks()[0], sep='\n')
    print('---------- org._tasks && org.get_tasks')
    org = Organization.query.filter(Organization.openid == 1).one_or_none()
    print(org, org._tasks, org.get_tasks()[0], sep='\n')
    print('---------- task._publisher && task.get_publisher')
    task = Task.query.filter(Task.id == 1).one_or_none()
    print(task, task._publisher, task.get_publisher(), sep='\n')
    print('---------- test')
    print(stu._tasks[0], org._tasks[0], task._publisher, sep='\n') """


def test_time(db_helper, update_add_num):
    print('---------- 根据时间加载最新10条')
    orders = ['id', 'publish_time']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task()
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据时间加载后10条')
        tasks = db_helper.get_task(last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    print('---------- 根据tag加载最新10条')
    orders = ['id', 'publish_time', 'tag']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task_by_tag(ALL_TAGS[QUESTIONNAIRE_INDEX])
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据tag加载后10条')
        tasks = db_helper.get_task_by_tag(
            ALL_TAGS[QUESTIONNAIRE_INDEX], last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    print('---------- 根据text加载最新10条')
    orders = ['id', 'publish_time', 'title', 'content']
    patterns = make_pattern(len(orders))
    tasks = db_helper.get_task_by_text('word2')
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('---------- 根据text加载后10条')
        tasks = db_helper.get_task_by_text('word2', last_id=last_id)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('什么鬼！！！ something wrong happen')
        return
    else:
        print('not enough tasks')

    test_publish_task(db_helper.get_all_publish_tasks, 4, 6,
              '加载组织6发布的最新4条任务', '加载组织6发布的后4条任务')


def test_accetp_and_publish(db_helper, update_add_num):
    openid = 6
    update_add_num = 5
    test_publish_task(db_helper.get_all_publish_tasks, openid, update_add_num,
                     '加载组织{}发布的所有的最新{}条任务'.format(openid, update_add_num),
                     '加载组织{}发布的所有的后{}条任务'.format(openid, update_add_num))
    test_publish_task(db_helper.get_ongoing_publish_tasks, openid, update_add_num,
                     '加载组织{}发布的进行中的最新{}条任务'.format(openid, update_add_num),
                     '加载组织{}发布的进行中的后{}条任务'.format(openid, update_add_num))
    test_publish_task(db_helper.get_finished_publish_tasks, openid, update_add_num,
              '加载组织{}发布的已完成的最新{}条任务'.format(openid, update_add_num),
              '加载组织{}发布的已完成的后{}条任务'.format(openid, update_add_num))

    openid = 1000041
    update_add_num = 5
    test_accept_task(db_helper.get_all_accept_tasks, openid, update_add_num,
                     '加载学生{}接受的所有的最新{}条任务'.format(openid, update_add_num),
                     '加载学生{}接受的所有的后{}条任务'.format(openid, update_add_num))
    test_accept_task(db_helper.get_ongoing_accept_tasks, openid, update_add_num,
                     '加载学生{}接受的进行中的最新{}条任务'.format(openid, update_add_num),
                     '加载学生{}接受的进行中的后{}条任务'.format(openid, update_add_num))
    test_accept_task(db_helper.get_complete_accept_tasks, openid, update_add_num,
                     '加载学生{}接受的结束了的最新{}条任务'.format(openid, update_add_num),
                     '加载学生{}接受的结束了的后{}条任务'.format(openid, update_add_num))
    test_accept_task(db_helper.get_finished_accept_tasks, openid, update_add_num,
                     '加载学生{}接受的已完成的最新{}条任务'.format(openid, update_add_num),
                     '加载学生{}接受的已完成的后{}条任务'.format(openid, update_add_num))


def test_publish_task(method, openid, update_add_num, message1, message2):
    print('----------', message1)
    orders = ['id', 'publish_time', 'limit_time']
    patterns = make_pattern(len(orders))
    tasks = method(openid=openid, length=update_add_num)
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        last_id = tasks[-1].id
        print('----------', message2)
        tasks = method(openid=openid, last_id=last_id, length=update_add_num)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('---------- 什么鬼！！！ something wrong happen')
        return
    else:
        print('---------- not enough tasks')


def test_accept_task(method, openid, update_add_num, message1, message2):
    print('----------', message1)
    orders = ['id', 'publish_time', 'limit_time']
    patterns = make_pattern(len(orders))
    tasks, last_accept_time = method(openid=openid, length=update_add_num)
    for task in tasks:
        print(model_repr(task, patterns, orders))
    num_tasks = len(tasks)
    if num_tasks == update_add_num:
        print('----------', message2)
        tasks, last_accept_time = method(
            openid=openid, last_accept_time=last_accept_time, length=update_add_num)
        for task in tasks:
            print(model_repr(task, patterns, orders))
    elif num_tasks > update_add_num:
        print('---------- 什么鬼！！！ something wrong happen')
        return
    else:
        print('---------- not enough tasks')


def test_create_student_and_organization(db_helper):
    '''
    # 只产生学生与组织
    '''
    stus = random_stus(10)
    org = random_orgs(10)
    db_helper.save_all(stus)
    db_helper.save_all(org)
    db_helper.commit()


def test_some_methods(db_helper, app, update_add_num):
    # ---------- test save / query_student / query_oraganization / delete_all
    # stu = Student(email='liangyy75@qq.com', password='liangyy75@pass', student_id='16340134', name='liangyy75', sex='男', collage='数据科学与计算机学院', grade=2016, edu_bg='本科')
    # print(db_helper.save(stu))
    # print(db_helper.query_student(openid=stu.openid))
    # org = Organization(email='liangyy75@qq.com', password='liangyy75@pass', name='test org')
    # db_helper.save(org)
    # print(db_helper.query_oraganization(org.openid))
    # db_helper.delete(stu)
    # db_helper.delete_all([org])

    # ---------- test delete
    # print(db_helper.query_oraganization(openid=11))
    # db_helper.delete(db_helper.query_oraganization(openid=11))
    # print(db_helper.query_oraganization(openid=11))

    # ---------- test update_student_or_organization
    # print(db_helper.query_student(openid=app.config['SPLIT_STU_ORG'] + 10).sex)
    # print(db_helper.update_student_or_organization(
    #     app.config['SPLIT_STU_ORG'] + 10, 'sex', '男'))
    # print(db_helper.query_student(openid=app.config['SPLIT_STU_ORG'] + 10).sex)
    # print(db_helper.update_student_or_organization(
    #     app.config['SPLIT_STU_ORG'] + 10, 'sex', '女'))
    # print(db_helper.query_student(openid=app.config['SPLIT_STU_ORG'] + 10).sex)

    # ---------- test has_accept / get_recipient / sign_up_true / accept_task
    # recipients = db_helper.get_recipient(1, length=100)
    # print(len(recipients))
    # print(db_helper.has_accept(recipients[0].openid, 1))
    # print(db_helper.sign_up_true(email='liangyy75@qq2.com', password='liangyy75@pass2', student_id='16340134', sex='男', collage='数据科学与计算机学院', grade=2016, name='liangyy75'))
    # stu = Student.query.filter(Student.email == 'liangyy75@qq2.com').one_or_none()
    # print(db_helper.has_accept(stu.openid, 1))
    # print(db_helper.accept_task(stu.openid, 1))
    # print(len(db_helper.get_recipient(1, length=100)))
    # print(db_helper.has_accept(stu.openid, 1))
    # print(db_helper.delete(stu))
    # print(len(db_helper.get_recipient(1, length=100)))
    # print(db_helper.has_accept(stu.openid, 1))

    # ---------- test get_xxx_publish_task / get_xxx_accept_task / get_task_by_xxx
    # test_time(db_helper, update_add_num)
    # print('-' * 100)
    # test_accetp_and_publish(db_helper, update_add_num)

    # ---------- test get_publisher / get_recipient / get_all_problems / get_all_answers
    # print(db_helper.get_task_by_id(1))
    # print(db_helper.get_publisher(1))
    # print(db_helper.get_publisher(1) == db_helper.get_task_by_id(1).publisher)
    # print(len(db_helper.get_recipient(1, length=100)))
    # print(len(db_helper.get_all_problems(1).split('^')))
    # print(len(db_helper.get_all_answers(1)))
    # print(sum(map(lambda item: len(item), db_helper.get_all_answers(1))))

    # ---------- test finish_task / cancel_task / accept_task / has_accept
    # print(db_helper.sign_up_true(email='liangyy75@qq2.com', password='liangyy75@pass2', student_id='16340134', sex='男', collage='数据科学与计算机学院', grade=2016, name='liangyy75'))
    # stu = Student.query.filter(Student.email == 'liangyy75@qq2.com').one_or_none()
    # print(db_helper.cancel_task(stu.openid, 1))
    # print(db_helper.has_accept(stu.openid, 1))
    # print(db_helper.accept_task(stu.openid, 1))
    # print(db_helper.has_accept(stu.openid, 1))
    # print(Accept.query.filter(Accept.accept_id == stu.openid).filter(
    #     Accept.task_id == 1).one_or_none().finish_time)
    # print(db_helper.finish_task(stu.openid, 1))
    # print(Accept.query.filter(Accept.accept_id == stu.openid).filter(
    #     Accept.task_id == 1).one_or_none().finish_time)
    # db_helper.delete(stu)

    # ---------- test charge / carry_over / cash_in
    print(db_helper.query_oraganization(openid=1).cash)
    print(db_helper.charge(1, 1000))
    print(db_helper.query_oraganization(openid=1).cash)
    print(db_helper.query_student(openid=app.config['SPLIT_STU_ORG']).cash)
    print(db_helper.carry_over(source_id=1, target_id=app.config['SPLIT_STU_ORG'], money_num=1000))
    print(db_helper.query_student(openid=app.config['SPLIT_STU_ORG']).cash)
    print(db_helper.query_oraganization(openid=1).cash)

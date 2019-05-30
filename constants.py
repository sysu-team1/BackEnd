''' 存储常量
'''

'''
    code_element_list
    存储随机验证码的生成元素
''' 
code_element_list = []
# 添加0-9数字
for i in range(10):
    code_element_list.append(str(i))
# 添加A-Z数字
for i in range(65, 91):
    code_element_list.append(chr(i))
# 添加a-z数字
for i in range(97, 123):
    code_element_list.append(chr(i))
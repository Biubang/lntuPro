import configparser

from lxml import etree

from core.parser import LNTUParser
from core.spider import get_class_table, get_std_info
from core.urls import URLEnums, URLManager
from core.util import GetWeek


def test_url_utils():
    print(list(URLEnums))
    print(URLManager.get_all_urls())


def test_parse_week():
    courses = [
        ['"206427(H101730023056.01)"', '"信息系统分析与设计(H101730023056.01)"', '"4809"', '"静远楼239(辽宁工大葫芦岛校区)"',
         '"00111111111100000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"206427(H101730023056.01)"', '"信息系统分析与设计(H101730023056.01)"', '"4809"', '"静远楼239(辽宁工大葫芦岛校区)"',
         '"00111111111100000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"211848(H101730004040.01)"', '"会计学(H101730004040.01)"', '"4943"', '"静远楼238(辽宁工大葫芦岛校区)"',
         '"01010101010101000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"211848(H101730004040.01)"', '"会计学(H101730004040.01)"', '"4632"', '"尔雅楼107(辽宁工大葫芦岛校区)"',
         '"01111111111111000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"214040(H101750028056.01)"', '"信息系统项目管理(H101750028056.01)"', '"4812"', '"静远楼242(辽宁工大葫芦岛校区)"',
         '"01111111111000000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"214040(H101750028056.01)"', '"信息系统项目管理(H101750028056.01)"', '"4812"', '"静远楼242(辽宁工大葫芦岛校区)"',
         '"01111111111000000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"209061(H101750041048.01)"', '"统计机器学习(H101750041048.01)"', '"4809"', '"静远楼239(辽宁工大葫芦岛校区)"',
         '"01111111111100000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"209061(H101750041048.01)"', '"统计机器学习(H101750041048.01)"', '"4809"', '"静远楼239(辽宁工大葫芦岛校区)"',
         '"00101010101000000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"210072(H101750042048.01)"', '"大数据开发技术(H101750042048.01)"', '"4812"', '"静远楼242(辽宁工大葫芦岛校区)"',
         '"01010101010101000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""'],
        ['"210072(H101750042048.01)"', '"大数据开发技术(H101750042048.01)"', '"4812"', '"静远楼242(辽宁工大葫芦岛校区)"',
         '"01111111111111000000000000000000000000000000000000000"', 'null', 'null', 'assistantName', '""',
         '""']]
    [
        print(F"{course[1]}-{GetWeek().marshal(course[4], 3, 1, 100)}")
        for course in courses
    ]


def test_parse_stu_info():
    with open('testHTML/stu-info.html', 'r') as fp:
        html_text = fp.read()
        html_doc = etree.HTML(html_text)
    results = LNTUParser.parse_std_info(html_doc)
    print(results)


def test_parse_class_table():
    with open('testHTML/class-table.html', 'r') as fp:
        html_text = fp.read()
        html_doc = etree.HTML(html_text)
    all_course_dict = LNTUParser.parse_class_table_bottom(html_doc=html_doc)
    # print(all_course_dict)
    results = LNTUParser.parse_class_table_body(html_text=html_text, all_course_dict=all_course_dict)
    print(results)
    return results


def test_parse_all_scores():
    with open('testHTML/scores.html', 'r') as fp:
        html_text = fp.read()
        html_doc = etree.HTML(html_text)
    results = LNTUParser.parse_all_scores(html_doc=html_doc)
    # print(all_course_dict)
    # results = LNTUParser.parse_class_table_body(html_text=html_text, all_course_dict=all_course_dict)
    print(results)
    return results


def test_parse_all_GPAs():
    with open('testHTML/scores.html', 'r') as fp:
        html_text = fp.read()
        html_doc = etree.HTML(html_text)
    results = LNTUParser.parse_all_GPAs(html_doc=html_doc)
    return results


def test_login(username, password):
    get_std_info(username, password)
    get_class_table(username, password)


def load_account():
    config_path = 'static/config.ini'
    config = configparser.ConfigParser()
    config.read(config_path)
    # print(config.sections())
    for key in config.sections():
        if key == 'account':
            return config.items(key)


if __name__ == '__main__':
    try:
        accounts = load_account()
        for each in accounts:
            username, password = each[0], each[1]
            test_login(username, password)
            # print(username, password)
            # test_parse_week()
            # test_parse_stu_info()
            # test_parse_class_table()
            # test_parse_all_scores()
            # test_parse_all_GPAs()
    except Exception as e:
        print(e)

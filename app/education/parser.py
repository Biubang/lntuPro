import parse
from sentry_sdk import capture_exception

from app import schemas
from app.education.utils import GetWeek


def parse_stu_info(username, html_doc) -> schemas.UserInfo:
    info = schemas.UserInfo(username=username)

    # 个人基本信息
    basic_info_keys = ['username', 'name', 'photoURL', 'nickname', 'gender', 'grade', 'educationLast', 'project',
                       'education', 'studentType', 'college', 'major', 'direction', 'enrollDate', 'graduateDate',
                       'chiefCollege', 'studyType', 'membership', 'isInSchool', 'campus', 'majorClass', 'effectAt',
                       'isInRecord', 'studentStatus', 'isWorking']
    basic_info_values = []
    try:
        rows = html_doc.xpath('/html/body/div[1]/div[2]/div[@id="tabPage1"]/table/tr')
        for row in rows[1:-1]:
            for td in row.xpath('./td[not(@class="title")]'):
                basic_info_values.append(str(td.text))
        else:
            data = dict(zip(basic_info_keys, basic_info_values))
            info = schemas.UserInfo(**data)
            info.photoURL = f"/eams/showSelfAvatar.action?user.name={data.get('username', 'None')}"
    except Exception as e:
        capture_exception(e)

    # 联系信息、火车站
    try:
        home_data = html_doc.xpath('/html/body/div[1]/div[2]/div[@id="tabPage3"]/table[1]')[0]
        info.address = home_data.xpath('./tr[2]/td[4]/text()')[0]
        info.train = home_data.xpath('./tr[3]/td[4]/text()')[0]
    except Exception as e:
        capture_exception(e)
    return info


def parse_course_table_bottom(html_doc) -> [schemas.CourseTable]:
    course_list: [schemas.CourseTable] = []
    rows = html_doc.xpath('//*[@id="tasklesson"]/div/table/tbody/tr')
    for row in rows:
        try:
            cells = row.xpath('./td')
            if not len(cells):  # 处理课表为空的情况（可能是学期字段错误）
                continue
            data_row = ["".join(cell.xpath('string(.)').split()) for cell in cells[2:-2]]
            """['大数据开发技术', '3', 'H101750042048.01', '杨韬']"""
            single_course_dict = {
                'code': data_row[2],
                'name': data_row[0],
                'credit': data_row[1],
                'teacher': data_row[3],
            }
            course_list.append(schemas.CourseTable(**single_course_dict))
        except Exception as e:
            capture_exception(e)
    return course_list


def parse_course_table_body(html_text, course_dict_list: [schemas.CourseTable]) -> [schemas.CourseTable]:
    def decrypt_week(week: str) -> schemas.CourseTableSchedule:
        """"
            转换周为列表：
            单 1-9 -> [1, 3, 5, 7, 9]
            双 2-10 -> [2, 4, 6, 8, 10]
            2-15 -> [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        week: 00001111111100000000000000000000000000000000000000000
        """
        schedule = schemas.CourseTableSchedule()
        tmp_room = info_result.get('room')
        if '（' in tmp_room:
            schedule.room = tmp_room.rsplit('（', maxsplit=1)[1].replace('）', '')
        else:
            schedule.room = tmp_room

        if not week.isdigit():
            return schedule
        tmp_weeks = GetWeek().marshal(week, 2, 1, 26)
        schedule.weeksString = tmp_weeks
        for each in tmp_weeks.split(' '):
            if ('单' in each) or ('双' in each):  # '单1-9' or '双2-10'
                start_week, end_week = map(int, each[1:].split('-'))
                schedule.weeks.extend(list(range(start_week, end_week + 1, 2)))
            elif '-' in each:  # '2-15'
                start_week, end_week = map(int, each.split('-'))
                schedule.weeks.extend(list(range(start_week, end_week + 1)))
            elif each != '':
                schedule.weeks.extend([int(each)])
            else:  # ''
                pass
        return schedule

    try:
        # 使最后一个课程的索引上下文符合 parse模式
        cleaned_course_content_text = html_text.replace('table0.marshalTable',
                                                        'var teachers; activity = new TaskActivity')
        tmp_course_list = cleaned_course_content_text.split('activity = new TaskActivity')
        for tmp_course in tmp_course_list[1:-1]:  # 去除垃圾数据(非 activity = new TaskActivity 部分)
            course_pattern = """(actTeacherId.join({}),actTeacherName.join({}),{},"{name}({code})","{room_id}","{room}","{encrypted_week}",null,null,assistantName,{course_content},{},{});{time}var teachers"""
            course_result_list = parse.findall(course_pattern, tmp_course)

            for course in course_result_list:
                # 解析基本信息: function TaskActivity(teacherId,teacherName,courseId,courseName,roomId,roomName,vaildWeeks,taskId,remark,assistantName,experiItemName,schGroupNo){"""
                info_result = course.named

                # 解析课程时间
                original_schedule = course.named['time']
                schedule_pattern_str = 'index ={:d}*unitCount+{:d};'
                # index =1*unitCount+6; -> 意味着 [周二第七小节]
                schedule_all_result = parse.findall(schedule_pattern_str, original_schedule)
                schedule_day_index_tuple_list = [tuple(map(lambda x: x + 1, each)) for each in
                                                 schedule_all_result]  # [(2, 3),(2, 4)] 周二第三、四小节

                info_result['encrypted_week'] = str(info_result.get('encrypted_week'))

                schedule_list = []
                for (day, index) in schedule_day_index_tuple_list:
                    schedule = decrypt_week(info_result.get('encrypted_week'))
                    if index % 2 == 0:  # 抛弃偶数节课方便转换为大节课，TODO 可能有单节偶数小课的 bug
                        continue
                    odd_index = index
                    schedule.weekday = day
                    schedule.index = odd_index - (odd_index // 2)  # 小节课转大节课（十节课转五节课）
                    schedule_list.append(schedule)

                for i in schedule_list:
                    [course.scheduleList.append(i) for course in course_dict_list if
                     info_result.get('code') == course.code]
    except Exception as e:
        capture_exception(e)
    return course_dict_list


def parse_grade_table(html_doc) -> [schemas.GradeTable]:
    course_grade_list: [schemas.GradeTable] = []
    rows = html_doc.xpath('/html/body/table[2]/tr')
    cells_element = []
    cells = []
    try:
        for row in rows[1:]:
            cells_element.append(row[:4])
            if row[-1].text != '\xa0':
                # 处理一行多个成绩的情况
                cells_element.append(row[4:])
        for tr in cells_element:
            tmp_course_grade_info = []
            for td in tr:
                tmp_course_grade_info.append(td.text)
            course_grade_style = tr[2].xpath('./@style')
            # 重修、补考、正常 元素的样式不同:
            # 斜线为补考成绩: ['font-style:italic; ']
            # 下划线为重新学习成绩: ['text-decoration:underline; ']
            if len(course_grade_style) != 0:
                course_grade_style = course_grade_style[0]
                course_grade_style = schemas.GradeTable.CourseStatusEnum.reStudy if (
                        'underline' in course_grade_style) else schemas.GradeTable.CourseStatusEnum.makeUp
            else:
                course_grade_style = schemas.GradeTable.CourseStatusEnum.normal
            tmp_course_grade_info.append(course_grade_style)
            cells.append(tmp_course_grade_info)
        for each in cells:
            # each: ['数据结构与算法分析', '4', '95', '2018-2019(1)', '重修']
            course_grade_table = schemas.GradeTable(name=each[0])
            course_grade_table.credit = each[1]
            course_grade_table.result = each[2]
            course_grade_table.semester = each[3]
            course_grade_table.status = each[4]
            course_grade_list.append(course_grade_table)
    except Exception as e:
        capture_exception(e)
    return course_grade_list


def parse_grade(html_doc) -> [schemas.CourseTable]:
    course_list: [schemas.CourseTable] = []
    score_table_rows = html_doc.xpath('/html/body/div[@class="grid"]/table/tbody/tr')
    for row in score_table_rows:
        cells = []
        for td in row:
            cells.append(''.join(td.xpath('string(.)').split()))
        if len(cells) == 0:
            continue
        try:
            # cells: ['2019-20202', 'H101730023056', 'H101730023056.01', '信息系统分析与设计', '专业必修', '3.5', '95', '94', '89', '93.3', '93.3', '4', '查卷申请']
            course = schemas.Grade(name=cells[3], code=cells[2])
            # 转换学期：2019-20202 -> 2020-春
            semester_start_year = int(cells[0].split('-')[0])
            if cells[0][-1] == '1':
                course.semester = f'{semester_start_year}-秋'
            else:
                course.semester = f'{semester_start_year + 1}-春'
            course.courseType = cells[4]
            course.credit = cells[5]
            course.midTerm = cells[6]
            course.endTerm = cells[7]
            course.usual = cells[8]
            # 有无 [补考记录] 导致总评成绩(totalScore)和最终成绩(result)不一样
            course.totalScore = cells[-4]
            course.result = cells[-3]
            course.point = cells[-2]
            if '补考' in course.name:  # 有无 [补考记录] 导致页面结构不一样
                course.status = schemas.GradeTable.CourseStatusEnum.makeUp.value
                course.makeUpScore = cells[-6]
                course.makeUpScoreResult = cells[-5]
            elif '重学' in course.name:
                course.status = schemas.GradeTable.CourseStatusEnum.reStudy.value
            else:
                course.status = schemas.GradeTable.CourseStatusEnum.normal
            course_list.append(course)
        except Exception as e:
            capture_exception(e)
    return course_list


def parse_exam(html_doc) -> [schemas.Exam]:
    exam_list: [schemas.Exam] = []
    rows = html_doc.xpath('/html/body/div[@class="grid"]/table/tbody/tr')
    for row in rows:  # 处理每一行
        data_row = []
        for td in row:
            data_row.append(''.join(td.xpath('string(.)').split()))
        if len(data_row) == 0:
            continue
        try:
            exam = schemas.Exam(code=data_row[0])
            exam.name = data_row[1]
            exam.type = data_row[2]
            exam.date = data_row[3]
            exam.time = data_row[4]
            exam.location = data_row[5]
            exam.seatNumber = data_row[-3] if data_row[-3].isdigit() else '未知'  # 期末评教阶段，座位号会被隐藏
            exam.status = data_row[-2]
            exam.comment = data_row[-1]
            exam_list.append(exam)
        except Exception as e:
            capture_exception(e)
    return exam_list


def parse_exam_id(html_doc) -> dict:
    batch_id_dict = {}
    batch_id_option_list = html_doc.xpath('//*[@id="examBatchId"]/option')
    if len(batch_id_option_list) == 0:
        return batch_id_option_list
    else:
        for exam in batch_id_option_list:
            exam_type = exam.text
            exam_id = exam.xpath('./@value')[0]
            batch_id_dict[exam_type] = exam_id
    return batch_id_dict


def parse_plan(html_doc) -> [schemas.PlanGroup]:
    plan_group_list: [schemas.PlanGroup] = []
    rows = html_doc.xpath('/html/body/div/table/tr')
    plan_group = schemas.PlanGroup()
    for row in rows[1:]:  # 跳过表头，处理每一行
        data_row = []
        for td in row:
            data_row.append(''.join(td.xpath('string(.)').split()))
        try:
            if len(data_row) == 0:  # 当前行数据为空
                continue
            elif len(data_row) == 6:  # 当前行数据是培养方案组
                plan_group = schemas.PlanGroup()
                for i in list('一二三四五六七八九十'):
                    data_row[0] = data_row[0].replace(i, '')
                plan_group.type = data_row[0]
                plan_group.creditRequired = data_row[1]
                plan_group.creditGained = data_row[2]
                plan_group.result = data_row[3]
                plan_group.status = data_row[4]
                plan_group.comment = data_row[5]
                plan_group_list.append(plan_group)
            else:  # 当前行数据是培养方案组中的单个课程
                plan = schemas.Plan(code=data_row[1])
                plan.id = data_row[0]
                plan.name = data_row[-6]
                plan.creditRequired = data_row[-5]
                plan.creditGained = data_row[-4]
                plan.result = data_row[-3]
                plan.status = data_row[-2]
                plan.comment = data_row[-1]
                plan.type = plan_group.type
                plan_group.courseList.append(plan)
        except Exception as e:
            capture_exception(e)
    return plan_group_list


def parse_other_exam(html_doc) -> [schemas.OtherExam]:
    other_exam_list: [schemas.OtherExam] = []
    rows = html_doc.xpath('/html/body/form/div[@class="grid"]/table/tbody/tr')
    for row in rows:  # 处理每一行
        data_row = []
        for td in row:
            data_row.append(''.join(td.xpath('string(.)').split()))
        if len(data_row) == 0:
            continue
        try:
            exam = schemas.OtherExam(name=data_row[0])
            exam.result = data_row[1]
            exam.status = data_row[2]
            exam.semester = data_row[3]
            other_exam_list.append(exam)
        except Exception as e:
            capture_exception(e)
    return other_exam_list


def parse_teacher_evaluation(html_doc) -> [schemas.TeacherEvaluationResponse]:
    evaluation_list: [schemas.TeacherEvaluationResponse] = []
    rows = html_doc.xpath('/html/body/div[@class="grid"]/table/tbody/tr')
    for row in rows:  # 处理每一行
        data_row = []
        for td in row:
            data_row.append(''.join(td.xpath('string(.)').split()))
        if len(data_row) == 0:
            continue
        try:
            evaluation = schemas.TeacherEvaluationResponse(code=data_row[0])
            evaluation.name = data_row[1]
            evaluation.teacher = data_row[3]
            evaluation.status = '未完成评教' if ('进行评教' in data_row[-1]) else data_row[-1]
            tmp_id_info = row.xpath('./td/a/@href')
            for each in tmp_id_info:
                evaluation.id = each.split('=')[1]
            evaluation_list.append(evaluation)
        except Exception as e:
            capture_exception(e)
    return evaluation_list

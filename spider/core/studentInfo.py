from lxml import etree

from spider.utils.UrlEnums import UrlEnums
from web.models import StudentInfo


def studentInfo_get_html(session):
    url = UrlEnums.STUDENT_INFO
    response = session.get(url)
    return etree.HTML(response.text)


def studentInfo_parser(html_doc, user):
    try:
        student = StudentInfo.objects.get_or_create(number=user)[0]
        table = html_doc.xpath('/html/body/center/table[1]')[0]
        student.number = table.xpath('tr[1]/td[1]')[0].text.strip()
        student.citizenship = table.xpath('tr[1]/td[2]')[0].text.strip()
        student.name = table.xpath('tr[2]/td[1]')[0].text.strip()
        student.native_from = table.xpath('tr[2]/td[2]')[0].text.strip()
        student.foreign_name = table.xpath('tr[3]/td[1]')[0].text.strip()
        student.birthday = table.xpath('tr[3]/td[2]')[0].text.strip()
        student.card_kind = table.xpath('tr[4]/td[1]')[0].text.strip()
        student.politics = table.xpath('tr[4]/td[1]')[0].text.strip()
        student.ID_number = table.xpath('tr[5]/td[1]')[0].text.strip()
        student.section = table.xpath('tr[5]/td[2]')[0].text.strip()
        student.gender = table.xpath('tr[6]/td[1]')[0].text.strip()
        student.nation = table.xpath('tr[6]/td[2]')[0].text.strip()
        student.academy = table.xpath('tr[7]/td[1]')[0].text.strip()
        student.major = table.xpath('tr[7]/td[2]')[0].text.strip()
        student.class_number = table.xpath('tr[8]/td[1]')[0].text.strip()
        student.category = table.xpath('tr[8]/td[2]')[0].text.strip()
        student.province = table.xpath('tr[9]/td[1]')[0].text.strip()
        student.score = table.xpath('tr[9]/td[2]')[0].text.strip()
        student.exam_number = table.xpath('tr[10]/td[1]')[0].text.strip()
        student.graduate_from = table.xpath('tr[10]/td[2]')[0].text.strip()
        student.foreign_language = table.xpath('tr[11]/td[1]')[0].text.strip()
        student.enroll_number = table.xpath('tr[11]/td[2]')[0].text.strip()
        student.enroll_at = table.xpath('tr[12]/td[1]')[0].text.strip()
        student.enroll_method = table.xpath('tr[12]/td[2]')[0].text.strip()
        student.graduate_at = table.xpath('tr[13]/td[1]')[0].text.strip()
        student.train_method = table.xpath('tr[13]/td[2]')[0].text.strip()
        student.address = table.xpath('tr[14]/td[1]')[0].text.strip()
        student.zip = table.xpath('tr[14]/td[2]')[0].text.strip()
        student.phone = table.xpath('tr[15]/td[1]')[0].text.strip()
        student.email = table.xpath('tr[15]/td[2]')[0].text.strip()
        student.roll_number = table.xpath('tr[16]/td[1]')[0].text.strip()
        student.source_from = table.xpath('tr[16]/td[2]')[0].text.strip()
        student.graduate_to = table.xpath('tr[17]/td[1]')[0].text.strip()
        student.comment = table.xpath('tr[18]/td[1]')[0].text
        student.img_url = "http://202.199.224.121:11180/newacademic/manager/studentinfo/photo/photo/{}.jpg".format(
            student.number)
        student.save()
        return True
    except Exception as e:
        print(e.with_traceback())
        return False
import datetime
from typing import Union, List

from pydantic import BaseModel

from app.exceptions import StatusCodeEnum


class ResponseT(BaseModel):
    code: StatusCodeEnum = StatusCodeEnum.SUCCESS
    message: str = "success"
    data: Union[list, dict] = []


class User(BaseModel):
    username: int
    password: str

    class Config:
        orm_mode = True


# Notice
class NoticeDetail(BaseModel):
    class NoticeDetailAppendix(BaseModel):
        url: str
        name: str

    title: str = None
    date: str = None
    content: str = None
    appendix: List[NoticeDetailAppendix] = []


class Notice(NoticeDetail):
    url: str


# ClassRoom
class ClassRoom(BaseModel):
    name: str = None
    # building_id: int = -1
    capacity: int = -1
    category: str = None  # TODO 多媒体教室	语音室	专用教室
    week: int = -1
    monday: str = None
    tuesday: str = None
    wednesday: str = None
    thursday: str = None
    friday: str = None
    saturday: str = None
    sunday: str = None
    # updated_at = models.DateTimeField(auto_now=True)


class ClassTableCourseSchedule(BaseModel):
    room: str = None
    weeks: Union[list, None] = []
    weekday: int = None
    index: int = None


class ClassTableCourse(BaseModel):
    code: str
    name: str = None
    teacher: str = None
    credit: str = None
    schedules: List[ClassTableCourseSchedule] = []

    def self_dict(self):
        return self.dict()


class UserInfo(BaseModel):
    username: int
    name: str
    photoUrl: str = None
    nickname: str = None
    gender: str = None
    grade: str = None
    educationLast: str = None
    project: str = None
    education: str = None
    studentType: str = None
    college: str = None
    major: str = None
    direction: str = None
    enrollDate: datetime.date = None
    graduateDate: datetime.date = None
    chiefCollege: str = None
    studyType: str = None
    membership: str = None
    isInSchool: str = None
    campus: str = None
    majorClass: str = None
    effectAt: str = None
    isInRecord: str = None
    studentStatus: str = None
    isWorking: str = None


class Grade(BaseModel):
    code: str = None
    name: str = None
    semester: str = None
    courseType: str = None
    grade: str = None
    credit: str = None
    usual: str = None
    midterm: str = None
    termEnd: str = None
    score: str = None


class GradeTable(BaseModel):
    name: str
    credit: str = None
    score: str = None
    semester: str = None


# GPA
class GPA(BaseModel):
    semester: str = "1999-1"
    gradePointAverage: float = 0.0
    weightedAverage: float = 0.0
    gradePointTotal: float = 0.0
    scoreTotal: float = 0.0
    creditTotal: float = 0.0
    courseCount: int = 0

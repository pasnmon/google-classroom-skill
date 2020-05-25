from datetime import datetime, date, timedelta

import pickle
import os.path

# Mycroft
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler

# Google
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.coursework.me']


def create_auth():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        # If there are no (valid) credentials available, let the user log in.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)


def get_date(due_date):
    if not due_date:
        return False
    datetime_string = "{}-{}-{}".format(
        due_date.get("year"),
        due_date.get("month"),
        due_date.get("day"),
    )
    return datetime.strptime(datetime_string, "%Y-%m-%d")


def build_date(day):
    """
    Returns the date object of the string
    :param day: String
    :return date object
    """
    if day == "tomorrow":
        return date.today() + timedelta(days=1)
    if day == "yesterday":
        return date.today() - timedelta(days=1)
    return date.today()


class GoogleClassroomSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.connection = None

    def initialize(self):
        self.connect()

    def connect(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        else:
            self.speak_dialog('classroom.google.setting.auth')
            return
        if not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                self.speak_dialog('classroom.google.setting.auth')
                return

        self.connection = build('classroom', 'v1', credentials=creds)
        return self.connection

    @intent_file_handler('google.classroom.news.intent')
    def handle_news_intent(self, message):
        courses = self.connection.courses.list().execute()
        day = date.today()
        new_course = []
        new_cw = []
        for course in courses:
            if day == get_date(course.get("createDay")):
                new_course.append(course)
            course_works = self.connection.courses().courseWork().list(courseId=course.google_id).execute()
            new_cw += [cw for cw in course_works if day == get_date(cw.get("createDate"))]
        self.speak_dialog('google.classroom.news.dialog', {
            'number': len(new_course) or 'no', 'number': len(new_cw) or 'no'
        })

    @intent_file_handler(IntentBuilder('google.classroom.due.intent').require('day'))
    def handel_due_intent(self, message):
        courses = self.connection.courses.list().execute()
        day_str = message.data.get('day')
        day = build_date(day_str)
        cw_to_notify = []
        for course in courses:
            course_works = self.connection.courses().courseWork().list(courseId=course.google_id).execute()
            cw_to_notify += [cw for cw in course_works if day == get_date(cw.get("dueDate"))]
        if cw_to_notify:
            self.speak_dialog('google.classroom.due.dialog', {'day': day_str, 'number': len(cw_to_notify)})
        else:
            self.speak_dialog('google.classroom.nothing.due.dialog', {'day': day_str})


def create_skill():
    return GoogleClassroomSkill()


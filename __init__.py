from mycroft import MycroftSkill, intent_file_handler
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, date, timedelta
import inflect

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


def get_due_date(due_date, due_time):
    if not due_date:
        return False
    if due_date and due_time.get("hours") and due_time.get("minutes"):
        datetimeString = "{}-{}-{}T{}:{}".format(
            due_date.get("year"),
            due_date.get("month"),
            due_date.get("day"),
            due_time.get("hours"),
            due_time.get("minutes")
        )
        return datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M")

    datetimeString = "{}-{}-{}".format(
        due_date.get("year"),
        due_date.get("month"),
        due_date.get("day"),
    )
    return datetime.strptime(datetimeString, "%Y-%m-%d")

def build_date(day,day_num,month,year):
    sug_date = None
    if day:
        if day == "today":
            sug_date = date.today()
        elif day == "yesterday":
            sug_date = date.today() - timedelta(days=1)
        elif day == "tomorrow":
            sug_date = date.today() + timedelta(days=1)
        return sug_date
    if day_num and month:
        inf = inflect.engine()
        num = inf.

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
    def handle_classroom_google(self, message):
        self.speak_dialog('classroom.google')

    @intent_file_handler('google.classroom.due.intent')
    def handel_due_intent(self, message, connection):
        courses = self.connection.courses.list().execute()
        day = message.data.get('day')
        year = message.data.get('year')
        day_num = message.data.get('day_num')
        month = message.data.get('month')
        for course in courses:
            course_works = self.connection.courses().courseWork().list(courseId=course.google_id).execute()
            for cw in course_works:

def create_skill():
    return GoogleClassroomSkill()


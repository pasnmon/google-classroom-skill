from mycroft import MycroftSkill, intent_file_handler


class GoogleClassroom(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('classroom.google.intent')
    def handle_classroom_google(self, message):
        self.speak_dialog('classroom.google')


def create_skill():
    return GoogleClassroom()


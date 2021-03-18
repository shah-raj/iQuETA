from flask import session
class userType:
    def __init__(self,type=None):
        self._type = type
    
    def get_type(self):
        return self._type
    
    def setTypeToTeacher(self):
        self._type = "teacher"
    
    def setTypeToStudent(self):
        self._type = "student"
    
    def isStudent(self):
        if self._type == "student":
            return True
        return False
    
    def isTeacher(self):
        if self._type == "teacher":
            return True
        return False

currentUserType = userType()
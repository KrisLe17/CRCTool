from DBModule.database import mysql_database
from DBModule.obfuscate import hash_pass


class User():
    def __init__(self, user_name=None, pwd=None, id=None):
        db = mysql_database('credentials.yaml')
        self.id = None
        self.name = None
        self.pwd = None
        self.stored_pwd = None
        self.admin = False
        try:
            if user_name != None:
                user_record = db.get_records_by_value("user", "user_name", user_name)[0]
            else:
                user_record = db.get_records_by_value("user", "user_id", id)[0]
            self.id = user_record["user_id"]
            self.name = user_record["user_name"]
            self.stored_pwd = user_record["user_pwd"]
            self.pwd = pwd
            self.admin = user_record["user_admin"]
        except:
            pass
           
    
    def is_authenticated(self):
        if self.id != None and hash_pass.check_pass(self.stored_pwd, self.pwd):
            return True
        return False

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False      

    def is_admin(self):
        return self.admin    

    def get_id(self):         
        return str(self.id)
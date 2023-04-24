# Form object
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, DateField, TimeField, IntegerField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from datetime import date
from werkzeug.utils import secure_filename

class MaintenanceForm(FlaskForm):
    """Maintenance Request Form"""
    hosts = StringField(
        'Input Hosts for Maintenance'
    )
    files = FileField(
        'Browse...'
    )

    date = DateField(
        'Maintenance Date',
        [DataRequired("Please Enter a Valid Start Date")]
    )

    time = TimeField(
        'Start Time (Central US)',
        [DataRequired("Please Enter a Valid Start Time")]
    )

    duration = IntegerField(
        'Duration',
        [DataRequired("Please Enter a Positive Whole Number")]
    )

    
    def validate_hosts(form, field):
        print(field.data, flush=True)
    
    def validate_files(form, field):
        print("file field is ", field.data, ".", flush=True)
        ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
        file = field.data
        if file:
            filename = secure_filename(file.filename)
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                raise ValidationError("File Type Not Allowed")
            
    def validate_date(form, field):
        if field.data < date.today():
            raise ValidationError("Date Cannot Be in the Past!")
    
    def validate_duration(form, field):
        test = str(field.data)
        if '.' in test:
            raise ValidationError("Please Enter a Positive Whole Number")
        if field.data < 0:
            raise ValidationError("Please Enter a Positive Whole Number")
        
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if not (self.hosts.data or self.files.data):
                self.hosts.errors.append("Please Enter Comma-Separated Host Names")
                self.files.errors.append("Or Upload a File")
                return False
            else:
                return True
        return False


class LoginForm(FlaskForm):
    """Login Request Form"""
    username = StringField(
        'Username',
        [DataRequired()]
    )
    password = PasswordField(
        'Password',
        [DataRequired()]
    )

class LookupForm(FlaskForm):
    """Monitor Lookup Form"""
    hosts = StringField(
        'Find Host',
        [DataRequired("Please Enter a Single Host Name For Lookup")]
    )

    
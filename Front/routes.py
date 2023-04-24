from flask import (
    Flask,
    url_for,
    render_template,
    redirect,
    request
)
import pandas as pd
from forms import MaintenanceForm, LookupForm
import Back.nagiosmaintenance as nagios
import Back.site24maintenance as site24
import Back.lookup as dblookup
from werkzeug.utils import secure_filename
import logging


UPLOAD_FOLDER = '/uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('config.DevConfig')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

##### Logging #####
logging.basicConfig(filename="maintlog.log", format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

def is_csv(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() == 'csv'

@app.route('/', methods= ['GET', 'POST'])
def maint():
    unfound_string = ""
    form = MaintenanceForm()
    username = request.environ.get('REMOTE_USER')
    # logger.info("User logged in: " + username)

    if form.validate_on_submit():
        file = form.files.data
        host_names = []
        if file:
            filename = secure_filename(file.filename)
            if is_csv(filename):
                host_names = (pd.read_csv(file, header=None).iloc[:, 0]).tolist()
            else:
                host_names = (pd.read_excel(file, header=None).iloc[:, 0]).tolist()
        hosts = list(form.hosts.data.split(','))
        while '' in hosts:
            hosts.remove('')
        hosts = [host.strip().lower() for host in hosts] #remove leading and trailing spaces from the string split...
        hosts = set(hosts + host_names)
        username = "Testing"
        results = nagios.nagios_maintenance(hosts, form.date.data, form.time.data, form.duration.data)
        multiple_results = results[1]
        results = site24.site24_maintenance(results[0], form.date.data, form.time.data, form.duration.data, username)
        print(results, flush=True)
        unfound_string = ""
        multiple_string = ""
        for host in results[0]:
            unfound_string += host + ","
            hosts.remove(host) # we'll use the host list minus the unfound hosts to track which were placed in maint
        for host in results[1]:
            multiple_string += host + ","
        for host in multiple_results:
            multiple_string += host + ","
        # logger.info("Maintenance was set by " + username + " for Hosts: " + str(hosts) + ". Maint Date: " + str(form.date.data) + " : " + str(form.time.data) + " for " + str(form.duration.data) + " minutes ")
        unfound_string = unfound_string[:-1] #Get rid of trailing ,
        multiple_string = multiple_string[:-1]
        return redirect(url_for("result", unfound=unfound_string, multiple=multiple_string))

    #it didn't validate, or this is the first time loading.
    return render_template(
        "index.html",
        form=form,
        template="form-template"
    )

@app.route('/lookup', methods= ['GET', 'POST'])
def lookup():
    form = LookupForm()

    if form.validate_on_submit():
        host_names = form.hosts.data
        return redirect(url_for("found", host_names=host_names))

    #it didn't validate, or this is the first time loading.
    return render_template(
        "lookup.html",
        form=form,
        template="form-template"
    )

@app.route('/found/', methods=['GET'])
def found():
    hosts = request.args.get('host_names', [])
    host_names = list(hosts.split(','))
    host_names = [host.strip().lower() for host in host_names] #remove leading and trailing spaces from the string split...
    info = dblookup.lookup(host_names)
    return(render_template("host_info.html", info=info))

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     error = None
#     username = request.environ.get('REMOTE_USER')
#     logger.info("User logged in: " + username)
#     if request.method == 'POST':
#         user = User(user_name=form.username.data, pwd=form.password.data)
#         #print("user is ", user, flush=True)
#         if user.is_authenticated():
#             login_user(user)
#             return redirect(url_for('maint'))
#         else:
#             error = 'Invalid Credentials. Please try again.'
#             logger.warning("Login Failed for User: " + form.username.data)
#     return render_template('login.html', error=error, form=form)

@app.route('/result/', methods= ['GET'])
def result():
    unfound = request.args.get('unfound', [])
    if unfound:
        unfound = unfound.split(',')
    print("result", unfound, flush=True)
    multiple = request.args.get('multiple', [])
    if multiple:
        multiple = multiple.split(',')
    print("multiple", multiple, flush=True)
    return render_template("result.html", result = unfound, multiple = multiple)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# @login_manager.user_loader
# def load_user(user_id):
#     return User(id=user_id)

if __name__ == '__main__':
   app.run(debug=True)
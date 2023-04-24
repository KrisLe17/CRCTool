import urllib3 # ignore silly warnings about insecure requests to Nagios API
from NagiosModule.agios import Agios
import os.path
import inspect
from NagiosModule.nagiosconfiguration import Configuration
from DBModule.database import mysql_database

#### TODO: optimize by removing gets? try just posting to every board with full list of hosts?
#### Configure the Nagios Instances ####
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
basedir = os.path.dirname(inspect.getfile(Configuration))
config = Configuration(os.path.join(basedir, 'nagiosconfig.yaml'))

def nagios_maintenance(hosts, start_date, start_time, duration):
    db = mysql_database('crcdb.yaml')

    board_configs = config.get_board_configs()

    # This is where we'll store our boards (agios instances)
    boards = []

    # Take information we got from the config file (config.yaml) and create board instances, adding each to the "boards" array
    for board_config in board_configs:
        boards.append(Agios(board_config["api_key"], board_config["hostname"], board_config["timezone"],
                            should_verify_https_cert=board_config["should_verify_https_cert"]))

    #### Find Host Information and append to maint list or append unfound hosts to unfound_monitors ####
    maintenance_list = []
    unfound_monitors = []
    multiple_list = []
    ## for every host, find it in our monitor dict so we can figure out what board it's on
    for entry in hosts:
        found = False
        if entry.lower() != "localhost":
            records = db.get_records_by_value("monitor", "monitor_name", entry) #exact match
            if len(records) == 0:
                records = db.get_record_like("monitor", "monitor_name", entry) #if no exact match, try a non exact match on end of entered name
            if len(records) == 1:
                board = db.get_record_by_id("board", records[0]['board_id'])
                if board[0]["board_type"] == "Nagios":
                    found = True
                    maintenance_list.append([records[0]["monitor_name"], start_date, start_time, duration, board[0]['board_name']])
            elif len(records) > 1:
                active_count = 0
                for record in records:
                    if record["monitor_state"] == "Active":
                        active_count += 1
                        active_record = record
                if active_count == 1:
                    maintenance_list.append([active_record["monitor_name"], start_date, start_time, duration, board[0]["board_name"]])
                else:
                    print("Multiple records located for ", entry, "Please narrow your search parameters.")
                multiple_list.append(entry)
                found = True
        if not found:
            #print(entry, "was unfound")
            unfound_monitors.append(entry)

    #Sort by the XI name
    maintenance_list = sorted(maintenance_list, key = lambda x: x[4])
    #print("sorted list", maintenance_list, flush=True)
    ########################################
    if len(maintenance_list) > 0:
        prev = maintenance_list[0][4]
        sublist = []

        posted = False # flag to tell if the maint was posted for the current Nagios XI already, as it currently checks each board
        for entry in maintenance_list:
            if entry[4] == prev:
                sublist.append(entry)
            else:
                for board in boards: # can probably change this to a list comp
                    if prev == board.api_host and not posted:
                        board.post_maint(sublist)
                        posted = True
                sublist = [entry]
                posted = False
            prev = entry[4]

        for board in boards: # post the final entry
            if prev == board.api_host and not posted:
                board.post_maint(sublist)
                posted = True
    return (unfound_monitors, multiple_list)

    ########################################

#nagios_maintenance('LC0921-PF1KN0QA, KristinaLaptop, dub-modem01, wartortle.epicorhosting.local, irv-uccetools, LON-VMIS33', '01/17/2023', '08:00', '5')

# #### Unused. Was for handling CSV files when script run directly. May add back if needed ####
# def get_hosts_from_file(file):
    
#     #### File (CSV) Handling ####
#     # This section should be repurposed to a function in the event a csv file is passed instead of a string in the form
#     maintenance_dict = {}

#     #if exists, open file and put all contents into a list
#     if os.path.exists(os.path.join(basedir, file)): #if the csv file exists, continue with program. otherwise make them restart
#         with open(os.path.join(basedir, file), encoding='utf-8-sig') as csvfile:
#             reader = csv.reader(csvfile)
#             row_count=0
#             for row in reader:
#                 if row_count == 0: #skip the header row
#                     row_count += 1
#                 else:
#                     maintenance_dict[row[0]] = {}
#                     maintenance_dict[row[0]]["duration"] = row[1]
#                     maintenance_dict[row[0]]["startdate"] = row[2]
#                     maintenance_dict[row[0]]["starttime"] = row[3]
#     else:
#         print("File 'monitors.csv' Not Found. Please Check File Name and Location and Retry.")
#         sys.exit(1)

#     return maintenance_dict

#     ########################################

# #### If the script was run by itself, run the above function ####
# if __name__ == '__main__':
#     nagios_maintenance()
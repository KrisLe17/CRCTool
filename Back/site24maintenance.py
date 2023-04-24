import os.path
import inspect
from Site24Module.Site24x7 import Site24x7
from Site24Module.site24configuration import Configuration
from DBModule.database import mysql_database


basedir = os.path.dirname(inspect.getfile(Configuration))
config = Configuration(os.path.join(basedir, 'Site24config.yaml'))

def site24_maintenance(hosts, start_date, start_time, duration, username):
    db = mysql_database('crcdb.yaml')
    Site24 = Site24x7()

    #pp.pprint(monitor_list)

    maintenance_list = []
    unfound_hosts = []
    multiple_list = []

    for entry in hosts:
        # we need the monitor id to be able to set maintenance, so we'll get it by name
        #maintenance_list[Site24.get_monitor(row["monitor"], read_acc_token)] = row["minutes"]
        #print("entry", entry, flush=True)
        found = False
        if entry.lower() != "localhost":
            records = db.get_records_by_value("monitor", "monitor_name", entry) #exact match
            if len(records) == 0:
                records = db.get_record_like("monitor", "monitor_name", entry) #if no exact match, try a non exact match on end of entered name
            if len(records) == 1:
                found = True
                # maintenance_list is ([hostname, monitor_id, startdate, starttime, duration, businessunit])
                maintenance_list.append([records[0]["monitor_name"], records[0]["monitor_site24_id"], start_date, start_time, duration, db.get_record_by_id("board", records[0]['board_id'])[0]['board_bu_id']])
            elif len(records) > 1:
                active_count = 0
                for record in records:
                    if record["monitor_state"] == "Active":
                        active_count += 1
                        active_record = record
                if active_count == 1:
                    maintenance_list.append([active_record["monitor_name"], active_record["monitor_site24_id"], start_date, start_time, duration, db.get_record_by_id("board", active_record["board_id"])[0]["board_bu_id"]])
                print("Multiple records located for ", entry, "Please narrow your search parameters.")
                multiple_list.append(entry)
                found = True
        if not found:
            unfound_hosts.append(entry)

    #print("maintenance list", maintenance_list, flush=True)
    #post the maint
    if len(maintenance_list) > 0:
        Site24.handle_maintenance_list(maintenance_list, username)
    return(unfound_hosts, multiple_list)


# #### Unused. Was for handling CSV files when script run directly. May add back if needed ####

   # import our maintenance list from the csv file;
    # columns are host_name, duration(minutes), start_date, start_time
    # maintenance_dict = {}

    # #if exists, open file and put all contents into a list
    # if os.path.exists('maintenance.csv'): #if the csv file exists, continue with program. otherwise make them restart
    #     with open('maintenance.csv', encoding='utf-8-sig') as csvfile:
    #         reader = csv.reader(csvfile)
    #         row_count=0
    #         for row in reader:
    #             if row_count == 0: #skip the header row
    #                 row_count += 1
    #             else:
    #                 maintenance_dict[row[0]] = {}
    #                 maintenance_dict[row[0]]["duration"] = row[1]
    #                 maintenance_dict[row[0]]["startdate"] = row[2]
    #                 maintenance_dict[row[0]]["starttime"] = row[3]
    # else:
    #     print("File 'monitors.csv' Not Found. Please Check File Name and Location and Retry.")
    #     sys.exit(1)
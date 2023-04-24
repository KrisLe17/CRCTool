from DBModule.database import mysql_database

def lookup(host_list):
    db = mysql_database('crcdb.yaml')
    host_info = []
    for entry in host_list:
        records = []
        records = db.get_records_by_value("monitor", "monitor_name", entry) #exact match
        if len(records) == 0:
            records = db.get_record_like("monitor", "monitor_name", entry) #if no exact match, try a non exact match on end of entered name
        if len(records) == 0:
            host_info.append({"monitor_name": entry,
                          "monitor_ip": "Monitor not found",
                          "board_type": "Monitor not found",
                          "board_name": "Monitor not found"})
        else:
            for record in records:
                display = {}
                board = db.get_record_by_id("board", record["board_id"])[0]
                display["board_type"] = board["board_type"]
                display["board_name"] = board["board_name"]
                display["monitor_name"] = record["monitor_name"]
                display["monitor_ip"] = record["monitor_ip"]
                host_info.append(display)
    
    return host_info
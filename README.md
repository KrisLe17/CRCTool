# Monitor Maintenance Tool
Webtool to place monitors in maintenance mode on Site24x7 or Nagios. Backend written in Python 3.0.

## Uses:
- Site24Module
- NagiosModule

## Purpose
This script uses API requests to place hosts in maintenance mode on Site24x7 or Nagios.

## Features
- Accepts comma seperated list of hosts in search box
- Accepts CSV file of hosts
- Set duration of maintenance
- Start time can be scheduled in advance or will run as "start now"

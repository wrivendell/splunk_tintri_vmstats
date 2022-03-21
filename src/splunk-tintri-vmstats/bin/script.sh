#!/bin/bash
##############################################################################################################
# Contact: Will Rivendell 
# 	E1: wrivendell@splunk.com
# 	E2: contact@willrivendell.com
##############################################################################################################
### python3.7+ - NOTE you may need full path to "script" file below when Splunk is running it
python3 script.py \
    -sn 'server1.com' 'server2.com' \
    -un 'admin' \
    -pw 'password' \
    -suri 'https://127.0.0.1:8088' \
    -hec '612caa11-79b7-4cc2-ba51-a531d77e2857' \
    -es 'tintri_ta' \
    -est 'json' \
    -met False\
    -csv True \
    -csvo False \
    -rc 5 \
    -d  True \
    -ll "{$SPLUNK_HOME}/etc/apps/splunk-tintri-vmstats/logs" \
    -csvl "{$SPLUNK_HOME}/etc/apps/splunk-tintri-vmstats/csv"

# You should always try and use the "AIO" (all in one) version as it doesn't need any outside dependencies including Python
# \  = indicates cmd continues on next line in bash
# -sn = --server_names - A list of Tintri Device Name(s) in single quotes, separated by SPACES, ie. 'zeus.portland.local' '98.112.32.123'
# -un = --user_name - Tintri Devices Username
# -pw = --password - Tintri Devices Password
# -suri = --splunk_uri - Splunk Server URI with HEC token port, i.e 'https://mygreatsplunkserver.com:8088'
# -hec = --splunk_hec_token - Splunk HEC token -> create in Splunk (dont forget to enable in Global settings after create) i.e '612caa11-79b7-4cc2-ba51-a531d77e2857'
# -es = --event_source - i.e. 'tintri_ta'
# -est = --event_sourcetype - i.e. 'json'
# -met = --metrics - True to send data as Metrics rather than Events to the HEC token
# -csv = --csv_output - Write output to a CSV in addition to sending to Splunk HEC -> ./csv
# -csvo = --csv_only - Write out a CSV of stats data only and skip send to Splunk
# -rc = --retain_csv - Number of days to retain CSV outputs (csvs older than this number of days will be auto removed next run)
# -d  = --debug - Enable more console debugging
# -ll = --log_location - full path to where to store the logs, i.e '/opt/splunk/var/log/tintri_ta' or "{$SPLUNK_HOME}/etc/apps/splunk-tintri-vmstats/logs" - use double quotes and {} if using $SPLUNK_HOME
# -csvl = --csv_location - full path to where to store the csvs, i.e '/opt/splunk/var/log/tintri_ta/csv' or "{$SPLUNK_HOME}/etc/apps/splunk-tintri-vmstats/csv" - use double quotes and {} if using $SPLUNK_HOME
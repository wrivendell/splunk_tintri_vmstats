# splunk-tintri-vmstats
This TA will gather VM Stats from a provided list of Tinri VM Devices. It will also gather basic info of the devices themselves.
This data is formated into Splunk events or Metrics and fed into Splunk via HEC. 

Optionally the TA can be configured to write out a CSV instead or as well. 
If CSV is preferred, the user could configure the inputs.conf to monitor the CSVs rather than upload via HEC.

See $SPLUNK_HOME/etc/apps/splunk-tintri-vmstats/bin/script.sh for configuration descriptions and options.
***All configuration for logging should be done in this file:*** $SPLUNK_HOME/etc/apps/splunk-tintri-vmstats/bin/script.sh

***All configuration for how often this ta runs the above script should be done in:*** $SPLUNK_HOME/etc/apps/splunk-tintri-vmstats/local/inputs.conf
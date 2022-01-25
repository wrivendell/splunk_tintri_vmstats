#!/usr/bin/env python3
##############################################################################################################
# Contact: Will Rivendell 
# 	E1: wrivendell@splunk.com
# 	E2: contact@willrivendell.com
##############################################################################################################

### Imports
import argparse

### CLASSES ###########################################

class LoadFromFile (argparse.Action):
	#Class for Loading Arguments in a file if wanted
	def __call__ (self, parser, namespace, values, option_string = None):
		with values as f:
			parser.parse_args(f.read().split(), namespace)

### FUNCTIONS ###########################################

def str2bool(string: str) -> bool:
	#Define common 'string values' for bool args to accept 'Yes' as well as 'True'
	if isinstance(string, bool):
		return(string)
	if string.lower() in ('yes', 'true', 't', 'y', '1'):
		return(True)
	elif string.lower() in ('no', 'false', 'f', 'n', '0'):
		return(False)
	else:
		raise argparse.ArgumentTypeError('Boolean value expected. True / False.')

def checkPositive(value: str) -> int:
	ivalue = int(value)
	if ivalue < 0:
		raise argparse.ArgumentTypeError('%s is an invalid (or below 0) int value' % value)
	return ivalue

def Arguments():
	# Arguments the app will accept
	global parser
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", type=open, action=LoadFromFile)
	parser.add_argument("-sn", "--server_names", nargs="*", required=True, help="A list of Tintri Device Name(s) separated by commas, ie. 'zeus.portland.local','98.112.32.123' ")
	parser.add_argument("-un", "--user_name", nargs="?", required=False, help="Tintri Device Username.")
	parser.add_argument("-pw", "--password", nargs="?", required=False, help="Tintri Device Password.")
	parser.add_argument("-suri", "--splunk_uri", nargs="?", required=False, help="Splunk Server URI, i.e 'https://mygreatsplunkserver.com' ")
	parser.add_argument("-hec", "--splunk_hec_token", nargs="?", required=False, help="Splunk HEC token.")
	parser.add_argument("-es", "--event_source", nargs="?", required=False, default='tintri_ta', help="Splunk formatted event source.")
	parser.add_argument("-est", "--event_sourcetype", nargs="?", required=False, default='json', help="Splunk formatted event sourcetype")
	parser.add_argument("-met", "--metrics", type=str2bool, nargs="?", const=True, default=False, required=False, help="True to send the data as Metrics via HEC token.")
	parser.add_argument("-csv", "--csv_output", type=str2bool, nargs="?", const=True, default=False, required=False, help="Write out a CSV of stats data.")
	parser.add_argument("-csvo", "--csv_only", type=str2bool, nargs="?", const=True, default=False, required=False, help="Write out a CSV of stats data only and skip send to Splunk.")
	parser.add_argument("-rc", "--retain_csv", type=checkPositive, nargs="?", const=True, default=False, required=False, help="How many days to retain the CSV events, days beyond the number specified here will be deleted.")
	parser.add_argument("-d", "--debug", type=str2bool, nargs="?", const=True, default=False, required=False, help="Enable extra console logging for troubleshooting of confirmation testing.")
	parser.add_argument("-dm", "--debug_modules", type=str2bool, nargs="?", const=True, default=False, required=False, help="Will enable deep level debug on all the modules that make up the script. Enable if getting errors, to help dev pinpoint.")
	parser.add_argument("-ll", "--log_location", nargs="?", required=False, Default='./logs', help="Full path to where the log file will be written.")
	parser.add_argument("-csvl", "--csv_location", nargs="?", required=False, Default='./csv', help="Full path to where the csv file will be written.")

############## RUNTIME
Arguments()
args = parser.parse_args() 
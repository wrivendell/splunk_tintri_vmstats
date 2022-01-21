##############################################################################################################
# Contact: Will Rivendell 
# 	E1: wrivendell@splunk.com
# 	E2: contact@willrivendell.com
##############################################################################################################

### Imports ###########################################
import datetime, time, sys, requests, json, urllib3

from lib import wr_logging as log
from lib import wr_arguments as arguments

### Globals ###########################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disables the nagging insecure warning, we know we're hitting our own splunk servers so we dont care
log_file = log.LogFile('splunk_tintri_ta', remove_old_logs=True, log_level=1, log_retention_days=0, debug=False)
if arguments.args.debug:
	print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Log file created in ./logs/\n\n")
tintri_session_id = ''
vmstats_raw_json = []
splunk_events_list = []

### Functions ###########################################
# generate a time stamp that Splunk likes based on system time (not used, used epoch instead)
def time_stamp() -> str:
	offset = str( round(time.timezone/3600, 2) ).replace('.', ':')
	if offset.endswith(':0'):
		offset += '0'
	time_stamp = datetime.datetime.now().strftime("%Y-%m-%dT%T.%f-" + offset)
	return(time_stamp)

# log in to the Tintri VMStore device (validate credentials)
def login_to_vmstore(server_name:str) -> str:
	'''
	This will attempt to create a login session to the Tintri device.
	The return will be a session_id from the cookies entry in the response.
	'''
	# TNTRI - VMStore Login Info - Payload, header and URL for login call
	headers =   {'content-type': 'application/json'}
	url = 'https://' + server_name + '/api/v310/session/login'
	payload =   {
					"newPassword": None, 
					"username": arguments.args.user_name, 
					"roles": None,
					"password": arguments.args.password, 
					"typeId": "com.tintri.api.rest.vcommon.dto.rbac.RestApiCredentials"
				}
	if arguments.args.debug:				
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to: " + server_name)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name)

	log_file.writeLinesToFile([
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to: " + server_name,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name,
		])

	# Attempt login -> check for errors on response code
	try:
		r = requests.post(url, json.dumps(payload), headers=headers, verify=False)
	except requests.ConnectionError:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: API Connection error occurred"])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: API Connection error occurred")
		sys.exit()
	except requests.HTTPError:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: HTTP error occurred"])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: HTTP error occurred")
		sys.exit()
	except requests.Timeout:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: Request timed out"])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: Request timed out")
		sys.exit()
	except Exception:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: An unexpected error occurred"])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: An unexpected error occurred")
		sys.exit()
	# if http Response is not 200 then raise an exception and exit
	if not r.status_code == 200:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: HTTP Status code is not 200, exiting on: " + str(r.status_code)])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri Login ERROR: HTTP Status code is not 200, exiting on: " + str(r.status_code))
		sys.exit()

	# success
	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code))
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The Json response COOKIE of login call to the server: " + server_name + " is: \n" + str(r.cookies) + "\n\n")

	log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The Json response COOKIE of login call to the server: " + server_name + " is: \n" + str(r.cookies) + "\n\n"])
	log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code)])
	
	# Return SessionId from Cookie
	return(r.cookies['JSESSIONID'])

# get the Tintri Device Info
def get_device_info(session_id:str, server_name:str):
	'''
	This will attempt to pull the device info, SN, name, OS etc...
	Returns the raw response (JSON)
	'''
	#Header and URL for info call
	headers = {'content-type': 'application/json','cookie': 'JSESSIONID=' + session_id}
	url = 'https://' + server_name + '/api/v310/appliance/default/info'

	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to get device info for: " + server_name)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name)
	
	log_file.writeLinesToFile([
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to get device info for: " + server_name,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name,
		])
	
	# Attempt pull of Device info -> check for non 200 status
	try:
		r = requests.get( url, headers=headers, verify=False )
		# if http Response is not 200 then raise an exception and exit
		if not r.status_code == 200:
			log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri get_device_info ERROR: HTTP Status code is not 200 on Device Info API, exiting on: " + str(r.status_code)])
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri get_device_info ERROR: HTTP Status code is not 200 on Device Info API, exiting on: " + str(r.status_code))
			sys.exit()
	except Exception:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri get_device_info ERROR: An unexpected error occurred trying to get Device Info from API, exiting."])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri get_device_info ERROR: An unexpected error occurred trying to get Device Info from API, exiting.")
		sys.exit()

	# success
	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code))
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The Json response of login call to the server: " + server_name + " is: \n" + r.text + "\n\n")
	log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code)])

	return(r.text)

# get the Tintri VMStats from vmstats api
def get_vmstats(session_id:str, server_name:str):
	'''
	Retrieve the JSON payload from the Tintri VMStats api
	Combines the VMSTATS for the Tintri Device and the info of the device itself into a dictionary
	The returned dictionary has one key and one value, the key is the device server name, the value is the combined dict data
	'''
	# Get device info details first
	device_details = json.loads(get_device_info(session_id, server_name))

	# Header and URL for vmstats call
	headers = {'content-type': 'application/json','cookie': 'JSESSIONID=' + session_id}
	url = 'https://' + server_name + '/api/v310/datastore/default/statsSummary'

	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to get vmstats for: " + server_name)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url)
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name)

	log_file.writeLinesToFile([
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting login to get vmstats for: " + server_name,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using URL: " + url,
		"TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Using Username: " + arguments.args.user_name,
		])
	
	# Attempt pull of VMStats data summary -> check for non 200 status
	try:
		r = requests.get( url, headers=headers, verify=False )

		# if http Response is not 200 then raise an exception and exit
		if not r.status_code == 200:
			log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Tintri get_vmstats ERROR: HTTP Status code is not 200 on VMStats Summary API, exiting on: " + str(r.status_code)])
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"):  Tintri get_vmstats ERROR: HTTP Status code is not 200 on VMStats Summary API, exiting on: " + str(r.status_code))
			sys.exit()
	except Exception:
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"):  Tintri get_vmstats ERROR: An unexpected error occurred trying to get VMStats Summary from API, exiting."])
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"):  Tintri get_vmstats ERROR: An unexpected error occurred trying to get VMStats Summary from API, exiting.")
		sys.exit()

	# success
	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code))
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The Json response of login call to the server: " + server_name + " is: \n" + r.text + "\n\n")
	log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): The HTTP Status code is: " + str(r.status_code)])

	tmp_dict = {}
	vmstats_info = {}
	vmstats_info = json.loads(r.text) # store vmstats info in dict
	vmstats_info.update(device_details) # add device info to vmstats info dict
	tmp_dict[server_name]=vmstats_info # add the server name identifier to make a 1 kv pair dict for return
	return(tmp_dict)

# parse the vmstats data for input to Splunk and optional CSV output
def parse_vmstats(vmstats:dict) -> dict:
	'''
	This parses the vmstats json data into events for Splunk and/or CSV
	'''
	# separate the server name from the rest of the data in the dict
	server_name = list(vmstats.keys())[0]
	vmstats_data = vmstats[server_name]
	
	if arguments.args.debug:
		print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Parsing JSON response data from VMStats\Device Info API.")
	log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Parsing JSON response data from VMStats\Device Info API."])
	
	## store device info into easier to read vars
	# device info
	current_capacity = str(vmstats_data['currentCapacityGiB'])
	filesystem_id = str(vmstats_data['filesystemId'])
	model_name = str(vmstats_data['modelName'])
	os_version = str(vmstats_data['osVersion'])
	product_id = str(vmstats_data['productId'])
	serial_number = str(vmstats_data['serialNumber'])

	# vm stats
	physical_space = str( round(vmstats_data['spaceTotalGiB']/1024, 5) )
	physical_free = str( round(vmstats_data['spaceRemainingPhysicalGiB']/1024, 5) )
	physical_used = str( round((vmstats_data['spaceTotalGiB']-vmstats_data['spaceRemainingPhysicalGiB'])/1024, 5) )
	logical_space = str( round((vmstats_data['spaceTotalGiB'] * vmstats_data['spaceSavingsFactor'])/1024, 5) )
	logical_free = str( round((vmstats_data['spaceRemainingPhysicalGiB'] * vmstats_data['spaceSavingsFactor'])/1024, 5) )
	logical_used = str( round( ((vmstats_data['spaceTotalGiB'] - vmstats_data['spaceRemainingPhysicalGiB']) * vmstats_data['spaceSavingsFactor'])/1024, 5 ) )
	percent_used = str( round(100 - (vmstats_data['spaceRemainingPhysicalGiB'] / vmstats_data['spaceTotalGiB'] * 100), 5) )
	saving_factor = str( round(vmstats_data['spaceSavingsFactor'], 5) )
	number_of_vms = str(vmstats_data['vmsCount'])
	snapshots_on_hypervisor_gb = str( round(vmstats_data['spaceUsedSnapshotsHypervisorGiB'], 5) )
	snapshots_on_tintri_gb = str( round(vmstats_data['spaceUsedSnapshotsTintriGiB'], 5) )
	total_snapshots = str( round(vmstats_data['spaceUsedSnapshotsHypervisorGiB'] + vmstats_data['spaceUsedSnapshotsTintriGiB'], 5) )

	# check if we're doing UPLOAD to Splunk or just CSV write out
	if not arguments.args.csv_only:
		if arguments.args.metrics:
			# METRICS - we want to send this as metrics to Splunk rather than events
			event_payload =	{
				"time": time.time(),
				"event": "metric",
				"host": server_name,
				"source": "tintri_ta",
				"sourcetype": "json",
				"fields": { 
					"Tintri_Name": server_name,
					"Current_capacity": current_capacity,
					"Filesystem_id": filesystem_id,
					"Model_name": model_name,
					"OS_Version": os_version,
					"Product_ID": product_id,
					"Serial_Number": serial_number,
					"Physical_Space": physical_space,
					"Physical_Free": physical_free,
					"Physical_Used": physical_used,
					"Logical_Space": logical_space,
					"Logical_Free": logical_free,
					"Logical_Used": logical_used,
					"Percent_Used": percent_used,
					"Saving_Factor": saving_factor,
					"Number_of_VMs": number_of_vms,
					"Snapshots_on_Hypervisor_GB": snapshots_on_hypervisor_gb,
					"Snapshots_on_Tintri_GB": snapshots_on_tintri_gb,
					"Total_Snapshots": total_snapshots
				}
			}
		else:
			# EVENTS - we want to send this as events to Splunk rather than metrics
			event_payload =	{
				"time": time.time(),
				"host": server_name,
				"source": "tintri_ta",
				"sourcetype": "json",
				"event": { 
					"Tintri_Name": server_name,
					"Current_capacity": current_capacity,
					"Filesystem_id": filesystem_id,
					"Model_name": model_name,
					"OS_Version": os_version,
					"Product_ID": product_id,
					"Serial_Number": serial_number,
					"Physical_Space": physical_space,
					"Physical_Free": physical_free,
					"Physical_Used": physical_used,
					"Logical_Space": logical_space,
					"Logical_Free": logical_free,
					"Logical_Used": logical_used,
					"Percent_Used": percent_used,
					"Saving_Factor": saving_factor,
					"Number_of_VMs": number_of_vms,
					"Snapshots_on_Hypervisor_GB": snapshots_on_hypervisor_gb,
					"Snapshots_on_Tintri_GB": snapshots_on_tintri_gb,
					"Total_Snapshots": total_snapshots
				}
			}

		if arguments.args.debug:
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): " + str(server_name) + " event formatted for Splunk: \n\n" + str(event_payload) + "\n\n")
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) + "): " + str(server_name) + " event formatted for Splunk: \n\n" + str(event_payload) + "\n\n" ])

	if arguments.args.csv_output or arguments.args.csv_only:
		if arguments.args.debug:
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Writing CSV Output as requested.")
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Writing CSV Output as requested."])

		# create a wr_logging class for the CSV file
		event_csv = log.CSVFile("vmstats.csv", log_folder='./csv/', remove_old_logs=True, log_retention_days=arguments.args.retain_csv, prefix_date=True, debug=False)

		# create the row of values to write and the header row
		event_csv.writeLinesToCSV([[
				server_name,
				current_capacity,
				filesystem_id,
				model_name,
				os_version,
				product_id,
				serial_number,				
				physical_space,
				physical_free,
				physical_used,
				logical_space,
				logical_free,
				logical_used,
				percent_used,
				saving_factor,
				number_of_vms,
				snapshots_on_hypervisor_gb,
				snapshots_on_tintri_gb,
				total_snapshots
			]],
			header_row=[
				"Tintri_Name",
				"Current_capacity",
				"Filesystem_id",
				"Model_name",
				"OS_Version",
				"Product_ID",
				"Serial_Number",
				"Physical_Space",
				"Physical_Free",
				"Physical_Used",
				"Logical_Space",
				"Logical_Free",
				"Logical_Used",
				"Percent_Used",
				"Saving_Factor",
				"Number_of_VMs",
				"Snapshots_on_Hypervisor_GB",
				"Snapshots_on_Tintri_GB",
				"Total_Snapshots"
			])

		if arguments.args.debug:
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Writing CSV: Complete")
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Writing CSV: Complete"])
	
	# return the Splunk formatted events/metrics for upload or simply return nothing if CSV only
	if not arguments.args.csv_only:
		return(event_payload)
	else:
		return('')

# send events to Splunk
def send_to_splunk_hec(splunk_events_list:list):
	'''
	Input a list of Dictionaries
	Each dict in the list represents an event in Splunk
	'''
	if not arguments.args.csv_only:
		headers = {'Authorization': 'Splunk ' + arguments.args.splunk_hec_token}
		final = []

		if arguments.args.debug:
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting to compile events from all API calls from all devices to Splunk compatible JSON\n" )
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting to compile events from all API calls from all devices to Splunk compatible JSON"])

		# compile the list of events and make them one long nested JSON string (as per Splunk preferred format)
		for i in splunk_events_list:
			final.append(json.dumps(i))
		final = ''.join(final) # convert to string for splunk hec

		if arguments.args.debug:
			print("TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting to send events to Splunk: " + arguments.args.splunk_uri + "/services/collector\n" )
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Attempting to send events to Splunk: " + arguments.args.splunk_uri + "/services/collector"])

		r = requests.post(arguments.args.splunk_uri + '/services/collector', headers=headers, data=final, verify=False)
		print("tintri_ta_upload_to_splunk_status_code:" + str(r.status_code)) # in non-debug mode this will get sent to Splunk log - formatted as such
		log_file.writeLinesToFile(["TINTRI_TA(" + str(sys._getframe().f_lineno) +"): Upload to Splunk Status: " + str(r.status_code)])

### Runtime ########################################### >>


# get all the vmstats for each specified device
for device in arguments.args.server_names:
	# log into Tintri device and get session_id
	tintri_session_id = login_to_vmstore(device)
	vmstats_raw_json.append(get_vmstats(tintri_session_id, device))

# parse each json return into splunk friendly json and add to list
for vmstat in vmstats_raw_json:
	splunk_events_list.append(parse_vmstats(vmstat))

# send event list to Splunk via HEC
if splunk_events_list:
	send_to_splunk_hec(splunk_events_list)
sys.exit()
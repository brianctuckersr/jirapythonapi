#GetJIRAGroupMembers - with pagination
#authored by Brian Tucker 
#08/04/2017 

#Gets list of groups and members and creates a flat comma delimited csv file. 
import json
import requests
import csv
import getpass
import os    
import sys
from pprint import pprint


username = input('username:') 				
password = getpass.getpass('password:')
domain = input('domain:')			
try:     
    response = requests.get('https://'+domain+'.atlassian.net/rest/api/2/groups/picker?maxResults=100', auth=(username, password))
    data = response.json()
except json.decoder.JSONDecodeError:
    print('Failed to authenticate')
    sys.exit(1)
print('Authentication successful')
myGroupList = []
for item in data['groups']:
    myGroupList.append(item['name'])
print(myGroupList)							#verify your list of groups
filename = 'jiragroupmembers.csv'			#prepare to write to file 
csv_file =  open(filename, 'w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['groupName','displayName','active','emailAddress'])
print('Writing to csv file...')
#Request list of users in a group 
for groupName in myGroupList: 				#groupname value should be a variable that will be fed from another loop
	payload = {'isLast':'false', 'includeInactiveUsers':'true', 'groupname':groupName} #how do I pass in groupName as a variable
	response = requests.get('https://'+domain+'.atlassian.net/rest/api/2/group/member', auth=(username,password), params=payload)
	data = response.json()
	#pprint(data)
	stopGets = (data['isLast'])
	#print(stopGets)						#variable isLast variable set
	for item in data['values']:				#Print the groupnames and the first page of members
		print(groupName + ',' + item['displayName'] + ',' + str(item['active']) +','+ item['emailAddress'])
		writer.writerow([groupName, item['displayName'], item['active'], item['emailAddress']])
	if (data['isLast']) == False:			#Only loop if it is not the last page
		getNext = (data['nextPage']) 		#create variable to hold nextPage URL
		while stopGets == False:			#print the next pages of users using getNext
			#print(getNext) 					#verify nextPage URL variable set
			response = requests.get(getNext, auth=(username,password))
			data = response.json()
		#print(data)
			for item in data['values']:
				print(groupName + ',' + item['displayName'] + ',' + str(item['active']) + ',' + item['emailAddress'])
				writer.writerow([groupName, item['displayName'], item['active'], item['emailAddress']])
			for item in data['values']:
				if (data['isLast'] == False):
					getNext = (data['nextPage'])
				stopGets = (data['isLast'])
print('File created successfully at: '+ filename)
csv_file.close()
os.system('libreoffice ' + filename)
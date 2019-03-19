

import json
import requests
import csv
import getpass
import os
import sys
import collections
from pprint import pprint

print (' Welcome to the Jira project membership list generator. \n \
Enter your credentials to retrieve records and generate a csv. \n \
The csv will be created in a \\csv folder beneath your current directory. \n \
brian.tucker 11.01.2018 1.0')

#authentication 
username = input('Enter your username:')
password = getpass.getpass('Password:')
domain = input('Domain:')

filepath = os.path.join('csv', 'jiraprojectroles.csv')
if not os.path.exists('csv'):
    os.makedirs('csv')
csv_file =  open(filepath, 'w', newline='')
writer = csv.writer(csv_file)
writer.writerow(['project_key','project_name','role','group','member', 'email','domain','active', 'type'])


#initial call to find out if there are more pages - i.e. isLast = False
response = requests.get('https://' + domain + '.atlassian.net/rest/api/3/project/search', auth=(username, password))
projects = response.json()
nextrecordset=0 #set the first recordset Jira returns 50 by default - i.e. 0-49. 
page = 1
print (projects['total'],' projects')

#Retrieve project info until you hit the last page of result
while projects['isLast']is False: 
	lastpagechk = projects['isLast']
	print (lastpagechk)
	print('Page---> ',page)

	#get all projects 
	response = requests.get('https://' + domain + '.atlassian.net/rest/api/3/project/search?startAt='+str(nextrecordset)+'', auth=(username, password))
	projects = response.json()
	for count,item in enumerate(projects['values']):
		pid = item['id']
		pname = item['name']
		pkey = item['key']
		print(count,'-',pid,',', item['name'],',', item ['key']) #display the project info 
		
		# get the roles for each project 
		response = requests.get('https://' + domain +'.atlassian.net/rest/api/3/project/'+str(pid)+'/role', auth=(username, password))
		roles = response.json()
		for key, value in roles.items(): 
			if key!= 'atlassian-addons-project-access': #ignore addons
				print (key, value) #returns the role name and url for the project role
				
				#get the members for each role; value is the name of the user or group
				response = requests.get(value, auth=(username, password)) #value = user or groupname
				members = response.json() 
				if members['actors']: #if there are actors
					for item in members['actors']: 

						#if the user type returned is a user do these steps. WARNING, if a user has been deleted from Jira, but still has membership to a project, in Project settings > People, they will be displayed as 'Former User'. 
						# Currently, this breaks the script, because Former User does not have an email. In the future, I should handle this exception. 

							if item['actorUser']!={}: 
								accountid = item['actorUser']['accountId']
								response = requests.get('https://' + domain +'.atlassian.net/rest/api/3/user?accountId='+accountid+'', auth=(username, password))
								mbr_details = response.json()
								if mbr_details['emailAddress']: 
									email = mbr_details['emailAddress']
									status = mbr_details['active']
									domainpart = email.split('@')[1]	
									print (pkey,',',pname,',',key, ',','directmember',',',item['displayName'],',',email,',',domainpart,',',status,', user')
									writer.writerow ([pkey,pname,key,'directmember',item['displayName'], email, domainpart, status, 'user'])
								else: 
									print (pkey,',',pname,',',key, ',','directmember',',',item['displayName'],',','noemail',',','nodomainpart',',',status,', user')
									writer.writerow ([pkey,pname,key,'directmember',item['displayName'], 'noemail', 'nodomainpart', status, 'user'])	
							else: 
								print (pkey,',',pname,',',key, ',','directmember',',',item['displayName'],', noacctid, nodomainpart, unknown, user')
								writer.writerow ([pkey,pname,key,'directmember',item['displayName'], 'noacctid','nodomainpart','unknown','user'])
						
						#if the user type returned is a group then exec group steps... 
						elif item['type']=='atlassian-group-role-actor':
							groupname = item['displayName'].replace('+','%2B') #some group names have special characters that will break the url in the api call 
							print(groupname)

							#make the api call to get the group members
							response = requests.get('https://' + domain +'.atlassian.net/rest/api/3/group/member?groupname='+groupname+'', auth=(username, password))
							groupmbr = response.json()

							#if the group is not found - status_code != 200, the group is "orphaned"
							#orphaned: group is a group that was deleted before it was removed from the project
							grp_recordset = 0 #pagination startAt = 0 will get records 0 to 50
							if response.status_code!=200:
								print (pkey,',',pname,',',key,',',groupname, ', orphaned, #N/A, #N/A, #N/A, #N/A')
								writer.writerow ([pkey,pname,key,groupname.replace('%2B','+'),'orphaned','#N/A','#N/A','#N/A','#N/A'])

							#else if the group is found - status_code ==200, get the group details
							else:	
								grp_lastpage = groupmbr['isLast'] #true if the last page
								if groupmbr['isLast'] is True: 
									for item in groupmbr['values']:
										gname = item['displayName']
										if item['emailAddress']:
											email = item['emailAddress']
											status = item['active']
											domainpart = email.split('@')[1]
											print (pkey,',',pname,',',key,',',groupname, ',', gname,',', email,',',domainpart,',',status, ', groupuser')
											writer.writerow ([pkey,pname,key,groupname.replace('%2B','+'),gname, email, domainpart, status, 'groupuser'])
										else:
											print (pkey,',',pname,',',key,',',groupname, ',', gname,',', 'noemail',',','nodomainpart',',',status, ', groupuser')
											writer.writerow ([pkey,pname,key,groupname.replace('%2B','+'),gname, 'noemail', 'nodomainpart', status, 'groupuser'])	
								else:
									while groupmbr['isLast'] is False: #false if there are more pages
										response = requests.get('https://' + domain +'.atlassian.net/rest/api/3/group/member?groupname='+groupname+'&startAt='+str(grp_recordset)+'', auth=(username, password))
										groupmbr = response.json()
										for item in groupmbr['values']:
											gname = item['displayName']
											if item['emailAddress']:
												email = item['emailAddress']
												status = item['active']
												domainpart = email.split('@')[1]
												print (pkey,',',pname,',',key,',',groupname, ',', gname, ',', email, ',',domainpart,',',status,', groupuser')
												writer.writerow ([pkey,pname,key,groupname.replace('%2B','+'), gname, email, domainpart, status, 'groupuser'])
											else:
												print (pkey,',',pname,',',key,',',groupname, ',', gname, ',', 'noemail', ',','nodomainpart',',',status,', groupuser')
												writer.writerow ([pkey,pname,key,groupname.replace('%2B','+'), gname, 'noemail', 'nodomainpart', status, 'groupuser'])
										grp_recordset+=50						
	nextrecordset+=50
	page+=1


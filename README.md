# jirapythonapi
A handy Python script to pull paginated group member data from JIRA and convert to csv format.

This script takes your username, password, and domain as inputs to do the following: 
1)Retrieves a list of groups from your JIRA Cloud 
2)Takes that list of groups and generates a list of users in that group. 

JIRA Cloud limits the response to 50 users, but I've take care of paginating the results. So it will retrieve all usernames using the nextPage URL returned in the API response. 

The user list includes inactives, and provides the group_name, display_name, account_status, and email_address. 

Domain input assumes your domain is https://mycompany.atlassian.com. When prompted for domain, enter only the value for "mycompany". 

Upon successful authentication, the group memer list will print to the screen. When the process is complete, the data will be written to a csv file for use in your favorite spreadsheet app - sheets, libreoffice, or excel. 

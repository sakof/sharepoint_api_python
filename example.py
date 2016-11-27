#! /bin/env python
import requests
import pprint
from requests_ntlm import HttpNtlmAuth
sharepoint_user = 'mysharepointuser'
sharepoint_password = 'mysharepointpassword'
#Sharepoint URL should be the address of the site followed by /_api/web/
sharepoint_url = 'https://mysharepointsiteurl/_api/web/'
sharepoint_contextinfo_url = 'https://mysharepointsiteurl/_api/contextinfo'
sharepoint_listname = 'MyDevopsBooks'
headers = {
    "Accept":"application/json; odata=verbose",
    "Content-Type":"application/json; odata=verbose",
    "odata":"verbose",
    "X-RequestForceAuthentication": "true"
}
auth = HttpNtlmAuth(sharepoint_user, sharepoint_password)
#Get List information
r = requests.get(sharepoint_url+"lists/getbytitle('%s')" % sharepoint_listname, auth=auth, headers=headers, verify=False)
list_id = r.json()['d']['Id']
list_itemcount = r.json()['d']['Id']
##### Query all items from the list ######
list_cursor = 0 
list_pagesize = 400
api_items_url = sharepoint_url + "Lists(guid'%s')/Items" % list_id
concat_items = []
# We start by an initial request and then loop through pages returned by sharepoint
cur_page = requests.get(api_items_url, auth=auth, headers=headers,verify=False)
concat_items += cur_page.json()['d']
while '__next' in cur_page.json()['d']['results']:
    cur_page = requests.get(cur_page.json()['d']['__next'], auth=auth, headers=headers, verify=False)
    concat_items += cur_page.json()['d']['results']
# Let's see the data we collected:
pprint.pprint(concat_items)
#### Update an Item in a list #### 
# First of all get the context info
r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']
item_id = 2 #This id is one of the Ids returned by the code above 
api_page = sharepoint_url + "lists/GetByTitle('%s')/GetItemById(%d)" % (sharepoint_listname, item_id)
update_headers = {
    "Accept":"application/json; odata=verbose",
    "Content-Type":"application/json; odata=verbose",
    "odata":"verbose",
    "X-RequestForceAuthentication": "true",
    "X-RequestDigest" : form_digest_value,
    "IF-MATCH": "*",
    "X-HTTP-Method" : "MERGE"
}
r = requests.post(api_page, {'some_column':'some_value'}, auth=auth, headers=update_headers,verify=False)
if ret.status_code == 204:
    print('Well done, you just updated a list item, don\'t rush to sharepoint gui yet, there might be a delay due to internal caching')
#### Add an entry in a list ####
r = requests.post(sharepoint_contextinfo_url, auth=auth, headers=headers, verify=False)
form_digest_value = r.json()['d']['GetContextWebInformation']['FormDigestValue']
post_headers = {
    "Accept":"application/json; odata=verbose",
    "Content-Type":"application/json; odata=verbose",
    "odata":"verbose",
    "X-RequestForceAuthentication": "true",
    "X-RequestDigest": form_digest_value
}
# First we need to get the item type, dirtybutworks: get it fro previously 
# requested items
item_type = concat_items[1]['__metadata']['type']
input = {'Column1': 'Value1', 'Column2':'value2'} #This of course depends on your list
input['__metadata'] = {
    'type' : item_type,
}
r = requests.post(api_page, input, auth=auth, headers=post_headers, verify=False)
if r.status_code == 201:
    print('Successfully added')

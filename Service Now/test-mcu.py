import requests
import pickle
import pandas as pd
import json
ts = requests.session()

ts.auth = ('apiuser', 'Snow2016!')
ts.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/37.0.2062.120 Safari/537.36"}

r = ts.get('https://cdwsam.com/api/customers/35/computers/69952/?$format=json')
js = r.json()
links = js['Body']
print(links)


#
# r = ts.get('http://192.168.111.132/api/customers/1/computers/424/?$format=json')
# print(r.content)
# js = r.json()
# links = js['Body']
#
# # print(links)
#
# ifile = open('SnowData/idlist729.pickle','rb')
# idl = pickle.load(ifile)
# ifile.close()
# print(len(idl))
#
# cdf = pd.read_pickle('SnowData/computers.pickle')
# cdf_id = list(cdf['Id'])
#
# failed = list(filter(lambda x: x not in cdf_id, idl))
# print(failed)
#
# ss = requests.session()
# ss.auth = ('admin','Snow2016!')
# ss.headers = {"Content-Type":"application/json","Accept":"application/json"}
#
# data_d = {"software": "USBDLM 4", "installed_on": "COMPUTER1185", "name": "Uwe Sieber"}
# data_j = json.dumps(data_d)
# # ut = 'https://' + SNINST + '.service-now.com/u_test_snow_computers?JSONv2&sysparm_action=insertMultiple'
# ut = 'https://' + 'dev16641' + '.service-now.com/' + 'x_snsab_snow_cmdb_softwareinstancestagin' + '.do?JSONv2&sysparm_action=insert'
# print(ut)
# response = ss.post(ut, data=data_j)
# print('Posting ' + 'Software Data' + ':')
#
# print(response.content)
#
# # Check for HTTP codes other than 200
# if response.status_code != 200:
#     print('Error')
#     print(response.content)
#     pass
#

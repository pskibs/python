import requests
import pickle
import pandas as pd

ts = requests.session()

ts.auth = ('apiuser', 'Snow1951!')
ts.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/37.0.2062.120 Safari/537.36"}

# r = ts.get('http://192.168.111.132/api/customers/1/computers/1/?$format=json')
# js = r.json()
# links = js['Links']
#
# print((links[4])['Href'])

#
# r = ts.get('http://192.168.111.132/api/customers/1/computers/424/?$format=json')
# print(r.content)
# js = r.json()
# links = js['Body']
#
# print(links)

ifile = open('SnowData/idlist729.pickle','rb')
idl = pickle.load(ifile)
ifile.close()
print(len(idl))

cdf = pd.read_pickle('SnowData/computers.pickle')
cdf_id = list(cdf['Id'])

failed = list(filter(lambda x: x not in cdf_id, idl))
print(failed)


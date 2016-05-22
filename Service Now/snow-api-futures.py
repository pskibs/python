# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 15:02:40 2016

@author: parker


"""
__author__ = 'Parker Skiba'

import requests
import pandas as pd
import pickle


import multiprocessing as mp
import time
import os
import configparser
import concurrent.futures
import json as JS
config = configparser.ConfigParser()

config.read('config.ini')


'''
GLOBALS Adding all the global variables
'''

print(config['SLM']['ssl'])

if str(config['SLM']['ssl']) == 'true':
    HT = 'https://'
else:
    HT = 'http://'

headers_string={"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/37.0.2062.120 Safari/537.36"}

APIUSER = config['SLM']['apiuser']
APIPASS = config['SLM']['apipwd']
APIAUTH = (APIUSER,APIPASS)
CID = config['SLM']['cid']

SNUSER = config['ServiceNow']['user']
SNPASS = config['ServiceNow']['password']
SNINST = config['ServiceNow']['instance']
SNAUTH = (SNUSER,SNPASS)


SNSESSION = requests.Session()
SNSESSION.auth = SNAUTH
SNSESSION.headers = {"Content-Type":"application/json","Accept":"application/json"}

SLMHOST = config['SLM']['hostname']

SLMSESSION = requests.Session()
SLMSESSION.auth = APIAUTH
SLMSESSION.headers.update = headers_s

'''
URI GEN MACHINE
'''


# This function keeps adding 100 more items to pages
def newurlgen(url):
    if '$skip' in url:
        skip_pos = [pos for pos in range(len(url)) if url[pos:].startswith('$skip')]
        skip_prep = url[skip_pos[0]:]
        skip_old = int(skip_prep.replace('$skip=',''))
        skip_new = int(skip_old + 100)
        newurl = url.replace(str(skip_old),str(skip_new))
        return newurl
    else:
        return str(str(url) + str('&$skip=100'))


# This generates a application Name List
def genuriAPPlistJSON(url, nrange):
    id_list = []
    print("Started Genurilist")    
    first_list = getAPPitemsJSON(url)
    try:
        id_list = id_list + first_list
    except:
        id_list = first_list
    newurl = newurlgen(url)
    more_items = True
    while more_items:
        x = getAPPitemsJSON(newurl)
        if x == None:
            print("NO MORE VALUES")
            
            more_items = False
        else:
            
            id_list = id_list + x
            newurl = newurlgen(newurl)
#            print(len(id_list))
    f = open('SnowData/idlist'+str(nrange)+'.pickle','wb')
    pickle.dump(id_list, f)
    f.close()    
    return id_list


# Generates URL List
def genurilistJSON(url, nrange):
    id_list = []
    print("Started Genurilist")    
    first_list = getiditemsJSON(url)
    try:
        id_list = id_list + first_list
    except:
        id_list = first_list
    newurl = newurlgen(url)
    more_items = True
    while more_items:
        x = getiditemsJSON(newurl)
        if x == None:
            print("NO MORE VALUES")
            
            more_items = False
        else:
            
            id_list = id_list + x
            newurl = newurlgen(newurl)
#            print(len(id_list))
    f = open('SnowData/idlist'+str(nrange)+'.pickle','wb')
    pickle.dump(id_list, f)
    f.close()    
    return id_list


#   Get the In line count
def getInlineCountJSON(pages):
    uri = HT+SLMHOST+'/api/customers/'+CID+'/'+pages+'/?$inlinecount=allpages&$format=json'
    print(uri)
    requestJSON = SLMSESSION.get(uri)

    data_dict = requestJSON.json()
    pan = pd.DataFrame(data_dict['Meta'])

    pls = pan.loc[pan['Name']== 'Count']
    return int(pls["Value"].values[0])


def getFInlineCountJSON(urlinput):
    uri = urlinput+'/?$inlinecount=allpages&$format=json'
    print(uri)
    requestJSON = SLMSESSION.get(uri)

    data_dict = requestJSON.json()
    pan = pd.DataFrame(data_dict['Meta'])

    pls = pan.loc[pan['Name']== 'Count']
    return int(pls["Value"].values[0])

def getIdItemsJSONPandas(url):
    pass
    

def getAPPitemsJSON(url):
    try:
        print("Starting Get ID Items")
        print(url)
        df = pd.DataFrame(reqBodyJSON(url))
        
        return ((pd.DataFrame(df['Body'].tolist()))['Name'].tolist())
    except:
        print("##### End of IDs #####")
        print(url)
        pass
    
def getiditemsJSON(url):
    try:
        print("Starting Get ID Items")
        print(url)
        df = pd.DataFrame(reqBodyJSON(url))
        
        return ((pd.DataFrame(df['Body'].tolist()))['Id'].tolist())
    except:
        print("##### End of IDs #####")
        print(url)
        pass
'''
URL STUFF
'''

def urlgen(url, params):
    urllist = []
    urllist.append(url)
    for x in params:
        urllist.append(x)
    
    return str(str('/'.join(urllist))+'/').rstrip('/')

def host_urlgen(hostname, params):
    base_string = (str(HT+'{}/api/customers/'+CID).format(hostname))
    return urlgen(base_string, params)
'''
JSON STUFF
'''
def reqJSON(uri):
    requestJSON = SLMSESSION.get(uri)
    data_dict = requestJSON.json()
    return data_dict


def reqBodyJSON(uri):
    start_time = time.time()

    requestJSON = SLMSESSION.get(uri)
    data_dict = requestJSON.json()
    print('took ',str(time.time() - start_time), 'to pull body')
    return data_dict['Body']

def reqComputerBodyJSON(uri):
    start_time = time.time()

    requestJSON = SLMSESSION.get(uri)
    data_dict = requestJSON.json()
    print('took ',str(time.time() - start_time), 'to pull body')
    data = data_dict['Body']
    appcnt = getFInlineCountJSON(str(uri.replace('/?$format=json','')+'/applications'))
    app_uri = genurilistJSON(str(uri.replace('/?$format=json','')+'/applications/?$format=json'), appcnt)
    print(appcnt)
    data['Applications'] = app_uri
    return pd.Series(data)


def iterpagesJSONFutures(url_list,pages):
    series_list = []
    if pages == 'computers':
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    
            future_to_url = {executor.submit(reqComputerBodyJSON, url): url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    
                    series_list.append(data)
                except Exception as exc:
                    print(url)
                    print(exc)
                else:
                    print('comment')
        return pd.DataFrame(series_list)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    
            future_to_url = {executor.submit(reqBodyJSON, url): url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    
                    series_list.append(pd.Series(data))
                except Exception as exc:
                    print(url)
                    print(exc)
                else:
                    print('comment')
        return pd.DataFrame(series_list)

def url_reap(pages, item_list):
    newrl = str(HT+SLMHOST+'/api/customers/'+CID+'/'+pages)
    return [str(newrl+'/'+str(nuri)+'/?$format=json') for nuri in item_list]
    
    
def test_all_items_futures(pages):
    st= time.time()
    cmpcnt = getInlineCountJSON(pages)
    cmp_url = host_urlgen(SLMHOST, [pages,'?$format=json'])
    cmpuri = genurilistJSON(cmp_url, cmpcnt)
    urls = url_reap(pages, cmpuri)
    comps = iterpagesJSONFutures(urls,pages)
    comps.to_pickle('SnowData/'+str(pages)+'.pickle')
    print('TOOK ',str(time.time()-st),'to finish futures grab')
    print(comps.head(5))
    staging_for_servicenow(comps)


def staging_for_servicenow(dframe):
    record_list = []
    for x in dframe[['Name','Manufacturer','OperatingSystem','IpAddresses']].itertuples():
        record_dictionary = {}
        host = x[1]
        man = x[2]
        os = x[3]
        if not x[4]:
            ip = '0.0.0.0'
        else:
            ip = (x[4])[0]
        print(host,man,os,ip)
        record_dictionary['name'] = host
        record_dictionary['ip_address'] = ip
        record_dictionary['manufacturer'] = man
        record_dictionary['os'] = 'Windows'
        record_list.append(record_dictionary)
    data_json = JS.dumps({"records":record_list})
    json_pickle_dump = open('jsondump.pickle','wb')
    pickle.dump(data_json, json_pickle_dump)
    json_pickle_dump.close()
    post_to_servicenow_jsonv2(data_json)
    
def post_to_servicenow_jsonv2(json_records):
     # Set the request parameters
    url = 'https://dev13758.service-now.com/api/now/table/u_snow_computers'
    
    # Eg. User name="admin", Password="admin" for this code sample.
    user = 'admin'
    pwd = 'Password'
    
    # Set proper headers    
    # Do the HTTP request
    ut = 'https://dev13758.service-now.com/u_snow_computers.do?JSONv2&sysparm_action=insertMultiple'
    response = SNSESSION.post(ut,data=json_records)
    print(response.content)
    print('Posting Computer:')
    # Check for HTTP codes other than 200
    if response.status_code != 200: 
        print('Error')
        print(response.content)
        pass   
    
    
    
def main():
    test_all_items_futures('computers')
main()
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 15:02:40 2016

@author: parker


"""
__author__ = 'Parker Skiba'

import requests
import pandas as pd
import pickle

from datetime import date, datetime
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

THREADS = int(config['Settings']['thread_count'])

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
SLMSESSION.headers.update = headers_string

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
    # print("Started Genurilist")
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
            # print("NO MORE VALUES")
            
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
    # print("Started Genurilist")
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
    # print(uri)
    requestJSON = SLMSESSION.get(uri)

    data_dict = requestJSON.json()
    pan = pd.DataFrame(data_dict['Meta'])

    pls = pan.loc[pan['Name']== 'Count']
    return int(pls["Value"].values[0])


def getFInlineCountJSON(urlinput):
    uri = urlinput+'/?$inlinecount=allpages&$format=json'
    # print(uri)
    requestJSON = SLMSESSION.get(uri)

    data_dict = requestJSON.json()
    pan = pd.DataFrame(data_dict['Meta'])

    pls = pan.loc[pan['Name']== 'Count']
    return int(pls["Value"].values[0])


    

def getAPPitemsJSON(url):
    try:
        # print("Starting Get ID Items")
        # print(url)
        df = pd.DataFrame(reqBodyJSON(url))
        # a = (pd.DataFrame(df['Body'].tolist()))[['Name','ManufacturerName']]
        # print(a)
        
        return (pd.DataFrame(df['Body'].tolist()))[['Name','ManufacturerName']]
    except Exception as e:
        print("##### End of IDs #####")
        print(url)
        print(url)
        print('ERROR: ',e)
        pass
    
def getiditemsJSON(url):
    try:
        # print("Starting Get ID Items")
        # print(url)
        df = pd.DataFrame(reqBodyJSON(url))
        
        return ((pd.DataFrame(df['Body'].tolist()))['Id'].tolist())
    except Exception as e:
        print("##### End of IDs #####")
        print(url)
        print('ERROR: ',e)
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
    return data_dict['Body']

def reqComputerBodyJSON(uri):
    start_time = time.time()

    requestJSON = SLMSESSION.get(uri)
    data_dict = requestJSON.json()



    data_cmp = data_dict['Body']
    appcount = getFInlineCountJSON(str(uri.replace('/?$format=json','')+'/applications'))
    app_uri = genuriAPPlistJSON(str(uri.replace('/?$format=json','')+'/applications/?$format=json'), appcount)

    # Get link to MFU ( Most Frequent User Link )
    try:
        data_link = data_dict['Links']
        mfu_link = (data_link[4])['Href']
        most_frequent_user = (reqBodyJSON(mfu_link))['Username']
        data_cmp['MostFrequentUser'] = most_frequent_user
    except:
        print('!!!No User Link for Device!!!')
        data_cmp['MostFrequentUser'] = ''
    data_cmp['Applications'] = app_uri
    return pd.Series(data_cmp)


def iterpagesJSONFutures(url_list, pages):
    series_list = []
    if pages == 'computers':
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
    
            future_to_url = {executor.submit(reqComputerBodyJSON, url): url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    
                    series_list.append(data)
                except Exception as exc:
                    print(url)
                    print('CONCURRENT ERROR:',exc)
                else:
                    pass
        return pd.DataFrame(series_list)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
    
            future_to_url = {executor.submit(reqBodyJSON, url): url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    
                    series_list.append(pd.Series(data))
                except Exception as exc:
                    print(url)
                    print(exc)
                    print('CONCURRENT ERROR!!')
                else:
                    print('comment')
        return pd.DataFrame(series_list)

def url_reap(pages, item_list):
    newrl = str(HT+SLMHOST+'/api/customers/'+CID+'/'+pages)
    return [str(newrl+'/'+str(nuri)+'/?$format=json') for nuri in item_list]

def check_for_snowdata_folder():
    directory = "SnowData"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    
def test_all_items_futures(pages):
    st= time.time()

    # Make directory if one doesnt exist for SnowData
    check_for_snowdata_folder()

    # Run Functions to recieve Snow Api Data
    cmpcnt = getInlineCountJSON(pages)
    cmp_url = host_urlgen(SLMHOST, [pages,'?$format=json'])
    cmpuri = genurilistJSON(cmp_url, cmpcnt)
    urls = url_reap(pages, cmpuri)
    comps = iterpagesJSONFutures(urls,pages)

    # time_stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    comps.to_pickle('SnowData/'+str(pages)+'.pickle')

    # comps_static = pd.read_pickle('SnowData/computers.pickle')
    # print(len(comps_static))
    # computer_staging_for_servicenow(comps)

def computer_staging_for_servicenow(dframe):
    record_list = []
    software_instance_list = []
    logical_disk_list = []
    network_adapter_list = []
    optical_drive_list = []
    for computer in dframe[['Name','Manufacturer','OperatingSystem','IpAddresses', 'Hardware',\
                     'Domain','IsVirtual','Model','MostFrequentUser','OperatingSystemServicePack', 'Applications']].itertuples():
        record_dictionary = {}

        optical_drive_dict = {}

        hostname = computer[1]
        manufacturer = computer[2]
        operating_system = computer[3]

        domain = computer[6]
        is_virtual = str(computer[7]).title()
        model = computer[8]
        most_frequent_user = computer[9]
        os_service_pack = computer[10]

        applications = computer[11]


        ### HARDWARE ###
        bios_serial_number = (computer[5])['BiosSerialNumber']
        cores_per_processor = (computer[5])['CoresPerProcessor']
        number_of_processors = (computer[5])['NumberOfProcessors']
        physical_memory = (computer[5])['PhysicalMemoryMb']
        processor_type = (computer[5])['ProcessorType']
        total_disk_space = (computer[5])['TotalDiskSpaceMb']
        logical_disks = (computer[5])['LogicalDisks']
        network_adapters = (computer[5])['NetworkAdapters']



        try:
            for app in applications.values:
                software_instance_dict = {}
                software_instance_dict['software'] = app[0]
                software_instance_dict['name'] = app[1]
                software_instance_dict['installed_on'] = hostname
                software_instance_list.append(software_instance_dict)
        except Exception as e:
            print('Incomplete Application Data')
            print(e)

        try:
            for disk in logical_disks:
                logical_disk_dict = {}
                logical_disk_dict['name'] = disk['Name']
                logical_disk_dict['drive_type'] = disk['VolumeName']
                logical_disk_dict['computer'] = hostname
                logical_disk_list.append(logical_disk_dict)
        except Exception as e:
            print('Logical Disk Info')
            print(e)

        try:
            for netad in network_adapters:
                network_adapter_dict = {}
                network_adapter_dict['name'] = netad['Name']
                network_adapter_dict['ip_address'] = netad['IpAddress']
                network_adapter_dict['mac_address'] = netad['']
        except Exception as e:
            print('Logical Disk Info')
            print(e)




        computer_list = [hostname, manufacturer, operating_system, domain, \
              is_virtual, model, most_frequent_user, os_service_pack, \
              bios_serial_number, cores_per_processor, number_of_processors, \
              physical_memory, processor_type, total_disk_space]


        record_dictionary['name'] = hostname
        record_dictionary['manufacturer'] = manufacturer
        record_dictionary['os'] = operating_system
        record_dictionary['serial_number'] = bios_serial_number
        record_dictionary['cpu_core_count'] = cores_per_processor
        record_dictionary['os_domain'] = domain
        record_dictionary['virtual'] = is_virtual
        record_dictionary['model_id'] = model
        record_dictionary['assigned_to'] = most_frequent_user
        record_dictionary['ram'] = physical_memory
        record_dictionary['cpu_type'] = processor_type
        record_dictionary['cpu_name'] = processor_type
        record_dictionary['disk_space'] = total_disk_space
        record_list.append(record_dictionary)
    data_json = JS.dumps({"records": record_list})
    json_pickle_dump = open('jsondump.pickle','wb')
    pickle.dump(data_json, json_pickle_dump)
    json_pickle_dump.close()
    post_to_servicenow_jsonv2(data_json)


# Post to Service_Now with JSONv2 Web Services
def post_to_servicenow_jsonv2(json_records):

    # Set the request parameters
    url = 'https://'+SNINST+'.service-now.com/api/now/table/u_snow_computers'
    
    # Eg. User name="admin", Password="admin" for this code sample.
    user = 'admin'
    pwd = 'Password'
    
    # Set proper headers    
    # Do the HTTP request

    # ut = 'https://' + SNINST + '.service-now.com/u_test_snow_computers?JSONv2&sysparm_action=insertMultiple'
    ut = 'https://'+SNINST+'.service-now.com/x_snsab_snow_cmdb_computerstaging.do?JSONv2&sysparm_action=insertMultiple'
    response = SNSESSION.post(ut,data=json_records)
    print('Posting Computer:')

    # Check for HTTP codes other than 200
    if response.status_code != 200: 
        print('Error')
        print(response.content)
        pass   
    
    
# This is the main function
def main():
    test_all_items_futures('computers')
main()
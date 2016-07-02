# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 15:02:40 2016

@author: parker


"""
__author__ = 'Parker Skiba'

import requests
import pandas as pd
import pickle
import decimal


from datetime import date, datetime
import multiprocessing as mp
import time
import os
import configparser
import concurrent.futures
import json as JS
config = configparser.ConfigParser()

config.read('config.ini')

idl = open('missinglist.pickle', 'rb')
MISSING = pickle.load(idl)
idl.close()

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
def get_applications_for_computer(url):
    pass


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

def get_applications_for_computer(uri_list):
    computer_applications = []
    for url in uri_list:
        apps_body = getAPPitemsJSON(url)
        computer_applications.append(apps_body)
    return computer_applications



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
    print(uri)
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


def get_basic_info(url, info_list):
    series_list = []
    try:

        temp = reqBodyJSON(url)
        x = (pd.DataFrame(temp)['Body'])
        df = (pd.DataFrame(list(x.values)))

        # return temp
        return df


    except Exception as e:
        print(url)
        print("BASIC INFO ERROR:", e)



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
    print(uri)

    requestJSON = SLMSESSION.get(uri)
    data_dict = requestJSON.json()



    data_cmp = data_dict['Body']
    computer_id = data_cmp['Id']
    appcount = getFInlineCountJSON(str(uri.replace('/?$format=json','')+'/applications'))
    # print(appcount)
    basic_pages = [page_skip for page_skip in range(0, (appcount + 100), 100)]
    basic_urls = gen_basic_page_urls(str(uri.replace('/?$format=json','')+'/applications/?$format=json'), basic_pages, str('computers/'+str(computer_id)+'/applications'))
    # print(basic_urls)
    applications = get_applications_for_computer(basic_urls)
    apps = pd.concat(applications)

    # app_uri = genuriAPPlistJSON(str(uri.replace('/?$format=json','')+'/applications/?$format=json'), appcount)

    # Get link to MFU ( Most Frequent User Link )
    try:
        data_link = pd.DataFrame(data_dict['Links'])
        ref_link = []


        dl = (data_link.loc[data_link['Rel'] == 'MostFrequentUser'])['Href']
        print("MFU = ", dl.values[0])

        most_frequent_user = (reqBodyJSON(dl.values[0])['Username'])
        print(most_frequent_user)
        data_cmp['MostFrequentUser'] = most_frequent_user
    except Exception as e:
        print('!!!No User Link for Device!!!')
        print(e)
        data_cmp['MostFrequentUser'] = ''

    try:
        data_cmp['Applications'] = apps
    except:
        print("Applications Error")
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
    elif pages == 'users' or pages == 'applications':
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:

            future_to_url = {executor.submit(get_basic_info, url, []):\
                                 url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()

                    series_list.append(data)
                except Exception as exc:
                    print(url)
                    print('CONCURRENT ERROR:', exc)
                else:
                    pass

        return series_list
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

def gen_basic_page_urls(base_url, page_numbers, pages):
    pages_list = [base_url]
    for page in page_numbers[1:]:
        url = str(HT + SLMHOST + '/api/customers/' + CID + '/'+ pages+'/?$format=json&$skip='+str(page))
        pages_list.append(url)
    return pages_list


def get_items_async(pages):
    # Run Functions to recieve Snow Api Data
    if pages == 'users' or pages == 'applications':
        in_line_count = getInlineCountJSON(pages)
        base_url = host_urlgen(SLMHOST, [pages,'?$format=json'])
        print(in_line_count)
        basic_pages = [page_skip for page_skip in range(0,(in_line_count+100),100)]
        basic_urls = gen_basic_page_urls(base_url, basic_pages, pages)
        items = iterpagesJSONFutures(basic_urls, pages)

        df = pd.concat(items, ignore_index=True)

        df.to_pickle('SnowData/'+str(pages)+'.pickle')

        return df
    elif pages == 'targetcomputer':
        print("GETTING MISSING COMPUTERS")
        urls = url_reap('computers',MISSING)
        items = iterpagesJSONFutures(urls, 'computers')

        items.to_pickle('missingcomputers.pickle')


    else:

        cmpcnt = getInlineCountJSON(pages)
        print("INLINE COUNT FOR {} IS {}".format(pages,cmpcnt))
        cmp_url = host_urlgen(SLMHOST, [pages,'?$format=json'])
        cmpuri = genurilistJSON(cmp_url, cmpcnt)
        urls = url_reap(pages, cmpuri)
        # print(urls)
        comps = iterpagesJSONFutures(urls,pages)

        # time_stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        comps.to_pickle('SnowData/'+str(pages)+'.pickle')
        return comps


def u_staging_for_servicenow(user_df):
    users_list = []
    user_df['Email'] = ''
    user_df['PhoneNumber'] = ''

    for user in (user_df[['FullName', 'Username', 'Email', 'PhoneNumber']]).itertuples():
        user_dict = {}

        full_name = str(user[1]).split()
        first_name = full_name[0]
        last_name = " ".join(full_name[1:])

        username = user[2]
        email = user[3]
        phone_number = user[4]

        user_dict['first_name'] = first_name
        user_dict['last_name'] = last_name
        user_dict['email'] = email
        user_dict['user_name'] = username
        user_dict['phone'] = phone_number
        users_list.append(user_dict)

    users_tup = ('x_snsab_snow_cmdb_userstaging', users_list)
    return users_tup



def a_staging_for_servicenow(application_df):
    software_list = []
    for application in (application_df[['Name', 'ManufacturerName']]).itertuples():
        app_dict = {}
        app_name = application[1]
        manufacturer_name = application[2]

        app_dict['name'] = app_name
        app_dict['manufacturer'] = manufacturer_name
        software_list.append(app_dict)

    software_tup = ('x_snsab_snow_cmdb_softwarestaging', software_list)
    return software_tup


def computer_staging_for_servicenow(dframe):

    print("$$$$ STARTING STAGING $$$$$$")
    record_list = []
    software_instance_list = []
    logical_disk_list = []
    network_adapter_list = []
    optical_drive_list = []
    for computer in dframe[['Name','Manufacturer','OperatingSystem','IpAddresses', 'Hardware',\
                     'Domain','IsVirtual','Model','MostFrequentUser','OperatingSystemServicePack', 'Applications']].itertuples():
        record_dictionary = {}



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
        optical_drives = (computer[5])['OpticalDrives']

        try:

            for app in pd.DataFrame((applications.values)).itertuples():
                software_instance_dict = {}
                software_instance_dict['name'] = app[1]
                software_instance_dict['manufacturer'] = app[2]
                software_instance_dict['installed_on'] = hostname
                software_instance_list.append(software_instance_dict)
        except Exception as e:
            print(hostname)
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
            print('Logical Disk Info Incomplete')
            print(e)

        try:
            for netad in network_adapters:
                network_adapter_dict = {}
                network_adapter_dict['name'] = netad['Name']
                network_adapter_dict['ip_address'] = netad['IpAddress']
                network_adapter_dict['mac_address'] = netad['MacAddress']
                network_adapter_dict['cmdb_ci'] = hostname
                network_adapter_list.append(network_adapter_dict)
        except Exception as e:
            print('Network Adapter Info Incomplete')
            print(e)

        try:
            for opt_drive in optical_drives:
                optical_drive_dict = {}
                optical_drive_dict['name'] = opt_drive['Name']
                optical_drive_dict['drive_type'] = opt_drive['Type']
                optical_drive_dict['computer'] = hostname
                optical_drive_list.append(optical_drive_dict)

        except Exception as e:
            print('Optical Drive Info Incomplete')
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

    # #Dumpt Computers
    # computers_data_json = JS.dumps({"records": record_list})
    # logical_disk_data_json = JS.dumps({"records": logical_disk_list})
    # optical_drive_data_json = JS.dumps({"records": optical_drive_list})
    # network_adapter_data_json = JS.dumps({"records": network_adapter_list})
    # software_instance_data_json = JS.dumps({"records": software_instance_list})




    # print("Applications:", len(software_list))
    #
    # computers_tup = (computers_data_json, 'x_snsab_snow_cmdb_computerstaging')
    # log_disk_tup = (logical_disk_data_json, 'x_snsab_snow_cmdb_diskstaging')
    # net_ad_tup = (network_adapter_data_json, 'x_snsab_snow_cmdb_networkadapterstaging')
    # soft_inst_tup = (software_instance_data_json, 'x_snsab_snow_cmdb_softwareinstancestagin')

    assets_list = [('x_snsab_snow_cmdb_computerstaging',record_list),\
                   ('x_snsab_snow_cmdb_diskstaging', logical_disk_list), \
                   ('x_snsab_snow_cmdb_diskstaging', optical_drive_list), \
                   ('x_snsab_snow_cmdb_networkadapterstaging', network_adapter_list),\
                   ('x_snsab_snow_cmdb_softwareinstancestagin', software_instance_list)]

    return assets_list


def async_post_json_chuncks(concurrent_assets_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_jsonv2post = {executor.submit(post_to_servicenow_jsonv2, asset): asset for asset in concurrent_assets_list}
        for future in concurrent.futures.as_completed(future_to_jsonv2post):
            xml = future_to_jsonv2post[future]
            try:
                data = future.result()
                print("posted successfully")
            except Exception as exc:
                # print(url)
                print("FUCK")
                print(exc)
            else:
                print('POSTED')


def gen_json_post_list(asset_list_tupples):
    futures_list = []
    for asset_tupple in asset_list_tupples:
        chunked_list = [(asset_tupple[1])[i:i+400] for i in range(0, len(asset_tupple[1]), 400)]
        for chunk in chunked_list:
            json_dump_chunk = JS.dumps({"records":chunk})
            json_tupple = (json_dump_chunk, str(asset_tupple[0]))
            futures_list.append(json_tupple)

    f = open('flist', 'w')
    f.write(str(futures_list))
    f.close()

    return futures_list


# Post to Service_Now with JSONv2 Web Services
def post_to_servicenow_jsonv2(json_records):

    # ut = 'https://' + SNINST + '.service-now.com/u_test_snow_computers?JSONv2&sysparm_action=insertMultiple'
    ut = 'https://'+SNINST+'.service-now.com/'+json_records[1]+'.do?JSONv2&sysparm_action=insertMultiple'
    print(ut)
    response = requests.post(ut, data=json_records[0], auth=SNAUTH)

    f = open('debug.txt', 'w')
    f.write(json_records[0])
    g = open('response.txt','wb')
    g.write(response.content)
    # Check for HTTP codes other than 200
    if response.status_code != 200: 
        print('Error')
        print(response.content)
        pass   
    f.close()
    g.close()


def upload_ordered_assets_list( users, apps, computers):
    users_tupple = u_staging_for_servicenow(users)
    apps_tupple = a_staging_for_servicenow(apps)
    computer_tupple_list = computer_staging_for_servicenow(computers)

    # concurrent_assets_list = gen_json_post_list(assets_list)
    #
    # async_post_json_chuncks(concurrent_assets_list)

    users_chunked = gen_json_post_list([users_tupple])
    apps_chunked = gen_json_post_list([apps_tupple])
    computers_chunked = gen_json_post_list(computer_tupple_list)
    #
    print("Posting Users")
    async_post_json_chuncks(users_chunked)

    print("Posting Applications")
    async_post_json_chuncks(apps_chunked)

    print("Posting Computers")
    async_post_json_chuncks(computers_chunked)

def test_all_items_futures(pages):
    #
    # # Make directory if one doesnt exist for SnowData
    check_for_snowdata_folder()
    #

    users_static = get_items_async('users')

    apps_static = get_items_async('applications')

    comps_static = get_items_async('computers')
    # missing_comp = get_items_async('targetcomputer')

    # users_static = pd.read_pickle('SnowData/users.pickle')
    # apps_static = pd.read_pickle('SnowData/applications.pickle')
    # comps_static = pd.read_pickle('SnowData/computers.pickle')


    upload_ordered_assets_list(users_static, apps_static, comps_static)






# This is the main function
def main():
    s = time.time()
    test_all_items_futures('computers')


    print('EXECUTION TIME: ', str(time.time()-s))

if __name__ == '__main__':
    main()
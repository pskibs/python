# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 11:25:01 2016

@author: parker
"""
import pandas as pd
from collections import OrderedDict
from lxml import etree as et

import os


# This is kind of pointless, but in case I need to return all object attributes

class IterMixin(object):
    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value


# Super Class, In case I want inheritance
class SnowXML(IterMixin):
    __isOptional = True

    def getIsOptional(self):
        return self.__isOptional

    def setIsOptional(self, isOptional):
        self.__isOptional = isOptional


class Client(SnowXML):
    # reusableValues
    na = '(n/a)'
    ddate = '1900-01-01T12:00:00'
    tdate = '2016-03-09T11:04:19'

    def __init__(self, hostname):
        self.setIsOptional(False)

        # Application Object list
        self.applications = []

        # Client object components
        self.memory = object
        self.networkadapter = object
        self.os = object
        self.processor = object

        # properties for Client
        self.properties = OrderedDict()
        self.properties['isdmisupported'] = False
        self.properties['isapmsupported'] = False
        self.properties['isplugandplay'] = False
        self.properties['primarybustype'] = False
        self.properties['secondarybustype'] = False
        self.properties['hasusb'] = False
        self.properties['biosreleasedate'] = self.ddate
        self.properties['biosmanufacturer'] = 'Dell'
        self.properties['biosserialnumber'] = '123ABC'
        self.properties['biosversion'] = self.na
        self.properties['company'] = self.na
        self.properties['dmiversion'] = False
        self.properties['hasflashbios'] = False
        self.properties['hostname'] = hostname
        self.properties['isportable'] = False
        self.properties['lastupdate'] = self.tdate
        self.properties['numberofprocessors'] = 1
        self.properties['manufacturer'] = 'Dell'
        self.properties['model'] = 'PowerEdge 710'
        self.properties['username'] = 'defaultuser'
        self.properties['installdate'] = self.ddate
        self.properties['sitename'] = 'default'
        self.properties['clientidentifier'] = hostname
        self.properties['clienttype'] = 0
        self.properties['isvdi'] = False


class Memory(SnowXML):
    def __init__(self):
        # Properties with default values
        self.properties = OrderedDict()
        self.properties['freeslots'] = 0
        self.properties['freeswap'] = 0
        self.properties['maxphysical'] = 0
        self.properties['totalslots'] = 0
        self.properties['totalphysical'] = 0
        self.properties['totalvirtual'] = 0
        self.properties['freevirtual'] = 0
        self.properties['freephysical'] = 0
        self.properties['totalswap'] = 0


class NetworkAdapter(SnowXML):
    def __init__(self):
        # Properties with default values
        self.properties = OrderedDict()
        self.properties['dnsserver'] = 0
        self.properties['macaddress'] = 0
        self.properties['productname'] = 0
        self.properties['defaultipgateway'] = 0
        self.properties['dhcpenabled'] = True
        self.properties['ipaddress'] = '0.0.0.0'
        self.properties['ipsubnet'] = 0
        self.properties['dhcpserver'] = 0


class OperatingSystem(SnowXML):
    def __init__(self):
        # Properties with default values
        self.properties = OrderedDict()
        self.properties['activedesktop'] = 0
        self.properties['cdkey'] = 0
        self.properties['defaultbrowser'] = 0
        self.properties['tempdirectory'] = 0
        self.properties['username'] = 0
        self.properties['useruilanguage'] = 0
        self.properties['buildnumber'] = 0
        self.properties['buildtype'] = 0
        self.properties['codeset'] = 0
        self.properties['computername'] = 0
        self.properties['countrycode'] = 0
        self.properties['currenttimezonecode'] = 0
        self.properties['domainname'] = 0
        self.properties['localecode'] = 0
        self.properties['manufacturer'] = 'Microsoft'
        self.properties['name'] = 'Windows Server 2008 R2 Enterprise Edition'
        self.properties['organization'] = 0
        self.properties['registereduser'] = 0
        self.properties['serialnumber'] = 0
        self.properties['systemdirectory'] = 0
        self.properties['systemuilanguagecode'] = 0
        self.properties['version'] = 6.1
        self.properties['versioninfo'] = 'Service Pack 1'
        self.properties['windowsdirectory'] = 0


class Processor(SnowXML):
    def __init__(self):
        # Properties with Default values
        self.properties = OrderedDict()
        self.properties['hyperthreading'] = 1
        self.properties['mathcoprocessor'] = 1
        self.properties['mmx'] = 1
        self.properties['numberofcores'] = 4
        self.properties['voltage'] = 4
        self.properties['currentclockspeed'] = 3000
        self.properties['manufacturer'] = 'Intel'
        self.properties['maxclockspeed'] = 3000
        self.properties['name'] = 'Xeon E5500'
        self.properties['processorid'] = 0
        self.properties['model'] = 'Xeon E5500'
        self.properties['numberofprocessors'] = 2


class Application(SnowXML):
    # reusableValues
    na = '(n/a)'
    ddate = '1900-01-01T12:00:00'

    # Instantiate Application
    def __init__(self, name):
        # properties with default values
        self.properties = OrderedDict()
        self.properties['binarytype'] = 0
        self.properties['format'] = 0
        self.properties['installdate'] = self.ddate
        self.properties['name'] = name
        self.properties['islocal'] = True
        self.properties['ismsi'] = True
        self.properties['isshortcut'] = True
        self.properties['processortype'] = 0
        self.properties['uninstallstring'] = 0
        self.properties['filename'] = self.na
        self.properties['filepath'] = self.na
        self.properties['filedatetime'] = self.ddate
        self.properties['filesize'] = 0
        self.properties['version'] = 2012
        self.properties['manufacturer'] = self.na
        self.properties['language'] = 'Language Neutral'
        self.properties['fullcappeakdate'] = self.ddate
        self.properties['isrecognized'] = True
        self.properties['coresublimit'] = 0
        self.properties['issubcapacity'] = False
        self.properties['subcappeakdate'] = self.ddate
        self.properties['pvusubcap'] = 0
        self.properties['ispvu'] = False
        self.properties['coresubcap'] = 0
        self.properties['pvusublimit'] = 0


# root is the xml object, parent is a string and children
#   are the dict values.



def build_xml(root, parent, children):
    # if there are children ie application, or memory
    if parent != None:
        par = et.SubElement(root, parent)
        for k, v in children.items():
            subel = et.SubElement(par, k)

            # Convert Boolean Values to lowercase
            if type(v) is bool:
                textv = str(v)
                subel.text = textv.lower()
            else:
                subel.text = str(v)
    else:
        for k, v in children.items():
            subel = et.SubElement(root, k)
            if type(v) is bool:
                textv = str(v)
                subel.text = textv.lower()
            else:
                subel.text = str(v)

    xml = et.tostring(root, pretty_print=True)
    formatted_xml = xml.decode('ascii')
    return formatted_xml


# Prints nice separator for Debugging
def printsep():
    print("#" * 70)


def printFXML(xml):
    xmls = et.tostring(xml, pretty_print=True)
    formatted_xml = xmls.decode('ascii')
    print(formatted_xml)


def retFXML(xml):
    xmls = et.tostring(xml, pretty_print=True)
    formatted_xml = xmls.decode('ascii')
    return formatted_xml


# print Elements of XML in nice table!!!
def printel(d):
    for e in d.iter():
        print("| {} : {}".format(e.tag, e.text))
        print("-" * 70)


def export_XMLFile(formatted_xml, filename):
    file = open(str(filename + '.xml'), 'w', encoding='utf-8')
    file.write(formatted_xml)
    file.close()


# Builds the XML File
def build_snowXML(client):
    # Create the XML Object
    ROOT = et.Element('client')

    # Build Client Properties
    build_xml(ROOT, None, client.properties)
    build_xml(ROOT, 'memory', client.memory.properties)
    # Loop through applications
    for app in client.applications:
        build_xml(ROOT, 'application', app.properties)

    build_xml(ROOT, 'networkadapter', client.networkadapter.properties)
    build_xml(ROOT, 'operatingsystem', client.os.properties)
    build_xml(ROOT, 'processor', client.processor.properties)

    return ROOT


def get_client_number(data, groupname):
    return len(data.groupby(groupname))


def generate_clients(df, groupname):
    clientlist = []
    for index, data in df.groupby(groupname):
        client = Client(index)
        mem = Memory()
        netad = NetworkAdapter()
        os = OperatingSystem()
        proc = Processor()

        client.memory = mem
        client.networkadapter = netad
        client.os = os
        client.processor = proc

        print(groupname + ": ", index)
        for row in data.itertuples():
            app = Application(row[1])
            app.properties['version'] = row[2]
            #            for i in range(len(row)):
            #                print(i,":",row[i])
            client.applications.append(app)
        # Add client to array
        clientlist.append(client)
    return (clientlist)


#   Export Clients to Files
def export_clients(clients):
    directory = "SnowXML"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for client in clients:
        xml = build_snowXML(client)
        fxml = retFXML(xml)
        printFXML(xml)
        export_XMLFile(fxml, str(r'SnowXML/' + str(client.properties['hostname'])))


#   Main Program Fucntion
def main():
    # Path to CSV File
    csvpath = 'sds.csv'

    #
    groupmap = 'ComputerName'

    df = pd.read_csv(csvpath)

    print()
    printsep()

    #Get the nnumber of lients
    print(get_client_number(df, groupmap))

    # Print Separators
    printsep()

    # Get a list of the Clients
    clients = generate_clients(df, groupmap)
    export_clients(clients)


    print("FINISHED")


main()
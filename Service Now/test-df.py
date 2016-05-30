import pandas as pd
import pickle
from datetime import date,datetime


# pklf = open('SnowData/idlist729.pickle', 'rb')
# idl = pickle.load(pklf)
# pklf.close()
#
# print(idl)

def ps():
    print("*"*100)

df = pd.read_pickle('SnowData/computers.pickle')
hw = df.head(1)
print(df['Applications'])
print(hw['MostFrequentUser'])

# for h in hw[0].items():
#     print(h)

data = df[['Name','Manufacturer','OperatingSystem','IpAddresses', 'Hardware', 'OperatingSystemServicePack','Applications']]

for computer in data[:5].itertuples():

    print(computer[6])

    ps()
    #BIOS SN
    bios_serial_number = (computer[5])['BiosSerialNumber']
    print(bios_serial_number)
    ps()

    # Cores Per Processor
    cores_per_processor = (computer[5])['CoresPerProcessor']
    print(cores_per_processor)
    ps()

    # Number of Processors
    number_of_processors = (computer[5])['NumberOfProcessors']
    print(number_of_processors)
    ps()

    # Physical Memory MB
    physical_memory = (computer[5])['PhysicalMemoryMb']
    print(physical_memory)
    ps()

    # Processor Type
    processor_type = (computer[5])['ProcessorType']
    print(processor_type)
    ps()

    # Total Disk Space MB
    total_disk_space = (computer[5])['TotalDiskSpaceMb']
    print(total_disk_space)
    ps()

    # Logical Disks
    logical_disks = (computer[5])['LogicalDisks']
    for disk in logical_disks:
        print(disk['Name'])
    print(logical_disks)
    ps()

    # # Network Adadapters
    network_adapters  = (computer[5])['NetworkAdapters']
    print(network_adapters)
    ps()

    # Optical Drives
    optical_drives = (computer[5])['OpticalDrives']
    print(optical_drives)
    ps()

    # # Applications
    # applications = (computer[7])
    # for x in applications.values:
    #     print(x[1])
    # ps()



d_test = df[:5]


#
# for computer in d_test[['Name', 'Manufacturer', 'OperatingSystem', 'IpAddresses', 'Hardware', \
#                         'Domain', 'IsVirtual', 'Model', 'MostFrequentUser',
#                         'OperatingSystemServicePack' ]].itertuples():
#     record_dictionary = {}
#     hostname = computer[1]
#     manufacturer = computer[2]
#     operating_system = computer[3]
#
#     domain = computer[6]
#     is_virtual = computer[7]
#     model = computer[8]
#     most_frequent_user = computer[9]
#     os_service_pack = computer[10]
#
#     ### HARDWARE ###
#     bios_serial_number = (computer[5])['BiosSerialNumber']
#     cores_per_processor = (computer[5])['CoresPerProcessor']
#     number_of_processors = (computer[5])['NumberOfProcessors']
#     physical_memory = (computer[5])['PhysicalMemoryMb']
#     processor_type = (computer[5])['ProcessorType']
#     total_disk_space = (computer[5])['TotalDiskSpaceMb']
#     ps()
#     print('hostname:',hostname, \
#           '\nmanufacturer:',manufacturer, \
#           '\noperating_system:',operating_system, \
#           '\ndomain:',domain, \
#           '\nis_virtual:',is_virtual, \
#           '\nmodel:',model, \
#           '\nmost_frequent_user:',most_frequent_user, \
#           '\nos_service_pack:',os_service_pack, \
#           '\nbios_serial_number:',bios_serial_number, \
#           '\ncores_per_processor:',cores_per_processor, \
#           '\nnumber_of_processors:',number_of_processors, \
#           '\nphysical_memory:',physical_memory, \
#           '\nprocessor_type:',processor_type, \
#           '\ntotal_disk_space:',total_disk_space)


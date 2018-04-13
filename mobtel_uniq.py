# CDR parser for VBTS reports
# v2.0 Feb 2, 2018
# CAB


import csv
import sys

try:
    site = sys.argv[1]
    month = sys.argv[2]
    year = sys.argv[3]
except IndexError:
    print "Missing args!!!"
    print "Usage: python ./mobtel_uniq.py  {site #} {month} {year}"
    print "Example: python ./mobtel_uniq.py site1 01 2018"
    quit()


def str2num(coststr):
    try:
        ret = float(coststr.replace(',', ''))
    except ValueError:
        ret = 0
    return ret

mergepoolimsis=[]

for i in range(01,32):
    if i < 10:
        fname = "./daily_S%s/vbts_konekt_%s_%s-0%s-%s.csv" % (site[4:], site, month, i, year)
    else:
        fname = "./daily_S%s/vbts_konekt_%s_%s-%s-%s.csv" % (site[4:], site, month, i, year)

    # input the imsis for the vendors, coop and test sims
    vendor_list = []
    coop_list = []
    test_sim_list = []

    retailer_list = coop_list + vendor_list

    unique_loader_list = []
    unique_subs = []


    try:
        with open(fname) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                imsi = row['Subscriber IMSI']
                if imsi in test_sim_list:
                    continue

                event_type = row['Type of Event']
                
                # Money events
                if imsi not in retailer_list:
                    # lets count actual subscribers
                    if imsi not in unique_loader_list and event_type == 'transfer':
                        unique_loader_list.append(imsi)
                    elif imsi not in unique_subs:
                        unique_subs.append(imsi)

        uniq_mobtels = list(set(unique_loader_list) - set(mergepoolimsis))
        print "%s: %s" % (fname, len(uniq_mobtels))
        mergepoolimsis += unique_loader_list
    except:
        pass

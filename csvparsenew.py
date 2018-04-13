# CDR parser for VBTS reports
# 2.0 Feb 2, 2018
# CAB

import csv
import sys

try:
    fname = sys.argv[1]
    site = fname[12:17]
except IndexError:
    print "Missing args!!!"
    print "Usage: python ./csvparsenew.py  {filename}"
    quit()

def str2num(coststr):
    try:
        ret = float(coststr.replace(',', ''))
    except ValueError:
        ret = 0
    return ret


events = ["local_call", "local_sms", "outside_call", "outside_sms",
          "free_call", "free_sms", "incoming_sms", "error_sms",
          "error_call", "transfer", "add_money", "deduct_money",
          "set_balance", "unknown", "Provisioned", "local_recv_call",
          "local_recv_sms", "incoming_call", "gprs"]
call_events = ["local_call", "outside_call",
               "free_call",
               "error_call", "local_recv_call",
               "incoming_call"]
sms_events = ["local_sms", "outside_sms",
              "free_sms", "incoming_sms", "error_sms",
              "local_recv_sms"]

#input the imsis here
vendor_list_site1 = []
vendor_list_site2 = []
vendor_list_site3 = []
coop_list = []

retailer_list = coop_list + \
                vendor_list_site1 +\
                vendor_list_site2 +\
                vendor_list_site3

#input the imsis here
test_sim_list = []

prefix_globe = [
    '63905',
    '63906',
    '63915',
    '63916',
    '63917',
    '63926',
    '63927',
    '63935',
    '63945',
    '63955',
    '63956',
    '63966',
    '63975',
    '63976',
    '63977',
    '63995',
    '63997',
]

prefix_globe_abscbn = ['63937']

prefix_globe_cherry = ['63996']

prefix_smart = [
    '63918',
    '63919',
    '63920',
    '63921',
    '63928',
    '63929',
    '63938',
    '63939',
    '63946',
    '63947',
    '63948',
    '63949',
    '63950',
    '63962',
    '63998',
    '63999',
]

prefix_smart_piltel = [
    '63907',
    '63908',
    '63909',
    '63910',
    '63912',
    '63930',
]

prefix_sun = [
    '63922',
    '63923',
    '63925',
    '63931',
    '63932',
    '63933',
    '63942',
    '63943',
]

prefix_tmbrgy = ['63936']

prefixes = ['globe', 'tmbrgy', 'globe_abscbn', 'globe_cherry', 'sun', 'smart',
            'smart_piltel', 'others']
inter_globe = ['globe', 'globe_abscbn', 'globe_cherry', 'tmbrgy']
inter_smart = ['sun', 'smart', 'smart_piltel']

count = {}
event_count = {}
event_cost = {}
unique_loader_list = []
retailer_stats = {}

for event in events:
    count[event] = 0
    if event in ['outside_sms', 'outside_call', 'incoming_sms', 'incoming_call']:
        event_count[event] = {}
        event_cost[event] = {}
        for prefix in prefixes:
            event_count[event][prefix] = 0
            event_cost[event][prefix] = 0
    else:
        event_count[event] = 0
        event_cost[event] = 0

for imsi in retailer_list:
    retailer_stats[imsi] = {
        'load_sales': 0,
        'top_up': 0,
        'personal_use': 0
    }


with open(fname) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        imsi = row['Subscriber IMSI']
        if imsi in test_sim_list:
            continue

        event_type = row['Type of Event']
        from_num = row['From Number']
        to_num = row['To Number']
        cost = str2num(row["Cost (PHP)"])

        count[event_type] += 1

        # Money events
        if imsi in retailer_list:
            if event_type == "transfer":
                if cost > 0:  # this is the coop transferring load to retailer
                    retailer_stats[imsi]['top_up'] += cost
                else:
                    retailer_stats[imsi]['load_sales'] += cost
            elif event_type == "add_money":
                retailer_stats[imsi]['top_up'] += cost
            elif event_type == 'deduct_money':
                retailer_stats[imsi]['top_up'] -= cost
            else:
                retailer_stats[imsi]['personal_use'] += cost

        else:
            # lets count actual subscribers
            if imsi not in unique_loader_list and event_type == 'transfer':
                unique_loader_list.append(imsi)

        # Check call events
        if event_type[-4:] == "call":
            call_duration = str2num(row['Billable Call Duration (sec)'])

            if event_type in ['incoming_call', 'outside_call']:
                if event_type == 'incoming_call':
                    num = '63' + from_num  # they don't have the 63 prefix
                else:
                    if to_num[:2] == '09':
                        num = '63' + to_num[1:]
                    elif to_num[:1] == '+':
                        num = to_num[1:]
                    else:
                        num = to_num

                if num[:5] in prefix_globe:
                    event_count[event_type]['globe'] += call_duration
                    event_cost[event_type]['globe'] += cost
                elif num[:5] in prefix_globe_abscbn:
                    event_count[event_type]['globe_abscbn'] += call_duration
                    event_cost[event_type]['globe_abscbn'] += cost
                elif num[:5] in prefix_globe_cherry:
                    event_count[event_type]['globe_cherry'] += call_duration
                    event_cost[event_type]['globe_cherry'] += cost
                elif num[:5] in prefix_smart:
                    event_count[event_type]['smart'] += call_duration
                    event_cost[event_type]['smart'] += cost
                elif num[:5] in prefix_smart_piltel:
                    event_count[event_type]['smart_piltel'] += call_duration
                    event_cost[event_type]['smart_piltel'] += cost
                elif num[:5] in prefix_sun:
                    event_count[event_type]['sun'] += call_duration
                    event_cost[event_type]['sun'] += cost
                elif num[:5] in prefix_tmbrgy:
                    event_count[event_type]['tmbrgy'] += call_duration
                    event_cost[event_type]['tmbrgy'] += cost
                else:
                    event_count[event_type]['others'] += call_duration
                    event_cost[event_type]['others'] += cost

            else:
                event_count[event_type] += call_duration
                event_cost[event_type] += cost

        # Check SMS events
        elif event_type[-3:] == "sms":
            if event_type in ['incoming_sms', 'outside_sms']:

                if event_type == 'incoming_call':
                    num = from_num
                else:
                    num = to_num

                if num[:5] in prefix_globe:
                    event_count[event_type]['globe'] += 1
                    event_cost[event_type]['globe'] += cost
                elif num[:5] in prefix_globe_abscbn:
                    event_count[event_type]['globe_abscbn'] += 1
                    event_cost[event_type]['globe_abscbn'] += cost
                elif num[:5] in prefix_globe_cherry:
                    event_count[event_type]['globe_cherry'] += 1
                    event_cost[event_type]['globe_cherry'] += cost
                elif num[:5] in prefix_smart:
                    event_count[event_type]['smart'] += 1
                    event_cost[event_type]['smart'] += cost
                elif num[:5] in prefix_smart_piltel:
                    event_count[event_type]['smart_piltel'] += 1
                    event_cost[event_type]['smart_piltel'] += cost
                elif num[:5] in prefix_sun:
                    event_count[event_type]['sun'] += 1
                    event_cost[event_type]['sun'] += cost
                elif num[:5] in prefix_tmbrgy:
                    event_count[event_type]['tmbrgy'] += 1
                    event_cost[event_type]['tmbrgy'] += cost
                else:
                    event_count[event_type]['others'] += 1
                    event_cost[event_type]['others'] += cost


            else:
                event_count[event_type] += 1
                event_cost[event_type] += cost
        else:
            event_count[event_type] += 1
            event_cost[event_type] += cost

per_network = {}
per_network_cost = {}
for event in ['incoming_call', 'incoming_sms', 'outside_call', 'outside_sms']:
    per_network[event] = {}
    per_network_cost[event] = {}
    per_network[event]['inter_globe'] = 0
    per_network[event]['inter_smart'] = 0
    per_network_cost[event]['inter_globe'] = 0
    per_network_cost[event]['inter_smart'] = 0
    for prefix in inter_globe:
        per_network[event]['inter_globe'] += event_count[event][prefix]
        per_network_cost[event]['inter_globe'] += event_cost[event][prefix]
    for prefix in inter_smart + ['others']:
        per_network[event]['inter_smart'] += event_count[event][prefix]
        per_network_cost[event]['inter_smart'] += event_cost[event][prefix]

print "################################################"
print "STATS for %s" % fname
print "################################################\n"

print "************ ACTIVATION ************************"
print "Gross Activation:\t%s" % event_count['Provisioned']
print "Churn:\tNA"
print "Unique Loaders:\t%s" % len(unique_loader_list)
print "\n"


print "************ GROSS REVENUE *********************"
print "OUTBOUND"
print "\tVoice"
print "Voice intra (mins):\t\t%.2f" % (event_cost['local_call']*-1)
print "Voice inter, Globe (mins)\t%.2f" % (per_network_cost['outside_call']['inter_globe']*-1)
print "Voice inter, Others (mins)\t%.2f" % (per_network_cost['outside_call']['inter_smart']*-1)

print "\tSMS"
print "SMS intra:\t\t%s" % (event_cost['local_sms']*-1)
print "SMS inter, Globe\t%s" % (per_network_cost['outside_sms']['inter_globe']*-1)
print "SMS inter, Others\t%s" % (per_network_cost['outside_sms']['inter_smart']*-1)
print "\n"

# keeping this, may still be useful in the future - claire
# print "INBOUND"
# print "Voice intra (mins):\t%.2f" % (event_count['local_recv_call'])
# print "Voice inter, Globe (mins)\t%.2f" % (per_network['incoming_call']['inter_globe'])
# print "Voice inter, Others (mins)\t%.2f" % (per_network['incoming_call']['inter_smart'])

# print "SMS intra:\t%s" % event_count['local_recv_sms']
# print "SMS inter, Globe\t%s" % per_network['incoming_sms']['inter_globe']
# print "SMS inter, Others\t%s" % per_network['incoming_sms']['inter_smart']
# print "\n"


print "************ TRAFFIC ***************************"
print "OUTBOUND TRAFFIC, "
print "\tVoice"
print "Voice intra (mins):\t\t%.2f" % (event_count['local_call']/60)
print "Voice inter, Globe (mins)\t%.2f" % (per_network['outside_call']['inter_globe']/60)
print "Voice inter, Others (mins)\t%.2f" % (per_network['outside_call']['inter_smart']/60)

print "\tSMS"
print "SMS intra:\t\t%s" % event_count['local_sms']
print "SMS inter, Globe\t%s" % per_network['outside_sms']['inter_globe']
print "SMS inter, Smart\t%s" % per_network['outside_sms']['inter_smart']
print "\n"

print "INBOUND TRAFFIC"
print "\tVoice"
print "Voice intra (mins):\t\t%.2f" % (event_count['local_recv_call']/60)
print "Voice inter, Globe (mins)\t%.2f" % (per_network['incoming_call']['inter_globe']/60)
print "Voice inter, Others (mins)\t%.2f" % (per_network['incoming_call']['inter_smart']/60)

print "\tSMS"
print "SMS intra:\t\t%s" % event_count['local_recv_sms']
print "SMS inter, Globe\t%s" % per_network['incoming_sms']['inter_globe']
print "SMS inter, Others\t%s" % per_network['incoming_sms']['inter_smart']
print "\n"

print "************ RETAILER REPORT *******************"
for imsi in eval('vendor_list_%s' % site):
    print "--IMSI%s" % imsi
    print "%s\t%s" % ('load sales', -1*retailer_stats[imsi]['load_sales'])
    print "%s\t\t%s" % ('topup', retailer_stats[imsi]['top_up'])
    print "%s\t%s" % ('personal use', -1 * retailer_stats[imsi]['personal_use'])
    print "\n"

print "************ COOP REPORT *******************"
for imsi in coop_list:
    print "--IMSI%s" % imsi
    print "%s\t%s" % ('load sales', -1*retailer_stats[imsi]['load_sales'])
    print "%s\t\t%s" % ('topup', retailer_stats[imsi]['top_up'])
    print "%s\t%s" % ('personal use', -1 * retailer_stats[imsi]['personal_use'])
    print "\n"

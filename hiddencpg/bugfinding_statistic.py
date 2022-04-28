#!/usr/bin/env python2
import sys, os
import json

def func(elem):
    return int(elem.split(',')[0])

if __name__ == "__main__":
    system_cpg_dir = os.listdir(sys.argv[1])
    log_name = sys.argv[2]
    tot_loc = 0
    tot_files = 0
    dd_cfg_call_gen_time = 0
    ast_gen_time = 0
    # {u'loc': 46323, u'star': 1913, u'dd_cfg_call_generation': 1.2157800197601318, u'ast_generation': 0.5608029365539551, u'clone_url': u'https://github.com/Qsnh/meedu.git', u'num_of_files': 628}
    system_cpg_dir = sorted(system_cpg_dir, reverse=True, key=func)
    num_of_nodes = 0
    num_of_edges = 0
    time_load = 0
    time_exe = 0
    num_of_bugs = 0
    num_of_total_bugs = 0
    bug_app = 0
    c = dict()

    count = 1
    for system_cpg_path in system_cpg_dir:
        print system_cpg_path
        if not os.path.isfile(os.path.join(sys.argv[1], system_cpg_path, log_name)):
            continue
        with open(os.path.join(sys.argv[1], system_cpg_path, log_name)) as f:
            a = f.read()
        if "Total execution time" not in a:
            continue

        #print system_cpg_path
        time_load += float(a.split("Total load time:")[1].split("\n")[0].strip())
        time_exe += float(a.split("Total execution time:")[1].split("\n")[0].strip())

        if "Found" in a:
            print "[*] Bugs found in System app: %s" % system_cpg_path
            for i in a.split("[*]"):
                if "Found" in i:
                    print i.strip()
                    if i.strip().split('\n')[0] not in c.keys():
                        c[i.strip().split('\n')[0]] = i.count("Found!!")
                    else:
                        c[i.strip().split('\n')[0]] += i.count("Found!!")
                    num_of_total_bugs += i.count("Found!!")
                    num_of_bugs += 1
            bug_app += 1
        with open(os.path.join(sys.argv[1], system_cpg_path, "meta_data.json"), 'r') as json_file:
            meta_data = json.load(json_file)
        num_of_nodes += meta_data['num_of_nodes']
        num_of_edges += meta_data['num_of_edges']
        count += 1

    print "count" , count
    print "time load", time_load
    print "time exe", time_exe
    print "# or nodes:", num_of_nodes
    print "# of edges:", num_of_edges
    print "# of bugs found", num_of_bugs
    print "# of bug app", bug_app
    print num_of_total_bugs
    for k in c:
        print str(k) + ": " + str(c[k])



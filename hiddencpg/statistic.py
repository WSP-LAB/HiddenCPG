#!/usr/bin/env python2
import sys, os
import json

def func(elem):
    return int(elem.split(',')[0])

if __name__ == "__main__":
    system_cpg_dir = os.listdir(sys.argv[1])
    tot_loc = 0
    tot_files = 0
    dd_cfg_call_gen_time = 0
    ast_gen_time = 0
    # {u'loc': 46323, u'star': 1913, u'dd_cfg_call_generation': 1.2157800197601318, u'ast_generation': 0.5608029365539551, u'clone_url': u'https://github.com/Qsnh/meedu.git', u'num_of_files': 628}
    system_cpg_dir = sorted(system_cpg_dir, reverse=True, key=func)

    count = 1
    for system_cpg_path in system_cpg_dir:
        print count
        if not os.path.isfile(os.path.join(sys.argv[1], system_cpg_path, "meta_data.json")):
            break

        with open(os.path.join(sys.argv[1], system_cpg_path, "meta_data.json"), 'r') as json_file:
            meta_data = json.load(json_file)
        tot_loc += meta_data['loc']
        tot_files += meta_data['num_of_files']
        dd_cfg_call_gen_time += meta_data['dd_cfg_call_generation']
        ast_gen_time += meta_data['ast_generation']
        count += 1

    print "# of cloned and cpg apps: %s" % len(system_cpg_dir)
    print "loc:", tot_loc
    print "# of files", tot_files
    print "dd_cfg_call_edge gen", dd_cfg_call_gen_time
    print "ast_gen", ast_gen_time

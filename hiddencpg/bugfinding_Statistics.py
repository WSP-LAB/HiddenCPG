#!/usr/bin/env python2
import sys, os
import json

def func(elem):
    return int(elem.split(',')[0])

if __name__ == "__main__":
    system_cpg_dir = os.listdir(sys.argv[1])
    log_name1 = "final_eval.log"
    log_name2 = "additional_eval_test.log"
    tot_loc = 0
    tot_files = 0
    dd_cfg_call_gen_time = 0
    ast_gen_time = 0
    system_cpg_dir = sorted(system_cpg_dir, reverse=True, key=func)
    num_of_nodes = 0
    num_of_edges = 0
    time_load = 0
    time_exe = 0
    num_of_bugs = 0
    num_of_total_bugs = 0
    bug_app = 0
    c = dict()

    count = 0
    star_bug = dict()
    star = 0
    tot_end_time = 0
    q = set()


    for system_cpg_path in system_cpg_dir:
        with open(os.path.join(sys.argv[1], system_cpg_path, log_name1)) as f:
            a = f.read()
        with open(os.path.join(sys.argv[1], system_cpg_path, log_name2)) as f:
            b = f.read()

        if "Total execution time" not in a:
            continue
        if "Total execution time" not in b:
            continue

        end_time = a.count("end of time") + b.count("end of time")
        tot_end_time += end_time


        #print system_cpg_path
        final = float(a.split("Total execution time:")[1].split("\n")[0].strip())
        additional = float(b.split("Total execution time:")[1].split("\n")[0].strip())
        execute_time = final + additional
        with open(os.path.join(sys.argv[1], system_cpg_path, "meta_data.json"), 'r') as json_file:
            meta_data = json.load(json_file)
        num_of_nodes = meta_data['num_of_nodes']
        num_of_edges = meta_data['num_of_edges']
        q.add(num_of_nodes)
    print sorted(q)

        #print num_of_nodes + num_of_edges, execute_time

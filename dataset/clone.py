#!/usr/bin/env python2
import sys, os
import pickle
import json
import subprocess
import time
from collections import OrderedDict
from operator import getitem

def load_dict():
    mydict = {}
    try:
        with open('crawl_dict.pkl', 'rb') as f:
            mydict = pickle.load(f)
    except:
        return {}
    return mydict

def fileCount(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count



if __name__ == "__main__":

    repo_dict = load_dict()


    res = OrderedDict(sorted(repo_dict.items(),
           key = lambda x: getitem(x[1], 'star'), reverse=True))

    for repo in res:
        log = {}
        a = res[repo]['star']
        log['star'] = a
        log['clone_url'] = res[repo]['clone_url']
        b = repo.split('/')[0]
        c = repo.split('/')[1]
        print repo
        if os.path.isdir(os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c))):
            continue
        os.mkdir(os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c)))

        os.mkdir(os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "code"))
        os.mkdir(os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "cpg"))
        repo_dir = os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "code")
        os.system("git clone %s %s" % (res[repo]['clone_url'], repo_dir))

        out = subprocess.Popen(['phploc', repo_dir],
           stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()


        php_files = fileCount(repo_dir, '.php')
        print php_files
        try:
            php_loc = int(stdout.split("Lines of Code (LOC)")[1].split('\n')[0].strip())
        except:
            php_loc = 1
        log['num_of_files'] = php_files
        log['loc'] = php_loc

        start = time.time()
        os.system("~/phpjoern/php2ast %s" % repo_dir)
        end = time.time()
        log['ast_generation'] = end - start

        start = time.time()
        os.system("~/joern/phpast2cpg nodes.csv rels.csv")
        end = time.time()
        log['dd_cfg_call_generation'] = end - start

        os.system("mv cpg_edges.csv %s" % os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "cpg")
)
        os.system("mv nodes.csv %s" % os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "cpg")
)
        os.system("mv rels.csv %s" % os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), "cpg")
)
        with open(os.path.join(sys.argv[1], str(a) + "," + str(b) + "," + str(c), 'meta_data.json'), 'w') as fp:
            json.dump(log, fp)

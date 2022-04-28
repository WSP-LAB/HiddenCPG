#!/usr/bin/env python2

from github import Github
import sys
import pickle

def write_dict(mydict):
    with open('crawl_dict.pkl', 'wb') as f:
        pickle.dump(mydict, f)

def load_dict():
    mydict = {}
    try:
        with open('crawl_dict.pkl', 'rb') as f:
            mydict = pickle.load(f)
    except:
        return {}
    return mydict

github = Github(sys.argv[1])

mydict = load_dict()
most_star = 99999
min_star = 100


while True:
        while True:
            a = github.get("/search/repositories?q=stars:<=%s+language:php&sort=stars&order=desc&per_page=100" % most_star)
            if a == None:
                continue
            else:
                break

        for j in a["items"]:
            if j["stargazers_count"] < min_star:
                print "The number of star is less than %s" % min_star
                print "Current dict length:", len(mydict)
                write_dict(mydict)
                sys.exit()
            repo_name = j["clone_url"].split('/')[-1].split('.git')[0]
            owner = j["clone_url"].split('/')[-2]
            if not owner + '/' + repo_name in mydict.keys():
                mydict[owner + '/' + repo_name] = {}
                mydict[owner + '/' + repo_name]['clone_url'] = j["clone_url"]
                mydict[owner + '/' + repo_name]['star'] = j["stargazers_count"]
            most_star = int(j['stargazers_count'])
            print "Current star:", most_star
            print "Current dict length:", len(mydict)

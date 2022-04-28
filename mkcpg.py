#!/usr/bin/python2
import os
import sys
import subprocess


os.system("./phpjoern/php2ast %s" % sys.argv[1])
os.system("./joern/phpast2cpg nodes.csv rels.csv")

if not os.path.exists(sys.argv[2]):
    os.makedirs(sys.argv[2])

os.system("mv cpg_edges.csv %s" % sys.argv[2])
os.system("mv nodes.csv %s" % sys.argv[2])
os.system("mv rels.csv %s" % sys.argv[2])


#!/usr/bin/python2
import json
import os
import networkx
import sys
import pickle
import operator
import copy
import time
import signal
from PHPBuiltIn import *
from WPBuiltIn import *
from CPG import CPG
from CPGPath import CPGPath
from VF2 import vf

def append_log(path, content):
    with open(path, "a+") as f:
        f.write(content + "\n")

def read_cpg_path(file_path):
  with open(file_path, 'rb') as f:
    path = pickle.load(f)
  return path

def handler(signum, frame):
  raise Exception("end of time")

def usage():
    print "[*] Usage: %s [System CPG] [Directory for CPG query]" % sys.argv[0]
    sys.exit()

def cpg_norm(nodes, ast_edges, cf_edges, dd_edges, call_edges, cd_edges):
    idx = 0
    Path = []
    Nodes = dict()
    ASTEdges = dict()
    CFEdges = dict()
    DDEdges = dict()
    CallEdges = dict()
    CDEdges = dict()

    mapping = {}

    for i in nodes:
        Nodes[idx] = nodes[i]
        mapping[i] = idx
        idx += 1
    for i in ast_edges:
        ASTEdges[mapping[i]] = []
        for j in ast_edges[i]:
            if j == -1:
                continue
            ASTEdges[mapping[i]].append(mapping[j])
    for i in cf_edges:
        CFEdges[mapping[i]] = []
        for j in cf_edges[i]:
            CFEdges[mapping[i]].append(mapping[j])
    for i in dd_edges:
        DDEdges[mapping[i]] = []
        for j in dd_edges[i]:
            DDEdges[mapping[i]].append(mapping[j])
    for i in call_edges:
        CallEdges[mapping[i]] = []
        for j in call_edges[i]:
            CallEdges[mapping[i]].append(mapping[j])
    for i in cd_edges:
        CDEdges[mapping[i]] = []
        for j in cd_edges[i]:
            CDEdges[mapping[i]].append(mapping[j])

    return Nodes, ASTEdges, CFEdges, DDEdges, CallEdges, CDEdges, mapping


def graph_to_string(nodes, ast_edges, cf_edges, dd_edges, call_edges, cd_edges):
   Nodes, ASTEdges, CFEdges, DDEdges, CallEdges, CDEdges, mapping = \
           cpg_norm(nodes, ast_edges, cf_edges, dd_edges, call_edges, cd_edges)
   string = "t # 0\n"
   for i in range(len(Nodes)):
       if Nodes[i][0] == 'string':
           node = 'string:' + str(Nodes[i][1])
       else:
           node = str(Nodes[i][0])
       string += "v %d %s\n" % (i, node)

   for i in range(len(Nodes)):
       if i in CFEdges.keys():
           for j in CFEdges[i]:
               string += "e %d %d %d\n" % (i, j, 1)

       if i in ASTEdges.keys():
           for j in ASTEdges[i]:
               string += "e %d %d %d\n" % (i, j, 2)

       if i in DDEdges.keys():
           for j in DDEdges[i]:
               string += "e %d %d %d\n" % (i, j, 3)

       if i in CallEdges.keys():
           for j in CallEdges[i]:
               string += "e %d %d %d\n" % (i, j, 4)

       if i in CDEdges.keys():
           for j in CDEdges[i]:
               string += "e %d %d %d\n" % (i, j, 5)

   string += "t # -1"
   return string, mapping

def normalize_smaller_path(smaller_path_cpg):
    flag = False

    for i in smaller_path_cpg.Nodes:
        string_value = smaller_path_cpg.Nodes[i][1]
        if string_value == None:
            continue
        if smaller_path_cpg.Nodes[i][0] == "string":
            if len(string_value) > 2 and (string_value[-1] == "\"" or string_value[-2:] == "\"\\"):
                a = string_value.rfind("<input")
                b = string_value.rfind("<a")
                if a == -1 and b == -1:
                    pass
                elif b > a:
                    smaller_path_cpg.Nodes[i] = ("string", "<a_double")
                    continue
                else:
                    smaller_path_cpg.Nodes[i] = ("string", "<input_double")
                    continue

            if len(string_value) > 2 and (string_value[-1] == "\'" or string_value[-2:] == "\'\\"):
                a = string_value.rfind("<input")
                b = string_value.rfind("<a")
                if a == -1 and b == -1:
                    pass
                elif b > a:
                    smaller_path_cpg.Nodes[i] = ("string", "<a_single")
                    continue
                else:
                    smaller_path_cpg.Nodes[i] = ("string", "<input_single")
                    continue

            if flag is True:
              flag = False
              continue
            if string_value == "preg_replace" or \
                    string_value == "preg_split" or \
                    string_value == "preg_match" or \
                    string_value == "ereg_replace":
              flag = True

            if string_value is not None and ((string_value in PHPBuiltIn) or string_value.startswith('wp') or string_value.startswith('WP') or string_value.startswith('mysql') or string_value.startswith('MYSQL') or (string_value in WPBuiltIn)):
              pass
            else:
              smaller_path_cpg.Nodes[i] = ("string", None)



def cbcd_opt(bigger_graph_cpg, smaller_path_dir, system_cpg_path, log_name):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(300)
    try:
        # Read CPG for bigger graph and smaller path
        tot_load_time = 0
        tot_exe_time = 0
        print smaller_path_dir
        start = time.time()
        smaller_path_cpg = read_cpg_path(smaller_path_dir)
        normalize_smaller_path(smaller_path_cpg)
        tot_load_time += time.time() - start


        print "# of vuln nodes:", len(smaller_path_cpg.Nodes)
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - # of vuln nodes: %s" % len(smaller_path_cpg.Nodes))
        tot_edges = 0
        if smaller_path_cpg.Edges != {}:
            for i in smaller_path_cpg.Edges:
                tot_edges += len(smaller_path_cpg.Edges[i])
        if smaller_path_cpg.CFEdges != {}:
            for i in smaller_path_cpg.CFEdges:
                tot_edges += len(smaller_path_cpg.CFEdges[i])
        if smaller_path_cpg.DDEdges != {}:
            for i in smaller_path_cpg.DDEdges:
                tot_edges += len(smaller_path_cpg.DDEdges[i])
        if smaller_path_cpg.CallEdges != {}:
            for i in smaller_path_cpg.CallEdges:
                tot_edges += len(smaller_path_cpg.CallEdges[i])
        if smaller_path_cpg.CDEdges != {}:
            for i in smaller_path_cpg.CDEdges:
                tot_edges += len(smaller_path_cpg.CDEdges[i])

        print "# of vuln edges:", tot_edges
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - # of vuln edges: %s" % tot_edges)

        temp = []
        for vuln_src_node in smaller_path_cpg.Edges:
            if smaller_path_cpg.Edges[vuln_src_node] == []:
                temp.append(vuln_src_node)
        for i in temp:
            smaller_path_cpg.Edges[i] = [i + 1]



        start = time.time()
        # Optimization 1: Exclude Irrelevant Edges and Nodes from the System CPG
        opt1_nodes = {}
        opt1_ast_edges = {}
        opt1_cf_edges = {}
        opt1_call_edges = {}
        opt1_dd_edges = {}
        opt1_cd_edges = {}
        #    Remove AST Edges
        for vuln_src_node in smaller_path_cpg.Edges:
            vuln_dest_node_values = []
            for vuln_dest_node in smaller_path_cpg.Edges[vuln_src_node]:
                vuln_dest_node_values.append( \
                        smaller_path_cpg.Nodes[vuln_dest_node])

            edge_match_flag = False
            for system_src_node in bigger_graph_cpg.ASTEdge:
                if smaller_path_cpg.Nodes[vuln_src_node] \
                       == bigger_graph_cpg.Nodes[system_src_node]:
                    vuln_dest_node_values_copy = copy.deepcopy(vuln_dest_node_values)
                    #print smaller_path_cpg.Nodes[vuln_src_node]
                    #print vuln_dest_node_values_copy
                    for system_dest_node in bigger_graph_cpg.ASTEdge[system_src_node]:
                        #print bigger_graph_cpg.Nodes[system_dest_node]
                        #if vuln_dest_node_values_copy == []:
                        #    edge_match_flag = True
                        #    break
                        if vuln_dest_node_values_copy[0] == bigger_graph_cpg.Nodes[system_dest_node]:
                            vuln_dest_node_values_copy.pop(0)
                        if vuln_dest_node_values_copy == []:
                            #print "Match!!"
                            edge_match_flag = True
                            break
                    if vuln_dest_node_values_copy == []:
                        opt1_nodes[system_src_node] = bigger_graph_cpg.Nodes[system_src_node]
                        for system_dest_node1 in bigger_graph_cpg.ASTEdge[system_src_node]:
                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                if system_src_node not in opt1_ast_edges:
                                    opt1_ast_edges[system_src_node] = []
                                if system_dest_node1 not in opt1_ast_edges[system_src_node]:
                                    opt1_ast_edges[system_src_node].append(system_dest_node1)

                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                opt1_nodes[system_dest_node1] = bigger_graph_cpg.Nodes[system_dest_node1]
            if edge_match_flag == False:
                print "No matching ast edge set"
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - No matching ast edge set")
                tot_exe_time += time.time() - start
                signal.alarm(0)
                return tot_load_time, tot_exe_time, False

        #    Remove CF Edges
        for vuln_src_node in smaller_path_cpg.CFEdges:
            vuln_dest_node_values = set()
            for vuln_dest_node in smaller_path_cpg.CFEdges[vuln_src_node]:
                vuln_dest_node_values.add( \
                        smaller_path_cpg.Nodes[vuln_dest_node])
            edge_match_flag = False
            for system_src_node in bigger_graph_cpg.CFEdge:
                if smaller_path_cpg.Nodes[vuln_src_node] \
                       == bigger_graph_cpg.Nodes[system_src_node]:
                    vuln_dest_node_values_copy = copy.deepcopy(vuln_dest_node_values)
                    #print smaller_path_cpg.Nodes[vuln_src_node]
                    #print vuln_dest_node_values_copy
                    for system_dest_node in bigger_graph_cpg.CFEdge[system_src_node]:
                        #print bigger_graph_cpg.Nodes[system_dest_node]
                        if bigger_graph_cpg.Nodes[system_dest_node] in vuln_dest_node_values_copy:
                            vuln_dest_node_values_copy.remove(bigger_graph_cpg.Nodes[system_dest_node])
                        if len(vuln_dest_node_values_copy) == 0:
                            edge_match_flag = True
                            break
                    if len(vuln_dest_node_values_copy) == 0:
                        opt1_nodes[system_src_node] = bigger_graph_cpg.Nodes[system_src_node]
                        for system_dest_node1 in bigger_graph_cpg.CFEdge[system_src_node]:
                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                if system_src_node not in opt1_cf_edges:
                                    opt1_cf_edges[system_src_node] = []
                                if system_dest_node1 not in opt1_cf_edges[system_src_node]:
                                    opt1_cf_edges[system_src_node].append(system_dest_node1)

                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                opt1_nodes[system_dest_node1] = bigger_graph_cpg.Nodes[system_dest_node1]
            if edge_match_flag == False:
                print "No matching cf edge set"
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - No matching cf edge set")

                tot_exe_time += time.time() - start
                signal.alarm(0)
                return tot_load_time, tot_exe_time, False


        #    Remove DD Edges
        for vuln_src_node in smaller_path_cpg.DDEdges:
            vuln_dest_node_values = set()
            for vuln_dest_node in smaller_path_cpg.DDEdges[vuln_src_node]:
                vuln_dest_node_values.add( \
                        smaller_path_cpg.Nodes[vuln_dest_node])
            edge_match_flag = False
            for system_src_node in bigger_graph_cpg.DDEdge:
                if smaller_path_cpg.Nodes[vuln_src_node] \
                       == bigger_graph_cpg.Nodes[system_src_node]:
                    vuln_dest_node_values_copy = copy.deepcopy(vuln_dest_node_values)
                    #print smaller_path_cpg.Nodes[vuln_src_node]
                    #print vuln_dest_node_values_copy
                    for system_dest_node in bigger_graph_cpg.DDEdge[system_src_node]:
                        #print bigger_graph_cpg.Nodes[system_dest_node]
                        if bigger_graph_cpg.Nodes[system_dest_node] in vuln_dest_node_values_copy:
                            vuln_dest_node_values_copy.remove(bigger_graph_cpg.Nodes[system_dest_node])
                        if len(vuln_dest_node_values_copy) == 0:
                            edge_match_flag = True
                            break
                    if len(vuln_dest_node_values_copy) == 0:
                        opt1_nodes[system_src_node] = bigger_graph_cpg.Nodes[system_src_node]
                        for system_dest_node1 in bigger_graph_cpg.DDEdge[system_src_node]:
                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                if system_src_node not in opt1_dd_edges:
                                    opt1_dd_edges[system_src_node] = []
                                if system_dest_node1 not in opt1_dd_edges[system_src_node]:
                                    opt1_dd_edges[system_src_node].append(system_dest_node1)

                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                opt1_nodes[system_dest_node1] = bigger_graph_cpg.Nodes[system_dest_node1]
            if edge_match_flag == False:
                print "No matching dd edge set"
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - No matching dd edge set")
                tot_exe_time += time.time() - start
                signal.alarm(0)
                return tot_load_time, tot_exe_time, False


        #    Remove Call Edges
        for vuln_src_node in smaller_path_cpg.CallEdges:
            vuln_dest_node_values = set()
            for vuln_dest_node in smaller_path_cpg.CallEdges[vuln_src_node]:
                vuln_dest_node_values.add( \
                        smaller_path_cpg.Nodes[vuln_dest_node])
            edge_match_flag = False
            for system_src_node in bigger_graph_cpg.CallEdge:
                if smaller_path_cpg.Nodes[vuln_src_node] \
                       == bigger_graph_cpg.Nodes[system_src_node]:
                    vuln_dest_node_values_copy = copy.deepcopy(vuln_dest_node_values)
                    #print smaller_path_cpg.Nodes[vuln_src_node]
                    #print vuln_dest_node_values_copy
                    for system_dest_node in bigger_graph_cpg.CallEdge[system_src_node]:
                        #print bigger_graph_cpg.Nodes[system_dest_node]
                        if bigger_graph_cpg.Nodes[system_dest_node] in vuln_dest_node_values_copy:
                            vuln_dest_node_values_copy.remove(bigger_graph_cpg.Nodes[system_dest_node])
                        if len(vuln_dest_node_values_copy) == 0:
                            edge_match_flag = True
                            break
                    if len(vuln_dest_node_values_copy) == 0:
                        opt1_nodes[system_src_node] = bigger_graph_cpg.Nodes[system_src_node]
                        for system_dest_node1 in bigger_graph_cpg.CallEdge[system_src_node]:
                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                if system_src_node not in opt1_call_edges:
                                    opt1_call_edges[system_src_node] = []
                                if system_dest_node1 not in opt1_call_edges[system_src_node]:
                                    opt1_call_edges[system_src_node].append(system_dest_node1)

                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                opt1_nodes[system_dest_node1] = bigger_graph_cpg.Nodes[system_dest_node1]
            if edge_match_flag == False:
                print "No matching call edge set"
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - No matching call edge set")
                tot_exe_time += time.time() - start
                signal.alarm(0)
                return tot_load_time, tot_exe_time, False

        #    Remove CD Edges
        for vuln_src_node in smaller_path_cpg.CDEdges:
            vuln_dest_node_values = set()
            for vuln_dest_node in smaller_path_cpg.CDEdges[vuln_src_node]:
                vuln_dest_node_values.add( \
                        smaller_path_cpg.Nodes[vuln_dest_node])
            edge_match_flag = False
            for system_src_node in bigger_graph_cpg.CDEdge:
                if system_src_node == -1:
                    continue
                if smaller_path_cpg.Nodes[vuln_src_node] \
                       == bigger_graph_cpg.Nodes[system_src_node]:
                    vuln_dest_node_values_copy = copy.deepcopy(vuln_dest_node_values)
                    #print smaller_path_cpg.Nodes[vuln_src_node]
                    #print vuln_dest_node_values_copy
                    for system_dest_node in bigger_graph_cpg.CDEdge[system_src_node]:
                        if system_dest_node == -1:
                            continue
                        if bigger_graph_cpg.Nodes[system_dest_node] in vuln_dest_node_values_copy:
                            vuln_dest_node_values_copy.remove(bigger_graph_cpg.Nodes[system_dest_node])
                        if len(vuln_dest_node_values_copy) == 0:
                            edge_match_flag = True
                            break
                    if len(vuln_dest_node_values_copy) == 0:
                        opt1_nodes[system_src_node] = bigger_graph_cpg.Nodes[system_src_node]
                        for system_dest_node1 in bigger_graph_cpg.CDEdge[system_src_node]:
                            if system_dest_node1 == -1:
                                continue
                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                if system_src_node not in opt1_cd_edges:
                                    opt1_cd_edges[system_src_node] = []
                                if system_dest_node1 not in opt1_cd_edges[system_src_node]:
                                    opt1_cd_edges[system_src_node].append(system_dest_node1)

                            if bigger_graph_cpg.Nodes[system_dest_node1] in vuln_dest_node_values:
                                opt1_nodes[system_dest_node1] = bigger_graph_cpg.Nodes[system_dest_node1]
            if edge_match_flag == False:
                print "No matching cd edge set"
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - No matching cd edge set")
                tot_exe_time += time.time() - start
                signal.alarm(0)
                return tot_load_time, tot_exe_time, False

        bigger_graph_cpg.Nodes = opt1_nodes
        bigger_graph_cpg.ASTEdge = opt1_ast_edges
        bigger_graph_cpg.CallEdge = opt1_call_edges
        bigger_graph_cpg.CFEdge = opt1_cf_edges
        bigger_graph_cpg.DDEdge = opt1_dd_edges
        bigger_graph_cpg.CDEdge = opt1_cd_edges
        # Optimization 2: Break the System CPG into Small Graphs
        smaller_path_node_type_set = set()

        node_count = {}
        vuln_node_count = {}
        for idx in smaller_path_cpg.Nodes:
            if  smaller_path_cpg.Nodes[idx][0] == 'string':
                smaller_path_node = 'string:' + str(smaller_path_cpg.Nodes[idx][1])
            else:
                smaller_path_node = str(smaller_path_cpg.Nodes[idx][0])
            smaller_path_node_type_set.add(smaller_path_node)
            node_count[smaller_path_node] = 0
            if smaller_path_node not in vuln_node_count:
                vuln_node_count[smaller_path_node] = 0
            vuln_node_count[smaller_path_node] += 1



        for idx in bigger_graph_cpg.Nodes:
            if bigger_graph_cpg.Nodes[idx][0] == 'string':
                bigger_graph_cpg_node = 'string:' + str(bigger_graph_cpg.Nodes[idx][1])
            else:
                bigger_graph_cpg_node = str(bigger_graph_cpg.Nodes[idx][0])
            if bigger_graph_cpg_node in list(smaller_path_node_type_set):
                node_count[bigger_graph_cpg_node] += 1
        node_count = sorted(node_count.items(), key=operator.itemgetter(1))
        if node_count[0][1] == 0:
            print "VKkmin count is 0"
            append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - VKkmin count is 0")
            tot_exe_time += time.time() - start
            signal.alarm(0)
            return tot_load_time, tot_exe_time, False
        VKmin = node_count[0][0]

        print "VKmin node type:", VKmin
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - VKmin node type: %s" % VKmin)

        print "Number of VKmin from system CPG:", node_count[0][1]
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - Number of VKmin from system CPG: %s" % node_count[0][1])


        tot_exe_time += time.time() - start

        start = time.time()
        smaller_graph_networkx = networkx.Graph()
        for i in smaller_path_cpg.Edges:
            for j in smaller_path_cpg.Edges[i]:
                smaller_graph_networkx.add_edge(i, j)
        for i in smaller_path_cpg.CFEdges:
            for j in smaller_path_cpg.CFEdges[i]:
                smaller_graph_networkx.add_edge(i, j)
        for i in smaller_path_cpg.DDEdges:
            for j in smaller_path_cpg.DDEdges[i]:
                smaller_graph_networkx.add_edge(i, j)
        for i in smaller_path_cpg.CallEdges:
            for j in smaller_path_cpg.CallEdges[i]:
                smaller_graph_networkx.add_edge(i, j)
        for i in smaller_path_cpg.CDEdges:
            for j in smaller_path_cpg.CDEdges[i]:
                smaller_graph_networkx.add_edge(i, j)
        tot_load_time += time.time() - start


        start = time.time()

        min_distance = 50000000
        # Calcluate db
        for idx in smaller_path_cpg.Nodes:
            if  smaller_path_cpg.Nodes[idx][0] == 'string':
                smaller_path_node = 'string:' + str(smaller_path_cpg.Nodes[idx][1])
            else:
                smaller_path_node = str(smaller_path_cpg.Nodes[idx][0])
            if smaller_path_node == VKmin:
                # Calculate maximum distance
                distance_dict = networkx.shortest_path_length(smaller_graph_networkx, idx)
                distance = sorted(distance_dict.items(), key=operator.itemgetter(1))[-1][1]

                if min_distance > distance:
                    min_distance = distance
        db = min_distance
        print "db:", db
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), " - db: %s" % db)


        subgraphs = {}

        tot_exe_time += time.time() - start

        start = time.time()
        bigger_graph_networkx = networkx.DiGraph()
        for i in bigger_graph_cpg.ASTEdge:
            for j in bigger_graph_cpg.ASTEdge[i]:
                bigger_graph_networkx.add_edge(i, j, weight='ast')
        for i in bigger_graph_cpg.CFEdge:
            for j in bigger_graph_cpg.CFEdge[i]:
                bigger_graph_networkx.add_edge(i, j, weight = 'cf')
        for i in bigger_graph_cpg.DDEdge:
            for j in bigger_graph_cpg.DDEdge[i]:
                bigger_graph_networkx.add_edge(i, j, weight = 'dd')
        for i in bigger_graph_cpg.CallEdge:
            for j in bigger_graph_cpg.CallEdge[i]:
                bigger_graph_networkx.add_edge(i, j, weight = 'call')
        for i in bigger_graph_cpg.CDEdge:
            for j in bigger_graph_cpg.CDEdge[i]:
                bigger_graph_networkx.add_edge(i, j, weight = 'cd')
        tot_load_time += time.time() - start

        start = time.time()


        # Extract sub-graphs
        for idx in bigger_graph_cpg.Nodes:
            if bigger_graph_cpg.Nodes[idx][0] == 'string':
                bigger_graph_cpg_node = 'string:' + str(bigger_graph_cpg.Nodes[idx][1])
            else:
                bigger_graph_cpg_node = str(bigger_graph_cpg.Nodes[idx][0])
            if bigger_graph_cpg_node == VKmin:

                ego = networkx.ego_graph(bigger_graph_networkx, idx, radius = db, undirected=True)

                node = {}
                ast_edges = {}
                cf_edges = {}
                dd_edges = {}
                call_edges = {}
                cd_edges = {}

                for edge_data in ego.edges.data():

                    node[edge_data[0]] = bigger_graph_cpg.Nodes[edge_data[0]]
                    node[edge_data[1]] = bigger_graph_cpg.Nodes[edge_data[1]]

                    if edge_data[0] in bigger_graph_cpg.ASTEdge and edge_data[1] in bigger_graph_cpg.ASTEdge[edge_data[0]]:
                        if edge_data[0] not in ast_edges:
                            ast_edges[edge_data[0]] = []
                        ast_edges[edge_data[0]].append(edge_data[1])
                    if edge_data[0] in bigger_graph_cpg.CFEdge and edge_data[1] in bigger_graph_cpg.CFEdge[edge_data[0]]:
                        if edge_data[0] not in cf_edges:
                            cf_edges[edge_data[0]] = []
                        cf_edges[edge_data[0]].append(edge_data[1])
                    if edge_data[0] in bigger_graph_cpg.DDEdge and edge_data[1] in bigger_graph_cpg.DDEdge[edge_data[0]]:
                        if edge_data[0] not in dd_edges:
                            dd_edges[edge_data[0]] = []
                        dd_edges[edge_data[0]].append(edge_data[1])
                    if edge_data[0] in bigger_graph_cpg.CallEdge and edge_data[1] in bigger_graph_cpg.CallEdge[edge_data[0]]:
                        if edge_data[0] not in call_edges:
                            call_edges[edge_data[0]] = []
                        call_edges[edge_data[0]].append(edge_data[1])
                    if edge_data[0] in bigger_graph_cpg.CDEdge and edge_data[1] in bigger_graph_cpg.CDEdge[edge_data[0]]:
                        if edge_data[0] not in cd_edges:
                            cd_edges[edge_data[0]] = []
                        cd_edges[edge_data[0]].append(edge_data[1])



                subgraph = CPGPath(None, node, ast_edges, cf_edges, dd_edges, call_edges, cd_edges)

                subgraphs[idx] = subgraph


        # Optimization 3: Exclude Irrelevant CPGs
        relevant_subgraphs = []
        for cls in subgraphs:
            subgraph_node_count = {}
            for idx in subgraphs[cls].Nodes:
                if  subgraphs[cls].Nodes[idx][0] == 'string':
                    subgraph_node = 'string:' + str(subgraphs[cls].Nodes[idx][1])
                else:
                    subgraph_node = str(subgraphs[cls].Nodes[idx][0])
                if subgraph_node not in subgraph_node_count:
                    subgraph_node_count[subgraph_node] = 0
                subgraph_node_count[subgraph_node] += 1
            flag = False
            for i in vuln_node_count:
                if (i not in subgraph_node_count) or subgraph_node_count[i] < vuln_node_count[i]:
                    flag = True
                    break
            if flag == False:
                relevant_subgraphs.append(subgraphs[cls])
        if relevant_subgraphs == []:
            print 'Zero relevant subgraphs'
            append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), ' - Zero relevant subgraphs')
            signal.alarm(0)
            return tot_load_time, tot_exe_time, False

        tot_exe_time += time.time() - start

        # XXX: Optimization 4: Break Up Large Bug Code Segments

        # CBCD vs. VF2

        vf2 = vf.Vf()

        start = time.time()
        print smaller_path_cpg.Nodes
        print smaller_path_cpg.Edges
        print smaller_path_cpg.CFEdges
        print smaller_path_cpg.DDEdges
        print smaller_path_cpg.CallEdges
        print smaller_path_cpg.CDEdges
        vuln_cpg_string, vuln_mapping = graph_to_string(smaller_path_cpg.Nodes, \
                             smaller_path_cpg.Edges, \
                             smaller_path_cpg.CFEdges,  \
                             smaller_path_cpg.DDEdges,  \
                             smaller_path_cpg.CallEdges, \
                             smaller_path_cpg.CDEdges)
        tot_load_time += time.time() - start
        for i in relevant_subgraphs:
            start = time.time()
            system_cpg_string, system_mapping = graph_to_string(i.Nodes, \
                              i.Edges, \
                              i.CFEdges,  \
                              i.DDEdges,  \
                              i.CallEdges, \
                              i.CDEdges)
            tot_load_time += time.time() - start
            start = time.time()
            result = vf2.main(system_cpg_string, vuln_cpg_string)
            if result[0] == True:
                print "Found"

                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), 'Found!!')
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), str(result[1]))
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "Vuln mapping: %s" % str(vuln_mapping))
                append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "System mapping: %s" % str(system_mapping))

            tot_exe_time += time.time() - start
        signal.alarm(0)
        return tot_load_time, tot_exe_time, False
    except Exception, exc:
        print exc
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "end of time")
        return 0, 300, False



def func(elem):
    return int(elem.split(',')[0])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()

    log_name = sys.argv[3]
    bigger_graph_cpg = sys.argv[1]
    vuln_cpg_path = sys.argv[2]

    system_cpg_dir =  os.listdir(bigger_graph_cpg)
    system_cpg_dir = sorted(system_cpg_dir, reverse=True, key=func)
    for system_cpg_path in system_cpg_dir:
        print system_cpg_path
        tot_load_time = 0
        tot_exe_time = 0
        if os.path.isfile(os.path.join(sys.argv[1], system_cpg_path, log_name)):
            continue
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "start!")

        start = time.time()
        bigger_cpg_origin = CPG(os.path.join(sys.argv[1], system_cpg_path))
        tot_load_time += time.time() - start
        for j in os.listdir(vuln_cpg_path):
            bigger_cpg = copy.deepcopy(bigger_cpg_origin)
            smaller_path_dir = os.path.join(sys.argv[2], j)
            append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "[*] %s" % smaller_path_dir)
            load_time, exe_time, _ = cbcd_opt(bigger_cpg, \
                         smaller_path_dir, system_cpg_path, log_name)
            signal.alarm(0)
            append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "")

            tot_load_time += load_time
            tot_exe_time += exe_time
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "- Total load time: %s" % tot_load_time)
        append_log(os.path.join(sys.argv[1], system_cpg_path, log_name), "- Total execution time: %s" % tot_exe_time)

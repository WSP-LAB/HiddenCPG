import os, sys
import shutil

import commands

filter_list = ['115,Nu1LCTF,n1ctf-2019', '537,wonderkun,CTF_web', '164,webshellpub,awsome-webshell', '222,code-scan,GourdScan', '202,robocoder,rips-scanner', '118,S9MF,S9MF-php-webshell-bypass', '104,carcabot,iCloud-Bypass', '348,opsxcq,exploit-CVE-2016-10033', '1508,JohnTroony,php-webshells', '192,backdoorhub,shell-backdoor-list', '407,BlackArch,webshells', '251,ripsscanner,rips', '382,nikicat,web-malware-collection', '521,cfreal,exploits', '390,Bo0oM,PHP_imap_open_exploit', '133,adambrett,php-shell-wrapper', '1025,zhuifengshaonianhanlu,pikachu', '315,incredibleindishell,SSRF_Vulnerable_Lab', '147,kenjis,php-orm-benchmark', '214,mikehaertl,php-shellcommand', '580,ysrc,webshell-sample', '740,MrRio,shellwrap', '118,shimmeris,CTF-Web-Challenges', '588,susers,Writeups', '130,eryx,php-framework-benchmark', '705,duoergun0729,1book', '210,lcatro,PHP-WebShell-Bypass-WAF', '384,pentestmonkey,php-reverse-shell', '1022,kenjis,php-framework-benchmark', '346,steverobbins,magescan', '133,dermotblair,webvulscan', '854,mm0r1,exploits', '101,RickGray,Bypass-PHP-GD-Process-To-RCE', '132,RamadhanAmizudin,Wordpress-scanner', '222,scr34m,php-malware-scanner', '117,ollyxar,php-malware-detector', '140,Hcamael,CTF_repo', '839,flozz,p0wny-shell', '151,incredibleindishell,CORS-vulnerable-Lab', '218,samdark,yii2-webshell', '142,malwares,ExploitKit', '142,10up,wp-vulnerability-scanner', '1446,psecio,iniscan', '1875,orangetw,My-CTF-Web-Challenges', '200,chuckfw,owaspbwa', '135,incredibleindishell,sqlite-lab', '3022,cytopia,devilbox', '5976,tennc,webshell', '154,m0xiaoxi,CTF_Web_docker', '365,tanjiti,webshellSample', '127,yiisoft,yii2-shell', '508,bramus,mixed-content-scan', '189,Dhayalanb,windows-php-reverse-shell', '352,Insolita,unused-scanner', '352,offensive-security,masscan-web-ui', '176,zsxsoft,my-ctf-challenges', '120,WhiteWinterWolf,wwwolf-php-webshell', '245,wofeiwo,webcgi-exploits', '684,mattiasgeniar,php-exploit-scripts', '145,Automattic,vip-scanner', '163,bugku,BWVS', '110,mIcHyAmRaNe,wso-webshell', '113,vanilla-php,benchmark-php', '1217,jvoisin,php-malware-finder', "132,SniperOJ,Attack-Defense-Challenges"]

list_of_queries = os.listdir("../final_extracted_cpg_query")

with open("eval_bugs_found_result.txt") as f:
    lines = f.read()

apps = lines.strip().split("[*] Bugs found in System app: ")

total_num_bugs = 0


xss_normal = 0
xss_incor = 0
ufu_normal = 0
ufu_incor = 0

sqli_normal = 0
sqli_incor = 0
lfi_normal = 0
lfi_incor = 0

xss_normal_pur = 0
xss_incor_pur = 0
ufu_normal_pur = 0
ufu_incor_pur = 0

sqli_normal_pur = 0
sqli_incor_pur = 0
lfi_normal_pur = 0
lfi_incor_pur = 0

num_of_vuln_apps = 0
num_of_vuln_apps_pur = 0

app_set = set()

cnt = 0

query_size_dict = dict()

vuln_count = 0

for i in apps[1:]:

   # cnt += 1
    app_name = i.split("\n")[0]

#       if app_name in filter_list:
#            num_of_vuln_apps_pur += 1
#       else:
#            num_of_vuln_apps += 1
#    app_set.add(app_name)







    for j in i.split("../")[1:]:
        query_name = j.split("/")[1].split("\n")[0]
        if query_name in list_of_queries:
            #if not app_name in filter_list and "XSS" in query_name:
            #    print app_name
            #    print j
            if not "incorrect" in query_name and "XSS" in query_name:
                if query_name.split(",")[-2] != query_name.split(",")[-1]:
                   vuln_count += j.count("Found")
            num_bug_for_query = j.count("Found")

            status, output = commands.getstatusoutput("../temp.py  ../final_extracted_cpg_query/%s" % query_name)
            num_edge = int(output.split('\n')[0].split(":")[1].strip())
            num_node = int(output.split('\n')[1].split(":")[1].strip())
            graph_size = num_edge + num_node

            if not graph_size in query_size_dict:
                query_size_dict[graph_size] = num_bug_for_query
            else:
                query_size_dict[graph_size] += num_bug_for_query


            total_num_bugs += num_bug_for_query
            if "incorrect" in query_name:
                if "xss" in query_name:
                    if app_name in filter_list:
                        xss_incor_pur += num_bug_for_query
                    else:
                        xss_incor += num_bug_for_query


                if "ufu" in query_name:
                    if app_name in filter_list:
                        ufu_incor_pur += num_bug_for_query
                    else:
                        ufu_incor += num_bug_for_query
            elif "xss" in query_name or "XSS" in query_name:
                if app_name in filter_list:
                    xss_normal_pur += num_bug_for_query
                else:
                    xss_normal += num_bug_for_query
            elif "sqli" in query_name:
                if app_name in filter_list:
                    sqli_normal_pur += num_bug_for_query
                else:
                    sqli_normal += num_bug_for_query


                #print app_name, num_bug_for_query
            elif "lfi" in query_name:

                if app_name in filter_list:
                    lfi_normal_pur += num_bug_for_query
                else:
                    lfi_normal += num_bug_for_query

                    print app_name, num_bug_for_query


print "Total number of bugs:", total_num_bugs
print "Total number of xss_normal bugs:", xss_normal
print "Total number of xss_normal_pur bugs:", xss_normal_pur
print "Total number of xss_incor bugs:", xss_incor
print "Total number of xss_incor_pur bugs:", xss_incor_pur
print "Total number of ufu_normal bugs:", ufu_normal
print "Total number of ufu_normal_pur bugs:", ufu_normal_pur
print "Total number of ufu_incor bugs:",  ufu_incor
print "Total number of ufu_incor_pur bugs:",  ufu_incor_pur
print "Total number of sqli_normal bugs:", sqli_normal
print "Total number of sqli_normal_pur bugs:", sqli_normal_pur
print "Total number of sqli_incor bugs:",  sqli_incor
print "Total number of sqli_incor_pur bugs:",  sqli_incor_pur
print "Total number of lfi_normal bugs:",  lfi_normal
print "Total number of lfi_normal_pur bugs:",  lfi_normal_pur
print "Total number of lfi_incor bugs:", lfi_incor
print "Total number of lfi_incor_pur bugs:", lfi_incor_pur
print
print "Total number of vuln apps:", num_of_vuln_apps
print "Total number of vuln apps_pur:", num_of_vuln_apps_pur

# Star counting
#count = dict()
#for i in app_set:
#    star_num = int(i.split(",")[0])
#    if star_num in count:
#        count[star_num] += 1
#    else:
#        count[star_num] = 1
#
#print count
#tot = 0
#for i in  sorted(count.keys()):
#    if i >= 800 and i < 900:
#       tot +=  count[i]
#
#
#print tot
#





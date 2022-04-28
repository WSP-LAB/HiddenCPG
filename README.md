# HiddenCPG

HiddenCPG is a vulnerable clone detection system using code property graph
(CPG) for uncovering various web vulnerabilities HiddenCPG is capable of
detecting unknown web vulnerabilities that stem from the absence of input
sanitization and incorrect sanitization.  The details of the testing strategy
is in our [paper](https://dl.acm.org/doi/pdf/10.1145/3485447.3512235),
"HiddenCPG: Large-Scale Vulnerable Clone Detection Using Subgraph Isomorphism
of Code Property Graphs", which appeared in WWW 2022. To see how to configure
and execute HiddenCPG, see the followings.

# Setup
## Install

1. Install dependencies
```
# apt-get install pickle
# apt-get install json
# apt-get install networkx
# apt-get install operator
# apt-get install copy
# apt-get install signal
# apt-get install github
```

2. Clone HiddenCPG
```
$ git clone https://github.com/WSP-LAB/FUSE
```

3. Install joern and phpjoern

* Build [joern](joern) and make sure that `php2ast` is working correctly.
* Build [phpjoern](phpjoern) and make sure that `phpast2cpg` is working correctly.

## Usage
### System CPG

* To convert the target applications to CPG, use the following command:
```
$ python2 mkcpg.py [Root directory of target PHP code] [Output directory]
```

### CPG query

* First, convert the vulnerable application into a CPG.

```
$ pytho2 mkcpg.py [Root directory of vulnerable PHP code] [Output directory]
```

* Then, extract the CPG query by specifying the location of the sink and source
in the command (Here, the sink and source locations refer to the node number of
the top level statement visited by the control flow edge among the AST nodes).

```
$ python2 Extractor.py [CPG directory] [Source node] [Sink node] [Path number] [Output directory]
```

Note that an extracted query is stored using python pickle.

### HiddenCPG

* You need two directories: the directory where the system
CPGs are collected and the directory where the CPG queries are collected.

```
SystemCPG
│
└───application1
│   │   cpg_edges.csv
│   │   nodes.csv
│   │   rels.csv
│
└───application2
    │   cpg_edges.csv
    │   nodes.csv
    │   rels.csv

CPGQuery
│
└───query1
│
└───query2
```

* Execute HiddenCPG

```
$ cd hiddencpg
$ python2 hiddencpg.py [SystemCPG] [CPGQuery] [Log name]
```

Logs are written to each systemCPG directory. When HiddenCPG finds a bug, it
records which node is mapped to which node in the log.

### Dataset

* Crwaler

```
$ cd dataset
$ python2 crawler.py [Github token]
```

* Cloning dataset

```
$ ./clone [Output directory]
```


# Authors

This research project has been conducted by [WSP Lab](https://wsp-lab.github.io) at KAIST.

* [Seongil Wi](https://seongil-wi.github.io/)
* Sijae Woo
* [Joyce Jiyoung Whang](https://bdi-lab.kaist.ac.kr/g5/theme/big/page/professor.php)
* [Sooel Son](https://sites.google.com/site/ssonkaist/home)

# Citing HiddenCPG
To cite our paper:
```
@INPROCEEDINGS{wi:www:2022,
    author = {Wi, Seongil and Woo, Sijae and Whang, Joyce Jiyoung and Son, Sooel},
    title = {{HiddenCPG}: Large-Scale Vulnerable Clone Detection Using Subgraph Isomorphism of Code Property Graphs},
    booktitle = {Proceedings of the ACM Web Conference},
    year = 2022,
    pages = {755--766}
}
```



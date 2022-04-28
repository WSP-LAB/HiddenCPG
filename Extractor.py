#!/usr/bin/python2

import sys

from CPG import CPG
from CPGPath import CPGPath
from PHPBuiltIn import *
from WPBuiltIn import *
from utils import *

MAX_NODE = 500

class Extractor:
  def __init__(self, CPG, Sink, Source):
    self.CPG = CPG
    self.Sink = Sink
    self.Source = Source
    self.Paths = []

  def findCallers(self, Id, Callers):
    if self.CPG.isTerminalNode(Id): return
    if self.CPG.hasCallEdge(Id): Callers += [Id]
    for c in self.CPG.getChildNodes(Id):
      self.findCallers(c, Callers)

  def followCallEdge(self, Id, Path):
    # Call stmt at top-level
    if self.CPG.hasCallEdge(Id):
      Callee = self.CPG.getCallee(Id)
      CalleeEntry = self.CPG.getFuncEntry(Callee)

      # Prevent multiple calls on same function
      if Callee in Path: return [[]]

      IntraPaths = []
      self.findPath(CalleeEntry, [Callee, CalleeEntry], IntraPaths)
      return IntraPaths
    # Explore call stmts under this subtree
    else:
      Callers = []
      self.findCallers(Id, Callers)
      # TODO: handle multiple call stmts under this subtree
      if len(Callers) == 1:
        return self.followCallEdge(Callers[0], Path)
      else:
        return [[]]

  def followCFEdge(self, Id, Path, IntraPaths):
    if self.CPG.isFuncExit(Id) or Id == self.Sink:
      IntraPaths += [Path]
      return

    if self.CPG.isCFSrc(Id):
      for DesId in self.CPG.getCFDes(Id):
        if DesId not in Path:
          self.findPath(DesId, Path + [DesId], IntraPaths)

  def reachedSink(self, Path):
    return (Path[0] == self.Source and Path[-1] == self.Sink) or \
           (Path[0] == self.Source and Path[0] == self.Sink)


  def findPath(self, Id, Path, CurIntraPaths):
    if len(Path) > MAX_NODE:
      print 'Error: Maximum # of nodes reached'
      return
    # Follow call edge at this node
    IntraPaths = self.followCallEdge(Id, Path)


    # Follow control flow edges at this node
    for IntraPath in IntraPaths:
      if self.reachedSink(Path + IntraPath):
        TopPath = Path + IntraPath
        if TopPath[0] == self.Sink and TopPath[-1] != self.Sink:
          self.Paths += [TopPath + [self.Sink]]
        else:
          self.Paths += [TopPath]
      else:
        self.followCFEdge(Id, Path + IntraPath, CurIntraPaths)

    if self.reachedSink(Path) and IntraPaths == []:
      self.Paths += [Path]

def temp(DirPath, Source, Sink, PathNum = None, PathDumpFileName = None):

  # Initialize CPG
  cpg = CPG(DirPath)

  # Extract path
  print cpg, Sink, Source
  e = Extractor(cpg, Sink, Source)
  e.findPath(Source, [Source], [])
  if PathNum == None:
    print "Number of path: %s" % len(e.Paths)
    for p in e.Paths:
      print p
      '''
      for Id in p:
        print cpg.getSubtree(Id)
      '''
    return e.Paths, cpg


  topLevelPath = e.Paths[PathNum]

  pathAllNodes = []
  for Id in topLevelPath:
    pathAllNodes.extend(cpg.getSubtree(Id))

  pathNodes = {}
  pathEdges = {}
  pathCFEdges = {}
  pathDDEdges = {}
  pathCallEdges = {}
  pathCDEdges = {}

  for Id in pathAllNodes:
    if cpg.Nodes[Id][1] is not None:
      pathNodes[Id] = (cpg.Nodes[Id][0], cpg.Nodes[Id][1][1:-1])
    else:
      pathNodes[Id] = (cpg.Nodes[Id][0], None)

    if Id in cpg.ASTEdge.keys():
      if cpg.Nodes[Id][0] in ['AST_FUNC_DECL', 'AST_METHOD']:
        pathEdges[Id] = []
      else:
        pathEdges[Id] = cpg.ASTEdge[Id]

    if Id in cpg.CFEdge.keys():
      inpath_edge = list(set(pathAllNodes) & set(cpg.CFEdge[Id]))
      if inpath_edge != []:
        pathCFEdges[Id] = inpath_edge

    if Id in cpg.DDEdge.keys():
      inpath_edge = list(set(pathAllNodes) & set(cpg.DDEdge[Id]))
      if inpath_edge != []:
        pathDDEdges[Id] = inpath_edge

    if Id in cpg.CallEdge.keys():
      inpath_edge = list(set(pathAllNodes) & set([cpg.CallEdge[Id]]))
      if inpath_edge != []:
        pathCallEdges[Id] = inpath_edge

    if Id in cpg.CDEdge.keys():
      inpath_edge = list(set(pathAllNodes) & set(cpg.CDEdge[Id]))
      if inpath_edge != []:
        pathCDEdges[Id] = inpath_edge


  path =  CPGPath(e.Paths[PathNum], \
                  pathNodes, \
                  pathEdges, \
                  pathCFEdges, \
                  pathDDEdges, \
                  pathCallEdges, \
                  pathCDEdges)
  print path
  save_cpg_path(PathDumpFileName, path)


if __name__ == '__main__':
  if len(sys.argv) == 4:
    DirPath = sys.argv[1]
    Source = int(sys.argv[2])
    Sink = int(sys.argv[3])
    temp(DirPath, Source, Sink)
  elif len(sys.argv) == 6:
    DirPath = sys.argv[1]
    Source = int(sys.argv[2])
    Sink = int(sys.argv[3])
    PathNum = int(sys.argv[4])
    PathDumpFileName = sys.argv[5]
    temp(DirPath, Source, Sink, PathNum, PathDumpFileName)
  else:
    print("TODO: Usage")
    sys.exit()



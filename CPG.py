import os

from GraphUtils import *

class CPG:
  def __init__(self, DirPath):
    NodePath = os.path.join(DirPath, 'nodes.csv')
    ASTEdgePath = os.path.join(DirPath, 'rels.csv')
    CPGEdgePath = os.path.join(DirPath, 'cpg_edges.csv')

    self.Nodes, self.ASTEdge = {}, {}
    self.CallEdge, self.CFEdge, self.DDEdge, self.CDEdge = {}, {}, {}, {}
    collectNodeDict(NodePath, self.Nodes)
    collectEdges(CPGEdgePath, self.CFEdge, self.CallEdge, self.DDEdge, self.CDEdge)
    collectASTEdges(ASTEdgePath, self.ASTEdge)

  def getNode(self, Id):
    return self.Nodes[Id]

  def getNodeType(self, Id):
    return self.Nodes[Id][0]

  def isFuncExit(self, Id):
    return self.getNodeType(Id) == 'CFG_FUNC_EXIT'

  def getCFDes(self, Id):
    for DesId in self.CFEdge[Id]:
      yield DesId

  def isCFSrc(self, Id):
    return Id in self.CFEdge

  def hasCallEdge(self, Id):
    return Id in self.CallEdge

  def getCallee(self, Id):
    return self.CallEdge[Id]

  def getFuncEntry(self, CalleeId):
    return CalleeId + 1

  def isTerminalNode(self, Id):
    return Id not in self.ASTEdge

  def getChildNodes(self, Id):
    for ChildId in self.ASTEdge[Id]:
      yield ChildId

  def traverse(self, Id, Subtree):
    Subtree += [Id]
    if self.isTerminalNode(Id): return
    for c in self.getChildNodes(Id):
      self.traverse(c, Subtree)

  def getSubtree(self, Id):
    Subtree = []
    # FuncDecl nodes are placeholders for call edges
    if self.getNodeType(Id) in ['AST_FUNC_DECL', 'AST_METHOD']:
      return [Id]
    self.traverse(Id, Subtree)
    return Subtree

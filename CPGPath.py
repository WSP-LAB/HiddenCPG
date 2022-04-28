import os

from GraphUtils import *

class CPGPath:
  def __init__(self, Path, Nodes, Edges, CFEdges, DDEdges, CallEdges, CDEdges):
    self.Path = Path
    self.Nodes = Nodes
    self.Edges = Edges
    self.CFEdges = CFEdges
    self.DDEdges = DDEdges
    self.CallEdges = CallEdges
    self.CDEdges = CDEdges

  def __str__(self):
    pathinfo = "[*] Top-level path: %s\n" % self.Path
    pathinfo += "[*] Node: %s\n" % self.Nodes
    pathinfo += "[*] ASTEdges: %s\n" % self.Edges
    pathinfo += "[*] CFEdges: %s\n" % self.CFEdges
    pathinfo += "[*] DDEdges: %s\n" % self.DDEdges
    pathinfo += "[*] CallEdges: %s\n" % self.CallEdges
    pathinfo += "[*] CDEdges: %s" % self.CDEdges

    return pathinfo

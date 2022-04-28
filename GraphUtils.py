def read(Path):
  with open(Path, 'rb') as f:
    return f.readlines()

def collectNodeDict(NodePath, Nodes):
  Lines = read(NodePath)
  for l in Lines[1:]:
    l = l.split('\t')
    Id = int(l[0])
    Type = l[2]
    if Type == 'string':
      if l[5][-1] == '\"':
        Nodes[Id] = (Type, l[5])
      else:
        real_str = ""
        for i in l[5:]:
            real_str += i

            if len(i) >= 1 and i[-1] == '\"':
                break
            real_str += "\t"
        Nodes[Id] = (Type, real_str)
    elif Type in ['AST_FUNC_DECL', 'AST_METHOD']:
        Nodes[Id] = (Type, l[11])
    else:
      Nodes[Id] = (Type, None)

def appendNode(Edges, Id1, Id2):
  if Id1 not in Edges: Edges[Id1] = []
  Edges[Id1] += [Id2]

def appendDDNode(Edges, Id1, Id2, label):
  if Id1 not in Edges: Edges[Id1] = []
  Edges[Id1] += [(Id2, label)]

def collectASTEdges(ASTEdgePath, ASTEdge):
  Lines = read(ASTEdgePath)
  for l in Lines[1:]:
    l = tuple(l.split())
    ParentID, ChildID = map(lambda x: int(x), l[:2])
    appendNode(ASTEdge, ParentID, ChildID)

flows = []
def collectEdges(CPGEdgePath, CFEdge, CallEdge, DDEdge, CDEdge):
  Lines = read(CPGEdgePath)
  for l in Lines[1:]:
    l = tuple(l.split())
    SrcID, DesID = map(lambda x: int(x), l[:2])
    if len(l) >= 3:
      Type = l[2]
      if Type == 'FLOWS_TO':
        appendNode(CFEdge, SrcID, DesID)
      elif Type == 'CALLS':
        CallEdge[SrcID] = DesID
      elif Type == 'REACHES':
        appendDDNode(DDEdge, SrcID, DesID, l[3])
      elif Type == 'CONTROLS':
        appendNode(CDEdge, SrcID, DesID)

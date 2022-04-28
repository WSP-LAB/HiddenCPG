from PHPBuiltIn import *
from WPBuiltIn import *
def read(Path):
  with open(Path, 'rb') as f:
    return f.readlines()

def collectNodeDict(NodePath, Nodes):
  Lines = read(NodePath)

  flag = False
  for l in Lines[1:]:
    l = l.split('\t')
    Id = int(l[0])
    Type = l[2]
    if Type == 'string':
      if l[5] is None:
        Nodes[Id] = (Type, None)
      else:
        Nodes[Id] = (Type, l[5][1:-1])

    else:
      Nodes[Id] = (Type, None)

   # if Type == 'string':
   #   if l[5] is None:
   #     Nodes[Id] = (Type, None)
   #   hihi = ""
   #   if l[5][-1] == '\"':
   #     hihi = l[5]
   #   else:
   #     real_str = ""
   #     for i in l[5:]:
   #         real_str += i

   #         if len(i) >= 1 and i[-1] == '\"':
   #             break
   #         real_str += "\t"
   #     hihi = real_str

   #   string_value = hihi[1:-1]
   #   if len(string_value) > 2 and (string_value[-1] == "\"" or string_value[-2:] == "\"\\"):
   #       a = string_value.rfind("<input")
   #       b = string_value.rfind("<a")
   #       if a == -1 and b == -1:
   #           pass
   #       elif b > a:
   #           Nodes[Id] = ("string", "<a_double")

   #           continue
   #       else:
   #           Nodes[Id] = ("string", "<input_double")
   #           continue

   #   if len(string_value) > 2 and (string_value[-1] == "\'" or string_value[-2:] == "\'\\"):
   #       a = string_value.rfind("<input")
   #       b = string_value.rfind("<a")
   #       if a == -1 and b == -1:
   #           pass
   #       elif b > a:
   #           Nodes[Id] = ("string", "<a_single")
   #           continue
   #       else:
   #           Nodes[Id] = ("string", "<input_single")
   #           continue

   #   if flag is True:
   #     Nodes[Id] = ("string", string_value)
   #     flag = False
   #     continue
   #   if string_value == "preg_replace" or \
   #           string_value == "preg_split" or \
   #           string_value == "preg_match" or \
   #           string_value == "ereg_replace":
   #     flag = True
   #     Nodes[Id] = ("string", string_value)
   #     continue

   #   if string_value is not None and ((string_value in PHPBuiltIn) or string_value.startswith('wp') or string_value.startswith('WP') or string_value.startswith('mysql') or string_value.startswith('MYSQL') or (string_value in WPBuiltIn)):
   #     Nodes[Id] = ("string", string_value)
   #   else:
   #     Nodes[Id] = ("string", None)
   # else:
   #   Nodes[Id] = (Type, None)

def appendNode(Edges, Id1, Id2):
  if Id1 not in Edges: Edges[Id1] = []
  Edges[Id1] += [Id2]

def collectASTEdges(ASTEdgePath, ASTEdge):
  Lines = read(ASTEdgePath)
  for l in Lines[1:]:
    l = tuple(l.split())
    ParentID, ChildID = map(lambda x: int(x), l[:2])
    appendNode(ASTEdge, ParentID, ChildID)

def collectEdges(CPGEdgePath, CFEdge, CallEdge, DDEdge, CDEdge):
  Lines = read(CPGEdgePath)
  for l in Lines[1:]:
    l = tuple(l.split())
    if len(l) >= 3:
      SrcID, DesID = map(lambda x: int(x), l[:2])
      if len (l) >= 3:
          Type = l[2]
          if Type == 'FLOWS_TO':
            appendNode(CFEdge, SrcID, DesID)
          elif Type == 'CALLS':
            CallEdge[SrcID] = [DesID]
          elif Type == 'REACHES':
            appendNode(DDEdge, SrcID, DesID)
          elif Type == 'CONTROLS':
            appendNode(CDEdge, SrcID, DesID)

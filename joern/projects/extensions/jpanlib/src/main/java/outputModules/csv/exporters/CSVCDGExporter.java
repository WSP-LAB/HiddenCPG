package outputModules.csv.exporters;

import cfg.nodes.ASTNodeContainer;
import cfg.nodes.CFGNode;
import cfg.nodes.AbstractCFGNode;
import databaseNodes.EdgeTypes;
import outputModules.common.CDGExporter;
import outputModules.common.Writer;
import cdg.CDG;
import cdg.CDGEdge;
import cfg.nodes.CFGNode;
import ast.ASTNode;

public class CSVCDGExporter extends CDGExporter
{

	@Override
	protected void addControlsEdge(CFGNode src, CFGNode dst)
	{
		long srcId = getId(src);
		long dstId = getId(dst);
		Writer.addEdge(srcId, dstId, null, EdgeTypes.CONTROLS);
	}

	private long getId(CFGNode node)
	{
        Long id = (node instanceof ASTNodeContainer) ? ((ASTNodeContainer)node).getASTNode().getNodeId()
						: ((AbstractCFGNode)node).getNodeId();
        return id;
	//	if (node instanceof ASTNodeContainer)
	//	{
	//		return Writer
	//				.getIdForObject(((ASTNodeContainer) node).getASTNode());
	//	}
	//	else
	//	{
	//		return Writer.getIdForObject(node);
	//	}
	}
    
	public void writeCDGEdges(CDG cdg) {

		for (CFGNode src : cdg.getVertices())
		{
			for (CDGEdge edge : cdg.outgoingEdges(src))
			{
				CFGNode dst = edge.getDestination();
                //if( src instanceof ASTNode && dst instanceof ASTNode) {

                 //   System.out.println("ihihihihiih");
			    	if (!src.equals(dst))
			    	{
			    		addControlsEdge(src, dst);
			    	}
             //   } 
			}
		}
        Writer.reset(); 
	}


}

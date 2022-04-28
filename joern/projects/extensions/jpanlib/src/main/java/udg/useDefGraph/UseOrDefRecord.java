package udg.useDefGraph;

import ast.ASTNode;
import ast.ASTNodeProperties;

public class UseOrDefRecord
{
	private ASTNode astNode;
	private boolean isDef;

	public UseOrDefRecord(ASTNode anASTNode, boolean aIsDef)
	{
		setAstNode(anASTNode);
		setDef(aIsDef);
	}

	public ASTNode getAstNode()
	{
		return astNode;
	}

	public void setAstNode(ASTNode astNode)
	{
		this.astNode = astNode;
	}

	public boolean isDef()
	{
		return isDef;
	}

	public void setDef(boolean isDef)
	{
		this.isDef = isDef;
	}
	
	@Override
	public String toString() {
		
		return (this.isDef ? "DEF" : "USE") + "@" + astNode.toString();
	}

};

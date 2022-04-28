package tests.udg;

import java.util.Stack;

import org.antlr.v4.runtime.ParserRuleContext;

import ast.ASTNode;
import ast.ASTNodeBuilder;
import ast.functionDef.FunctionDefBase;
import ast.walking.ASTNodeVisitor;
import ast.walking.ASTWalker;
import cfg.ASTToCFGConverter;
import cfg.CCFGFactory;
import cfg.CFG;
import parsing.ModuleParser;
import parsing.Modules.ANTLRCModuleParserDriver;

public class CFGCreator
{

	private class NodeVisitor extends ASTNodeVisitor
	{
		private CFG cfg;
		private ASTToCFGConverter astToCFG = new ASTToCFGConverter();

		public NodeVisitor()
		{
			astToCFG.setFactory(new CCFGFactory());
		}

		@Override
		public void visit(FunctionDefBase node)
		{
			cfg = astToCFG.convert(node);
		}

		public CFG getResult()
		{
			return cfg;
		}
	}

	private class Walker extends ASTWalker
	{

		NodeVisitor visitor = new NodeVisitor();

		@Override
		public void startOfUnit(ParserRuleContext ctx, String filename)
		{
		}

		@Override
		public void endOfUnit(ParserRuleContext ctx, String filename)
		{
		}

		@Override
		public void processItem(ASTNode node, Stack<ASTNodeBuilder> nodeStack)
		{
			node.accept(visitor);
		}

		public CFG getResult()
		{
			return visitor.getResult();
		}

	}

	public CFG getCFGForCode(String code)
	{
		ANTLRCModuleParserDriver driver = new ANTLRCModuleParserDriver();
		ModuleParser parser = new ModuleParser(driver);
		Walker walker = new Walker();
		parser.addObserver(walker);
		parser.parseString(code);

		return walker.getResult();
	}

}

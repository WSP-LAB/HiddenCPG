package tests.languages.c.parseTreeToAST;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.List;

import org.antlr.v4.runtime.ANTLRInputStream;
import org.junit.Test;

import antlr.ModuleLexer;
import ast.ASTNode;
import ast.c.functionDef.ParameterType;
import ast.declarations.ClassDefStatement;
import ast.declarations.IdentifierDecl;
import ast.functionDef.FunctionDefBase;
import ast.functionDef.ParameterBase;
import ast.statements.IdentifierDeclStatement;
import parsing.TokenSubStream;
import parsing.Modules.ANTLRCModuleParserDriver;

public class ModuleBuildersTest
{

	@Test
	public void testNestedStructs()
	{
		String input = "struct x{ struct y { struct z{}; }; }; abc";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement classDef = (ClassDefStatement) codeItems.get(0);
		ClassDefStatement yClass = (ClassDefStatement) classDef.content
				.getStatements().get(0);
		ClassDefStatement zClass = (ClassDefStatement) yClass.content
				.getStatements().get(0);

		assertTrue(codeItems.size() == 1);
		assertTrue(yClass.getIdentifier().getEscapedCodeStr().equals("y"));
		assertTrue(zClass.getIdentifier().getEscapedCodeStr().equals("z"));
	}

	@Test
	public void testStructName()
	{
		String input = "struct foo{};";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement codeItem = (ClassDefStatement) codeItems.get(0);
		assertTrue(codeItem.identifier.getEscapedCodeStr().equals("foo"));
	}

	@Test
	public void testUnnamedStruct()
	{
		String input = "struct {int x; } a;";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement codeItem = (ClassDefStatement) codeItems.get(0);
		assertTrue(codeItem.identifier.getEscapedCodeStr().equals("<unnamed>"));
	}

	@Test
	public void testStructContent()
	{
		String input = "struct foo{};";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement codeItem = (ClassDefStatement) codeItems.get(0);
		assertTrue(codeItem.content != null);
	}

	@Test
	public void testStructFunctionPointer()
	{
		String input = "struct foo{ int*** (**bar)(long*); };";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement codeItem = (ClassDefStatement) codeItems.get(0);
		IdentifierDeclStatement ptrStatement =
				(IdentifierDeclStatement) codeItem.content.getStatements().get(0);
		IdentifierDecl ptrItem =
				(IdentifierDecl) ptrStatement.getIdentifierDeclList().get(0);

		assertEquals(ptrItem.getType().completeType, "int * * * ( * * ) ( long * )");
	}


	@Test
	public void testFunctionInClass()
	{
		String input = "class foo{ bar(){} };";
		List<ASTNode> codeItems = parseInput(input);
		ClassDefStatement codeItem = (ClassDefStatement) codeItems.get(0);
		FunctionDefBase funcItem = (FunctionDefBase) codeItem.content.getStatements()
				.get(0);
		assertTrue(funcItem.getName().equals("bar"));
	}

	@Test
	public void testDecl()
	{
		String input = "int foo;";
		List<ASTNode> codeItems = parseInput(input);
		IdentifierDeclStatement codeItem = (IdentifierDeclStatement) codeItems
				.get(0);
		IdentifierDecl decl = (IdentifierDecl) codeItem.getIdentifierDeclList()
				.get(0);
		assertTrue(decl.getName().getEscapedCodeStr().equals("foo"));
	}

	@Test
	public void testDeclListAfterClass()
	{
		String input = "class foo{int x;} y;";
		List<ASTNode> codeItems = parseInput(input);
		IdentifierDeclStatement codeItem = (IdentifierDeclStatement) codeItems
				.get(codeItems.size() - 1);
		IdentifierDecl decl = (IdentifierDecl) codeItem.getIdentifierDeclList()
				.get(0);
		System.out.println(decl.getName().getEscapedCodeStr());
		assertTrue(decl.getName().getEscapedCodeStr().equals("y"));
	}

	@Test
	public void testClassDefBeforeContent()
	{
		String input = "class foo{int x;}";
		List<ASTNode> codeItems = parseInput(input);

		ClassDefStatement classCodeItem = (ClassDefStatement) codeItems.get(0);
		IdentifierDeclStatement identifierCodeItem = (IdentifierDeclStatement) classCodeItem.content
				.getStatements().get(0);
		IdentifierDecl decl = (IdentifierDecl) identifierCodeItem
				.getIdentifierDeclList().get(0);

		assertTrue(classCodeItem.identifier.getEscapedCodeStr().equals("foo"));
		assertTrue(decl.getName().getEscapedCodeStr().equals("x"));
	}

	@Test
	public void testFuncName()
	{
		String input = "void foo(){};";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		assertTrue(codeItem.getName().equals("foo"));
	}

	@Test
	public void testFuncSignature()
	{
		String input = "void foo(int x, char **ptr){};";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		System.out.println(codeItem.getEscapedCodeStr());
		assertTrue(codeItem.getEscapedCodeStr()
				.equals("foo (int x , char * * ptr)"));
	}

	@Test
	public void testSimpleParamList()
	{
		String input = "int foo(int x){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);

		System.out.println(codeItem.getChildCount());
		assertTrue(codeItem.getChildCount() == 4);
	}

	@Test
	public void testParamListGetCodeStr()
	{
		String input = "int foo(char *myParam, myType x){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		String codeStr = codeItem.getParameterList().getEscapedCodeStr();
		System.out.println(codeStr);
		assertTrue(codeStr.equals("char * myParam , myType x"));
	}

	@Test
	public void testParamGetCodeStr()
	{
		String input = "int foo(char *myParam, myType x){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		ParameterBase parameter = codeItem.getParameterList().getParameter(0);
		String codeStr = parameter.getEscapedCodeStr();
		System.out.println(codeStr);
		assertTrue(codeStr.equals("char * myParam"));
	}

	@Test
	public void testParamName()
	{
		String input = "int foo(myType myParam){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		String name = codeItem.getParameterList().getParameter(0).getName();
		assertTrue(name.equals("myParam"));
	}

	@Test
	public void testParamType()
	{
		String input = "int foo(char *myParam){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		ParameterType type = (ParameterType)codeItem.getParameterList().getParameter(0).getType();
		System.out.println(type.getEscapedCodeStr());
		assertTrue(type.getEscapedCodeStr().equals("char *"));
	}

	@Test
	public void testFunctionPtrParam()
	{
		String input = "int foo(void (*ptr)(char *)){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		System.out.println(codeItem.getEscapedCodeStr());
		assertTrue(codeItem.getName().equals("foo"));
	}

	@Test
	public void testEmptyParamList()
	{
		String input = "int foo(){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		assertTrue(codeItem.getChildCount() == 4);
		assertTrue(codeItem.getParameterList().getEscapedCodeStr().equals(""));
	}

	@Test
	public void testEmptyParamListLocation()
	{
		String input = "int foo(){}";
		List<ASTNode> codeItems = parseInput(input);
		FunctionDefBase codeItem = (FunctionDefBase) codeItems.get(0);
		assertTrue(codeItem.getParameterList().size() == 0);
	}

	private List<ASTNode> parseInput(String input)
	{
		ANTLRCModuleParserDriver parser = new ANTLRCModuleParserDriver();
		TestASTWalker testProcessor = new TestASTWalker();
		parser.addObserver(testProcessor);

		ANTLRInputStream inputStream = new ANTLRInputStream(input);
		ModuleLexer lex = new ModuleLexer(inputStream);
		TokenSubStream tokens = new TokenSubStream(lex);

		parser.parseAndWalkTokenStream(tokens);
		return testProcessor.codeItems;
	}

}

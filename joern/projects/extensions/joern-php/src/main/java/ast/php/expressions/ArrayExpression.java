package ast.php.expressions;

import java.util.Iterator;
import java.util.LinkedList;

import ast.ASTNode;
import ast.NullNode;
import ast.expressions.Expression;

public class ArrayExpression extends Expression implements Iterable<ArrayElement>
{

	private LinkedList<ArrayElement> arrayElements = new LinkedList<ArrayElement>();

	public int size()
	{
		return this.arrayElements.size();
	}

	public ArrayElement getArrayElement(int i) {
		return this.arrayElements.get(i);
	}

	// we expect either a null node or an ArrayElement
	public void addArrayElement(ASTNode arrayElement)
	{
		// This is a very special case; on the one hand PHPArrayExpression is "null-tolerant",
		// but on the other ASTNode.addChild(ASTNode) is not. So we add null to elements,
		// but NullNode to the list of children in ASTNode.

		if(arrayElement instanceof NullNode)
			this.arrayElements.add(null);
		else if(arrayElement instanceof ArrayElement)
			this.arrayElements.add((ArrayElement)arrayElement);
		else
			throw new RuntimeException("Trying to add array element"
			+ "to PHP array expression that is neither an ArrayElement"
			+ "nor a null node!");

		super.addChild(arrayElement);
	}

	@Override
	public Iterator<ArrayElement> iterator() {
		return this.arrayElements.iterator();
	}
}

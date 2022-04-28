package cfg.nodes;

import java.util.Map;

import databaseNodes.NodeKeys;

public class CFGEntryNode extends AbstractCFGNode
{

	@Override
	public String toString()
	{
		return -1 != getNodeId() ? "[(" + getNodeId() + ") ENTRY]" : "[ENTRY]";
	}

	@Override
	public Map<String, Object> getProperties()
	{
		Map<String, Object> properties = super.getProperties();
		properties.put(NodeKeys.CODE, "ENTRY");
		return properties;
	}
}

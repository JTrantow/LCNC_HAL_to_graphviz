# LCNC_HAL_to_graphviz Source
Source code for LCNC HAL(Hardware Abstraction Layer) to Graphviz DOT language python source code and documentation.

## Goals:
- [ ] Use multiple files for easy source control.

# Python coding steps:
- Parse HAL to dictionary using component type as key.
- Combine single layer numeric pin name fields.
- Create DotNodes from pins.out
- Create DotEdges from sig.out
- DotHeader(), DotFooter() helpers
- SearchDictionary() 
- Create Sinks and Sources node lists for invisible or connector tags.
- ShowComponentLevel()



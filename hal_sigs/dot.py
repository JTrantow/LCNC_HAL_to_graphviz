#
# Header for the output file.
#
def dot_header(Title):
        print('\n\ndigraph hal_nets {')
        print('\tgraph [rankdir="LR"];')
        print('\tlabel = ' + '"' + Title + '"')
        print('\tnode [fontsize = "8"];\n')

def dot_footer():    
        print('}\t#footer') 

#
# dot records don't like '-' or '.' in the field name.
#
def dot_field_name(c) :
        return c.replace('-','_').replace('.','_')

#
# Creates dot language clusters for each name in the dictionary component.
#
def create_subcomponent(pin_name_prefix_root, name_dict) :

        for name_key in name_dict.keys() :

                pin_name_prefix = pin_name_prefix_root;

                if (pin_name_prefix == ""):
                        print('\tsubgraph "component_' + name_key +'" {')
                else:
                        print('\tsubgraph "subcomponent_' + name_key +'" {')

                print('\t\tlabel = "' + name_key + '"')
                #
                # Build up the pin_name.
                #
                pin_name_prefix += name_key + '.'

                if (isinstance(name_dict[name_key], dict)) :
                        print('\t\tcluster = true;')
                        #
                        # Find the pins or subcomponents of this cluster.
                        #
                        sub_dict = name_dict[name_key]
                        #
                        # Figure out number of IN, OUT, I/O for table or tables.
                        #
                        in_count=0
                        out_count=0
                        io_count = 0
                        for k in sub_dict.keys() :                        
                                #
                                # If this is the leaf of the name create HTML at this level.
                                # else we need to create a sub/subgraph.
                                #
                                if isinstance(sub_dict[k], list) :
                                        [pin_dir, pin_type, pin_value] = sub_dict[k]

                                        if pin_dir == 'IN' :
                                                in_count=in_count+1
                                        elif pin_dir == 'OUT':
                                                out_count = out_count + 1
                                        elif pin_dir == 'I/O' :
                                                # Count I/O pins as IN. (FOR NOW)
                                                in_count += 1
                                                io_count += 1
                                        else :
                                                print('# Undefined pin type???')
                                                break;
                                else :
                                        #
                                        # Recurse down a level and create a sub subgraph
                                        #                                
                                        create_subcomponent(pin_name_prefix, {k: sub_dict[k]})

                        #
                        # Start a label for the pins defined at this level.
                        #
                        print('\t\t"' + pin_name_prefix[:-1]  + '" [ shape="none" margin=0 label=<')

                        if (in_count > 0) and (out_count > 0) :
                                print('\t\t\t<TABLE CELLBORDER="0" BORDER="0"><TR><TD> ')        

                        # IN Pin Direction
                        if (in_count > 0):
                                print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                                for k in sub_dict.keys() :
                                        if isinstance(sub_dict[k], list) :
                                                [pin_dir, pin_type, pin_value] = sub_dict[k]
                                                if (pin_dir == 'IN') or (pin_dir == 'I/O') :
                                                        print('\t\t\t\t\t<TR><TD ALIGN="LEFT" PORT="' + pin_name_prefix+k + '"> ' + k + '</TD></TR>')
                                print('\t\t\t\t</TABLE>')

                        if (in_count>0) and (out_count>0) :
                                print('\t\t\t\t</TD><TD>')

                        # OUT Pin Direction
                        if (out_count > 0):
                                print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                                for k in sub_dict.keys() :
                                        if isinstance(sub_dict[k], list) :
                                                [pin_dir, pin_type, pin_value] = sub_dict[k]
                                                if pin_dir == 'OUT' :
                                                        print('\t\t\t\t\t<TR><TD ALIGN="RIGHT" PORT="' + pin_name_prefix+k + '"> ' + k + '</TD></TR>')
                                print('\t\t\t\t</TABLE>')

                        if (in_count>0) and (out_count>0) :
                                print('\t\t\t</TD></TR></TABLE>')        
                        print('\t\t>]\n\t}      #  end sub/component_' + pin_name_prefix[:-1])        
                else :
                        print('\t\tcluster = false;')
                        print('\t\t"' + name_key + '" [ shape="box" ]')
                        print('\t}      #  end simple sub/component_' + pin_name_prefix[:-1])        

#
# Simply iterates through each component type in the component dictionary.
#
def create_subgraphs(component_dict) :
        for component_type_key in component_dict.keys() :
                create_subcomponent("", component_dict[component_type_key])

#
# Searches a particular component name dictionary for a pin name.
# Follow the name down to the leaf.
#
def search_pin_level(pin_name, name_dict) :
        name_index = 0        
        leaf_name = ""
        name_levels = pin_name.split('.')

        while (name_index < len(name_levels)) :
                name_to_match = ".".join(name_levels[0:name_index+1])
                if name_to_match in name_dict.keys() :
                        #
                        # Exact match to this dictionary name level.
                        #
                        if isinstance(name_dict[name_to_match], list) :
                                #
                                # Matched a leaf list.
                                #
                                leaf_name = name_to_match
                        else :
                                #
                                # Recurse down a level.
                                #
                                leaf_name = search_pin_level(pin_name[len(name_to_match)+1:], name_dict[name_to_match]) 
                                if leaf_name != "" :
                                        #
                                        # Found a leaf at a lower level
                                        #
                                        break;
                name_index+=1
        
        return leaf_name

#
# Searches the dictionary for a pin name and returns the cluster name.
# This is necessary when name levels are combined to simplify the name graph.
#
def search_pin(pin_name, name_dict) :
        leaf_name = ""
        #
        # From the halcmd signal output, We don't know the LCNC component type so search all component types in the dictionary.
        #
        for component_type_key in name_dict.keys() :
                #
                # 
                #
                for name in name_dict[component_type_key] :
                        if (pin_name.split('.')[0] == name[0:len(pin_name.split('.')[0])]) :
                                leaf_name =  search_pin_level(pin_name, name_dict[component_type_key])
                                break
                if leaf_name != "" :
                        break
        return leaf_name
#
# Returns the DOT reference for the full pin name.
# This function must match the DOT structures generated.
# Current implementation uses either 'cluster:port' for HTML records or 'cluster:node' for simple sub cluster nodes.
#
def edge_name(pin_name, name_structure) :
        if (0) :
                # Simple mapping that doesn't work when dictionary levels have been combined at the leaf.
                node_string = pin_name[0:pin_name.rfind('.')]
                n = '"' + node_string + '":"' + pin_name + '"'
        else :
                leaf_name = search_pin(pin_name, name_structure)
                cluster_name = pin_name.removesuffix('.' + leaf_name)
                n = '"' + cluster_name + '":"' + pin_name + '"'
        return n

#
# Create the DOT language subgraph for the sinks and source nodes from lists.
#
def create_sinks_sources(source_list, sink_list, io_list) :
        rank_source = ""
        rank_sink   = ""
        ret_string  = ""

        if (source_list) :  
                ret_string += '\tsubgraph sub_source {\n'
                for node in source_list :
                        ret_string += '\t\t' + node + "\t [shape=rarrow]\n"
                        rank_source += node + ' '
                ret_string += '\t}\n'
                ret_string += "\t{rank=source " + rank_source +"}\n\n"

        if (sink_list) :
                ret_string += '\tsubgraph sub_sink {\n'
                for node in sink_list :
                        ret_string += '\t\t' + node + "\t [shape=rarrow]\n"
                        rank_sink += node + ' '        
                ret_string += '\t}\n'
                ret_string += "\t{rank=sink " + rank_sink +"}\n\n"

        if (io_list) :
                ret_string += '\tsubgraph sub_io {\n'
                for node in io_list :
                        ret_string += '\t\t' + node + "\t [shape=octagon]\n"
                ret_string += '\t}\n\n'

        return ret_string
#
# Process lines than describe the hal signals and create dot edges.
# File is typically generated by "halcmd -s show sig | grep -v "^$" > sig.out" or equivalent.
#
def create_edges(signal_file_name, name_structure_dict) :
        #
        # Some signals may be missing a source or destination. 
        # Add some sink and source nodes for these signals.
        #
        sink_list=[]
        source_list=[]
        io_list=[]

        print("\n\t# ============== Create edges from " + signal_file_name + "===================")
        #
        # Use signal names from sig.out as edge labels instead of creating extra nodes. 
        #
        signal_list = open(signal_file_name, "r")

        for line in signal_list:
                if len(line.split()) >= 4 :
                        sig_list = line.split()
                        sig_type, sig_value, signal_name = sig_list[0:3]    
                        sig_declarations = sig_list[3:]
                        #
                        # Treat the remainder of the declaration as pairs of operator (<==, ==>, <=>) and node names.
                        #
                        sig_pairs = [(sig_declarations[i], sig_declarations[i+1]) for i in range(0, len(sig_declarations), 2)]

                        src_node_edge = None 
                        #
                        # Figure out the source, destinations edges for this signal edge.
                        #
                        #  
                        io_count = sum(1 for [d,n] in sig_pairs if d == "<=>")
                        if io_count == 0 :
                                #
                                # This signal is NOT <==>. 
                                #        
                                source_count = sum(1 for [d,n] in sig_pairs if d == "<==")
                                dest_count = sum(1 for [d,n] in sig_pairs if d == "==>")
                                if (0 == source_count) and (0 == dest_count) :
                                        print("#\tWARNING:  No source or destination or i/o for signal " + signal_name + "???")
                                elif (0 == source_count) and (1 <= dest_count) :                           
                                        #
                                        # Create a source for this signal.
                                        #
                                        source_list.append('"' + signal_name + '"')
                                        src_node_edge = source_list[-1]

                                        for [d,n] in sig_pairs :
                                                if d == "==>" :
                                                        dest_node_edge = edge_name(n, name_structure_dict)
                                                        print('\t' + src_node_edge + ':e -> ' + dest_node_edge + ' [label="' + signal_name + '"]')
                                elif (1 == source_count) and (0 == dest_count) :
                                        #
                                        # Create a sink for this signal.
                                        #
                                        sink_list.append('"' + signal_name + '"')
                                        dest_node_edge = sink_list[-1]

                                        source = [n for [d,n] in sig_pairs if d == "<=="] 
                                        src_node_edge = edge_name(source[0], name_structure_dict)
                                        
                                        print('\t' + src_node_edge + ' -> ' + dest_node_edge + ':w [label="' + signal_name + '"]')

                                elif (1 == source_count) and (1 <= dest_count) :
                                        #
                                        # Source and destination/s exist for this signal.
                                        #
                                        source = [n for [d,n] in sig_pairs if d == "<=="] 
                                        src_node_edge = edge_name(source[0], name_structure_dict)

                                        for [d,n] in sig_pairs :
                                                if d == "==>" :
                                                        dest_node_edge = edge_name(n, name_structure_dict)
                                                        print('\t' + src_node_edge + ' -> ' + dest_node_edge + ' [label="' + signal_name + '"]')

                        elif io_count == 1 :
                                #
                                # Create a dummy node for I/O signal.
                                #
                                io_list.append('"' + signal_name + '"')
                                src_node_edge = io_list[-1]

                                dest_node_edge = edge_name(sig_pairs[0][1], name_structure_dict)
                                print('\t' + src_node_edge + ' -> ' + dest_node_edge + ' [label="' + signal_name + '" dir="both" style="dashed"]')
                        else :
                                #
                                # More than one I/O pin for this signal.
                                # Assumes ALL pairs are <=>
                                #
                                src_node_edge = edge_name(sig_pairs[0][1], name_structure_dict)

                                for [d,n] in sig_pairs[1:] :
                                        dest_node_edge = edge_name(n, name_structure_dict)
                                        print('\t' + src_node_edge + ' -> ' + dest_node_edge + ' [label="' + signal_name + '" dir="both" style="dashed"]')

                                        src_node_edge = dest_node_edge 
                else :
                        print("#\tWARNING:\tcheck " + signal_file_name + " for empty lines")
                        break;
        #
        # Define the source/sink nodes for signal edges that are missing a source or destination pin.
        # These might be defined in another HAL that isn't loaded (suppressed to keep diagram simple).
        # Or maybe these signals can be deleted to simplify the .hal???
        #
        print("\t#============== Signals that don't have both source and destination pins. ===========")


        print(create_sinks_sources(source_list, sink_list, io_list))

#
# Header for the output file.
#
def dot_header(Title):
        print('\n\ndigraph hal_nets {')
        print('\tgraph [rankdir="LR"];')
        print('\tlabel = ' + '"' + Title + '"')
        print('\tnode [fontsize = "8"];\n')

def dot_footer():

        if (0) :
                print("\t# Test edges.")

                print("\tc")            

                print('\tc->"a":"a.pin0" ;')
                print('\t"b":"a.b.pin2" -> "aa":"a.b.c.pin5";')
    

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
                print('\t\tcluster = true;')
                #
                # Build up the pin_name.
                #
                pin_name_prefix += name_key + '.'

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
                                [pin_dir, pin_type] = sub_dict[k]

                                if pin_dir == 'IN' :
                                        in_count=in_count+1
                                elif pin_dir == 'OUT':
                                        out_count = out_count + 1
                                elif pin_dir == 'I/O' :
                                        # Count I/O pins as IN. (FOR NOW)
                                        in_count += 1
                                        io_count += 1
                                else :
                                        print('Undefined pin type.')
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
                                        [pin_dir, pin_type] = sub_dict[k]
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
                                        [pin_dir, pin_type] = sub_dict[k]
                                        if pin_dir == 'OUT' :
                                                print('\t\t\t\t\t<TR><TD ALIGN="RIGHT" PORT="' + pin_name_prefix+k + '"> ' + k + '</TD></TR>')
                        print('\t\t\t\t</TABLE>')

                if (in_count>0) and (out_count>0) :
                        print('\t\t\t</TD></TR></TABLE>')        
                print('\t\t>]\n\t}      #  end sub/component_' + pin_name_prefix[:-1])        
#
# Simply iterates through each component type in the component dictionary.
#
def create_subgraphs(component_dict) :
        for component_type_key in component_dict.keys() :
                create_subcomponent("", component_dict[component_type_key])



#
# Returns the DOT reference for the pin name using the name of the node and the port.
#
def edge_name(pin_name) :
        node_string = pin_name[0:pin_name.rfind('.')]
        n = '"' + node_string + '":"' + pin_name + '"'
        return n

#
# Process lines than describe the hal signals and create dot edges.
# File is typically generated by "halcmd -s show sig | grep -v "^$" > sig.out" or equivalent.
#
def create_edges(signal_file_name) :
        #
        # Some signals may be missing a source or destination. 
        # Add some sink and source nodes for these signals.
        #
        sink_list=[]
        source_list=[]

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
                        # Treat the remainder of the declaration as pairs of direction and component name.
                        # The signal will become the dot label.
                        #
                        # TODO Pay more attention to IN,OUT,I/O and use dir='both' with I/O.
                        #

                        #
                        # Figure out the source, destinations edges for this signal.
                        #
                        if len(sig_declarations) > 2 :
                                # Find the source pin for this signal(if it exists).
                                for count in range(0, len(sig_declarations), 2):
                                        if (sig_declarations[count] == "<==") or (sig_declarations[count] == "<=>") :
                                                # This is a source for the signal.

                                                src_node_edge = edge_name(sig_declarations[count+1])
                                                break;
                                if src_node_edge == None :
                                        src_node_edge = ""

                                # Find the destination pin or pins for this signal. 
                                for count in range(0, len(sig_declarations), 2):
                                        if (sig_declarations[count] ==  "==>") or (sig_declarations[count] ==  "<=>") :
                                                # This is a destination for the signal.
                                                dst_node_edge = edge_name(sig_declarations[count + 1])
                                                print('\t' + src_node_edge + "\t -> \t" + dst_node_edge + '\t [label="' + signal_name + '"]')
                                        elif sig_declarations[count] != "<==" :
                                                print("WARNING: Expected <== or ==> for ",end="")
                                                print(sig_declarations)
                        elif len(sig_declarations) == 2 :
                                #
                                # Signal doesn't have both a source and destination.
                                # Create an invisible node to be a sink or source for this signal.
                                #
                                if (sig_declarations[0] ==  "==>") or (sig_declarations[0] ==  "<=>") :
                                        dst_node_edge = edge_name(sig_declarations[1])
                                        source_list.append('"' + signal_name + '"')

                                        print('\t' + source_list[-1] + "\t -> \t" + dst_node_edge + '\t [label="' + signal_name + '"]')
                                elif (sig_declarations[0] == "<==") :
                                        src_node_edge = edge_name(sig_declarations[1])
                                        sink_list.append('"' + signal_name + '"')

                                        print('\t' + src_node_edge + '\t -> \t' + sink_list[-1] + '\t [label="' + signal_name + '"]')
                                else :
                                        print('#\tWARNING: Should be ==>, <=>, or <"" in ' + line)
                                
                        else :
                                print("#\tWARNING: Not enough sig_declarations in " + line)
                else :
                        print("#\tWARNING: Not enough sig_declarations.")
                        print("#\tcheck " + signal_file_name + " for empty lines")
                        break;
        #
        # Define the source/sink nodes for signal edges that are missing a source or destination pin.
        # These might be defined in another HAL that isn't loaded (suppressed to keep diagram simple).
        # Or maybe these signals can be deleted to simplify the .hal???
        #
        print("#\t ============== Signals that don't have both source and destination pins. ===========")
        ranksink=""
        ranksource=""
        for node in source_list :
                print('\t'+node + "\t [shape=rarrow]")
                ranksink += node+' '
        for node in sink_list :
                print('\t'+node + "\t [shape=rarrow]")
                ranksource += node+' '
        if (ranksink) :
                print("\t{rank=sink " + ranksink +"}")
        if (ranksource) :
                print("\t{rank=source " + ranksource +"}")

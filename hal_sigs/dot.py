#
# Header for the output file.
#
def dot_header(Title):
        print('\n\ndigraph hal_nets {')
        print('\tgraph [rankdir="LR"];')
        print('\tlabel = ' + '"' + Title + '"')
        print('\tnode [fontsize = "8"];\n')

def dot_footer():
        print('}        ')

#
# dot records don't like '-' or '.' in the field name.
#
def dot_field_name(c) :
        return c.replace('-','_').replace('.','_')

#
# Creates dot language clusters for each name in the dictionary component.
#
def create_cluster(pin_name_prefix, name_dict) :

        for name_key in name_dict.keys() :
                #print(name_key)
                print('\tsubgraph "cluster_' + name_key +'" {')
                print('\t\tlabel = "' + name_key + '"')
                print('\t\t"' + name_key + '" [ shape="box" label=<')
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
                                create_cluster(pin_name_prefix, {k: sub_dict[k]})

                if (in_count > 0) and (out_count > 0) :
                        print('\t\t\t<TABLE CELLBORDER="0" BORDER="0"><TR><TD> ')        

                # IN Pin Direction
                if (in_count > 0):
                        print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                        for k in sub_dict.keys() :
                                if isinstance(sub_dict[k], list) :
                                        [pin_dir, pin_type] = sub_dict[k]
                                        if (pin_dir == 'IN') or (pin_dir == 'I/O') :
                                                print('\t\t\t\t\t<TR><TD ALIGN="LEFT" PORT="' + pin_name_prefix+k + '"> ' + pin_name_prefix+k + '</TD></TR>')
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
                                                print('\t\t\t\t\t<TR><TD ALIGN="RIGHT" PORT="' + pin_name_prefix+k + '"> ' + pin_name_prefix+k + '</TD></TR>')
                        print('\t\t\t\t</TABLE>')

                if (in_count>0) and (out_count>0) :
                        print('\t\t\t</TD></TR></TABLE>')        
                print('\t\t>]\n\t}')        
#
# Simply iterates through each component type in the component dictionary.
#
def create_subgraphs(component_dict) :
        for component_type_key in component_dict.keys() :
                create_cluster("", component_dict[component_type_key])


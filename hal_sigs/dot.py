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
# Prints out HTML like dot description.
# Enclosing with "" allows names to include '.'.
# Notice I/O pins are currently grouped with the IN pins. Should break HTML into IN, OUT, I/O.
#
def my_cluster(label_name, node_list) :
        print('\tsubgraph "cluster_' + label_name +'" {')
        print('\t\tlabel = "' + label_name + '"')
        print('\t\t"' + label_name + '" [ shape="box" label=<')
        #
        # Figure out number of IN and OUT for table or tables.
        #
        in_count=0
        out_count=0
        for [pin_name, pin_dir] in node_list :
                if pin_dir == 'IN' :
                        in_count=in_count+1
                elif pin_dir == 'OUT':
                        out_count = out_count + 1
                elif pin_dir == 'I/O' :
                        # Count I/O pins as IN.
                        in_count += 1
                else :
                        print('Undefined pin type.')
                        break;
        if (in_count > 0) and (out_count > 0) :
                print('\t\t\t<TABLE CELLBORDER="0" BORDER="0"><TR><TD> ')        

        # IN Pin Direction
        if (in_count > 0):
                print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                for [pin_name, pin_dir] in node_list :
                        if (pin_dir == 'IN') or (pin_dir == 'I/O') :
                                print('\t\t\t\t\t<TR><TD ALIGN="LEFT" PORT="' + dot.dot_field_name(pin_name) + '"> ' + pin_name + '</TD></TR>')
                print('\t\t\t\t</TABLE>')

        if (in_count>0) and (out_count>0) :
                print('\t\t\t\t</TD><TD>')

        # OUT Pin Direction
        if (out_count > 0):
                print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                for [pin_name, pin_dir] in node_list :
                        if pin_dir == 'OUT' :
                                print('\t\t\t\t\t<TR><TD ALIGN="RIGHT" PORT="' + dot.dot_field_name(pin_name) + '"> ' + pin_name + '</TD></TR>')
                print('\t\t\t\t</TABLE>')

        if (in_count>0) and (out_count>0) :
                print('\t\t\t</TD></TR></TABLE>')        

        print('\t\t>]\n\t}')        

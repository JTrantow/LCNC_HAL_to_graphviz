#!/usr/bin/python
#
# This program converts files created by halcmd into graphviz graphs.
# halcmd will report whatever is running in your configuration. 
# The complexity of the graph can be limited by only loading .hal information you are interested in.
#
# You need to:
# 1) install graphviz, using "sudo apt-get install graphviz"
# 2) download the hal_sigs_graphviz.py attachment in a directory of your choice.
# 3) make a shell script inside the same dir, with the following lines in it and run it:
#       halcmd -s show pin | grep "==" > pin.out
#       halcmd -s show sig | grep -v "^$" > sig.out
#       python hal_sigs_graphviz.py > gv.in
#       dot -Tpng gv.in > gv.png
#

import string

#
# Finds a pin in a component dictionary.
#
def component(component_hash,pin):
        for lst in list(component_hash.values()):
                if pin in lst:
                        return list(component_hash.keys())[list(component_hash.values()).index(lst)]                

#
# Print the dictionary with one key per line.
#
def print_dictionary(dict) :
        for key in list(dict.keys()):
                print(key + ': ', end="")
                print(dict[key])
#
# Search the dictionary for the pin name.
# Returns the graphviz node and field name for the pin.
#  
def search_dictionary(dict, full_pin_name, debug) :

        if (debug == True):
                print('\tsd( ' + full_pin_name + ' ).')
        for key in list(dict.keys()):
                #
                # Start by just looking at the key.
                #
                if (debug == True):
                        print('\tsd( key ' + key + ' : ', end="")
                        print(dict[key], end="")
                        print(' ).')
                        print('\t' + full_pin_name[:len(key)+1] +'.' + '. vs ' + key )
                if (key + '.') == full_pin_name[:len(key)+1] :
                        #
                        # Continue match with pin name values.
                        #
                        if (debug == True) :
                                print('Found the key ' + key)

                        for [pin_name, pin_dir] in dict[key] :
                                if (key + '.' + pin_name) == full_pin_name :
                                        if (debug == True) :
                                                print('Found the full name ' + full_pin_name, end="")
                                                print(' Links to "' + key + '":' + pin_name)
                                        return('"' + key + '":' + dot_field_name(pin_name))

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
                                print('\t\t\t\t\t<TR><TD ALIGN="LEFT" PORT="' + dot_field_name(pin_name) + '"> ' + pin_name + '</TD></TR>')
                print('\t\t\t\t</TABLE>')

        if (in_count>0) and (out_count>0) :
                print('\t\t\t\t</TD><TD>')

        # OUT Pin Direction
        if (out_count > 0):
                print('\t\t\t\t<TABLE CELLBORDER="0" BORDER="1">')
                for [pin_name, pin_dir] in node_list :
                        if pin_dir == 'OUT' :
                                print('\t\t\t\t\t<TR><TD ALIGN="RIGHT" PORT="' + dot_field_name(pin_name) + '"> ' + pin_name + '</TD></TR>')
                print('\t\t\t\t</TABLE>')

        if (in_count>0) and (out_count>0) :
                print('\t\t\t</TD></TR></TABLE>')        

        print('\t\t>]\n\t}')

#
# Create a component hash of all the different components and pin_names and pin_dir.
#
f = open("pin.out", "r")
component_hash2={}
for line in f:
        comp_name, pin_type, pin_dir, pin_value, pin_name = line.split()[:5]
        if comp_name not in component_hash2:
                component_hash2[comp_name] = [];
        component_hash2[comp_name].append([pin_name, pin_dir])

if 0:
        print('\n\ncomponent_hash2')
        print_dictionary(component_hash2)

#
# Go through the component_hash2 and combine name levels if there is only one subtype.
# For instance mux4 with two sublevels can be simplified to one sublevel.
#"mux4" mux4.0.out mux4.0.sel0 mux4.0.sel1"
#"mux4_0" mux4_0.out mux4_0.sel0 mux4_0.sel1"
#
dot_node_dictionary = {}

for comp in list(component_hash2.keys()):
        #
        # Look at all the pins for this component type to figure out if a level can be combined. (Combine if names have only a numeric sublevel difference.)
        #
        #       mux4 float OUT 0    mux4.0.out 
        #       mux4 bit   IN FALSE mux4.0.sel0
        #       mux4 bit   IN FALSE mux4.0.sel1

        ignore_string = comp + "."
        level=1
        for [pin_name, pin_dir] in component_hash2[comp] :        
                pin_name_list = pin_name.split('.')
                if len(pin_name_list) > (level+1) and pin_name_list[level].isnumeric() :                
                        #
                        # Look at all the other pin names at this level.
                        #
                        level_same=True

                        for [p,d] in component_hash2[comp] :
                                p_name_list = p.split('.')
                                #print ('Compare ' + pin_name_list[level] + ' to ' + p_name_list[level])
                                if p_name_list[level] != pin_name_list[level]:
                                        level_same = False
                                        break
                        if level_same :
                                #print('Level can be combined.'  + comp + ' ' + pin_name + ' ' + pin_dir)
                                break
                else:
                        level_same = False
                        break
        if level_same :
                #
                # Combine the name and numeric as the new key.
                #
                key_name = pin_name_list[0] + "." + p_name_list[1]
                old_substring = p_name_list[0] + '.' + p_name_list[1]
                for [p,d] in component_hash2[comp] :       
                        p = p.replace(old_substring, key_name)
                        if key_name in dot_node_dictionary:
                                dot_node_dictionary[key_name].append([ p, d])                
                        else:
                                dot_node_dictionary.update({key_name:[[ p, d]]})                        
        else :

                dot_node_dictionary.update({comp: component_hash2[comp]})

if 0:
        print('\n\ndot_node_dictionary')
        print_dictionary(dot_node_dictionary)

#
# The default halcmd puts all named components of the same component type in one big list.
# Break named components into separate lists. 
# This drops the component key name which works for my naming convention. Could easily concatenate key name
#
named_components_dictionary = {}
for comp in list(dot_node_dictionary.keys()):
        #
        # Figure out if different component names are used which should be broken out as individual nodes.
        #
        node_name=None
        for [pin_name, pin_dir] in dot_node_dictionary[comp] :
                #
                # Check if the key name has been replaced.
                #
                if (comp + '.') == pin_name[:len(comp)+1] :
                        node_name = comp;
                        if node_name in named_components_dictionary :
                                named_components_dictionary[node_name].append([pin_name[len(comp)+1:],pin_dir])                
                        else:
                                named_components_dictionary.update({node_name:[[pin_name[len(comp)+1:],pin_dir]]})                        
                else :
                        #
                        # Look for simple named components. "simple" implies name of "component_name.pin".
                        #
                        pin_name_list = pin_name.split('.')
                        if (2 == len(pin_name_list)) :
                                pin_name_short = pin_name_list[0]
                                if node_name == None :
                                        node_name = pin_name_short
                                        print('\t' + node_name + ' - New name. type is ' + comp)                                        
                                else :                        
                                        if pin_name_short != node_name:
                                                print('\t' + pin_name_short + ' - This is a new name.')
                                                node_name = pin_name_short
                                
                                print ('\t\t' + pin_name_list[1] + ' ' + pin_dir)

                                #
                                # Add to a new dictionary list.
                                #
                                if node_name in named_components_dictionary :
                                        named_components_dictionary[node_name].append([pin_name_list[1],pin_dir])                
                                else:
                                        named_components_dictionary.update({node_name:[[pin_name_list[1],pin_dir]]})                        
                        else:
                                print('\t' + pin_name + ' NOT a simple name list. len() = ', len(pin_name_list))

if 0:
        print('\nnamed_components_dictionary')
        print_dictionary(named_components_dictionary)

#
# Generate the HTML like graphviz node definitions.
#
dot_header('Spindle.hal')
for node in list(named_components_dictionary.keys()):
        my_cluster(node,named_components_dictionary[node])

#
# Use signal names from sig.out as edge labels instead of creating extra nodes. 
#
f = open("sig.out", "r")
net_list = []
for line in f:
        sig_list = line.split()
        sig_type, sig_value, signal_name = sig_list[0:3]    
        sig_declarations = sig_list[3:]
        #
        # Treat the remainder of the declaration as pairs of direction and component name.
        # The signal will become the dot label.
        #
        # TODO Pay more attention to IN,OUT,I/O and use dir='both' with I/O.
        #

        # Find the source pin for this signal in the dictionary.
        if len(sig_declarations) > 2 :
                for count in range(0, len(sig_declarations), 2):
                        if (sig_declarations[count] == "<==") or (sig_declarations[count] == "<=>") :
                                # This is a source for the signal.
                                src_node_pin = search_dictionary(named_components_dictionary, sig_declarations[count + 1], False)            
                                if src_node_pin != None :
                                        #
                                        # Found the source pin name in the dictionary.
                                        #
                                        break;
                                else :
                                        print("WARNING source pin " + sig_declarations[count + 1] + ' not found.')
                # Find the destination pin or pins for this signal. 
                for count in range(0, len(sig_declarations), 2):
                        if (sig_declarations[count] ==  "==>") or (sig_declarations[count] ==  "<=>") :
                                # This is a destination for the signal.
                                dst_node_pin = search_dictionary(named_components_dictionary, sig_declarations[count + 1], False)                           
                                if dst_node_pin != None:                        
                                        net_list.append('\t' + src_node_pin + "\t -> \t" + dst_node_pin + '\t [label="' + signal_name + '"]')
                                else :
                                        print("WARNING destination pin " + sig_declarations[count + 1] + ' not found in dictionary.')
                        elif sig_declarations[count] != "<==" :
                                print("WARNING: Expected <== or ==> for ",end="")
                                print(sig_declarations)
        elif len(sig_declarations) == 2 :
                #
                # Signal doesn't have both a source and destination.
                # Create an invisible node to be a sink or source for this signal.
                #
                if (0):
                        print("signal without source or destination pin.")
                        print('sig_value: ' + signal_name + ' sig_declarations ', end="")
                        print(sig_declarations)
                        print('len() = ', end="")
                        print(len(sig_declarations))

                if (sig_declarations[0] ==  "==>") or (sig_declarations[0] ==  "<=>") :
                        # destination but no source.
                        dst_node_pin = search_dictionary(named_components_dictionary, sig_declarations[1], False)            
                        if dst_node_pin != None:
                                net_list.append('\tsrc_' + dot_field_name(signal_name) + "\t -> \t" + dst_node_pin + '\t [label="' + signal_name + '"]')
                        else :
                                print("WARNING destination pin " + sig_declarations[count + 1] + ' not found in dictionary.')

                elif (sig_declarations[0] == "<==") :
                        # source with no destination, Create an invisible sink node.
                        src_node_pin = search_dictionary(named_components_dictionary, sig_declarations[1], False)            
                        if src_node_pin != None:
                                net_list.append('\t' + src_node_pin + '\t -> \tdst_' + dot_field_name(signal_name) + '\t [label="' + signal_name + '"]')
                        else :
                                print("WARNING destination pin " + sig_declarations[count + 1] + ' not found in dictionary.')
                else :
                        print('WARNING: Should be ==>, <=>, or <""')
                
        else :
                print("WARNING: Not enough sig_declarations.")
for line in net_list:
        print(line + ";")
dot_footer()
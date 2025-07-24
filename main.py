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
from hal_sigs import *

print("\n\n\n\n\n\n\nmain() starts here");

#
# Create a component hash of all the different components and pin_names and pin_dir.
#
component_dict = dictionary.create_component_dictionary("pin.out")

print("\n============== Parsed file pin.out into a dictionary ================")
print(component_dict)

#
# Generate the HTML like graphviz node definitions.
#
dot.dot_header('Spindle.hal')

dot.create_subgraphs(component_dict)

print("\n============== Cluster subgraphs created ================")

if (0) :
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
                                    src_node_pin = dictionary.search_dictionary(named_components_dictionary, sig_declarations[count + 1], False)            
                                    if src_node_pin != None :
                                            #
                                            # Found the source pin name in the dictionary.
                                            #
                                            break;
                                    else :
                                            print("WARNING source pin " + sig_declarations[count + 1] + ' not found.')
                    # Find the destination pin or pins for this signal. 

                    if src_node_pin == None :
                            src_node_pin = ""
                    for count in range(0, len(sig_declarations), 2):
                            if (sig_declarations[count] ==  "==>") or (sig_declarations[count] ==  "<=>") :
                                    # This is a destination for the signal.
                                    dst_node_pin = dictionary.search_dictionary(named_components_dictionary, sig_declarations[count + 1], False)                           
                                    if dst_node_pin != None:                        
                                            print(src_node_pin)
                                            print(dst_node_pin)
                                            print(signal_name)
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
                            dst_node_pin = dictionary.search_dictionary(named_components_dictionary, sig_declarations[1], False)            
                            if dst_node_pin != None:
                                    net_list.append('\tsrc_' + dot.dot_field_name(signal_name) + "\t -> \t" + dst_node_pin + '\t [label="' + signal_name + '"]')
                            else :
                                    print("WARNING destination pin " + sig_declarations[count + 1] + ' not found in dictionary.')

                    elif (sig_declarations[0] == "<==") :
                            # source with no destination, Create an invisible sink node.
                            src_node_pin = dictionary.search_dictionary(named_components_dictionary, sig_declarations[1], False)            
                            if src_node_pin != None:
                                    net_list.append('\t' + src_node_pin + '\t -> \tdst_' + dot.dot_field_name(signal_name) + '\t [label="' + signal_name + '"]')
                            else :
                                    print("WARNING destination pin " + sig_declarations[count + 1] + ' not found in dictionary.')
                    else :
                            print('WARNING: Should be ==>, <=>, or <""')
                    
            else :
                    print("WARNING: Not enough sig_declarations.")
    for line in net_list:
            print(line + ";")


    dot.dot_footer()
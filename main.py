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

if (1) :
    #
    # Optional step that combines dictionary levels if there is only one element.
    #
    component_dict = dictionary.combine_dictionary_levels(component_dict)

    print(component_dict)

if (1) : 
    #
    # Generate the HTML like graphviz node definitions.
    #
    dot.dot_header('Combine Test')

    dot.create_subgraphs(component_dict)

    dot.create_edges("sig.out", component_dict)
    dot.dot_footer()
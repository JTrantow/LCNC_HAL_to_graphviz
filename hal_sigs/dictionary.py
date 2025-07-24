#
#
#
import sys

#
# dot records don't like '-' or '.' in the field name.
#
def dot_field_name(c) :
        return c.replace('-','_').replace('.','_')

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
        #        print(dict)
        if len(dict) > 0:
                for key in list(dict.keys()):
                        print(key , end="")
                        print(' : ', end="")
                        print(dict[key])
        else:
                print("empty dictionary")
#
# Search the dictionary for the pin name.
# Returns the graphviz node and field name for the pin.
#  
def search_dictionary(dict, full_pin_name, debug) :
        print("search_dictionary")

#
# Create and return a nested dictionary for the a subset of the full pin name.
#
def create_name_dict(name_list, pin_details) :
        #print("\t\tcreate_name_dict() ",end="")
        #print(name_list)
        
        pin_name_dict = {}
        #
        # Last dictionary value in list is the leaf pin name with details list.
        #
        pin_name_dict.update({name_list[-1]:pin_details})

        for n in reversed(name_list[:-1]) :
                pin_name_dict = {n:pin_name_dict}
        
        return(pin_name_dict)
#
# Parses the full pin_name and returns a nested dictionary list.
# Returns the pin name broken down into a list dictionaries of component,[subcomponent], and the final pin name.
# So pin name 'a.b.c' will be returned as [ {a:[{b:[{c:[pin_dir, pin_type]} ]} ]} ]
#
def parse_fullpinname(pin_name, pin_details, dict) :

        pin_splits = pin_name.split('.')
        
        match = True
        for name_index in range( len(pin_splits)) :
                #
                # Check all existing keys at this level for a match to the new pin name.
                #
                match = False
                for k in dict.keys() :
                        if (k == pin_splits[name_index]) :
                                dict=dict[k]
                                match = True; 
                                break
                if (match == False) :
                        #
                        # No match at this level. Append here.
                        #
                        dict.update(create_name_dict(pin_splits[name_index:], pin_details))
                        break 
#
# Creates a component dictionary from the halcmd show pins output file.
# The dictionary keys at the top level are the linuxcnc components.
#
def create_component_dictionary(filename) :
        #
        # Create a component hash of all the different base components and then call parse_pinname to parse the subgroups, pin_names and pin_dir.
        #
        component_dictionary = {}
        f = open(filename, "r")
        for line in f:
                if len(line.split()) >= 5 :
                        comp_name, pin_type, pin_dir, pin_value, pin_name = line.split()[:5]

                        #print("NEW FILE LINE " + comp_name, pin_name, pin_dir)
                        name_dictionary = component_dictionary.setdefault(comp_name,{})
                        parse_fullpinname(pin_name, [pin_dir, pin_type], name_dictionary)
                        #print('\n\n---- LINE COMPLETE ---------------------')
                        #print_dictionary(component_dictionary)
                        #print('---------------------------------------')
                else :
                        print("check " + filename + " for empty lines")
                        break;
        
        if (0) :
                #
                # Now that we have all the names in the dictionary, we can combine individual pin lists that share components and subcomponents which will aid the dot representation.
                #
                for key in list(component_dictionary.keys()):
                        print('=============== COMBINE ' + key + " ==================")
                        combine_pin_lists(pin_dictionary[key])

                        print_dictionary(pin_dictionary)

                        #for components_used_key in pin_dictionary.keys():
                                #print("component key:" + components_used_key)

                                #print(pin_dictionary[components_used_key][0])

                                #for component_name_key in pin_dictionary[components_used_key][0][0].keys():
                                #        print("\t"+component_name_key)
        
        return component_dictionary      


        
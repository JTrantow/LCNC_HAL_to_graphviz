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
# Creates a nested component dictionary from the halcmd show pins output file for all pin names.
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
        return component_dictionary      

#
# Searches all the names for a specific component for levels that can be simplified. (only one subcomponent name at a level)
# Return a copy of the dictionary to avoid problems adding and deleting to the dictionary while iterating.
# TODO: This only combines names at the component.sub1.sub2...leaf sub1 level. Could be extended to combine sub2..sunN levels.
# 
def combine_dictionary_names(names_dict) :
        
        combined_dict = {}

        for component_key in names_dict.keys() :  # First component(not subcomponent) name level. 
                #
                # Check One level down
                #
                sub_component_key = names_dict[component_key].keys()

                if (1 == len(sub_component_key)) and isinstance(names_dict[component_key][list(sub_component_key)[0]], dict):
                        key = list(sub_component_key)[0]
                        new_value = names_dict[component_key][key] #next(iter(sub_dictionary.values()))
                        new_key = component_key + '.' + key # We know there is only one, so take the first.
                        #
                        # New dictionary key that swallows a level.
                        #
                        combined_dict.update({new_key: new_value})
                else:
                        combined_dict.update( {component_key : names_dict[component_key] } )
        return(combined_dict)

#
# Searchs the component directory and combines names if there is a component or subcomponent dictionary level with only one key.
# This simplifies the graph by removing a subcluster.
#
def combine_dictionary_levels(dictionary) :
        combined_dict={}
        for cc in list(dictionary.keys()) :  # Copy of the keys.
                combined_dict.update({cc : combine_dictionary_names(dictionary[cc])})
        return(combined_dict)




                                


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
                                        return('"' + key + '":' + dot.dot_field_name(pin_name))
#
# Parses the full pin_name and returns a nested dictionary list.
# Returns the pin name broken down into a list dictionaries of component,[subcomponent], and the final pin name.
# So pin name 'a.b.c' will be returned as [ {a:[{b:[{c:[pin_dir, pin_type]} ]} ]} ]
#
def parse_pinname(pin_name, pin_dir, pin_type) :
        #print("\tparse_pinname( " + pin_name + "," +pin_dir + "," + pin_type + ")")

        pin_splits = pin_name.split('.')
        #
        # The last part of the pin_name(leaf) is special case.
        #
        name = pin_splits.pop()
        name_list=[{name: [pin_dir, pin_type]}]
        
        for name in reversed(pin_splits):
                name_list={name:name_list}
        return(name_list)
#
# Combine individual pin lists with common components and subcomponents.
#
def combine_pin_lists(l) :
        #print('combine_pin_list()')
        #
        # Iterate over the list of names for this type of component.
        # Compare the name to the other names to see if they can be combined.
        #        
        match_level=1
        #
        # Use a while loop because if we merge we want the for loops to restart.
        #
        while (match_level > 0) :
                match_level=0

                print("=========== starting a combine merge ============================")
                print(l)

                for idx_name, name in enumerate(l[:-1]) :
                        print("\nname:\t",end="")
                        print(name)
                        #
                        # Only need to compare the current name to the following names in the list.
                        # By construction next_name's are assumed to be simple (only one key per list level).
                        #
                        for idx_next, name_next in enumerate(l[l.index(name)+1:]):
                                print("next:\t",end="")
                                print(name_next)
                                #
                                # We now have the name and name_next lists that should be merged if possible.
                                #
                                name_test=name
                                next_test=name_next
                                #
                                # Loop until a key name doesn't have a match.
                                #                                
                                match_level=0
                                key2=0
                                matching_keys = True;                                                                                                              
                                while matching_keys :
                                        key2=list(next_test.keys())[0]

                                        #
                                        # display the name_test.keys
                                        # 
                                        print(name_test)
                                        print(type(name_test))
                                        for k in name_test.keys() :
                                                print("Search these keys: ",end="")
                                                print(k)

                                        for k in name_test.keys() :
                                                if (key2 == k):
                                                        print("MATCH key is ", end="")
                                                        print(key2)

                                                        match_level = match_level+1

                                                        print(type(name_test[k]))
                                                        print(name_test[k])

                                                        print(type(next_test[key2]))
                                                        print(next_test[key2])

                                                        if isinstance(name_test[k], list) and isinstance(next_test[key2], list) :
                                                                name_test = name_test[k][0]
                                                                next_test = next_test[key2][0]
                                                                
                                                                print("match level ",end="")
                                                                print(match_level)
                                                        else :
                                                                print('pin name leaf reached')                                             
                                                                break;
                                                else :
                                                        matching_keys = False
                                                        print("NOT A MATCH ", end="")
                                                        print(k,key2)
                                                        break;                                        
                                        print("for key match loop done.")
                                        if match_level > 0 :
                                                print("while key matching is done, match_level is : ", end = "")
                                                print(match_level)
                                        if match_level > 0 :
                                                #
                                                # Combine the dictionary for these two pin names.
                                                #
                                                print("MERGING")
                                                print(name_test)
                                                print(next_test)

                                                name_test.update(next_test)
                                                print("MERGED ",end="")                                                                                                
                                                print(name_test)
                                                #
                                                # Remove the pin name that was just merged.
                                                #
                                                print("REMOVING ",end="")
                                                print(l[idx_name+idx_next+1] )
                                                del l[idx_name+idx_next+1]                                          
                                                #sys.exit()
                                                #
                                                # Since we merged and deleted we need to restart the big while loop.
                                                #
                                                break;
                                        else:
                                               break;                                
                                print(match_level)
                                if (match_level > 0) :
                                        break;
                        if (match_level > 0) :
                                break;
        print("while no more matches done")
        print(l)
        return(l)
#
# Creates a pin dictionary from the halcmd show pins output.  
# The dictionary keys are the linuxcnc components.
#
def create_pin_dictionary(filename) :
        
        if (0) :
                print('test keys')
                #d = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
                d =  {'a': [{'pin1': ['IN', 'bit']}]}, {'a': {'b': [{'pin2': ['IN', 'bit']}]}}, {'a': {'b': [{'pin3': ['IN', 'bit']}]}}

                print(type(d))
                print(type(d[0]))
                print(d)
                #print(list(d.keys()))
        
        #
        # Create a component hash of all the different components and pin_names and pin_dir.
        # Each component has a dictionary of named components of the same type.
        #
        pin_dictionary={}

        #
        # Start by putting each pinname into the pin_dictionary (without any combining of component or subcomponent names)
        #
        f = open(filename, "r")
        for line in f:
                if len(line.split()) >= 5 :
                        comp_name, pin_type, pin_dir, pin_value, pin_name = line.split()[:5]

                        #print("NEW FILE LINE "+comp_name, pin_name, pin_dir)
                        p = parse_pinname(pin_name, pin_dir, pin_type)
                        pin_dictionary.setdefault(comp_name,[]).append(p)
                        #print('\n\n---- LINE COMPLETE ---------------------')
                        #print_dictionary(pin_dictionary)
                        #print('---------------------------------------')
                else :
                        print("check "+filename+" for empty lines")
                        break;
        #
        # Now that we have all the names in the dictionary, we can combine individual pin lists that share components and subcomponents which will aid the dot representation.
        #
        for key in list(pin_dictionary.keys()):
                print('=============== COMBINE ' + key + " ==================")
                combine_pin_lists(pin_dictionary[key])

                print_dictionary(pin_dictionary)

                #for components_used_key in pin_dictionary.keys():
                        #print("component key:" + components_used_key)

                        #print(pin_dictionary[components_used_key][0])

                        #for component_name_key in pin_dictionary[components_used_key][0][0].keys():
                        #        print("\t"+component_name_key)
        
        return pin_dictionary                
        
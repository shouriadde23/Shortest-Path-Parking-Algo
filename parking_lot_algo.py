import xml.etree.ElementTree as ET
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


################################################################################################
# 1.) Read Input file and get the starting location  and final parking location x, y coordinates.
# 2.) Read parking lot config file and store the parking lane information as node list.
# 3.) Add start and end point into node list.
# 4) Generate a node map based on speed using node list.
# 5) Generate a node map based on distance using node list.
# 6) Compute the shortest path between source and all other nodes  including end point.
# 7) Plot the parking lot as well as shortest path between start and end node.
###############################################################################################



# Description:
# pl_read_user_input is to read user config  file and get start location and end i.e final parking location
# X, Y coordinates and write them in a list

def pl_read_user_input(userinput_xml,start_pt,end_pt):
    newtree = ET.parse(userinput_xml)
    root1 = newtree.getroot()
    
    for child in root1:
       start_pt[0]=float(child[0].text)
       start_pt[1]=float(child[1].text)
       end_pt[0]=float(child[2].text)
       end_pt[1]=float(child[3].text)

# Description:
# The function is_coor_present_in_rectangle determines if a coordinate defined by
# (start_x,start_y) is present in the rectangle bounded by pl_entry_x, pl_entry_y,
# pl_exit_x, pl_exit_y, pl_width, pl_height.

def is_coor_present_in_rectangle(pl_entry_x, pl_entry_y, pl_exit_x, pl_exit_y, pl_width, pl_height, coordinate_x, coordinate_y):
    ##print("Entered function")

    if((coordinate_x <= pl_exit_x) and (coordinate_x >= pl_entry_x) and
       (coordinate_y <= pl_exit_y) and (coordinate_y >= pl_entry_y)):
        ##print("Starting coordinates are inside designated lane")
        ret_val = True
    else:
        ##print("Starting coordinates are NOT inside designated lane")
        ret_val = False
    return ret_val


# Description:
# The function pl_determine_pl_name_for_coordinate determines which parking lane
# a given coordinate belongs to. The function will iterate through all the PL entries
# in the present configuration XML file and determine the parking lane name in which
# the start coordinate is present.

def pl_determine_pl_name_for_coordinate(coordinate_x, coordinate_y):
    newtree = ET.parse("parking_config.xml")
    root1 = newtree.getroot()
    for child in root1:
        pl_name = child[0].text
        if("PL" in (child[0].text)):
           pl_en_x=int(child[1].text)
           pl_en_y=int(child[2].text)
           pl_ex_x=int(child[3].text)
           pl_ex_y=int(child[4].text)
           pl_width=int(child[5].text)
           pl_height=int(child[6].text)
           pl_orient=child[7].text
        #  #print("++++++++++++++++++++++++")
        #  #print(child[0].text)
        #  #print(child[1].text)
        #  #print(child[2].text)
        #  #print(child[3].text)
        #  #print(child[4].text)
        #  #print(child[5].text)
        #  #print(child[6].text)
        #  #print(coordinate_x, coordinate_y)
           ret_val = is_coor_present_in_rectangle(pl_en_x, pl_en_y, pl_ex_x, pl_ex_y, pl_width, pl_height, coordinate_x, coordinate_y)
        #  #print(ret_val)
           if ret_val == True:
               found_pl_name = pl_name
               #pl_calculate_entry_exit_coordinates_for_lane(pl_name,pl_en_x, pl_en_y, pl_ex_x, pl_ex_y, pl_width, pl_height,pl_orient)
               ##print(node_list)
    return found_pl_name


# Description:
#The function pl_calculate_entry_exit_coordinates_for_lane to calculate the entry coordinate/node
#and exit coordinate/node given the parking lane rectangle parameters, pl_entry_x, pl_entry_y, pl_exit_x, pl_exit_y, pl_width, pl_height
#Store the (entry_node_x, entry_node_y) and (exit_node_x,exit_node_y) in a dictionary as key value pairs.

def pl_calculate_entry_exit_coordinates_for_lane(pl_name,pl_en_x, pl_en_y, pl_ex_x, pl_ex_y, pl_width, pl_height,pl_orient,node_list):
    #node_list={}
    ret_value='true'
    if (pl_orient=="VERTICAL"):
        #print (" Lane is vertical")
        node_entry_x=pl_en_x+(pl_width/2)
        node_entry_y=pl_en_y
        node_exit_x=pl_en_x+(pl_width/2)
        node_exit_y=pl_ex_y
        #node_list[pl_name]=[[node_entry_x,node_entry_y],[node_exit_x,node_exit_y]]
    ##print(node_list)  
    elif(pl_orient=="HORIZONTAL"):
        #print (" Lane is Horizontal")
        node_entry_x=pl_en_x
        node_entry_y=pl_en_y+(pl_height/2)
        node_exit_x=pl_ex_x
        node_exit_y=pl_en_y+(pl_height/2)
    else:
        ret_value='false'

    if (ret_value=='true'):
        node_list[pl_name]=[[node_entry_x,node_entry_y],[node_exit_x,node_exit_y]]
        ##print(node_list)        
        
    return(ret_value)


# Description:
#The function pl_determine_pl_entry_exit_coordinate_for_all_lanes takes parking lot config file and
#generates node list for all lanes.Every lane's entry  is treated as a node , simillarly exit is also
#treated as node. Vertical lanes are excluded. Once all the nodes from config are added to node list array
# Start point/location and End point/Location are added as nodes into node list .

                   
def pl_determine_pl_entry_exit_coordinate_for_all_lanes(config_xml,start_pt,end_pt):
    ##print(config_xml)
    ret_value="true"
    newtree = ET.parse(config_xml)
    root1 = newtree.getroot()
    # TBD : Move node_list allocation out of this function, and pass the array into this function by allocating it from outside.
    node_list=np.zeros(64,dtype=[('name','U10'),('enex','U10'),('x','f4'),('y','f4'),('conn_arr','O'),('lane_entry_conn','U10'),('lane_exit_conn','U10'),('speed','f4')])
    connecting_lanes=np.zeros(64,dtype=[('name','U10'),('enex','U10'),('x','f4'),('y','f4'),('conn_arr','O'),('lane_entry_conn','U10'),('lane_exit_conn','U10'),('speed','f4')])

    # enter start and end pt information in to node list
    iter = 0
    conn_lanes_iter = 0 

    node_list[iter]['name'] = "start"
    node_list[iter]['enex'] = "inside"
    node_list[iter]['x'] = start_pt[0]
    node_list[iter]['y'] = start_pt[1]
    start_node_ln=pl_determine_pl_name_for_coordinate(start_pt[0],start_pt[1])
    node_list[iter]['conn_arr'] = [start_node_ln,"entry",start_node_ln,"exit"]

    iter = iter + 1
    for child in root1:
        found_valid_lane = 1
        ret_value = "true"
        pl_name = child[0].text
        ##print(pl_name) 
        if("PL" in (child[0].text)):
            pl_en_x=int(child[1].text)
            pl_en_y=int(child[2].text)
            pl_ex_x=int(child[3].text)
            pl_ex_y=int(child[4].text)
            pl_width=int(child[5].text)
            pl_height=int(child[6].text)
            pl_speed=int(child[8].text)
            pl_orient=child[9].text
            pl_connect=child[10].text
            pl_conn_entry_ln=child[11].text
            pl_conn_exit_ln=child[12].text
            #print(pl_orient)
            if (pl_orient=="VERTICAL"):   
                #print (" Lane is vertical")
                node_entry_x=pl_en_x+(pl_width/2)
                node_entry_y=pl_en_y
                node_exit_x=pl_en_x+(pl_width/2)
                node_exit_y=pl_ex_y
                #ret_value='false'
                found_valid_lane = 1 
                ##print("iamhere1")
		#if lane is vertical, fill connecting_lanes array.
                connecting_lanes[conn_lanes_iter]['name'] = pl_name
                connecting_lanes[conn_lanes_iter]['enex'] = 'entry'
                connecting_lanes[conn_lanes_iter]['x'] = node_entry_x 
                connecting_lanes[conn_lanes_iter]['y'] = node_entry_y
                connecting_lanes[conn_lanes_iter]['conn_arr'] = pl_connect.split(',')
                connecting_lanes[conn_lanes_iter]['lane_entry_conn'] = pl_conn_entry_ln
                connecting_lanes[conn_lanes_iter]['lane_exit_conn'] = pl_conn_exit_ln
                connecting_lanes[conn_lanes_iter]['speed'] = pl_speed

                conn_lanes_iter = conn_lanes_iter + 1
                connecting_lanes[conn_lanes_iter]['name'] = pl_name
                connecting_lanes[conn_lanes_iter]['enex'] = 'exit'
                connecting_lanes[conn_lanes_iter]['x'] = node_exit_x 
                connecting_lanes[conn_lanes_iter]['y'] = node_exit_y
                connecting_lanes[conn_lanes_iter]['conn_arr'] = pl_connect.split(',')
                connecting_lanes[conn_lanes_iter]['lane_entry_conn'] = pl_conn_entry_ln
                connecting_lanes[conn_lanes_iter]['lane_exit_conn'] = pl_conn_exit_ln
                connecting_lanes[conn_lanes_iter]['speed'] = pl_speed
                conn_lanes_iter = conn_lanes_iter + 1


		
		
            elif(pl_orient=="HORIZONTAL"):
                ##print (" Lane is Horizontal")
                node_entry_x=pl_en_x
                node_entry_y=pl_en_y+(pl_height/2)
                node_exit_x=pl_ex_x
                node_exit_y=pl_en_y+(pl_height/2)
                ##print("iamhere2")
                found_valid_lane = 1
		# if lane is horizontal, update node_list array.
                node_list[iter]['name'] = pl_name
                node_list[iter]['enex'] = 'entry'
                node_list[iter]['x'] = node_entry_x 
                node_list[iter]['y'] = node_entry_y
                node_list[iter]['conn_arr'] = pl_connect.split(',')
                node_list[iter]['lane_entry_conn'] = pl_conn_entry_ln
                node_list[iter]['lane_exit_conn'] = pl_conn_exit_ln
                node_list[iter]['speed'] = pl_speed

                iter = iter + 1
                node_list[iter]['name'] = pl_name
                node_list[iter]['enex'] = 'exit'
                node_list[iter]['x'] = node_exit_x 
                node_list[iter]['y'] = node_exit_y
                node_list[iter]['conn_arr'] = pl_connect.split(',')
                node_list[iter]['lane_entry_conn'] = pl_conn_entry_ln
                node_list[iter]['lane_exit_conn'] = pl_conn_exit_ln
                node_list[iter]['speed'] = pl_speed
                iter = iter + 1
            else:
                ret_value='false'

            ##print("###### ",pl_connect)
            #if ((found_valid_lane == 1 ) and
            #    (ret_value=="true")
            #    ): 
            #    node_list[iter]['name'] = pl_name
            #    node_list[iter]['enex'] = 'entry'
            #    node_list[iter]['x'] = node_entry_x 
            #    node_list[iter]['y'] = node_entry_y
            #    node_list[iter]['conn_arr'] = pl_connect.split(',')
            #    iter = iter + 1
            #    node_list[iter]['name'] = pl_name
            ##    node_list[iter]['enex'] = 'exit'
            #    node_list[iter]['x'] = node_exit_x 
            #    node_list[iter]['y'] = node_exit_y
            #    node_list[iter]['conn_arr'] = pl_connect.split(',')
            #    iter = iter + 1

    node_list[iter]['name'] = "end"
    node_list[iter]['enex'] = "inside"
    node_list[iter]['x'] = end_pt[0]
    node_list[iter]['y'] = end_pt[1]
    end_node_ln=pl_determine_pl_name_for_coordinate(end_pt[0],end_pt[1])
    node_list[iter]['conn_arr'] = [end_node_ln,"entry",end_node_ln,"exit"]
     
    iter = iter + 1          
    #print(node_list)
    #print (connecting_lanes)
    return ret_value, node_list,iter,connecting_lanes

            
# Description :
# The function pl_generate_node_map_with_weights is to generate node map based on the speed of the lanes as well as the
# location coordinates of each node.

def pl_generate_node_map_with_weights_time(node_list, num_elements_in_node_list,connecting_lanes) :
        # n=np.prod(node_list.shape)
        n = num_elements_in_node_list
        node_map=np.zeros((n,n))

        for i in range(n):
            for j in range(n):
                ##print node_list[i] and node_list[j] values.
                #print("++++++++++ i = ",i,";","j = ",j,"++++++++++++++++");
                #print(node_list[i]);
                #print(node_list[j]);
                # 1. Set entry to entry and exit to exits as zero.
                if (i == j):
                    node_map[i][j] = 0
                # 2. If i and j entries belong to the same PL name, check to see enex field to be entry or exit
                #    and subtract the x coordinate to fill in the weight.
                elif ((node_list[i]['name'] == node_list[j]['name'] ) and
                      (((node_list[i]['enex'] == 'entry' ) and (node_list[j]['enex'] == 'exit' )) or
                       ((node_list[i]['enex'] == 'exit' ) and (node_list[j]['enex'] == 'entry' )))) :
                    if (node_list[j]['x'] > node_list[i]['x']):
                        node_map[i][j] = (node_list[j]['x'] - node_list[i]['x'])/(node_list[j]['speed'])
                    else:
                        node_map[i][j] = (node_list[i]['x'] - node_list[j]['x'])/(node_list[j]['speed'])
                # 3. Check if a node entry connects to another node(s) entry.
                #    Check if a node exit connects to another node(s) exit.
                #    if this condition is satisfied, calculate the weight.
                elif ((node_list[i]['name'] != node_list[j]['name'] ) and
                      (node_list[i]['name'] != 'start' ) and
                      (node_list[i]['name'] != 'end') and
                      (node_list[j]['name'] != 'start' ) and
                      (node_list[j]['name'] != 'end') and
                      (((node_list[i]['enex'] == 'entry') and ( node_list[j]['enex'] == 'entry' )) or
                       ((node_list[i]['enex'] == 'exit') and ( node_list[j]['enex'] == 'exit' ))
                      )
                     ):
                    inode_conn_arr_num = len(node_list[i]['conn_arr'])
                    #print("$$$$$$ inode_conn_arr_num = ",inode_conn_arr_num,"$$$$$$$$$$$$$$$$$$$$$$")
                    #jnode_conn_arr_num = len(node_list[j]['conn_arr'])
                    #for ca_j in range(jnode_conn_arr_num):
                    match_found = 0
                    for ca_i in range(inode_conn_arr_num):
                        if ( node_list[i]['conn_arr'][ca_i] == node_list[j]['name'] ):
                            # if match occured, exit from the for ca_i loop.
                            #print("++++++++ WENT INTO IFFFFFFFFFF +++++++++++++")
                            # Obtain the connecting lane name between the 2 lanes.
                            # Example if PL_3 connects to PL_4 via PL_1 from entry
                            # and PL_2 from exit, then following code will assign
                            # connecting_lane accordingly.
                            if ( node_list[i]['enex'] == 'entry' ) :
                                conn_lane_name = node_list[i]['lane_entry_conn']
                            elif ( node_list[i]['enex'] == 'exit' ) :
                                conn_lane_name = node_list[i]['lane_exit_conn']

                            conn_lane_iter = 0
                            conn_lane_found = 0 
                            while ((conn_lane_iter < len(connecting_lanes) ) and ( conn_lane_found == 0 )) :
                                if ( connecting_lanes[conn_lane_iter]['name'] == conn_lane_name ) :
                                    conn_lane_speed = connecting_lanes[conn_lane_iter]['speed']
                                    conn_lane_found = 1
                                conn_lane_iter = conn_lane_iter + 1
                                
                            if ( node_list[j]['y'] > node_list[i]['y'] ):
                                #node_map[i][j] = node_list[j]['y'] - node_list[i]['y']
                                node_map[i][j] = (node_list[j]['y'] - node_list[i]['y'])/conn_lane_speed
                            else:
                                #node_map[i][j] = node_list[i]['y'] - node_list[j]['y']
                                node_map[i][j] = (node_list[i]['y'] - node_list[j]['y'])/conn_lane_speed
                            match_found = 1     
                        else:
                            #print("------ WENT INTO ELSE --------")
                            node_map[i][j] = 0 
                        #print("%%%%%%% Just updated i =",i," j =",j," value = ",node_map[i][j]," %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        if ( match_found == 1 ) :
                            break
                # 4. Check if a node is start node or end node.
                # Iterate through conn_arr elements and just connect them.
                # because by this time we know to which lane start and end node belong to.
                # if this condition is satisfied, calculate the weight.
                elif ((node_list[i]['name'] != node_list[j]['name'] ) and
                      (node_list[i]['name'] == 'start' ) or
                      (node_list[i]['name'] == 'end') 
                     ):
                    inode_conn_arr_num = len(node_list[i]['conn_arr'])
                    #print("$$$$$$ IN START/END CASE inode_conn_arr_num = ",inode_conn_arr_num,"$$$$$$$$$$$$$$$$$$$$$$")
                    #jnode_conn_arr_num = len(node_list[j]['conn_arr'])
                    #for ca_j in range(jnode_conn_arr_num):
                    match_found = 0
                    for ca_i in range(inode_conn_arr_num):
                        # When entered first time, check for 2 elements in conn_arr array, and skip count by 1.
                        ca_i_next = ca_i + 1;
                        if  ( ( node_list[i]['conn_arr'][ca_i] == node_list[j]['name'] ) and
                              ( node_list[i]['conn_arr'][ca_i_next] == node_list[j]['enex'] )
                            ):
                            # if match occured, exit from the for ca_i loop.
                            #print("++++++++ START/END CASE WENT INTO IFFFFFFFFFF +++++++++++++")
                            if ( node_list[j]['x'] > node_list[i]['x'] ):
                                #node_map[i][j] = node_list[j]['x'] - node_list[i]['x']
                                node_map[i][j] = (node_list[j]['x'] - node_list[i]['x']) / node_list[j]['speed']
                            else:
                                node_map[i][j] = (node_list[i]['x'] - node_list[j]['x']) / node_list[j]['speed']
                            # Trick... Set node_map[j][i] to node_map[i][j] here to populate unpopulated elements.
                            node_map[j][i] = node_map[i][j]
                            match_found = 1     
                        else:
                            #print("------ START/END CASE WENT INTO ELSE --------")
                            node_map[i][j] = 0 
                        #print("%%%%%%% START/END Just updated i =",i," j =",j," value = ",node_map[i][j]," %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        if ( match_found == 1 ) :
                            break
                        # Skip count by 1. Should use a while loop here instead of for loop. Bad programming.
                        # Who increments a variable in a for loop dah...
                        ca_i = ca_i + 1
                #5. No condition was met.
                else: 
                    node_map[i][j] = 0
            #print("###### END OF FOR LOOP i =",i,"###############################################")
        return(node_map)
                ##
            
# Description :
# The function pl_generate_node_map_with_weights is to generate node map based on the just distance .
# This function is not called in the current mode.


def pl_generate_node_map_with_weights_dist(node_list, num_elements_in_node_list) :
        # n=np.prod(node_list.shape)
        n = num_elements_in_node_list
        node_map=np.zeros((n,n))

        for i in range(n):
            for j in range(n):
                ##print node_list[i] and node_list[j] values.
                #print("++++++++++ i = ",i,";","j = ",j,"++++++++++++++++");
                #print(node_list[i]);
                #print(node_list[j]);
                # 1. Set entry to entry and exit to exits as zero.
                if (i == j):
                    node_map[i][j] = 0
                # 2. If i and j entries belong to the same PL name, check to see enex field to be entry or exit
                #    and subtract the x coordinate to fill in the weight.
                elif ((node_list[i]['name'] == node_list[j]['name'] ) and
                      (((node_list[i]['enex'] == 'entry' ) and (node_list[j]['enex'] == 'exit' )) or
                       ((node_list[i]['enex'] == 'exit' ) and (node_list[j]['enex'] == 'entry' )))) :
                    if (node_list[j]['x'] > node_list[i]['x']):
                        node_map[i][j] = node_list[j]['x'] - node_list[i]['x']
                    else:
                        node_map[i][j] = node_list[i]['x'] - node_list[j]['x']
                # 3. Check if a node entry connects to another node(s) entry.
                #    Check if a node exit connects to another node(s) exit.
                #    if this condition is satisfied, calculate the weight.
                elif ((node_list[i]['name'] != node_list[j]['name'] ) and
                      (node_list[i]['name'] != 'start' ) and
                      (node_list[i]['name'] != 'end') and
                      (node_list[j]['name'] != 'start' ) and
                      (node_list[j]['name'] != 'end') and
                      (((node_list[i]['enex'] == 'entry') and ( node_list[j]['enex'] == 'entry' )) or
                       ((node_list[i]['enex'] == 'exit') and ( node_list[j]['enex'] == 'exit' ))
                      )
                     ):
                    inode_conn_arr_num = len(node_list[i]['conn_arr'])
                    #print("$$$$$$ inode_conn_arr_num = ",inode_conn_arr_num,"$$$$$$$$$$$$$$$$$$$$$$")
                    #jnode_conn_arr_num = len(node_list[j]['conn_arr'])
                    #for ca_j in range(jnode_conn_arr_num):
                    match_found = 0
                    for ca_i in range(inode_conn_arr_num):
                        if ( node_list[i]['conn_arr'][ca_i] == node_list[j]['name'] ):
                            # if match occured, exit from the for ca_i loop.
                            #print("++++++++ WENT INTO IFFFFFFFFFF +++++++++++++")
                            if ( node_list[j]['y'] > node_list[i]['y'] ):
                                node_map[i][j] = node_list[j]['y'] - node_list[i]['y']
                            else:
                                node_map[i][j] = node_list[i]['y'] - node_list[j]['y']
                            match_found = 1     
                        else:
                            #print("------ WENT INTO ELSE --------")
                            node_map[i][j] = 0 
                        #print("%%%%%%% Just updated i =",i," j =",j," value = ",node_map[i][j]," %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        if ( match_found == 1 ) :
                            break
                # 4. Check if a node is start node or end node.
                # Iterate through conn_arr elements and just connect them.
                # because by this time we know to which lane start and end node belong to.
                # if this condition is satisfied, calculate the weight.
                elif ((node_list[i]['name'] != node_list[j]['name'] ) and
                      (node_list[i]['name'] == 'start' ) or
                      (node_list[i]['name'] == 'end') 
                     ):
                    inode_conn_arr_num = len(node_list[i]['conn_arr'])
                    #print("$$$$$$ IN START/END CASE inode_conn_arr_num = ",inode_conn_arr_num,"$$$$$$$$$$$$$$$$$$$$$$")
                    #jnode_conn_arr_num = len(node_list[j]['conn_arr'])
                    #for ca_j in range(jnode_conn_arr_num):
                    match_found = 0
                    for ca_i in range(inode_conn_arr_num):
                        # When entered first time, check for 2 elements in conn_arr array, and skip count by 1.
                        ca_i_next = ca_i + 1;
                        if  ( ( node_list[i]['conn_arr'][ca_i] == node_list[j]['name'] ) and
                              ( node_list[i]['conn_arr'][ca_i_next] == node_list[j]['enex'] )
                            ):
                            # if match occured, exit from the for ca_i loop.
                            #print("++++++++ START/END CASE WENT INTO IFFFFFFFFFF +++++++++++++")
                            if ( node_list[j]['x'] > node_list[i]['x'] ):
                                node_map[i][j] = node_list[j]['x'] - node_list[i]['x']
                            else:
                                node_map[i][j] = node_list[i]['x'] - node_list[j]['x']
                            # Trick... Set node_map[j][i] to node_map[i][j] here to populate unpopulated elements.
                            node_map[j][i] = node_map[i][j]
                            match_found = 1     
                        else:
                            #print("------ START/END CASE WENT INTO ELSE --------")
                            node_map[i][j] = 0 
                        #print("%%%%%%% START/END Just updated i =",i," j =",j," value = ",node_map[i][j]," %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        if ( match_found == 1 ) :
                            break
                        # Skip count by 1. Should use a while loop here instead of for loop. Bad programming.
                        # Who increments a variable in a for loop dah...
                        ca_i = ca_i + 1
                #5. No condition was met.
                else: 
                    node_map[i][j] = 0
            #print("###### END OF FOR LOOP i =",i,"###############################################")
        return(node_map)



    
#Description :
# The function pl_algo_print_solution is to print node and distance of the node from source

def pl_algo_print_Solution(node_list_count, dist,newpts):
        print("Vertex Distance from Source")
        for node in range(node_list_count):
            print( node,"and",dist[node],newpts)
 
    # A utility function to find the vertex with 
    # minimum distance value, from the set of vertices 
    # not yet included in shortest path tree


#Description :
# The function pl_algo_minDistance will calculate the minimum distance between source i.e zeroth node
# and  each node. it is called inside pl_alog_short_weight

def pl_algo_minDistance(dist, sptSet,node_list_count):
        global min_index
        # Initilaize minimum distance for next node
        min = sys.maxsize
 
        # Search not nearest vertex not in the 
        # shortest path tree
        for v in range(node_list_count):
                if ((dist[v] < min) and (sptSet[v] == False)):
                        min = dist[v]
                        min_index = v
        #print("min index is" ,min_index)                
        return min_index


#Description :
# The function pl_algo_short_weight  is to calculate the shortest path between the source and individual node
# Using short_weight algorithm first all paths between the start point and end point are computed and then the
# most optimal/shortest between source and nodes are computed
# short_weight's algorithm is used , which is for adjacency matrix representation of the graph
    
 
def pl_algo_short_weight(src,node_route,node_list_count,node_map):

        last_shortest_node= np.zeros((node_list_count,), dtype=int)
        dist = [sys.maxsize] * node_list_count
        dist[src] = 0
        sptSet = [False] * node_list_count
        #newpts[12]=0
 
        for cout in range(node_list_count):
 
            # Pick the minimum distance vertex from 
            # the set of vertices not yet processed. 
            # u is always equal to src in first iteration
            u = pl_algo_minDistance(dist, sptSet,node_list_count)
 
            # Put the minimum distance vertex in the 
            # shotest path tree
            sptSet[u] = True
 
            # Update dist value of the adjacent vertices 
            # of the picked vertex only if the current 
            # distance is greater than new distance and
            # the vertex in not in the shotest path tree
            #print("******** cout =",cout," *************")
            for v in range(node_list_count):
                if node_map[u][v] > 0 and sptSet[v] == False and dist[v] > dist[u] + node_map[u][v]:
                        dist[v] = dist[u] + node_map[u][v]
                        #print("cout =",cout,"v =",v,"u =",u," dist[v] = ",dist[v]," dist[u] = ",dist[u],"value =",graph[u][v])
                        #print("cout =",cout,"v =",v,"u =",u," dist[",v,"] = ",dist[v]," dist[",u,"] = ",dist[u],"value =",node_map[u][v])
                        # "u" tell us the shortest node, that is last visited prior to reaching "v".
                        #node_route[v][0] = u
                        last_shortest_node[v]=u
                        #newpts[v]=u
                        #print("inside dikstra loop",u,v,node_map[cout],[v])
 
        #printSolution(dist)
        for node in range(node_list_count):
            print( "Node : ",node ,"Weight(time) : ",dist[node])

        #print("INSIDEEEEEEEEE PRINTING last_shortest_node ")
        #print(last_shortest_node)
        #Build node list with the information stored in node_route from above loop.
        not_entered_inner_for_loop = 0
        incr = 0 
        for node in range(node_list_count):
            check_node = node
            not_entered_inner_for_loop = 0
            if ( last_shortest_node[check_node] == 0 ):
                continue
            else :
                if ( not_entered_inner_for_loop == 0 ):
                    check_node = node
                    incr = 0
                for route in range(node_list_count):
                    #print("node =",node,"route =",route)
                    not_entered_inner_for_loop = 1
                    if ( last_shortest_node[check_node] != 0 ) :
                        node_route[node][incr] = last_shortest_node[check_node]
                        incr = incr + 1
                        check_node = last_shortest_node[check_node]
                    else :
                        break 

# Description :
# This function pl_get_connected_nodes will read config file and for each node it will fetch the
# connecte node list.
 
def pl_get_conected_nodes(config_xml,node_name):        
    #open the config file and get the connected node information.
    newtree = ET.parse(config_xml)
    root1 = newtree.getroot()
    for child in root1:
        pl_name = child[0].text
        ##print(pl_name)
        ##print(node_name)
        if(node_name==(child[0].text)):
            connect_node=child[10].text

    ##print("this is return",connect_node)     
    return(connect_node)        
            

#Description :
# This function pl_get_trajectory_coor will generate all nodes the corresponds to the
# shortest path between source and end/destination location


def pl_get_trajectory_coor(node_route, node_list, node_list_count,plot_array):

    #index is the last element of node_route which is the end_node.
    index = node_list_count-1
    start_node = node_list[0]
    end_node = node_list[index]
    
    ##print("ROUTE : ")
    ##print("x =",start_node['x']," y= ",start_node['y'])
    ##print("x =",end_node['x']," y= ",end_node['y'])

    num = 0
    while ( node_route[index][num] != 0 ) :
        num = num + 1

    #print("&&&&&&& num = ",num," &&&&&&&&&" )

    fill = 0
    plot_array[fill]['x'] = start_node['x']
    plot_array[fill]['y'] = start_node['y']
    
    j = num     
    while ( j >= 0 ) :
        #print(node_route[index][j])       
        #print("x =",node_list[node_route[index][j]]['x']," y= ",node_list[node_route[index][j]]['y'])
        plot_array[fill]['x'] = node_list[node_route[index][j]]['x']
        plot_array[fill]['y'] = node_list[node_route[index][j]]['y']
        j = j - 1
        fill = fill + 1

    plot_array[fill]['x'] = end_node['x']
    plot_array[fill]['y'] = end_node['y']
    fill = fill + 1

    #print(plot_array)
    
    return fill


# Description :
# The function pl_plot_all_nodes will generate a list  of x and y coordinates to plot  using node_list.

def pl_plot_all_nodes(node_list,node_list_count,allnodes_array):

    for iter in range(node_list_count):
        allnodes_array[iter]['x']=node_list[iter]['x']
        allnodes_array[iter]['y']=node_list[iter]['y']
    #print("all nodes ",allnodes_array)        


# Description :
# The function pl_plot_trajectory will plot the trajectory of shortest path
# between source/start and end/destination  location.
    
def pl_plot_trajectory(plot_array,num_coordinates,allnodes_array,node_list_count) :
        plt.plot(*zip(*plot_array[:num_coordinates]), marker="o",color='b',linestyle="-",linewidth=3.0,label='Shortest path')
        #plt.legend(loc="upper right")
        #plt.ylabel('Y axis ')
        #plt.xlabel('X axis ')
        #plt.xticks(range(0,30))
        #plt.ylim(0,30)
        #plt.yticks(np.arange(0,30,1))
        plt.title(" Parking Lot ")
        plt.scatter(*zip(*allnodes_array[:node_list_count]), marker='o',color='r',linewidth=2.0,label="Nodes")
        #plt.legend(loc="upper right")
        #plt.grid()
        #plt.show()


# Description :
# The function pl_plot_parking_lot will plot the topology of the parking lot

def pl_plot_parking_lot(configxml):
    
    plt.figure(figsize=(20,20))
    currentAxis = plt.gca()
    newtree = ET.parse("parking_config.xml")
    root1 = newtree.getroot()
    for child in root1:
        pl_name = child[0].text
        if("PL" in (child[0].text)):
           pl_en_x=int(child[1].text)
           pl_en_y=int(child[2].text)
           pl_ex_x=int(child[3].text)
           pl_ex_y=int(child[4].text)
           pl_width=int(child[5].text)
           pl_height=int(child[6].text)
           pl_orient=child[7].text
           
           currentAxis.add_patch(Rectangle((pl_en_x,pl_en_y), pl_width, pl_height, fill=True, facecolor='gray',edgecolor='y',linewidth=3))
           #currentAxis.add_patch(Rectangle((3,3), 20, 2, fill=True, facecolor='yellow',edgecolor='g'))
           #plt.annotate(pl_name,xy=(pl_en_x,pl_en_y),color='r',ha='center',va="bottom")
           plt.annotate("Parking Lane"+ "  " +pl_name ,xy=(pl_en_x+(pl_width/2),pl_en_y+(pl_height/2)),color='r',ha='center',va="bottom")
        elif("PS" in (child[0].text)):
           ps_name=child[0].text 
           ps_en_x=int(child[1].text)
           ps_en_y=int(child[2].text)
           
           ps_width=int(child[5].text)
           ps_height=int(child[6].text)
           #ps_orient=child[7].text
           
           currentAxis.add_patch(Rectangle((ps_en_x,ps_en_y), ps_width, ps_height, fill=True, facecolor='white',edgecolor='black',linestyle='dotted',hatch='|',LineWidth='2'))
           #currentAxis.add_patch(Rectangle((3,3), 20, 2, fill=True, facecolor='yellow',edgecolor='g'))
           #plt.annotate(pl_name,xy=(pl_en_x,pl_en_y),color='r',ha='center',va="bottom")
           plt.annotate("Parking Slots"+ "  " +ps_name ,xy=(ps_en_x+(ps_width/2),ps_en_y+(ps_height/2)),color='r',ha='center',va="bottom")



           
    plt.grid(color='gray',lw=0.3)
    
       

def main():
    
        node_list=[]
        node_map=[]
        connecting_lanes=[]
	#connecting_lanes=np.zeros(64,dtype=[('name','U10'),('enex','U10'),('x','f4'),('y','f4'),('conn_arr','O'),('lane_entry_conn','U10'),('lane_exit_conn','U10'),('speed','f4')])
        start_pt=np.zeros(2)
        end_pt=np.zeros(2)
        node_list_count = 0
        plot_array=np.zeros(128,dtype=[('x','f4'),('y','f4')])
        configxml="parking_config.xml"
        pl_read_user_input("User_Input.xml",start_pt,end_pt)
        ret_value, node_list, node_list_count,connecting_lanes = pl_determine_pl_entry_exit_coordinate_for_all_lanes("parking_config.xml",start_pt,end_pt)
        node_map=pl_generate_node_map_with_weights_time(node_list, node_list_count,connecting_lanes) 
        #print(node_list)
        #print(connecting_lanes)
        #print(node_list_count)
        #print(ret_value)
        #print(node_map)
        #n=10    
        graph=node_map
        node_route=np.zeros((node_list_count,node_list_count), dtype=int)
            #visted=[]
            ###print(graph)
        # First argument is start node.
        pl_algo_short_weight(0,node_route,node_list_count,node_map)
        #print("$$$$$$$$ Outside short_weight $$$$$$$$$$$$$$")
        #print(node_route)
          
        #num_coordinates = pl_plot_trajectory(node_route, node_list, node_list_count, plot_array)
        num_coordinates = pl_get_trajectory_coor(node_route, node_list, node_list_count,plot_array)
        #print("============== ",num_coordinates)
        #allnodes_plot=np.zeros(node_list_count, dtype=)
        allnodes_array=np.zeros(node_list_count,dtype=[('x','f4'),('y','f4')])
        pl_plot_all_nodes(node_list,node_list_count,allnodes_array)
        pl_plot_parking_lot("parking_config.xml")
        pl_plot_trajectory(plot_array,num_coordinates,allnodes_array,node_list_count)
        plt.show() 
main()
    

           

    
    

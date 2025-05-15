# --- IMPORT LIBRARIES ---
import pandas as pd
import os
import shutil

# --- USER INPUTS ---
#in_dir: directory of .csv file to be converted
in_dir = '/home/yifan/tunnel/3d/'
#ori_file: name of .csv file to be converted (must be comma-delimited .csv)
#convert .msh to .csv before using this tool
ori_file = 'tunnel3d.csv'
#mesh_flag: if true, will output mesh.txt file
mesh_flag = True
#entity_sets_flag: if true, will output entity_sets.json files for each surface
#setup for bounding box only
entity_sets_flag = True
#velocity_constraints_flag: if true, will output velocity_constrains.txt file
#setup for bounding box only; does not consider duplicates/conflicts on edges
velocity_constraints_flag = True
#velocity constraints: insert desired values per direction; X=0, Y=1, Z=2
#() for no BC on that bounding box surface; None for no BC in that direction
Surface_Xmin = (0, None, None)
Surface_Xmax = (0, None, None)
Surface_Ymin = (0, 0, 0)
Surface_Ymax = (None, None, None)
Surface_Zmin = (None, None, 0)
Surface_Zmax = (None, None, 0)
Tunnel_side = (0, 0, None)
Tunnel_front = (None, None, None)

# --------------------------------------------------------------------
def gmsh_converter_tet(in_dir,
                       ori_file,
                       mesh_flag,
                       entity_sets_flag,
                       velocity_constraints_flag,
                       Surface_Xmin=pd.DataFrame(),
                       Surface_Xmax=pd.DataFrame(),
                       Surface_Ymin=pd.DataFrame(),
                       Surface_Ymax=pd.DataFrame(),
                       Surface_Zmin=pd.DataFrame(),
                       Surface_Zmax=pd.DataFrame(),
                       Tunnel_side=pd.DataFrame(),
                       Tunnel_front=pd.DataFrame()):

    # --- 0. USER INPUTS (CUSTOMIZATIONS) ---
    #mesh_file: name of converted mesh.txt
    mesh_file = 'mesh.txt'
    #velocity_constraints_file: name of converted velocity_constraints.txt
    velocity_constraints_file = 'velocity_constraints.txt'
    #entity_sets_file: name of converted entity_sets file WITHOUT suffix
    #will make a .json file
    entity_sets_file = 'entity_sets'
    #temp_space: name of temporary calculation space for conversion
    temp_space = 'temp_conversion_space_tet/'
    #nodes_file: name of temporary .csv to store all node information
    nodes_file = 'nodes_all.csv'
    #elements_file: name of temporary .csv to store all element information
    elements_file = 'elements_all.csv'
    #dflag: if true, will delete files/folders if already exist
    dflag = True
    #Volume_tags: dictionary of tags associated with each bounding box surface
    #tag numbers defined in gmsh input file
    Surface_tags = {
        **dict.fromkeys([140,228,384,540,628,716,804,892,980,118,206,362,518,606,694,782,870,958], Surface_Xmin),
        **dict.fromkeys([82,170,258,414,570,658,746,834,922,104,192,280,436,592,680,768,856,944], Surface_Xmax),
        **dict.fromkeys([70,114,136,92], Surface_Ymin),
        **dict.fromkeys([918,962,940,984], Surface_Ymax),
        **dict.fromkeys(range(1, 27), Surface_Zmin),
        **dict.fromkeys([989,945,901,857,813,769,725,681,637,549,505,471,1165,593,1121,393,437,1077,237,1033,349,149,315,281,193,105], Surface_Zmax),
        **dict.fromkeys([483,453,406,526,250,370,214,162], Tunnel_side),
        **dict.fromkeys([488,454,1143,1099,1055,1011,332,298], Tunnel_front)

    }
    Volume_tags = {
        "zatian1":41,"zatian2":42,"zatian3":43,"zatian4":44,
        "niantu1":37,"niantu2":38,"niantu3":39,"niantu4":40,
        "yunizhi1":33,"yunizhi2":34,"yunizhi3":35,"yunizhi4":36,
        "nianzhifen1":29,"nianzhifen2":30,"nianzhifen3":31,"nianzhifen4":32,"nianzhifen5":25,"nianzhifen6":26,"nianzhifen7":27,"nianzhifen8":28,"nianzhifen9":19,"nianzhifen10":20,"nianzhifen11":21,"nianzhifen12":22,
        "fenzhinian1_9":17,"fenzhinian1_10":18,"fenzhinian1_11":23,"fenzhinian1_12":24,"fenzhinian1_13":49,"fenzhinian1_14":50,"fenzhinian1_15":51,"fenzhinian1_16":52,
        "fenzhinian1_1":9,"fenzhinian1_2":10,"fenzhinian1_3":15,"fenzhinian1_4":16,"fenzhinian1_5":45,"fenzhinian1_6":46,"fenzhinian1_7":47,"fenzhinian1_8":48,
        "fenzhinian2_1":1,"fenzhinian2_2":2,"fenzhinian2_3":3,"fenzhinian2_4":4,"fenzhinian2_5":5,"fenzhinian2_6":6,"fenzhinian2_7":7,"fenzhinian2_8":8,"fenzhinian2_9":11,"fenzhinian2_10":12,"fenzhinian2_11":13,"fenzhinian2_12":14,
        "Tunnel1":11,"Tunnel2":13,"Tunnel3":45,"Tunnel4":47,"Tunnel5":49,"Tunnel6":51,"Tunnel7":19,"Tunnel8":21
        }

    # --- 1. SETUP ---
    # - 1.1 Directory setup -
    in_dir1 = in_dir
    in_dir2 = os.path.join(in_dir1, temp_space)
    try:
        os.mkdir(in_dir1 + temp_space)
    except FileExistsError:
        if dflag == True:
            shutil.rmtree(in_dir1 + temp_space)
            os.mkdir(in_dir1 + temp_space)
            print("Directory '%s' overwritten" % in_dir2)
        else:
            print("Directory '%s' already exists... quitting" % in_dir2)
            quit()

    # - 1.2 Read the csv file -
    df = pd.read_csv(in_dir1 + ori_file, header=None, low_memory=False)

    # - 1.3 Create working conversion files and read their dataframes -
    shutil.copyfile(in_dir1 + ori_file, in_dir2 + nodes_file)
    shutil.copyfile(in_dir1 + ori_file, in_dir2 + elements_file)
    df_n = pd.read_csv(in_dir2 + nodes_file, header=None, low_memory=False)
    df_e = pd.read_csv(in_dir2 + elements_file, header=None, low_memory=False)

    # - 1.4 Locate division between nodes and elements -
    Nlist = df.index[df[0] == '$EndNodes'].tolist()
    N = Nlist[0]

    # --- 2.0 NODES ---
    #find start and end of nodes in gmsh file
    Mlist = df.index[df[0] == '$Nodes'].tolist()
    Mn = Mlist[0] + 2
    Nn = N
    #slice to get only nodes, calculate number of nodes
    df_n = df_n.iloc[Mn:Nn, :]
    nnodes = df_n.shape[0]
    #correct node indices to start from 0
    df_n[0] = df_n[0].apply(lambda x: int(x) - 1)
    #export to .csv nodes_file
    df_n.to_csv(in_dir2 + nodes_file, index=False, header=False)

    # --- 3.0 ELEMENTS ---
    #find start and end of elements in gmsh file
    Mlist = df.index[df[0] == '$EndElements'].tolist()
    Me = Mlist[0]
    Ne = N + 3

    #slice to get only elements
    df_e = df_e.iloc[Ne:Me, :]
    #correct element indices to start from 0
    df_e[0] = df_e[0].apply(lambda x: int(x) - 1)
    for i in [5, 6, 7, 8]:
        df_e[i] = df_e[i].apply(lambda x: int(x) - 1 if pd.notnull(x) else x)
    #delete gmsh output column which provides no useful information
    del df_e[2]
    #export to .csv elements_file
    df_e.to_csv(in_dir2 + elements_file, index=False, header=False)
    
    # --- 4.0 MESH.TXT ---
    if mesh_flag == True:

        # - 4.1 Create & format parts -
        df_n_mesh = df_n
        #remove node indices column, reset headers
        del df_n_mesh[0]
        df_n_mesh.columns = range(df_n_mesh.columns.size)

        df_e_mesh = df_e
        #slice to get only surface elements, calculate number of surface elements
        df_e_mesh = df_e_mesh.loc[df_e_mesh.count(axis=1) == 8, [5, 6, 7, 8]]
        nelements_mesh = df_e_mesh.shape[0]

        #cast IDs to int then str (no trailing .0), reset headers
        df_e_mesh = df_e_mesh.astype(int).astype(str)
        df_e_mesh.columns = range(df_e_mesh.columns.size)

        #create header
        # yapf: disable
        df_mesh = pd.DataFrame([
            ['#!', 'elementShape', 'tetrahedron'],
            ['#!', 'elementNumPoints', 3],
            [str(nnodes), str(nelements_mesh), '']])
        # yapf: enable

        # - 4.2 Assemble parts & format -
        #assemble mesh.txt dataframe, remove extra trailing columns
        df_mesh = pd.concat([df_mesh, df_n_mesh, df_e_mesh],
                            axis=0,
                            ignore_index=True)
        df_mesh = df_mesh.drop(df_mesh.columns[[4, 5, 6, 7]], axis=1)
        
        # - 4.3 Export to .txt mesh_file -
        if not os.path.isfile(in_dir1 + mesh_file):
            df_mesh.to_csv(in_dir1 + mesh_file,
                           index=False,
                           header=False,
                           sep=' ')
        else:
            if dflag == True:
                os.remove(in_dir1 + mesh_file)
                df_mesh.to_csv(in_dir1 + mesh_file,
                               index=False,
                               header=False,
                               sep=' ')
                print("Mesh file '%s' overwritten" % mesh_file)
            else:
                print("Mesh file '%s' already exists... quitting" % mesh_file)
                quit()

    # --- 5.0 ENTITY_SETS.JSON ---
    if entity_sets_flag == True:
        # - 5.1 Create/reset/setup dataframes (outside loop) -
        df_entity_sets = pd.DataFrame()  #body
        #find location of start header, create footer
        first_surface_tag = list(Surface_tags.keys())[0]
        if Volume_tags:
            first_volume_tag = list(Volume_tags.values())[0]
        # yapf: disable
        df_entity_sets_middle_end = pd.DataFrame([
            ['', '', '', ']', '',],
            ['', '', '}', '', '',],
            ['', ']', '', '', '',]]) #footer
        df_entity_sets_end = pd.DataFrame([
            ['', '', '', ']', '',],
            ['', '', '}', '', '',],
            ['', ']', '', '', '',],
            ['}', '', '', '', '',]]) #footer
        # yapf: enable

        # - 5.2 Create & format parts of line dataframes (inside loop) -
        for tag in Surface_tags:
            df_tag = df_e.copy()
            
            # slice to get only line on tagged line
            df_tag = df_tag[df_tag.count(axis=1) == 7]
            df_tag = df_tag.loc[(df_tag[4] == tag), [5, 6, 7]]
            
            # create 1 column of all node indices for elements on tagged line
            df_tag = df_tag.stack().reset_index()
            df_tag = df_tag.drop(["level_0", "level_1"], axis=1)
            
            # reformat cols to entity_sets layout and eliminate node duplicates
            df_tag[1] = ''
            df_tag[2] = ''
            df_tag[3] = ''
            df_tag[4] = df_tag[0].astype(int).astype(str) + ','
            
            df_tag = df_tag.drop_duplicates(subset=[0])
            df_tag[0] = ''
            df_tag.loc[df_tag.index[-1], 4] = df_tag.loc[df_tag.index[-1], 4].rstrip(",")
            df_tag = df_tag.reset_index(drop=True)

            # - Create header dataframes -
            if tag == first_surface_tag:
                # first tag: node_sets start
                df_entity_sets_pre = pd.DataFrame([
                    ['{', '', '', '', ''],
                    ['', '"node_sets": [', '', '', ''],
                    ['', '', '{', '', ''],
                    ['', '', '', f'"id": {tag},', ''],
                    ['', '', '', '"set": [', '']
                ])
            else:
                # following tags: node_sets join
                df_entity_sets_pre = pd.DataFrame([
                    ['', '', '', ']', ''],
                    ['', '', '},', '', ''],
                    ['', '', '{', '', ''],
                    ['', '', '', f'"id": {tag},', ''],
                    ['', '', '', '"set": [', '']
                ])

            # - Concatenate each line dataframe -
            df_entity_sets = pd.concat(
                [df_entity_sets, df_entity_sets_pre, df_tag],
                axis=0,
                ignore_index=True
            )
        if Volume_tags:
            df_entity_sets = pd.concat([df_entity_sets, df_entity_sets_middle_end],
                                           axis=0,
                                           ignore_index=True)
        if Volume_tags:
            df_entity_sets = pd.concat(
                [df_entity_sets, pd.DataFrame([','])],
                axis=0,
                ignore_index=True
        )
        # ------------------------------------------------------
        # ------------------------------------------------------

        last_index = df_e[df_e.count(axis=1) == 7].index[-1]

        for tag in Volume_tags.values():
            df_tag = df_e.copy()
            # slice to get only elements on tagged surface
            df_tag = df_tag[df_tag.count(axis=1) == 8]
            df_tag = df_tag.loc[(df_tag[4] == tag)]
            # create 1 column of all node indices for elements on tagged surface
            df_tag = df_tag.reset_index()
            df_tag = df_tag[['index']]
            df_tag = df_tag.reset_index(drop=True)
            # reformat cols to entity_sets layout and eliminate node duplicates
            df_tag[1] = ''
            df_tag[2] = ''
            df_tag[3] = ''
            
            df_tag[4] = (df_tag['index'].astype(int) - last_index - 1).astype(str) + ','
            
            df_tag = df_tag.drop_duplicates(subset=['index'])
            
            df_tag['index'] = ''
            
            df_tag.loc[df_tag.index[-1], 4] = df_tag.loc[df_tag.index[-1], 4].rstrip(",")
            df_tag = df_tag.reset_index(drop=True)
            
            # - Create header dataframes for surface: cell_sets! -
            if tag == first_volume_tag:
                # first tag: node_sets start
                df_entity_sets_pre = pd.DataFrame([
                    ['', '"cell_sets": [', '', '', ''],
                    ['', '', '{', '', ''],
                    ['', '', '', f'"id": {tag},', ''],
                    ['', '', '', '"set": [', '']
                ])
            else:
                # following tags: node_sets join
                df_entity_sets_pre = pd.DataFrame([
                    ['', '', '', ']', ''],
                    ['', '', '},', '', ''],
                    ['', '', '{', '', ''],
                    ['', '', '', f'"id": {tag},', ''],
                    ['', '', '', '"set": [', '']
                ])
            
            # - Concatenate each surface dataframe -
            df_entity_sets = pd.concat(
                [df_entity_sets, df_entity_sets_pre, df_tag],
                axis=0,
                ignore_index=True
            )
        # - 5.5 Add footer to dataframe (outside loop) -
        df_entity_sets = pd.concat([df_entity_sets, df_entity_sets_end],
                                   axis=0,
                                   ignore_index=True)
        
        # - 5.6 Export to tagged entity_sets_file as a .json -
        if not os.path.isfile(in_dir1 + entity_sets_file + '.json'):
            df_entity_sets.to_csv(in_dir1 + entity_sets_file + '.json',
                                  index=False,
                                  header=False,
                                  sep='\t',
                                  quoting=3)
        else:
            if dflag == True:
                os.remove(in_dir1 + entity_sets_file + '.json')
                df_entity_sets.to_csv(in_dir1 + entity_sets_file + '.json',
                                      index=False,
                                      header=False,
                                      sep='\t',
                                      quoting=3)
                print("Entity sets file " + str(entity_sets_file) +
                      ".json overwritten")
            else:
                print("Entity sets file " + str(entity_sets_file) +
                      ".json already exists... quitting")
                quit()

    # --- 6.0 VELOCITY_CONSTRAINTS.TXT ---
    if velocity_constraints_flag == True:

        # - 6.1 Create & format parts, then concatenate to dataframe -
        df_velocity_constraints = pd.DataFrame()
        #loop through surfaces, ignore surfaces with no BCs
        for tag, tuple_loop in Surface_tags.items():
            if not (len(tuple_loop) == 0 or all(x is None
                                                for x in tuple_loop)):
                # - 6.2 Get desired node indices on each surface of interest -
                df_tag = df_e
                df_tag = df_tag[df_tag.count(axis=1) == 7]
                #slice to get only elements on tagged surface
                df_tag = df_tag.loc[(df_tag[4] == tag), [5, 6, 7]]
                #create 1 col of all node indices for elements on tagged surface
                df_tag = df_tag.stack().reset_index()
                df_tag = df_tag.drop("level_0", axis=1)
                df_tag = df_tag.drop("level_1", axis=1)
                #remove duplicate node indices on tagged surface, reset indices
                df_tag = df_tag.drop_duplicates(subset=[0])
                df_tag = df_tag.reset_index().drop("index", axis=1)

                # - 6.3 Create node indices, BCs for each direction needed -
                #create/reset empty dataframe for each surface
                df_tag_temp1 = pd.DataFrame()
                df_tag_temp2 = pd.DataFrame()
                #loop through directions, ignore directions with no BCs
                for i in range(len(tuple_loop)):
                    if not tuple_loop[i] == None:
                        #rows: 0 = node indices, 1 = direction, 2 = BC magnitude
                        df_tag_temp1[0] = df_tag[0].astype(int)
                        df_tag_temp1[1] = i
                        df_tag_temp1[2] = tuple_loop[i]
                        #concatenate direction i to surface-specific dataframe
                        df_tag_temp2 = pd.concat([df_tag_temp2, df_tag_temp1],
                                                 axis=0,
                                                 ignore_index=True)

                df_tag = df_tag_temp2
                #reset indices, reset headers
                df_tag = df_tag.reset_index().drop("index", axis=1)
                df_tag.columns = range(df_tag.columns.size)

                #assemble velocity_constraints.txt df by concatenating surfaces
                df_velocity_constraints = pd.concat(
                    [df_velocity_constraints, df_tag],
                    axis=0,
                    ignore_index=True)

        # - 6.4 Export to .txt velocity_constraints_file -
        if not os.path.isfile(in_dir1 + velocity_constraints_file):
            df_velocity_constraints.to_csv(in_dir1 + velocity_constraints_file,
                                           index=False,
                                           header=False,
                                           sep=' ')
        else:
            if dflag == True:
                os.remove(in_dir1 + velocity_constraints_file)
                df_velocity_constraints.to_csv(in_dir1 +
                                               velocity_constraints_file,
                                               index=False,
                                               header=False,
                                               sep=' ')
                print("Velocity constraints file '%s' overwritten" %
                      velocity_constraints_file)
            else:
                print(
                    "Velocity constraints file '%s' already exists... quitting"
                    % velocity_constraints_file)
                quit()


# --------------------------------------------------------------------
# --- MAIN ---
gmsh_converter_tet(in_dir, ori_file, mesh_flag, entity_sets_flag,
                   velocity_constraints_flag, Surface_Xmin,
                   Surface_Xmax, Surface_Ymin, Surface_Ymax,Surface_Zmin,Surface_Zmax,Tunnel_side,Tunnel_front)
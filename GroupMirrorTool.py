'''
Group Mirror Tool v1.3.0
-- mirror group objects by xy, yz, xz --
steps:
1. select the objects to be mirrored
2. run the tool
3. select the axis and apply

notice:
1. might have problem in maya 2015 
MAYA-16289
http://download.autodesk.com/us/support/files/maya_2015_service_pack_2/Maya2015_SP2_Readme_enu.html
negative scale make it looks black

TO-DO in v1.4.0
1. 'freeze' the new object
2. set the same hierarchy
3. rename system
4. change the GUI into a class

FIXED:
1. add rotation -- Sept 8
2. change the way to mirror, so that changing the pivot pos won't break it -- Sept 11
3. fixed mirroring parents oobject problem

Created on Sep 5, 2014

@author: FunghiApe
'''


import pymel.core as pm
import maya.cmds as cmds

"""unused
#groom the numbers
def showNiceDegree(input):
    if input < 360 and input >= 0:
        return input;
    elif input >= 360:
        input -= 360
        return showNiceDegree(input)
    elif input < 0:
        input += 360
        return showNiceDegree(input)
"""   
    

def killChildren(list, list_copy):
    for obj in list_copy:
        print obj
        obj_parent = obj.listRelatives(parent=True)
        if obj_parent:
            if obj_parent[0] in list_copy:
                print list
                list.remove(obj)
                print obj
                print list 
                print '---------------' 
                
                
#magic
def mirrorObjAlong(selection_list, axis):  
    ori_selected = list(selection_list)
    killChildren(ori_selected, selection_list)
    mir_selected_copy = pm.duplicate(ori_selected)
    mir_selected = list(mir_selected_copy)
    #fix bugs which caused by maya's group command removes parent hierachy
    print mir_selected  
    killChildren(mir_selected, mir_selected_copy)          
    mir_grp = pm.group(mir_selected, name='group_GMT_FA_mir')
    pm.xform(p=True, pivots=(0, 0, 0))
    if axis == 'x':
        mir_grp.scaleX.set(-1)
    if axis == 'y':
        mir_grp.scaleY.set(-1)
    if axis == 'z':
        mir_grp.scaleZ.set(-1)
        

    if(mir_grp.listRelatives(parent=True)):
        pm.parent(mir_selected, mir_grp.listRelatives(parent=True)[0])
    else:
        pm.parent(mir_selected, world = True)
    pm.delete('group_GMT_FA_mir') 
        
            
###########################################################
def runGroupMirror(*args):
    #get radio button selection
    getAxis = cmds.radioCollection("axis", q=True, sl=True)
    #show me all the selected objects in a list
    selection_list = pm.ls(selection = True)
    #check list empty
    if not selection_list:
        pm.confirmDialog(title='Error', button=['OK'], m='Please select the original objects!')
        return
    print "Selected: %s"%selection_list
    
    
    mirrorObjAlong(selection_list, getAxis)
    print "mirroring %s along axis %s"%(selection_list, getAxis)
        
        
def groupMirrorAndClose(*args):
    runGroupMirror()
    close()
    
    
def close(*args):
    cmds.deleteUI(myWin, window=True)
        


    
###########################################################
def goDocLink(*args):
    cmds.launch(web='https://docs.google.com/document/d/19BsWSH0c_mM2PvzfKd485EMTldCv5SkP7BA2OEEce4E/edit?usp=sharing')


#GUI
myWin = cmds.window(title="Group Mirror Tool", menuBar=True)
cmds.menu(label='Help')
cmds.menuItem(label='Design Doc', command=goDocLink)
cmds.columnLayout( adjustableColumn=True )
#cmds.radioButtonGrp( label='Along Axis: ', labelArray3=['X', 'Y', 'Z'],numberOfRadioButtons=3, vertical=True )
cmds.frameLayout( label='Mirror Along axis: ' )
cmds.radioCollection('axis')
cmds.radioButton('x', label='X', sl=True )
cmds.radioButton('y', label='Y' )
cmds.radioButton('z', label='Z' )


cmds.button(label='Apply and Close', command=groupMirrorAndClose)
cmds.button(label='Apply', command=runGroupMirror)
cmds.button(label='Close', command=close)
cmds.showWindow(myWin)

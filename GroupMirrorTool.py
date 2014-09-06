'''
Group Mirror Tool v1.0.0
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

TO-DO in v1.1.0
1. 'freeze' the new object
2. set the same hierarchy
3. rename system
4. change the GUI into a class


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
    

#magic
def mirrorObjAlong(obj, axis):
    mirObj = pm.duplicate(obj)[0]
    if axis == 'x':
        mirObj.translateX.set(-obj.translateX.get())
        mirObj.scaleX.set(-obj.scaleX.get())
    if axis == 'y':
        mirObj.translateY.set(-obj.translateY.get())
        mirObj.scaleY.set(-obj.scaleY.get())
    if axis == 'z':
        mirObj.translateZ.set(-obj.translateZ.get())
        mirObj.scaleZ.set(-obj.scaleZ.get())
        
        
        
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
    
    
    #iterate through the selected ones and make mirror
    for item in selection_list:
        mirrorObjAlong(item, getAxis)
        print "mirroring %s along axis %s"%(item, getAxis)
        
        
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
        

    


    
    
    
    
    
    
    
    
    
    
    
    
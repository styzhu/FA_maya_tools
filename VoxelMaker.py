import pymel.core as pm

class UI:
    def __init__(self):
        """UI for this tool"""
        winWidth = 400
        winHeight = 200
        winName = "voxel_maker_window"
        winTitle = "Voxel Maker"
        rightOffset = 10
        leftOffset = 10 
        topOffset = 2
        bottomOffset = 2
        
        if pm.window(winName, exists=True):
            pm.deleteUI(winName)
            
        mainWindow = pm.window(winName, title=winTitle, menuBar=True)
        
        # menu bar
        pm.menu(label='Edit')
        pm.menuItem(label='Save Settings')
        pm.menuItem(label='Reset Settings')
        pm.menu(label='Help')
        pm.menuItem(label='Design Doc', command=self.goDocLink)    
        
        # add layouts
        colLayout = pm.columnLayout(adj=True, parent=mainWindow)
        pm.radioCollection()
        
        # frame 1
        frameLayout_cube = pm.frameLayout(label='Cube Settings', borderStyle='etchedOut', parent=colLayout, mw=2)
        formLayout_cube = pm.formLayout(parent=frameLayout_cube)
        
        cvRButton = pm.radioButton(label='Cube Voxel', parent=formLayout_cube)
        #pm.addAttr(longName='bevel', attributeType='float')
        #testCtrlGrp = pm.attrControlGrp( attribute='defaultResolution.width' )
        
        formLayout_cube.attachForm(cvRButton, 'top', topOffset)
        formLayout_cube.attachForm(cvRButton, 'left', leftOffset)
        """
        formLayout_cube.attachControl(testCtrlGrp, 'top', topOffset, cvRButton)
        formLayout_cube.attachForm(testCtrlGrp, 'left', -100) # TODO
        """
        
        # frame 2
        frameLayout_custom = pm.frameLayout(label='Custom Voxel Settings', borderStyle='etchedOut', parent=colLayout)
        formLayout_custom = pm.formLayout(parent=frameLayout_custom)
        formLayout_custom_1 = pm.formLayout(parent=formLayout_custom)
        
        cusvRButton = pm.radioButton(label='Custom Voxel', parent=formLayout_custom)
        pm.radioCollection()
        importRButton = pm.radioButton(label='Import', parent=formLayout_custom_1)
        importField = pm.textFieldButtonGrp( label='Path', text='TODO', buttonLabel='Import',
                                             buttonCommand=self.getImportFilePath, parent=formLayout_custom_1 ) #TODO
        insceneRButton = pm.radioButton(label='In Scene', parent=formLayout_custom_1)
        
        formLayout_custom.attachForm(cusvRButton, 'top', topOffset)
        formLayout_custom.attachForm(cusvRButton, 'left', leftOffset)
        formLayout_custom.attachControl(formLayout_custom_1, 'top', topOffset, cusvRButton)
        formLayout_custom.attachForm(formLayout_custom_1, 'left', leftOffset)
        formLayout_custom_1.attachForm(importRButton, 'top', topOffset)
        formLayout_custom_1.attachForm(importRButton, 'left', leftOffset)
        formLayout_custom_1.attachControl(importField, 'top', topOffset, importRButton)
        formLayout_custom_1.attachForm(importField, 'left', leftOffset-100)
        formLayout_custom_1.attachControl(insceneRButton, 'top', topOffset, importField)
        formLayout_custom_1.attachForm(insceneRButton, 'left', leftOffset)    
        
        
        # frame 3
        frameLayout_density = pm.frameLayout(label='Density Settings', borderStyle='etchedOut', parent=colLayout)
        formLayout_density = pm.formLayout(parent=frameLayout_density)
        
        densityIntSlider = pm.intSliderGrp(field=True, label='Density', minValue=1, maxValue=20, fieldMinValue=1, fieldMaxValue=100, value=0, sliderStep=1)
    
        formLayout_density.attachForm(densityIntSlider, 'top', topOffset)
        formLayout_density.attachForm(densityIntSlider, 'left', leftOffset-100)
        
        # show window
        mainWindow.show()
        mainWindow.setWidthHeight((winWidth, winHeight))     
        
        
    def getImportFilePath(self, *args):
        filePath = pm.fileDialog2(fileMode = 1)
        if filePath == None:
            #pm.confirmDialog(title='!!!', button=['OK'], defaultButton='OK', m="Nothing imported")   
            return filePath
        else:
            return filePath
    
    
    def goDocLink(self, *args):
        """go to document/help"""
        pm.launch(web='https://docs.google.com/document/d/19BsWSH0c_mM2PvzfKd485EMTldCv5SkP7BA2OEEce4E/edit?usp=sharing')
    
    
myUI = UI()
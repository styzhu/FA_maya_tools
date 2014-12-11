import pymel.core as pm
import math as math
import maya.cmds as cmds

g_selectedMeshList = list(pm.selected())

""" math helpers """
def getLength(i_vector):
    x = i_vector[0]
    y = i_vector[1]
    z = i_vector[2]
    return math.sqrt(x*x + y*y + z*z)    

def normalize(i_vector):
    x = i_vector[0]
    y = i_vector[1]
    z = i_vector[2]
    length = getLength(i_vector)
    return (x/length, y/length, z/length)


def dotProduct(i_v1, i_v2):
    return (i_v1[0]*i_v2[0] + i_v1[1]*i_v2[1] + i_v1[2]*i_v2[2])


# get greates common divisor
def getGCD(i_numList):
    output = 0
    for i in range(len(i_numList)-1):
        if i == 0:
            output = getPairGCD(i_numList[i], i_numList[i+1])
        else:
            output = getPairGCD(output, i_numList[i+1])
        i += 1
    return output


def getPairGCD(a, b):
    tmp = max(a, b)
    b = min(a, b)
    a = tmp
    while b%a != 0:
        tmp = a - b
        if tmp > b:
            a = tmp
        else:
            a = b
            b = tmp
    return b
""" math helpers end """


""" helper function """
def NormalizeMesh(mesh):
    pm.makeIdentity(mesh, apply = True, translate=True, rotate=True)
    
    meshBBox = mesh.getBoundingBox()
    edgeList = []
    edgeList.append(meshBBox.height())
    edgeList.append(meshBBox.depth())
    edgeList.append(meshBBox.width())
    
    maxLength = 0.0
    
    for i in range(3):
        if edgeList[i] >= maxLength:
            maxLength = edgeList[i]
        else:
            continue
    
    if maxLength > 1:
        pm.scale(mesh, mesh.getScale()[0]/(maxLength), mesh.getScale()[1]/(maxLength), mesh.getScale()[2]/(maxLength))
    
    pm.makeIdentity(mesh, apply = True, translate=True, rotate=True, scale=True)





""" main function class """
class VoxelMaker:
    _voxelSize = 0
    _voxelsPosList = []
    _voxelsList = []
    _oriMdl = pm.nt.Transform()
    
    def __init__(self, i_step):
        self._oriMdl = pm.duplicate(g_selectedMeshList[0])[0]
        pm.makeIdentity(self._oriMdl, apply = True, scale = True, rotate=True)
        self._oriMdl.setMatrix((1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0))
        BBox = self._oriMdl.getBoundingBox() 
        self.buildVoxelList(i_step, BBox.max(), BBox.min())
        
        
    def __del__(self):
        pass
        #pm.delete(self._oriMdl)
        
        
    def getBBoxVol(self):
        BBox = self._oriMdl.getBoundingBox()
        return BBox.width()*BBox.height()*BBox.depth()
        
        
    def getSize(self, *args):
        return self._voxelSize
    
    
    def createShape(self, i_isGroup, i_mesh):
        distanceLimit = math.sqrt(self._voxelSize*self._voxelSize*3)
        for p in self._voxelsPosList:
            # print self._voxelsPosList
            r = self._oriMdl.getClosestPointAndNormal((p[0], p[1], p[2]))
            closestPoint = r[0] + self._oriMdl.getTranslation()
            
            # when the cube is far from the surface
            if distanceLimit < getLength((p[0]-closestPoint[0], 
                                          p[1]-closestPoint[1], 
                                          p[2]-closestPoint[2])):
                continue
            
            dp = dotProduct(normalize([p[0]-closestPoint[0], 
                                       p[1]-closestPoint[1], 
                                       p[2]-closestPoint[2]]), 
                            normalize(r[1]))
            
            # doc product > 0 means two vectors angle is from 0~90
            if dp < 0:
                # TODO
                # i_mesh: nt.Transform(u'pCube1'), nt.PolyCube(u'polyCube1')
                #print type(i_mesh)
                #print i_mesh
                #cube
                #if type(i_mesh) is 'list':
                    #mesh = pm.duplicate(i_mesh[0], name='Voxel1')
                #else:
                #custom
                    #mesh = pm.duplicate(i_mesh, name='Voxel1')
                mesh = pm.duplicate(i_mesh, name='Voxel1')
                pm.move(p[0], p[1], p[2], mesh, ws=True)
                self._voxelsList.append(mesh)
                # print "Create Voxel @ "+str(p[0])+","+str(p[1])+","+str(p[2])+" "+str(mesh)
                
        if i_isGroup ==True:
            if len(self._voxelsList)>1:
                pm.polyUnite(self._voxelsList, name='V1')
            pm.polyMergeVertex(distance=0.0)
            pm.delete(pm.polyInfo(laminaFaces=True))
            
        pm.delete(self._oriMdl)
        
        
    def getBound(self, i_num, i_isMax):
        if i_isMax:
            return math.ceil(i_num)
        else:
            return math.floor(i_num)         
     
        
    def buildVoxelList(self, i_step, i_maxPoint, i_minPoint):
        maxX = self.getBound(i_maxPoint[0], True)
        maxY = self.getBound(i_maxPoint[1], True)
        maxZ = self.getBound(i_maxPoint[2], True)
        minX = self.getBound(i_minPoint[0], False)
        minY = self.getBound(i_minPoint[1], False)
        minZ = self.getBound(i_minPoint[2], False) 
        
        self._voxelSize = getGCD([maxX-minX, maxY-minY, maxZ-minZ])/i_step
        numX = (int)((maxX-minX)/self._voxelSize)
        numY = (int)((maxY-minY)/self._voxelSize)
        numZ = (int)((maxZ-minZ)/self._voxelSize)
        
        for i in range(numX):
            for j in range(numY):
                for k in range(numZ):
                    self.addPoint(minX+i*self._voxelSize, minY+j*self._voxelSize, minZ+k*self._voxelSize)
        
        
        
    def addPoint(self, i_posX, i_posY, i_posZ):
        o_point = pm.dt.Point(i_posX+self._voxelSize/2, i_posY+self._voxelSize/2, i_posZ+self._voxelSize/2)
        self._voxelsPosList.append([i_posX+self._voxelSize/2, i_posY+self._voxelSize/2, i_posZ+self._voxelSize/2])        
        


""" GUI class """
class UI:
    _importFilePath = ''
    _mainWindow = None
    _customVoxelSelected = False
    _importSelected = False
    _seperated = False
    _density = 1

    #UI for this tool
    def __init__(self):
        winWidth = 400
        winHeight = 360
        winName = "voxel_maker_window"
        winTitle = "Voxel Maker"
        rightOffset = 10
        leftOffset = 10 
        topOffset = 2
        bottomOffset = 2
                
        if pm.window(winName, exists=True):
            pm.deleteUI(winName)
            
        self._mainWindow = pm.window(winName, title=winTitle, menuBar=True)
        
        # menu bar
        pm.menu(label='Edit')
        pm.menuItem(label='Save Settings')
        pm.menuItem(label='Reset Settings')
        pm.menu(label='Help')
        pm.menuItem(label='Design Doc', command=self.goDocLink)    
        
        # add layouts
        colLayout = pm.columnLayout(adj=True, parent=self._mainWindow)
        voxelType = pm.radioCollection('VoxelType')
        
        # frame 1
        frameLayout_cube = pm.frameLayout(label='Cube Settings', borderStyle='etchedOut', parent=colLayout, mw=2)
        formLayout_cube = pm.formLayout(parent=frameLayout_cube)
        
        cvRButton = pm.radioButton('default', label='Cube Voxel', parent=formLayout_cube, sl=not self._customVoxelSelected)
        #pm.addAttr(longName='bevel', attributeType='float')
        #testCtrlGrp = pm.attrControlGrp( attribute='defaultResolution.width' )
        
        formLayout_cube.attachForm(cvRButton, 'top', topOffset)
        formLayout_cube.attachForm(cvRButton, 'left', leftOffset)
        """
        formLayout_cube.attachControl(testCtrlGrp, 'top', topOffset, cvRButton)
        formLayout_cube.attachForm(testCtrlGrp, 'left', -100) # TODO
        """
        
        # frame 2
        frameLayout_custom = pm.frameLayout('custom', label='Custom Voxel Settings', borderStyle='etchedOut', parent=colLayout)
        formLayout_custom = pm.formLayout(parent=frameLayout_custom)
        formLayout_custom_1 = pm.formLayout(parent=formLayout_custom)
        
        cusvRButton = pm.radioButton('custom_voxel', label='Custom Voxel', parent=formLayout_custom,
                                     changeCommand=self.changeCustomVoxelSelected, sl = self._customVoxelSelected)
        pm.radioCollection()
        importRButton = pm.radioButton(label='Import', parent=formLayout_custom_1, enable=self._customVoxelSelected, sl=self._importSelected)
        importField = pm.textFieldButtonGrp( label='Path', text=self._importFilePath, buttonLabel='Find',
                                             buttonCommand=self.getImportFilePath, parent=formLayout_custom_1, 
                                             enable=self._customVoxelSelected ) #TODO
        insceneRButton = pm.radioButton(label='In Scene: Select the profile first, the sample object secondly', parent=formLayout_custom_1, enable=self._customVoxelSelected,
                                        changeCommand=self.changeImportSelected, sl=not self._importSelected)
        
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
        
        densityIntSlider = pm.intSliderGrp('density', field=True, label='Density', minValue=1, maxValue=20,
                                           fieldMinValue=1, fieldMaxValue=100, value=self._density, sliderStep=1, changeCommand=self.changeDensity)
    
        formLayout_density.attachForm(densityIntSlider, 'top', topOffset)
        formLayout_density.attachForm(densityIntSlider, 'left', leftOffset-100)

        # frame 4
        frameLayout_seperate = pm.frameLayout(label='Is Result Seperated', borderStyle='etchedOut', parent=colLayout)
        formLayout_seperate = pm.formLayout(parent=frameLayout_seperate)
        
        isSeperate = pm.radioCollection('IsSeperate')
        ySepRButton = pm.radioButton('Yes', label='Yes', parent=formLayout_seperate, changeCommand=self.changeSeperated, sl=self._seperated)
        nSepRButton = pm.radioButton('No', label='No', parent=formLayout_seperate, sl=not self._seperated)

        formLayout_seperate.attachForm(ySepRButton, 'top', topOffset)
        formLayout_seperate.attachForm(ySepRButton, 'left', leftOffset)
        formLayout_seperate.attachControl(nSepRButton, 'left', leftOffset, ySepRButton)
        formLayout_seperate.attachForm(nSepRButton, 'top', topOffset)
        
        # apply/close buttons
        acButton = pm.button(label='Apply and Close', command=pm.Callback(self.apply, voxelType, self._importFilePath, True), parent=colLayout)
        aButton = pm.button(label='Apply', command=pm.Callback(self.apply, voxelType, self._importFilePath, False), parent=colLayout)
        rButton = pm.button(label='Refresh', command=self.refresh, parent=colLayout)        
        cButton = pm.button(label='Close', command=self.close, parent=colLayout)
    
        
        # show window
        self._mainWindow.show()
        self._mainWindow.setWidthHeight((winWidth, winHeight))     
        
        
    def refresh(self, *args):
        g_selectedMeshList = list(pm.selected())
        self.__init__()
        
        
    def changeSeperated(self, *args):
        self._seperated = not self._seperated
        self.__init__()
        
        
    def changeDensity(self, *args):
        self._density = pm.intSliderGrp('density', q=True, value=True)
        
        
    def changeImportSelected(self, *args):
        self._importSelected = not self._importSelected
        self.__init__()    
        
        
    def changeCustomVoxelSelected(self, *args):
        self._customVoxelSelected = not self._customVoxelSelected
        self.__init__()
        
        
    def changeSelected(self, target):
        target = not target
        self.__init__()
        
    def selectCustomVoxel(self, i_isSelected):
        if i_isSelected == True:
            self._customVoxelSelected = True
        else:
            self._customVoxelSelected = False
        self.__init__()
            
        
    def getImportFilePath(self, *args):
        filePath = pm.fileDialog2(fileMode = 1)
        if filePath == None:
            #pm.confirmDialog(title='!!!', button=['OK'], defaultButton='OK', m="Nothing imported")   
            self._importFilePath = filePath[0]
        else:
            self._importFilePath = filePath[0]
        
        self.__init__()
    
    
    def goDocLink(self, *args):
        """go to document/help"""
        pm.launch(web='https://docs.google.com/document/d/1rGMKBQ3gdmisncroBUUkPibmySuQh--DR_MUgqCfOlY/edit?usp=sharing')
    
    
    def apply(self, i_voxelType, i_meshPath, i_isClose, *args):
        i_step = self._density
        vm = VoxelMaker(i_step)
        voxelSize = vm.getSize()
        # this is aimed to calculate the time will be costed
        detailLvl = vm.getBBoxVol()/(voxelSize**3)
        print "Voxel Size: "+str(voxelSize)+" Current Detail Level: "+str(detailLvl)
        
        if detailLvl > 10000:
            warnWin = pm.confirmDialog(title='Warning', message='It may take a while, save your file first!',
                                        button=['Continue', 'Stop'], defaultButton='Stop', cancelButton='Continue')
            if warnWin == 'Stop':
                return
        if detailLvl > 30000:
            warnWin = pm.confirmDialog(title='Warning', message='Danger ahead, Maya will not response for a long time!',
                                        button=['Continue', 'Stop'], defaultButton='Stop', cancelButton='Continue')
            if warnWin == 'Stop':
                return
        if detailLvl > 50000:
            warnWin = pm.confirmDialog(title='Warning', message='Death ahead, praise the sun!',
                                        button=['Continue', 'Stop'], defaultButton='Stop', cancelButton='Continue')
            if warnWin == 'Stop':
                return        
        
        if i_voxelType.getSelect() == 'custom_voxel':
            if self._importSelected:
                print pm.importFile(i_meshPath, returnNewNodes=True)
                transform = pm.importFile(i_meshPath, returnNewNodes=True)[-2]
                NormalizeMesh(transform)
            else:
                transform = g_selectedMeshList[1]
                NormalizeMesh(transform)
        else:
            transform = pm.polyCube(w=voxelSize, h=voxelSize, d=voxelSize)
        if self._seperated == True:
            vm.createShape(False, transform)
        else:
            vm.createShape(True, transform)
        
        pm.delete(transform)
        
        if i_isClose == True:
            self.close()
        else:
            self.__init__()
    
    
    def close(self, *args):
        pm.deleteUI(self._mainWindow, window=True)
    
    
def run():
    if len(g_selectedMeshList) == 0:
        pm.confirmDialog(title='Error', button=['OK'], defaultButton='OK', 
                         m="Please select the original model!")
        return
    if len(g_selectedMeshList) > 2:
        pm.confirmDialog(title='Error', button=['OK'], defaultButton='OK', 
                         m="more than 2 objects are selected: "+str(g_selectedMeshList))
        return        
    myUI = UI()
    
    
run()
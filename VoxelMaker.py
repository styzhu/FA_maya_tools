import pymel.core as pm
import math as math
import maya.cmds as cmds


"""math helpers"""
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
"""math helpers end"""


"""main function class"""
class VoxelMaker:
    _voxelSize = 0
    _voxelsPosList = []
    _voxelsList = []
    _oriMdl = pm.nt.Transform()
    
    def __init__(self, i_step):
        print "XXXXX"+str(type(self._oriMdl))
        self._oriMdl = pm.duplicate(pm.selected()[0])[0]
        pm.makeIdentity(apply = True, scale = True)
        self._oriMdl.setMatrix((1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0))
        BBox = self._oriMdl.getBoundingBox()  
        self.buildVoxelList(i_step, BBox.max(), BBox.min())
        
        
    def getSize(self, *args):
        return self._voxelSize
    
    
    def createShape(self, i_isGroup, i_mesh):
        distanceLimit = math.sqrt(self._voxelSize*self._voxelSize*3)
        for p in self._voxelsPosList:
            print self._voxelsPosList
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
                mesh = pm.duplicate(i_mesh, name='Voxel1')
                pm.move(p[0], p[1], p[2], mesh, ws=True)
                self._voxelsList.append(mesh)
                print "Create Voxel @ "+str(p[0])+","+str(p[1])+","+str(p[2])+" "+str(mesh)
                
        if i_isGroup ==True:
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
        


"""GUI class"""
class UI:
    _importFilePath = ''
    _mainWindow = None

    #UI for this tool
    def __init__(self):
        winWidth = 400
        winHeight = 300
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
        pm.radioCollection('VoxelType')
        voxelType = pm.radioCollection("VoxelType", q=True, sl=True)
        
        # frame 1
        frameLayout_cube = pm.frameLayout(label='Cube Settings', borderStyle='etchedOut', parent=colLayout, mw=2)
        formLayout_cube = pm.formLayout(parent=frameLayout_cube)
        
        cvRButton = pm.radioButton('default', label='Cube Voxel', parent=formLayout_cube, sl=True)
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
        
        cusvRButton = pm.radioButton(label='Custom Voxel', parent=formLayout_custom)
        pm.radioCollection()
        importRButton = pm.radioButton(label='Import', parent=formLayout_custom_1)
        importField = pm.textFieldButtonGrp( label='Path', text=self._importFilePath, buttonLabel='Set',
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
        
        densityIntSlider = pm.intSliderGrp('density', field=True, label='Density', minValue=1, maxValue=20, fieldMinValue=1, fieldMaxValue=100, value=0, sliderStep=1)
        o_step = pm.intSliderGrp('density', q=True, value=True)
    
        formLayout_density.attachForm(densityIntSlider, 'top', topOffset)
        formLayout_density.attachForm(densityIntSlider, 'left', leftOffset-100)
        
        # apply/close buttons
        
        acButton = pm.button(label='Apply and Close', command=pm.Callback(self.apply, voxelType, o_step, self._importFilePath, False), parent=colLayout)
        aButton = pm.button(label='Apply', command=self.goDocLink, parent=colLayout)
        cButton = pm.button(label='Close', command=self.close, parent=colLayout)
    
        
        # show window
        self._mainWindow.show()
        self._mainWindow.setWidthHeight((winWidth, winHeight))     
        
        
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
        pm.launch(web='https://docs.google.com/document/d/19BsWSH0c_mM2PvzfKd485EMTldCv5SkP7BA2OEEce4E/edit?usp=sharing')
    
    
    def apply(self, i_voxelType, i_step, i_meshPath, i_isClose, *args):
        vm = VoxelMaker(i_step)
        voxelSize = vm.getSize()
        if i_voxelType == 'custom':
            mesh = pm.importFile(input, returnNewNodes=True)[-1]
        else:
            mesh = pm.polyCube(w=voxelSize, h=voxelSize, d=voxelSize)
        #vm.createShape(i_isGroup, mesh)
        vm.createShape(True, mesh)
        
        pm.delete(mesh)
        
        if i_isClose == True:
            self.close()
    
    
    def close(self, *args):
        pm.deleteUI(self._mainWindow, window=True)    
    
    
    
def run():
    myUI = UI()
    
    
run()
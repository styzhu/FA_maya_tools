import pymel.core as pm


hiddenFaces = []
for j in range(len(pm.selected())):
    for i in pm.selected()[j]:
        if i.getArea() < 1.0e-4:
            hiddenFaces.append(i)
print hiddenFaces
    
result = pm.confirmDialog(title='!!!', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No', m="hidden faces number: {0} Kill them?".format(len(hiddenFaces)))
#pm.select(hiddenFaces)
#pm.delete(hiddenFaces)

if result == 'Yes':
    for face in hiddenFaces:
        pm.select(face)
        pm.polyListComponentConversion(fromFace = True, toVertex = True)
        pm.polyMergeVertex( distance=0.0 )
else:
    pm.select(hiddenFaces)
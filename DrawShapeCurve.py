""" 
DrawSahpeCurve
version 1.0
1/7/2015

* Draw some curve at the location of the edges of the selected object

author: Sty Zhu <zhu@junyuan.me>
"""

import pymel.core as pm


curveList = []
edgeList = pm.ls(pm.selected()[0].e, flatten=True)

myGroup = pm.group( empty=True, name='ShapeCurve1' )
        
for edge in edgeList:
    pm.select(edge)
    vertexList = pm.polyListComponentConversion(fromEdge = True, toVertex = True)
    vertexList = pm.ls( vertexList, flatten=True )
    vertexPosList = []
    for vertex in vertexList:
        vertexPosList.append(pm.xform(vertex, query=True, translation=True))
    c = pm.curve( d=1, p=vertexPosList )
    curveList.append(c)
    
tempCurve = pm.listRelatives(curveList)
pm.parent(tempCurve, myGroup, shape=True, addObject=True)
pm.delete(curveList)

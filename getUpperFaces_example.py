# Fusion360API Python script  by kantoku
# getUpperFaces_example

import adsk.core, adsk.fusion, traceback

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # select SolidBody
        msg :str = 'select SolidBody'
        selFiltter :str = 'SolidBodies'
        sel :adsk.core.Selection = selectEnt(msg ,selFiltter)
        if not sel: return
        body :adsk.fusion.BRepBody = sel.entity

        # select upper vector entity
        msg = 'Choose a flat surface to face up or a flat surface!'
        selFiltter :str = 'ConstructionPlanes,PlanarFaces'
        sel :adsk.core.Selection = selectEnt(msg ,selFiltter)
        if not sel: return
        upVec :adsk.core.Vector3D = sel.entity.geometry.normal
        upVec.normalize()

        # get upper faces
        uprFaces = getUpperFaces(body, upVec, True)

        # select faces
        sels = _ui.activeSelections
        sels.clear()
        for f in uprFaces:
            sels.add(f)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def selectEnt(
    msg :str, 
    filtterStr :str) -> adsk.core.Selection :

    try:
        sel = _ui.selectEntity(msg, filtterStr)
        return sel
    except:
        return None


# return list(BRepFace)
def getUpperFaces(
    body :adsk.fusion.BRepBody,
    upVec :adsk.core.Vector3D,
    flat_only :bool = True) -> list:

    try:
        # get matrix
        vec3D = adsk.core.Vector3D
        vecZ = vec3D.create(0,0,1)

        mat = adsk.core.Matrix3D.create()
        mat.setToRotateTo(upVec, vecZ)

        # get faces
        planeSurface = adsk.core.SurfaceTypes.PlaneSurfaceType
        if flat_only:
            faces = [f for f in body.faces if f.geometry.surfaceType == planeSurface]
        else:
            faces = [f for f in body.faces]

        tmpMgr = adsk.fusion.TemporaryBRepManager.get()
        facesMap = []
        for f in faces:
            # clone
            cloneBody :adsk.fusion.BRepBody = tmpMgr.copy(f)

            # transform
            tmpMgr.transform(cloneBody, mat)
            clone :adsk.fusion.BRepFace = cloneBody.faces[0]

            # check the normal
            if flat_only:
                normal :adsk.core.Vector3D = clone.geometry.normal
                if not vecZ.isParallelTo(normal):
                    continue

            facesMap.append((f, clone.boundingBox.maxPoint.z))

        # sort
        facesMap = sorted(facesMap, key=lambda x:x[1])
        facesMap.reverse()
        
        # get upper faces
        from itertools import groupby
        lst = [list(v) for k,v in groupby(facesMap, key=lambda x:x[1])]

        if len(lst):
            return [f for (f,z) in lst[0]]
        else:
            return []

    except:
        return []
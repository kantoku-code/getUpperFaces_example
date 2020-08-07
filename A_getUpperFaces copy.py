# Fusion360API Python script  by kantoku
# getUpperFaces_example

import adsk.core, adsk.fusion, traceback
app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)

def run(context):
    try:
        ### -- SETTING UP: 
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        # ensuring that there is model built & active:
        if not design:
            ui.messageBox('No active Fusion design', 'No Design')
            return
        # Get the root component of the active design:
        rootComp = design.rootComponent
        bodies = rootComp.bRepBodies
        ### --
        
        faces = []
        flat_only = True
        planeSurface = adsk.core.SurfaceTypes.PlaneSurfaceType
        for body in bodies: 
            if flat_only:             
                for f in body.faces: 
                    if f.geometry.surfaceType == planeSurface:
                        faces.append(f) 
            else: 
                for f in body.faces: 
                    faces.append(f)

        vectors_only = []
        faces_only = []

        for face in faces: 
            vec = face.geometry.normal
            vectors_only.append(vec)
        
        # Get center of mass from physical properties
        pp = rootComp.physicalProperties
        center_rootComp = pp.centerOfMass
        # --
        seen = []

        for vector_i in range(len(vectors_only)): 
            for vector_j in range(len(vectors_only)):

                if (not [vectors_only[vector_i], vectors_only[vector_j]] in seen) and (not [vectors_only[vector_j], vectors_only[vector_i]] in seen): 

                    if vectors_only[vector_i].isEqualTo(vectors_only[vector_j]):

                        found_faces_intersecting = rootComp.findBRepUsingRay(center_rootComp, vectors_only[vector_i], 1)
                        needed_face = found_faces_intersecting.item(found_faces_intersecting.count-1)
                        if needed_face not in faces_only: 
                            faces_only.append(needed_face)    

                    seen.append([vectors_only[vector_i], vectors_only[vector_j]])

            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



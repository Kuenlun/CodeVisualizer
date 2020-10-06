from extract_funcls import extract_funcls
#from manimlib.imports import *

funcls = extract_funcls('pruebas/caquitadelavaquita.py')
for kk in funcls:
    print(kk)

#class FlowDiagram(Scene):
#    def construct(self):
#        pass

#tipo:
#    creación de función     método      tipo    nombre  padre   profundidad
#    utilización de función              tipo    nombre  padre   profundidad
#    creación de clase       herencia    tipo    nombre  padre   profundidad
#    utilización de clase                tipo    nombre  padre   profundidad

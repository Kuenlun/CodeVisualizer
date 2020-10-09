from manimlib.imports import *
from CodeVisualizer import *
from extract_funcls import extract_funcls

# Constants
MANIM_WIDTH    = FRAME_WIDTH                                # [manim_u]
MANIM_HEIGHT   = PAPER_HEIGHT * MANIM_WIDTH / PAPER_WIDTH   # [manim_u]
PAPER_MM       = MANIM_WIDTH / PAPER_WIDTH                  # [manim_u / mm]

MANIM_TOP_MARGIN    = PAPER_TOP_MARGIN    * PAPER_MM    # [manim_u]
MANIM_BOTTOM_MARGIN = PAPER_BOTTOM_MARGIN * PAPER_MM    # [manim_u]
MANIM_RIGHT_MARGIN  = PAPER_RIGHT_MARGIN  * PAPER_MM    # [manim_u]
MANIM_LEFT_MARGIN   = PAPER_LEFT_MARGIN   * PAPER_MM    # [manim_u]


def create_label(element):
    # Obtener nombre
    label = element['name']
    if element['type'] == 'def_c':
        # Obtener texto método
        if 'method_of' in element.keys():
            label += '\tMétodo de: ' + element['method_of']
    elif element['type'] == 'cls_c':
        # Obtener texto herencia
        if 'inheritance' in element.keys():
            label += '\tHereda de: ' + element['inheritance']
    # Cambiamos carácteres especiales como la barrabaja y la tabulación
    label = label.replace('_','\\_')
    label = label.replace('\t','\\qquad ')
    # Creamos el texto en LaTex
    return TextMobject(label)

def create_diagram_recursive(element, final_vectors):
    print(element)
    if element['type'] in ('def', 'cls'):
        # Lo añadimos a final_vectors junto con el padre
        final_vectors.append((element['parent'], create_label(element)))
    else:
        # Creamos un grupo de vectores donde meteremos todo
        element_VGroup = VGroup()
        # Creamos el label
        if element['name'] != 'main':
            element_VGroup.add(create_label(element))
            # Creamos más cosas para que quede bonito
            pass
        # Vemos si alguno de los final vectors es hijo de este elemento
        aux_sons = list()
        for j in reversed(range(len(final_vectors))):
            if final_vectors[j][0] == element['name']:
                # Lo guardamos en un auxiliar
                aux_sons.append(final_vectors[j][1])
                # Lo eliminamos del original
                del(final_vectors[j])
        aux_sons.reverse()

        for son in aux_sons:
            if len(element_VGroup):
                son.next_to(element_VGroup[-1], DOWN)
            element_VGroup.add(son)
        # Creamos el rectángulo
        if element['name'] != 'main':
            rect_width = element_VGroup.get_width() + 10 * PAPER_MM
            rect_height = element_VGroup.get_height() + 10 * PAPER_MM
            if element['type'] == 'def_c':
                rectangle = Rectangle(width=rect_width, height=rect_height)
            elif element['type'] == 'cls_c':
                rectangle = RoundedRectangle(width=rect_width,
                               height=rect_height, corner_radius=5 * PAPER_MM)
            rectangle.set_fill(DARK_GREY, 1)
            rectangle.move_to(element_VGroup.get_center())
            # Añadimos el grupo de vectores a la lista, junto con el padre
            final_vectors.append((element['parent'],
                                  VGroup(rectangle, element_VGroup)))
        else:
            final_vectors.append((None, VGroup(element_VGroup)))

def create_diagram(file, omit_dunder=False):
    # Obtenemos las funciones y clases de un archivo
    funcls = extract_funcls(file, omit_dunder)

    done_idx = set()        # Índice de elementos ya hechos
    final_vectors = list()  # Elementos terminados

    # Buscamos la mayor profundidad
    max_depth = -1
    for i, element in enumerate(funcls):
        if i not in done_idx and element['type'] not in ('def', 'cls'):
            if element['depth'] > max_depth:
                max_depth = element['depth']

    while True:
        # Buscamos de más profundidad a menos
        same_depth = list()
        for i, element in enumerate(funcls):
            if i not in done_idx:
                if element['depth'] == max_depth:
                    same_depth.append(element)
        #
        for element in same_depth:
            create_diagram_recursive(element, final_vectors)
        max_depth -= 1
        if max_depth == -1:
            # Finally create main
            main = {'type': 'main', 'name' : 'main'}
            create_diagram_recursive(main, final_vectors)
            break

    diagram = final_vectors[0][1]
    # Vertical
    v_spacing = MANIM_TOP_MARGIN + MANIM_BOTTOM_MARGIN
    v_factor = (MANIM_HEIGHT - v_spacing) / diagram.get_height()
    # Horizontal
    h_spacing = MANIM_RIGHT_MARGIN + MANIM_LEFT_MARGIN
    h_factor = (MANIM_WIDTH - h_spacing) / diagram.get_width()
    # Elegimos que factor aplicar
    if v_factor <= h_factor:
        diagram.scale(v_factor)
    else:
        diagram.scale(h_factor)
    # Centramos el diagrama
    v_offset = (MANIM_TOP_MARGIN - MANIM_BOTTOM_MARGIN) / 2
    h_offset = (MANIM_RIGHT_MARGIN - MANIM_LEFT_MARGIN) / 2
    diagram.move_to(v_offset * DOWN + h_offset * LEFT)
    return diagram


class FlowDiagram(Scene):
    def construct(self):
        diagram = create_diagram(file, omit_dunder=omit_dunder)
        self.play(
            Write(diagram)
        )

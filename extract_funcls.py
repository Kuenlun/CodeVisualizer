import tokenize
from token import *

DUNDER_SET = {  '__abs__',
                '__add__',
                '__aenter__',
                '__aexit__',
                '__aiter__',
                '__and__',
                '__anext__',
                '__await__',
                '__bool__',
                '__bytes__',
                '__call__',
                '__class__',
                '__cmp__',
                '__complex__',
                '__contains__',
                '__delattr__',
                '__delete__',
                '__delitem__',
                '__delslice__',
                '__dir__',
                '__div__',
                '__divmod__',
                '__enter__',
                '__eq__',
                '__exit__',
                '__float__',
                '__floordiv__',
                '__format__',
                '__fspath__',
                '__ge__',
                '__get__',
                '__getattribute__',
                '__getitem__',
                '__getnewargs__',
                '__getslice__',
                '__gt__',
                '__hash__',
                '__iadd__',
                '__iand__',
                '__import__',
                '__imul__',
                '__index__',
                '__init__',
                '__init_subclass__',
                '__instancecheck__',
                '__int__',
                '__invert__',
                '__ior__',
                '__isub__',
                '__iter__',
                '__ixor__',
                '__le__',
                '__len__',
                '__lshift__',
                '__lt__',
                '__mod__',
                '__mul__',
                '__ne__',
                '__neg__',
                '__new__',
                '__next__',
                '__nonzero__',
                '__or__',
                '__pos__',
                '__pow__',
                '__prepare__',
                '__radd__',
                '__rand__',
                '__rdiv__',
                '__rdivmod__',
                '__reduce__',
                '__reduce_ex__',
                '__repr__',
                '__reversed__',
                '__rfloordiv__',
                '__rlshift__',
                '__rmod__',
                '__rmul__',
                '__ror__',
                '__round__',
                '__rpow__',
                '__rrshift__',
                '__rshift__',
                '__rsub__',
                '__rtruediv__',
                '__rxor__',
                '__set__',
                '__setattr__',
                '__setitem__',
                '__setslice__',
                '__sizeof__',
                '__str__',
                '__sub__',
                '__subclasscheck__',
                '__subclasses__',
                '__truediv__',
                '__xor__'}


def functions_tuple(lookup):
    return tuple(x['name'] for x in lookup if x['type'] == 'def_c')

def classes_tuple(lookup):
    return tuple(x['name'] for x in lookup if x['type'] == 'cls_c')

def funcls_tuple(lookup):
    return functions_tuple(lookup) + classes_tuple(lookup)

def find_next_name(token_tuple, i, end = -1):
    for i in range(i, len(token_tuple)):
        if end != -1:
            if i >= end:
                break
        if token_tuple[i].type == NAME:
            return token_tuple[i].string
    return None

def obtain_parentheses(token_tuple, i, end = -1):
    cont = 0
    for i in range(i, len(token_tuple)):
        if end != -1:
            if i >= end:
                break
        if token_tuple[i].type == OP:
            if token_tuple[i].string == '(':
                cont += 1
            elif token_tuple[i].string == ')':
                cont -= 1
        if cont == 0:
            break
    return i

def obtain_used_funcls(token_tuple, lookup, i, end = -1):
    out = list()
    for i in range(i, len(token_tuple)):
        if end != -1:
            if i >= end:
                break
        if token_tuple[i].type == NAME:
            if token_tuple[i].string in funcls_tuple(lookup):
                out.append(token_tuple[i].string)
    return out

def obtain_function(token_tuple, lookup, depth, start, end = -1):
    used_funcls = list()
    flag = 0
    for i in range(start, len(token_tuple)):
        if end != -1:
            if i >= end:
                break
        if flag == 0:
            if token_tuple[i].type == NAME and token_tuple[i].string != 'def':
                name = token_tuple[i].string
                flag = 1
        elif flag == 1:
            if token_tuple[i].type == OP and token_tuple[i].string == '(':
                parentheses_end = obtain_parentheses(token_tuple, i)
                used_funcls = obtain_used_funcls(token_tuple, lookup, i,
                                                 parentheses_end)
                flag = 2
        elif flag == 2:
            if token_tuple[i].type == OP and token_tuple[i].string == ':':
                break
    dictionary = {'type' : 'def_c', 'name' : name, 'depth' : depth,
                 'start_token' : start, 'end_token' : i}
    return dictionary, used_funcls


def obtain_class(token_tuple, lookup, depth, start, end = -1):
    used_funcls = list()
    inheritance = None
    flag = 0
    for i in range(start, len(token_tuple)):
        if end != -1:
            if i >= end:
                break
        if flag == 0:
            if token_tuple[i].type == NAME and token_tuple[i].string != 'class':
                name = token_tuple[i].string
                flag = 1
        elif flag == 1:
            if token_tuple[i].type == OP and token_tuple[i].string == '(':
                parentheses_end = obtain_parentheses(token_tuple, i)
                used_funcls = obtain_used_funcls(token_tuple, lookup, i,
                                                 parentheses_end)
                inheritance = find_next_name(token_tuple, i, parentheses_end)
                if inheritance in used_funcls:
                    used_funcls.remove(inheritance)
                flag = 2
            elif token_tuple[i].type == OP and token_tuple[i].string == ':':
                break
        elif flag == 2:
            if token_tuple[i].type == OP and token_tuple[i].string == ':':
                break
    dictionary = {'type' : 'cls_c', 'name' : name,
                  'inheritance' : inheritance, 'depth' : depth,
                  'start_token' : start, 'end_token' : i}
    return dictionary, used_funcls

def generate_dict(lookup, name, depth):
    for dictionary in lookup:
        if name == dictionary['name']:
            if dictionary['type'] == 'def_c':
                new_type = 'def'
            elif dictionary['type'] == 'cls_c':
                new_type = 'cls'
            else:
                continue
            dct = {'type' : new_type, 'name' : name, 'depth' : depth}
            lookup.append(dct)
            return

def convert_lookup(lookup):
    out = list()
    for i, dct in enumerate(lookup):
        dct_aux = {}
        dct_aux['n'] = i
        dct_aux['type'] = dct['type']
        dct_aux['name'] = dct['name']
        dct_aux['parent'] = dct['depth'][0]
        # Herencia
        if 'inheritance' in dct.keys():
            if dct['inheritance'] is not None:
                dct_aux['inheritance'] = dct['inheritance']
        # Es método
        if 'method_of' in dct.keys():
            dct_aux['method_of'] = dct['method_of']

        if dct['depth'][1] == -1:
            dct_aux['depth'] = 0
        else:
            for j in reversed(range(i)):
                if dct['depth'][0] == out[j]['name']:
                    dct_aux['depth'] = out[j]['depth'] + 1
                    break
        out.append(dct_aux)
    return out

####################
#####  PARSER  #####
####################
def extract_funcls(file, omit_dunder=False):
    lookup = list()
    with tokenize.open(file) as f:
        tokens = tokenize.generate_tokens(f.readline)
        token_tuple = tuple(token for token in tokens)

    depth = [('main', -1)]
    flag_cont_crea = 0
    flag_cont_aux = 0
    flag_cont_aux2 = 0
    cont = 0
    i = 0
    while True:
        if i >= len(token_tuple):
            break
        token = token_tuple[i]

        if flag_cont_aux == 1:
            if token.type != COMMENT and token.type != NEWLINE:
                flag_cont_aux2 = 1
            flag_cont_aux = 0

        if flag_cont_aux2 == 1:
            if token.type == NEWLINE or (token.type == OP and token.string == ';'):
                cont -= 1
                if depth[-1][1] >= cont:
                    del(depth[-1])
                flag_cont_aux2 = 0

        # Identation counter
        if token.type == INDENT:
            if flag_cont_crea == 0:
                cont += 1
            elif flag_cont_crea == 1:
                flag_cont_crea = 0
        elif token.type == DEDENT:
            cont -= 1
            if depth[-1][1] >= cont:
                del(depth[-1])

            if flag_cont_aux == 1:
                pass
        # Function and class finder
        elif token.type == NAME:
            if token.string == 'def':
                dictionary, prev = obtain_function(token_tuple, lookup, depth[-1], i)
                for name in prev:
                    generate_dict(lookup, name, depth[-1])
                # Comprobar si es método
                for _dict in lookup:
                    if depth[-1][0] == _dict['name']:
                        if _dict['type'] == 'cls_c':
                            dictionary['method_of'] = _dict['name']
                lookup.append(dictionary)
                i = dictionary['end_token']
                depth.append((dictionary['name'], cont))
                cont += 1
                flag_cont_crea = 1
                flag_cont_aux = 1
            elif token.string == 'class':
                dictionary, prev = obtain_class(token_tuple, lookup, depth[-1], i)
                for name in prev:
                    generate_dict(lookup, name, depth[-1])
                lookup.append(dictionary)
                i = dictionary['end_token']
                depth.append((dictionary['name'], cont))
                cont += 1
                flag_cont_crea = 1
                flag_cont_aux = 1
            elif token.string in funcls_tuple(lookup):
                generate_dict(lookup, token.string, depth[-1])
        i += 1
    out = convert_lookup(lookup)
    if omit_dunder:
        idx_set = set()
        for i, dct in enumerate(out):
            if dct['name'] in DUNDER_SET:
                idx_set.add(i)
        out = tuple(x for i, x in enumerate(out) if i not in idx_set)
    else:
        out = tuple(out)
    return out

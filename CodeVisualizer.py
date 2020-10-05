import tokenize
from token import *

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

def generate_dict(lookup, name, inside):
    for dictionary in lookup:
        if name == dictionary['name']:
            if dictionary['type'] == 'def_c':
                new_type = 'def'
            elif dictionary['type'] == 'cls_c':
                new_type = 'clc'
            else:
                continue
            dct = {'type' : new_type, 'name' : name, 'inside' : inside}
            lookup.append(dct)
            return


##################
#####  MAIN  #####
##################
lookup = list()
with tokenize.open('caquitadelavaquita.py') as f:
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

for _ in lookup:
    print(_)

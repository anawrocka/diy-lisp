# -*- coding: utf-8 -*-

from types import Environment, LispError, Closure
from ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer
from asserts import assert_exp_length, assert_valid_definition, assert_boolean
from parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""

def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_boolean(ast) or is_integer(ast):
        return ast
    if is_symbol(ast):
        return env.lookup(ast)
    if is_list(ast):
        if ast[0] == "quote":
            return ast[1]
        if ast[0] == "atom":
            atom_part = evaluate(ast[1], env)
            if is_list(atom_part):
                return False
            else: return True
        if ast[0] == "eq":
            ast1 = evaluate(ast[1], env)
            ast2 = evaluate(ast[2], env)
            if ast1 == ast2 and is_atom(ast1) and is_atom(ast2):
                return True
            else: return False
        if ast[0] in ['+', '-', '/', '*', 'mod', '>', '<']:
            op = ast[0]
            ast1 = evaluate(ast[1], env)
            ast2 = evaluate(ast[2], env)
            if is_integer(ast1) and is_integer(ast2):
                return evaluate_math(op, ast1, ast2)
            else: raise LispError
        if ast[0] == 'if':
            if evaluate(ast[1], env) == True:
                return evaluate(ast[2], env)
            else: return evaluate(ast[3], env)
        if ast[0] == 'define':
            if len(ast) == 3:
                if is_symbol(ast[1]) and not is_boolean(ast[1]):
                    return env.set(ast[1], evaluate(ast[2], env))
                else: raise LispError ("non-symbol")
            else: raise LispError("Wrong number of arguments")
        if ast[0] == 'lambda':
            return Closure(env, ast[1], ast[2])
            
def evaluate_math(op, arg1, arg2):
    if op == '+':
        return arg1 + arg2
    if op == '-':
        return arg1 - arg2
    if op == '*':
        return arg1 * arg2
    if op == '/':
        return arg1 / arg2
    if op == 'mod':
        return arg1 % arg2
    if op == '>':
        return arg1 > arg2
    if op == '<':
        return arg1 < arg2

        
        
            

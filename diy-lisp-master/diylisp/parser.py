# -*- coding: utf-8 -*-

import re
from nose.tools import assert_equals, assert_raises_regexp

def is_symbol(x):
    return isinstance(x, str)

def is_list(x):
    return isinstance(x, list)

def is_boolean(x):
    return isinstance(x, bool)

def is_integer(x):
    return isinstance(x, int)

def is_closure(x):
    return isinstance(x, Closure)

def is_atom(x):
    return is_symbol(x) \
        or is_integer(x) \
        or is_boolean(x) \
        or is_closure(x)


class LispError(Exception): 
    """General lisp error class."""
    pass

class Closure:
    
    def __init__(self, env, params, body):
        raise NotImplementedError("DIY")

    def __str__(self):
        return "<closure/%d>" % len(self.params)

class Environment:

    def __init__(self, variables=None):
        self.variables = variables if variables else {}

    def lookup(self, symbol):
        raise NotImplementedError("DIY")

    def extend(self, variables):
        raise NotImplementedError("DIY")

    def set(self, symbol, value):
        raise NotImplementedError("DIY")



"""
This is the parser module, with the `parse` function which you'll implement as part 1 of
the workshop. Its job is to convert strings into data structures that the evaluator can 
understand. 
"""


        
##
## Below are a few useful utility functions. These should come in handy when 
## implementing `parse`. We don't want to spend the day implementing parenthesis 
## counting, after all.
## 

def remove_comments(source):
    """Remove from a string anything in between a ; and a linebreak"""
    return re.sub(r";.*\n", "\n", source)

def find_matching_paren(source, start=0):
    """Given a string and the index of an opening parenthesis, determines 
    the index of the matching closing paren."""

    assert source[start] == '('
    pos = start
    open_brackets = 1
    while open_brackets > 0:
        pos += 1
        if len(source) == pos:
            raise LispError("Incomplete expression: %s" % source[start:])
        if source[pos] == '(':
            open_brackets += 1
        if source[pos] == ')':
            open_brackets -= 1
    return pos

def split_exps(source):
    """Splits a source string into subexpressions 
    that can be parsed individually.

    Example: 

        > split_exps("foo bar (baz 123)")
        ["foo", "bar", "(baz 123)"]
    """

    rest = source.strip()
    exps = []
    while rest:
        exp, rest = first_expression(rest)
        exps.append(exp)
    return exps

def first_expression(source):
    """Split string into (exp, rest) where exp is the 
    first expression in the string and rest is the 
    rest of the string after this expression."""
    
    source = source.strip()
    if source[0] == "'":
        exp, rest = first_expression(source[1:])
        return source[0] + exp, rest
    elif source[0] == "(":
        last = find_matching_paren(source)
        return source[:last + 1], source[last + 1:]
    else:
        match = re.match(r"^[^\s)']+", source)
        end = match.end()
        atom = source[:end]
        return atom, source[end:]

##
## The functions below, `parse_multiple` and `unparse` are implemented in order for
## the REPL to work. Don't worry about them when implementing the language.
##

def parse_multiple(source):
    """Creates a list of ASTs from program source constituting multiple expressions.

    Example:

        >>> parse_multiple("(foo bar) (baz 1 2 3)")
        [['foo', 'bar'], ['baz', 1, 2, 3]]

    """

    source = remove_comments(source)
    return [parse(exp) for exp in split_exps(source)]

def unparse(ast):
    """Turns an AST back into lisp program source"""

    if is_boolean(ast):
        return "#t" if ast else "#f"
    elif is_list(ast):
        if len(ast) > 0 and ast[0] == "quote":
            return "'%s" % unparse(ast[1])
        else:
            return "(%s)" % " ".join([unparse(x) for x in ast])
    else:
        # integers or symbols (or lambdas)
        return str(ast)



def test_parse_single_symbol():
    """Parsing a single symbol.

    Symbols are represented by text strings. Parsing a single atom should result
    in an AST consisting of only that symbol."""

    assert_equals('foo', parse('foo'))

def test_parse_boolean():
    """Parsing single booleans.

    Booleans are the special symbols #t and #f. In the ASTs they are represented 
    by Pythons True and False, respectively. """

    assert_equals(True, parse('#t'))
    assert_equals(False, parse('#f'))

def test_parse_integer():
    """Parsing single integer.

    Integers are represented in the ASTs as Python ints.

    Tip: String objects have a handy .isdigit() method.
    """

    assert_equals(42, parse('42'))
    assert_equals(1337, parse('1337'))

def test_parse_list_of_symbols():
    """Parsing list of only symbols.

    A list is represented by a number of elements surrounded by parens. Python lists 
    are used to represent lists as ASTs.

    Tip: The useful helper function `find_matching_paren` is already provided in
    `parse.py`.
    """

    assert_equals(['foo', 'bar', 'baz'], parse('(foo bar baz)'))
    assert_equals([], parse('()'))

def test_parse_list_of_mixed_types():
    """Parsing a list containing different types.

    When parsing lists, make sure each of the sub-expressions are also parsed 
    properly."""

    assert_equals(['foo', True, 123], parse('(foo #t 123)'))

def test_parse_on_nested_list():
    """Parsing should also handle nested lists properly."""

    program = '(foo (bar ((#t)) x) (baz y))'
    ast = ['foo', 
            ['bar', [[True]], 'x'], 
            ['baz', 'y']]
    assert_equals(ast, parse(program))

def test_parse_exception_missing_paren():
    """The proper exception should be raised if the expresions is incomplete."""

    with assert_raises_regexp(LispError, 'Incomplete expression'):
        parse('(foo (bar x y)')

def test_parse_exception_extra_paren():
    """Another exception is raised if the expression is too large.

    The parse function expects to recieve only one single expression. Anything
    more than this, should result in the proper exception."""

    with assert_raises_regexp(LispError, 'Expected EOF'):
        parse('(foo (bar x y)))')

def test_parse_with_extra_whitespace():
    """Excess whitespace should be removed."""

    program = """

       (program    with   much        whitespace)
    """

    expected_ast = ['program', 'with', 'much', 'whitespace']
    assert_equals(expected_ast, parse(program))

def test_parse_comments():
    """All comments should be stripped away as part of the parsing."""

    program = """
    ;; this first line is a comment
    (define variable
        ; here is another comment
        (if #t 
            42 ; inline comment!
            (something else)))
    """
    expected_ast = ['define', 'variable', 
                        ['if', True, 
                            42, 
                            ['something', 'else']]]
    assert_equals(expected_ast, parse(program))

def test_parse_larger_example():
    """Test a larger example to check that everything works as expected"""

    program = """
        (define fact 
        ;; Factorial function
        (lambda (n) 
            (if (<= n 1) 
                1 ; Factorial of 0 is 1, and we deny 
                  ; the existence of negative numbers
                (* n (fact (- n 1))))))
    """
    ast = ['define', 'fact', 
            ['lambda', ['n'], 
                ['if', ['<=', 'n', 1], 
                    1, 
                    ['*', 'n', ['fact', ['-', 'n', 1]]]]]]
    assert_equals(ast, parse(program))

## The following tests checks that quote expansion works properly

def test_expand_single_quoted_symbol():
    """Quoting is a shorthand syntax for calling the `quote` form.

    Examples:

        'foo -> (quote foo)
        '(foo bar) -> (quote (foo bar))

    """
    assert_equals(["foo", ["quote", "nil"]], parse("(foo 'nil)"))

def test_nested_quotes():
    assert_equals(["quote", ["quote", ["quote", ["quote", "foo"]]]], parse("''''foo"))

def test_expand_crazy_quote_combo():
    """One final test to see that quote expansion works."""

    source = "'(this ''''(makes ''no) 'sense)"
    assert_equals(source, unparse(parse(source)))


def parse(source):
    """Parse string representation of one *single* expression
    into the corresponding Abstract Syntax Tree."""
    source = remove_comments(source)
    source = re.sub( '\s+', ' ', source ).strip()
    
    def parse_tokens(tokens, inner):
        res = []
        print tokens
        if tokens == '()':
            res = res
        elif list(tokens).pop(0) == '(':
            if tokens.count('(') == 1 and tokens.count(')') == 1:
                tokens = (re.sub('[()]', '', tokens).split(' '))
                
                for i in tokens:
                    i = parse_tokens(i, False)
                    res.append(i)
            elif tokens.count('(') < tokens.count(')'):
                raise LispError('Expected EOF')
            else:
                tokens = split_exps(tokens[1:find_matching_paren(tokens)])
                for i in tokens:
                    if len(i) == 1 and i.count('(') == 0:
                        i = parse_tokens(i, False)
                        res.append(i)
                    else:
                        i = parse_tokens(i, False)
                        res.append(i)
        elif tokens[0] == "'":
            #tokens = ''.join((str('quote'), tokens[1:]))
            alist = []
            res.append("quote")
            tokens = parse_tokens(tokens[1:], False)
            res.append(tokens)
            #for i in tokens:
             #   i = parse_tokens(i, False)
              #  res.append(i)
            
            #res = parse_tokens(tokens, False)
        elif tokens == '#t':
            res = True
        elif tokens == '#f':
            res = False
        elif tokens.isdigit():
            res = int(float(tokens))
        elif isinstance(tokens, str):
            res.append(tokens)
            res = ''.join([str(item) for item in res])
        return res
    return parse_tokens(source, False)

print parse('foo')
print parse('233')
print parse('(foo bar)')
print parse('#t')
print parse('1337')
print parse('(foo bar baz)')
print parse('()')
print parse('(foo #t 123)')
program = '(foo (bar ((#t)) x) (baz y))'
print parse(program)
#print parse('(foo (bar x y)))')
print parse("''''foo")
print parse("""
    ;; this first line is a comment
    (define variable
        ; here is another comment
        (if #t 
            42 ; inline comment!
            (something else)))
    """)



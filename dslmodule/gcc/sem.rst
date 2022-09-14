SEM (PLY EXTENSION)
===================

This document provides an overview of semantic analysis with 
``sem.py``. ``sem.py`` is intended as an extension to PLY-4.0, to 
manage simple semantic analysis operations and transpile to Python 
script. The style of this script is therefore intended to be similar to 
PLY. In a similar fashion, the style of this documentation is intended
to be as close to that of PLY as possible. The PLY copyright notice is 
printed below::
  
> Copyright (C) 2001-2018
> David M. Beazley (Dabeaz LLC)
> All rights reserved.
> 
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions 
> are met:
> 
>     * Redistributions of source code must retain the above copyright 
>       notice, this list of conditions and the following disclaimer.
>     * Redistributions in binary form must reproduce the above 
>       copyright notice, this list of conditions and the following 
>       disclaimer in the documentation and/or other materials provided 
>       with the distribution.
>     * Neither the name of the David Beazley or Dabeaz LLC may be used 
>       to endorse or promote products derived from this software 
>       without specific prior written permission.
> 
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
> "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
> LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
> A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
> OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
> SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
> LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
> DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
> THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
> (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
> OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

As PLY-4.0 requires requires Python 3.6 or newer, this requirement 
also applies to ``sem.py``. For details on how to use PLY, please see 
the PLY documentation, which is available online at 
https://ply.readthedocs.io/en/latest/ply.html. 

SEM Overview
------------

Within the ``gcc`` package, are the module ``sem.py`` and the ``ply`` 
package, stored separately. To use ``lex.py`` and ``yacc.py``, instead 
of importing ``ply.lex`` and ``ply.yacc``, import ``gcc.ply.lex`` and
``gcc.ply.yacc``. To use ``sem.py``, import ``gcc.sem``.

One modification will be needed when using ``sem.py``. SEM is expecting
an AST as a tuple, with an occasional string "flag" to denote semantic
information. The flags and their uses are:

``("STATEMENT", <stmt>, <prg>)`` : 
    The next element is a statement, and the following element should
    be interpreted as a programme.
``("EMPTY")`` :
    There is no next element. This is the end of the input.
``("IDENTIFIER", <id>)`` :
    The next element is an identifier for a variable.
``("DECLARATION", <type>, ("IDENTIFIER", <id>))`` :
    This statement is declaring a variable. The next element is a type, 
    followed by an identifier.
``("ASSIGNMENT", ("IDENTIFIER", <id>), <value>)`` :
    This statement assigns a variable a particular value. The next
    element is an identifier, followed by the value.
``("DECLARE_ASSIGN", <type>, ("IDENTIFIER", <id>), <value>)`` :
    This statement declares a variable and assigns it a value. The next
    element is a type, followed by an identifier and the value.
``("OPERATOR", <operator>, <arg0>, <arg1>, <arg2>, ...)`` : 
    This executes an operator on the given operands (arguments).
``(<literal flag>, <literal>)`` : 
    This denotes a variable literal, which immediately follows. The
    literal flag is user determined, denotes a user-chosen datatype, 
    and is specified in the user's caller script.
    

Sem
---

``sem.py`` is used to carry out semantic analysis on an input AST. In
this implementation, there are four semantic analysis actions that are 
carried out:

1. Type checking - ``sem.py`` uses static typing.
2. Operator execution - ``sem.py`` can execute any operator with types 
   and format string specified. The format string will have its 
   placeholders replaced by the operands.
3. Symbol checking - ``sem.py`` maintains a table of symbols, ensuring 
   all have been declared before use and all have been assigned a 
   value, before being read.
4. Conversion to a working Python script. 

The specification of semantic constructs is done by defining them in 
the caller module. The next section shows how this is done using 
``sem.py``

Sem Example
^^^^^^^^^^^

The following example shows how ``sem.py`` is used to write a simple 
semantic analyser::

    # ------------------------------------------------------------
    # compsem.py
    #
    # analyser for a simple comparison tool for integers and 
    # booleans.
    # ------------------------------------------------------------
    import gcc.sem as sem
    
    # List of accepted datatypes, not including boolean.
    datatypes = [("I", "int")]
    
    # Defining boolean literals and datatype.
    booleans  = ("True", "False", "B", "boolean")
    
    # List of operators, of form:
    #     (<operator>, <num args>, [<tuple of types>, <tuple of
    #      types>, ...], <format string>)
    operators = [
        ("p"  , 1, [("I"), ("B")]                    , "print ({0})" ),
        ("eq" , 2, [("I", "I", "B"), ("B", "B", "B")], "({0}=={1})"  ),
        ("neq", 2, [("I", "I", "B"), ("B", "B", "B")], "({0}!={1})"  ),
        ("leq", 2, [("I", "I", "B")]                 , "({0}<={1})"  ),
        ("geq", 2, [("I", "I", "B")]                 , "({0}>={1})"  ),
        ("l"  , 2, [("I", "I", "B")]                 , "({0}<{1})"   ),
        ("g"  , 2, [("I", "I", "B")]                 , "({0}>{1})"   )
    ]
    
    # ast = ("STATEMENT", ("OPERATOR", "p", ("OPERATOR", "eq", ("int", 
    #        "4"), ("int", "3"))), ("STATEMENT", "EMPTY"))
    from compyacc import ast
    
    # Build the analyser.
    analyser = sem.sem ()
    
    # Run the analyser.
    pythonCode = analyser.analyse (ast)
    
When executed, the example will produce the following output:

>>> python3 compsem.py
print ((4==3))

The datatypes list
^^^^^^^^^^^^^^^^^^

All analysers must provide a list ``datatypes`` that defines all of the
possible datatypes used in the language, with the exception of the 
boolean datatype. This list is always required and is used to perform 
type checking on operators and assignments. Datatypes are of the form
``(<type name>, <literal flag>)``. The literal flag is how the AST 
labelled literals of that type. The type name is what the type is 
referred to as in the language. In the example, the following code 
specified the datatypes::

    datatypes = [("I", "int")]

The boolean tuple
^^^^^^^^^^^^^^^^^

All analysers must define a tuple ``booleans`` that defines the boolean
literals and the boolean datatype. The tuple is of the form ``(<true
literal>, <false literal>, <bool name>, <bool literal flag>)``. In the
example, the following code specified the booleans::

    booleans = ("True", "False", "B", "boolean")
    
The operators list
^^^^^^^^^^^^^^^^^^

All analysers must provide a list ``operators`` that defines all of the
possible operators used in the language. This list is used to perform
type checking on the arguments and code conversion to Python script.
Operators are of the form ``(<operator>, <num args>, <list of tuples of 
types>, <format string>)``.  ``<operator>`` refers to the symbol, or 
string form of the operator. ``<num args>`` refers to the number of 
operands (arguments) the operator takes.

``<list of tuples of types>`` will need some expanding, so let us start 
at the bottom and work our way up. We will think about the operator 
``"eq"``, defining equality of two integers or booleans:

1. A type is the name of a datatype, e.g. ``"I"`` for an integer. 
2. A tuple of types corresponds to the type of all arguments, and the 
   return type if applicable, e.g. ``("I", "I", "B")`` corresponds to 
   taking in two integers and returning a boolean value.
3. A list of tuples of types is a list of possible argument type 
   options, e.g. in ``"eq"``, you can compare two integers or booleans, 
   to return a boolean, giving: ``[("I", "I", "B"), ("B", "B", "B")]``.

``<format string>`` defines a Python format string, where the
placeholders will be replaced by the operands. The resulting string 
will be typed as the return type, or if there is no return type, as a 
string, e.g. using ``"eq"``, we have format string ``"({0}=={1})"``, so
that calling ``("OPERATOR", "eq", ("int", "4"), ("int", "3"))`` will 
give us ``"(4==3)"``.

In the example, the following code specified the operators::

    operators = [
        ("p"  , 1, [("I"), ("B")]                    , "print ({0})" ),
        ("eq" , 2, [("I", "I", "B"), ("B", "B", "B")], "({0}=={1})"  ),
        ("neq", 2, [("I", "I", "B"), ("B", "B", "B")], "({0}!={1})"  ),
        ("leq", 2, [("I", "I", "B")]                 , "({0}<={1})"  ),
        ("geq", 2, [("I", "I", "B")]                 , "({0}>={1})"  ),
        ("l"  , 2, [("I", "I", "B")]                 , "({0}<{1})"   ),
        ("g"  , 2, [("I", "I", "B")]                 , "({0}>{1})"   )
    ]

Building and using the analyser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To build the analyser, the function ``sem.sem ()`` is used. For 
example::

    analyser = sem.sem ()

This function uses Python reflection (or introspection) to read the
specifications of the language out of the calling context and build the
analyser. Once the analyser has been built, the analyse method can be 
used to analyse an input AST. This method will return working Python 
script that achieves the same function as the input::

    pythonCode = analyser.analyse (ast)

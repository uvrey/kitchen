"""Semantic Analyser Generator

This script is called by a caller module, that defines its own input 
AST, datatypes, boolean literals, and operators. When called, this 
script will convert the AST to	 an equivalent, executable python 
script. The python script will be passed as a string back to the caller 
module. This implementation is not thread safe. For more details, see 
the README provided.

Notes
-----
This script is intended as an extension to PLY, to manage simple 
semantic analysis operations and transpile to Python script. The style 
of this script is therefore intended to be similar to PLY [1]_. 
   
.. [1] The PLY copyright notice is printed below:
  
   Copyright (C) 2001-2018
   David M. Beazley (Dabeaz LLC)
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions 
   are met:

   * Redistributions of source code must retain the above copyright 
     notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright 
     notice, this list of conditions and the following disclaimer in 
     the documentation and/or other materials provided with the 
     distribution.
   * Neither the name of the David Beazley or Dabeaz LLC may be used 
     to endorse or promote products derived from this software without
     specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
   COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
   OF THE POSSIBILITY OF SUCH DAMAGE.

Examples
--------
The caller module should import its AST from a yacc.py caller module:
>>> from parse_lang import ast

It should then define its specifications as follows:
>>> datatypes = [(<name>, <flag in AST>), ...]
>>> booleans  = (<T literal>, <F literal>, <bool name>, <bool AST 
... flag>)
>>> operators = [(<symbol>, <num args>, [<tuple of types>, <tuple of
... types>, ...], <format string>)]

Finally, it should call this sem module:
>>> pythonCode = sem.sem ()

The output string will then be working Python code, which can be 
written to a file.

The type list on operators should account for each argument, and the
return type. The format string is a Python format string that the 
arguments will be slotted into, in the order given. As an example, let 
us define an integer datatype, a boolean datatype, and an operator (eq) 
that checks equality between integers or booleans:
>>> datatypes = [("I", "int")]
>>> booleans  = ("True", "False", "B", "bool") 
>>> operators = [("eq", 2, [("I", "I", "B"), ("B", "B", "B")], 
... "({0} == {1})")]

The AST flag represents the first element of the AST, indicating what
comes next. The most common flags used are "STATEMENT", "DECLARATION",
"ASSIGNMENT", etc. Literals are also flagged, with a special flag 
defined in the caller module. Here is an example AST, and its Python
code output:
>>> ("STATEMENT", ("DECLARE_ASSIGN", "I", ("IDENTIFIER", "var0"),
... ("int", "1")))
"var0 = 1\\n"
"""

from typing import Any, ClassVar, Collection, Dict
from typing import List, Optional, Tuple, Union
import sys
import os
import traceback

__version__    = '1.00'

# ---------------------------------------------------------------------
#                 === User configurable parameters ===
# 
#   Change these to modify the default behavior of sem (if you wish)
# ---------------------------------------------------------------------
FLAG_STATEMENT      = "STATEMENT"
FLAG_DECLARATION    = "DECLARATION"
FLAG_ASSIGNMENT     = "ASSIGNMENT"
FLAG_DECLARE_ASSIGN = "DECLARE_ASSIGN"
FLAG_OPERATOR       = "OPERATOR"
FLAG_IDENTIFIER     = "IDENTIFIER"
FLAG_EMPTY          = "EMPTY"
FLAG_PRODUCTION     = ""
# ---------------------------------------------------------------------


class SemError (Exception):
    """Base exception raised for semantic analysis errors.
    """

    pass
    
    
class SemSetupError (SemError):
    """Base exception raised for errors occuring during the setup of 
    the semantic analyser.
    """
    
    pass


class SemCallerError (SemError):
    """Exception where the caller module is unable to be found.
    """
    
    def __init__ (self) -> None:
        """Create a SemCallerError.
        """
        
        error_msg = "Unable to find the caller module."
        super ().__init__ (error_msg)


class SemTypeListError (SemSetupError):
    """Exception where no type list is defined.
    """

    def __init__ (self) -> None:
        """Create a SemTypeListError.
        """
        
        error_msg = "No type list was defined in the caller module."
        super ().__init__ (error_msg)


class SemTypeDuplicateError (SemSetupError):
    """Exception where two types are given the same name.
    """

    def __init__ (
      self,
      name : str
    ) -> None:
        """Create a SemTypeDuplicateError for a given type.
        
        Parameters
        ----------
        name : str
            The conflicting name of the datatype.
        """
        
        error_msg = "Type {} has already been defined.".format (name)
        super ().__init__ (error_msg)
    

class SemBoolError (SemSetupError):
    """Exception where booleans are incorrectly defined.
    """
    
    def __init__ (self) -> None:
        """Create a SemBoolError.
        """
        
        error_msg = "No boolean type was defined in the caller module."
        super ().__init__ (error_msg)


class SemOperatorListError (SemSetupError):
    """Exception where no operator list is defined.
    """
    
    def __init__ (self) -> None:
        """Create a SemOperatorListError.
        """
        
        error_msg = "No operator list was defined in the caller module."
        super ().__init__ (error_msg)


class SemOperatorDuplicateError (SemSetupError):
    """Exception where an operator with a given symbol has already been
    defined.
    """
    
    def __init__ (
      self,
      opString : str
    ) -> None:
        """Create a SemOperatorDuplicateError for a given operator.
        
        Parameters
        ----------
        opString : str
            The conflicting string of the operator.
        """
        
        error_msg = "Type {} has already been defined.".format (opString)
        super ().__init__ (error_msg)


class SemOperatorTypeError (SemSetupError):
    """Exception where an operator has a type list of the wrong size.
    """

    def __init__ (
      self, 
      opString : str
    ) -> None:
        """Create a SemOperatorTypeError for a given operator.
        
        Parameters
        ----------
        opString : str
            The string of the operator with a type list disparity.
        """
        
        error_msg  = "Operator {} ".format (opString)
        error_msg += "has an incorrect type list size."    
        super ().__init__ (error_msg)


class SemASTError (SemError):
    """Exception where the given AST is not readable.
    """
    
    def __init__ (self) -> None:
        """Create a SemASTError.
        """
        
        error_msg = "The supplied AST is not readable."
        super ().__init__ (error_msg)


class SemAnalysisError (SemError):
    """Base exception raised for errors occuring during analysis of 
    input code.
    """

    def __init__ (
      self,
      errorMsg : str,
      lineNo   : int
    ) -> None:
        """Create a SemAnalysisError for a given error message and line
        number.
        
        Parameters
        ----------
        errorMsg : str
            The error message to be displayed.
        lineNo   : int
            The line number of the statement with the error.
        """
        
        error_msg  = errorMsg + "\n"
        error_msg += "    Line number: {}.".format (lineNo)
        
        super ().__init__(error_msg)


class SemTypeError (SemAnalysisError):
    """Base exception raised for type errors.
    """

    pass


class SemTypeMismatchError (SemTypeError):
    """Exception where one or more operands are not of the expected
    type.
    """

    def __init__ (
      self, 
      opString  : str, 
      typeNames : List [str],
      lineNo    : int
    ) -> None:
        """Create a new SemTypeMismatchError for a given operator, list
        of types.
        
        Parameters
        ----------
        opString : str
            The string of the operator where the mismatch occured.
        strTypes : List [str]
            The list of datatypes of the operands the operator does not
            support.
        lineNo   : int
            The line number of the statement with the error.
        """
        
        error_msg = "Unsupported operand type(s) for {}: ".format (opString)
        length   = len (typeNames)
        
        if (length >= 1):
            error_msg += typeNames [0]
            
            if (length >= 2):
                for typeName in typeNames [:-1]:
                    error_msg += typeName + ", "
                error_msg += "and " + typeNames [-1]
            
        error_msg += "."                
        super ().__init__ (error_msg, lineNo)


class SemTypeNotFoundError (SemTypeError):
    """Exception where no type exists with the given name.
    """
    
    def __init__ (
      self, 
      typeName : str,
      lineNo   : int
    ) -> None:
        """Create a SemTypeNotFoundError for a given datatype.
        
        Parameters
        ----------
        type_string : str
            The name of the datatype that was not found.
        lineNo   : int
            The line number of the statement with the error.
        """
        
        error_msg = "Type {} is not defined.".format (typeName)
        super ().__init__ (error_msg, lineNo)


class SemTypeFlagNotFoundError (SemTypeError):
    """Exception where no type exists with the given literal flag.
    """
 
    def __init__ (
      self, 
      flag   : str,
      lineNo : str,
    ) -> None:
        """Create a SemTypeFlagNotFoundError for a given datatype.
        
        Parameters
        ----------
        flag : str
            The literal flag of the datatype that was not found.
        lineNo   : int
            The line number of the statement with the error.
        """

        error_msg = "Type with flag {} is not defined.".format (flag)
        super ().__init__ (error_msg, lineNo)
        

class SemOperatorError (SemAnalysisError):
    """Base exception raised for operator errors.
    """
    
    pass


class SemOperatorNotFoundError (SemOperatorError):
    """Exception where no operator exists with the given symbol.
    """
    
    def __init__ (
      self, 
      opString : str,
      lineNo   : int 
    ) -> None:
        """Create a SemOperatorNotFoundError for a given operator.
        
        Parameters
        ----------
        opString : str
            The string of the operator that was not found.
        lineNo   : int
            The line number of the statement with the error.
        """
    
        error_msg = "Operator {} is not defined.".format (opString)   
        super ().__init__ (error_msg, lineNo)


class SemOperatorFStringError (SemOperatorError):
    """Exception where an operator's format string is not valid for the
    operands given.
    """
    
    def __init__ (
      self,
      opString : str,
      fString  : str,
      operands : List [str],
      lineNo   : int
    ) -> None:
        """Create a SemOperatorFStringError for a given operator, 
        format string and list of operands. 
        
        Parameters
        ----------
        opString : str
            The string of the operator.
        fString  : str
            The format string of the operator.
        operands : List [str]
            The operands supplied to the operator.
        lineNo   : int
            The line number of the statement with the error.
        """
        
        error_msg  = "Unable to execute operator {} ".format (opString)
        error_msg += "with format string \"{}\" ".format (fString)
        
        length   = len (operands)
        
        if (length >= 1):
            error_msg += operands [0]
            
            if (length >= 2):
                for operand in operands [:-1]:
                    error_msg += operand + ", "
                error_msg += "and " + operands [-1]
        
        error_msg += "."
        
        super ().__init__ (error_msg, lineNo)


class SemSymbolError (SemAnalysisError):
    """Base exception raised for symbol table errors.
    """
    
    pass



class SemSymbolDeclaredError (SemSymbolError):
    """Exception where a new symbol has already been declared.
    """
    
    def __init__ (
      self, 
      name   : str,
      lineNo : int
    ) -> None:
        """Create a SemSymbolDeclaredError for a given symbol.
        
        Parameters
        ----------
        name   : str
            The name of the symbol.
        lineNo : int
            The line number of the statement with the error.
        """
        
        error_msg = "Symbol {} has already been defined.".format (name)
        super ().__init__ (error_msg, lineNo)


class SemSymbolNotDeclaredError (SemSymbolError):
    """Exception where a referenced symbol has not yet been declared.
    """
    
    def __init__ (
      self, 
      name   : str,
      lineNo : int
    ) -> None:
        """Create a SemSymbolNotDeclaredError for a given symbol.
        
        Parameters
        ----------
        name   : str
            The name of the symbol.
        lineNo : int
            The line number of the statement with the error.
        """
        
        error_msg = "Cannot find symbol {}.".format (name)
        super ().__init__ (error_msg, lineNo)


class SemSymbolNotAssignedError (SemSymbolError):
    """Exception where an accessed symbol has not yet been assigned a 
    value.
    """
    
    def __init__ (
      self, 
      name   : str,
      lineNo : int
    ) -> None:
        """Create a SemSymbolNotAssignedError for a given symbol.
        
        Parameters
        ----------
        name   : str
            The name of the symbol.
        lineNo : int
            The line number of the statement with the error.
        """
        
        error_msg = "Symbol {} has not been assigned a value.".format (name)
        super ().__init__ (error_msg, lineNo)
    
        
class SemType:
    """A class used to describe a datatype.
    
    Attributes
    ----------
    typeName  : str
        The name of the datatype.
    alias     : str
        The flag used in the AST to represent literals of the datatype.
    BOOL_TYPE : ClassVar ["SemType"]
        The datatype corresponding to a boolean variable.
    """
    
    def __init__ (
      self, 
      name : str, 
      flag : str
    ) -> None:
        """Create a SemType object with a given name and literal flag.
        
        Parameters
        ----------
        name : str
            The name of the datatype.
        flag : str
            The flag used in the AST to denote literals of that 
            datatype.
        """
        
        self.typeName = name
        self.alias    = flag


    def __str__ (self) -> str:
        """Return a readable form of the datatype.
        
        Returns
        -------
        str
            The name of the datatype.
        """
        
        if (self.typeName == None):
            return ""
        else:
            return self.typeName

    
# There is only one boolean type.
SemType.BOOL_TYPE = SemType ("bool", "bool")


class SemVariable:    
    """A class used to describe a variable.
    
    A variable does not necessarily correpond to a named variable. For
    example, myString is a variable, but "abcde" is also a variable.
    
    Attributes
    ----------
    value    : str
        The value of the variable.
    dtype    : SemType
        The datatype of the variable.
    assigned : bool
        Whether the variable has been assigned a value yet. Only ever
        true for named variables.
    """

    def __init__ (
      self,
      val : str,
      dt  : SemType
    ) -> None:
        """Create a SemVariable object with a given value and datatype.
        
        Parameters
        ----------
        val : str
            The value of the variable.
        dt  : SemType
            The datatype of the variable.
        """
        
        self.value    = val
        self.dtype    = dt
        self.assigned = False
    
    
    def __str__ (self) -> str:
        """Return a readable form of the variable.
        
        Returns
        -------
        str
            The value of the variable.
        """
        
        if (self.value == None):
            return ""
        else:
            return self.value
        

    def assign (
      self, 
      otherVar : "SemVariable",
      lineNo   : int
    ) -> None:
        """Assign a value to a named variable.
        
        Parameters
        ----------
        otherVar : SemVariable
            The other variable whose value you wish to assign to this 
            variable.
        lineNo   : int
            The line number of the statement making the call.

        Raises
        ------
        SemTypeMismatchError
            If a variable is assigned to another variable that does not 
            match its datatype.            
        """
        
        if (str (self.dtype) == str (otherVar.dtype)):
            self.value    = otherVar.value
            self.assigned = True
        else:
            assignOp = "assign {}".format (self.dtype)
            raise SemTypeMismatchError (assignOp, [otherVar.dtype], lineNo)
    

class SemOperator:
    """A class used to describe an operator.
    
    Attributes
    ----------
    opString : str
        The string of the operator.
    numArgs  : int
        The number of arguments the operator takes in.
    doReturn : bool
        True if the operator returns a variable; otherwise, False.
    typess   : List [Tuple [str, ...]]
        A list of possible types of each of those arguments, followed
        by an optional return type.
    fString  : str
        A Python format string corresponding to the desired execution
        of the operator.
        
    Examples
    --------
    If one wanted to created an operator, "A", to carry out addition of
    two arguments that can be either both "int"s or both "float"s, one 
    would define:
    
    >>> addOp = SemOperator (
    ...   "A", 
    ...   2, 
    ...   [("int", "int", "int"), ("float", "float", "float")],
    ...   "({0} + {1})"
    ... )
    """

    def __init__ (
      self,
      string : str,
      nArg   : str,
      # Use strings because SemType can be duplicated.
      tList  : List [Tuple [str, ...]],
      action : str
    ) -> None:
        """Create a SemOperator object with given parameters.
        
        Parameters
        ----------
        string : str
            The string of the operator.
        nArg   : str
            The number of operands the operator takes in.
        tList  : List [Tuple [str, ...]]
            A list of possible types of each of those operands, 
            followed by an optional return type.
        action : str
            A Python format string corresponding to the desired 
            execution of the operator.
            
        Raises
        ------
        SemOperatorTypeError
            If the list of datatypes associated with the operator is
            of the wrong size given the number of operands.
        """
        
        self.doReturn = False
        length        = 0
        
        if (len (tList) > 0):
            length = len (tList [0])
        
        if (length == nArg + 1):
            self.doReturn = True
        elif (length != nArg):
            raise SemOperatorTypeError (string)

        self.opString = string        
        self.numArgs  = nArg
        self.typess   = tList
        self.fString  = action


    def __str__ (self) -> str:
        """Return a readable form of the operator.
        
        Returns
        -------
        str
            The string of the operator.
        """
        
        if (self.opString == None):
            return ""
        else:
            return self.opString


    def checkTypes (
      self, 
      argTypes : List [str],
      lineNo   : int
    ) -> Optional [str]:
        """Check whether a given set of types is valid for this 
        operator.
        
        Parameters
        ----------
        argTypes : List [str]
            A list of operand types to check against the operator.
        lineNo   : int
            The line number of the statement making the call.
        
        Returns
        -------
        Optional [str]
            The name of the return type of the operator, or None if
            there is no return type.
            
        Raises
        ------
        SemTypeMismatchError
            If the types supplied do not match any of the operator's
            accepted operand types.
        """

        options = len (self.typess)
        valid   = (options == 0)
        rType   = None
        
        for i in range (options):
            check0 = True
            for j in range (self.numArgs):
                if (argTypes [j] != str (self.typess [i] [j])):
                    check0 = False
                    break
            
            if (check0):
                valid  = True
                if (self.doReturn):
                    rType = self.typess [i] [-1]
                break
        
        if (valid):
            return rType
        else:
            raise SemTypeMismatchError (str (self), argTypes, lineNo)


    def execute (
      self, 
      args   : List [SemVariable],
      lineNo : int
    ) -> Union [str, SemVariable]:
        """Performs the action of the operator on the given operands.
        
        Parameters
        ----------
        args   : List [SemVariable]
            The operands to be supplied to the operator.
        lineNo : int
            The line number of the statement making the call.
        
        Returns
        -------
        Union [str, SemVariable]
            The result of performing the action of the operator, as a 
            string if no return type is expected and as a variable if a
            return type is accepted.
        
        Raises
        ------
        SemTypeMismatchError
            If the types of the operands supplied do not match any of 
            the operator's accepted operand types.
        SemOperatorFStringError
            If the operator's format string is not valid for the 
            operands given.
        """

        execution = None
        argValues = [str (arg)                               for arg in args]
        argTypes  = [str (arg.dtype if arg != None else arg) for arg in args]
        
        returnType = self.checkTypes (argTypes, lineNo)
        
        try:
            execution = self.fString.format (*argValues)
            
            if returnType:
                return SemVariable (execution, returnType)
            else:
                return execution
        
        # Error with format string.        
        except Exception:
            raise SemOperatorFStringError (
              str (self), 
              self.fString, 
              argValues,
              lineNo
            )


class SemTypeTable:
    """ A table of datatypes of type SemType.
    
    All variables are statically typed and declared in this 
    implementation.
    
    Attributes
    ----------
    table : List [SemType]
        A list of accepted datatypes.
    """
    
    def __init__ (self) -> None:
        """Create an empty SemTypeTable.
        """
        
        self.table = []
    
    
    def retrieve (
      self, 
      name   : str,
      lineNo : int
    ) -> SemType:
        """Fetch a datatype with a certain name from the table.
        
        Parameters
        ----------
        name     : str
            The name of the datatype.
        lineNo   : int
            The line number of the statement making the call.
        
        Returns
        -------
        SemType
            The corresponding datatype from the table.
            
        Raises
        ------
        SemTypeNotFoundError
            If there is no datatype in the table matching the name 
            given.
        """
        
        next = None
        
        for i in range (len (self.table)):
            next = self.table [i]
            if (name == str (next)):
                return next
                
        raise SemTypeNotFoundError (name, lineNo)


    def retrieveAlias (
      self, 
      flag   : str,
      lineNo : int
    ) -> SemType:
        """Fetch a datatype with a certain literal flag from the table.
        
        Parameters
        ----------
        flag   : Optional [str]
            The literal flag of the datatype, as it appears in the AST.
        lineNo : int
            The line number of the statement making the call.
        
        Returns
        -------
        SemType
            The corresponding datatype from the table.
            
        Raises
        ------
        SemTypeFlagNotFoundError
            If there is no datatype in the table matching the flag 
            given.
        """
        
        next = None
        
        for i in range (len (self.table)):
            next = self.table [i]
            if (flag == next.alias):
                return next
        raise SemTypeFlagNotFoundError (flag, lineNo)

    
    def add (
      self, 
      newType : SemType
    ) -> None:
        """Add a new datatype to the table.
        
        Parameters
        ----------
        newType : SemType
            The datatype to be added to the table.
        
        Raises
        ------
        SemTypeDuplicateError
            If a datatype with the same name already exists in the 
            table.
        """
        
        try:
            name = str (newType)
            self.retrieve (name, 0)
            raise SemTypeDuplicateError (name)
            
        except SemTypeNotFoundError:
            self.table.append (newType)  


class SemOperatorTable:
    """A table of operators of type SemOperator.
    
    Attributes
    ----------
    table : List [SemOperator]
        A list of accepted operators.
    """

    def __init__ (self) -> None:
        """Create an empty SemOperatorTable.
        """
        
        self.table = []


    def retrieve (
      self, 
      opString : str,
      lineNo   : int
    ) -> SemOperator:
        """Fetch an operator with a certain string from the table.
        
        Parameters
        ----------
        opString : str
            The string of the operator.
        lineNo   : int
            The line number of the statement making the call.
        
        Returns
        -------
        SemOperator
            The corresponding operator from the table.
            
        Raises
        ------
        SemOperatorNotFoundError
            If there is no operator in the table matching the string 
            given.
        """
        
        next = None
        
        for i in range (len (self.table)):
            next = self.table [i]
            if (opString == str (next)):
                return next
        raise SemOperatorNotFoundError (opString, lineNo)


    def add (
      self, 
      operator : SemOperator
    ) -> None:
        """Add a new operator to the table.
        
        Parameters
        ----------
        operator : SemOperator
            The operator to be added to the table.
        
        Raises
        ------
        SemOperatorDuplicateError
            If an operator with the same string already exists in the 
            table.
        """
        
        try:
            opString = str (operator)
            self.retrieve (opString, 0)
            raise SemOperatorDuplicateError (opString)
            
        except SemOperatorNotFoundError:
            self.table.append (operator)  


class SemSymbolTable:
    """A table of symbols of type SemVariable.
    
    In this implementation, a symbol corresponds to a named variable.
    All symbols have global scope.
    
    Attributes
    ----------
    table : Dict [str, SemVariable]
        A dictionary of symbols currently in scope, organised by name.
    """

    def __init__ (self) -> None:
        """Create an empty SemSymbolTable.
        """

        self.table = {}


    def pop (
      self, 
      name   : str,
      lineNo : int
    ) -> SemVariable:
        """Remove and return a symbol with a certain name from the 
        table.
        
        Parameters
        ----------
        name : str
            The name of the symbol.
        lineNo   : int
            The line number of the statement making the call.
        
        Returns
        -------
        SemVariable
            The corresponding symbol from the table.
            
        Raises
        ------
        SemSymbolNotDeclaredError
            If no symbol with that name has been declared yet.
        """
        
        try:
            return self.table.pop (name)
            
        except KeyError:
            raise SemSymbolNotDeclaredError (name, lineNo)
 
        
    def retrieve (
      self, 
      name    : str,
      lineNo  : int,
      qAssign : bool = False
    ) -> SemVariable:
        """Fetch a symbol with a certain name from the table.
        
        Parameters
        ----------
        name    : str
            The name of the symbol.
        lineNo  : int
            The line number of the statement making the call.
        qAssign : bool, default = False
            True if an exception should be raised for an unassigned
            symbol, False if not.
        
        Returns
        -------
        SemVariable
            The corresponding symbol from the table.
            
        Raises
        ------
        SemSymbolNotDeclaredError
            If no symbol with that name has been declared yet.
        SemSymbolNotAssignedError
            If the qAssign parameter is set to True and the symbol has
            not yet been assigned a value.
        """
        
        symbol = self.pop (name, lineNo)
        self.table.update ({name: symbol})

        if (qAssign and (not symbol.assigned)):
            raise SemSymbolNotAssignedError (name, lineNo)                      
        else:
            return symbol
             
    
    def declare (
      self, 
      name     : str, 
      datatype : SemType,
      lineNo   : int
    ) -> None:
        """Add a new symbol with a given datatype to the table.
    
        The symbol will not be assigned a value.
    
        Parameters
        ----------
        name     : str
            The name of the symbol.
        datatype : SemType
            The datatype of the symbol.
        lineNo   : int
            The line number of the statement making the call.
        
        Raises
        ------
        SemSymbolDeclaredError
            If the symbol is already in the table.
        """
    
        try:
            self.retrieve (name, lineNo)
            raise SemSymbolDeclaredError (name, lineNo)
            
        except SemSymbolNotDeclaredError:
            symbol = SemVariable (None, datatype)
            self.table.update ({name: symbol})
                
                
    def assign (
      self, 
      name     : str, 
      otherVar : SemVariable,
      lineNo   : int
    ) -> None:
        """Assign a new value to a symbol in the table.
        
        Parameters
        ----------
        name     : str
            The name of the symbol.
        otherVar : SemVariable
            The variable that holds the new value.
        lineNo   : int
            The line number of the statement making the call.
            
        Raises
        ------
        SemSymbolNotDeclaredError
            If no symbol with that name has been declared yet.
        SemTypeMismatchError
            If the variable holding the new value does not match the
            datatype of the symbol.            
        """
        
        symbol = self.pop (name, lineNo) 
        symbol.assign (otherVar, lineNo)
        self.table.update ({name: symbol})


class SemReflect:
    """This class represents information extracted for building a 
    semantic analyser.
    
    Except for the datatypes, all attributes are immutable once 
    assigned.
    
    Attributes
    ----------
    SDICT     : Dict [str, str]
    datatypes : SemTypeTable
    BOOLEANS  : Tuple [str, str]
    OPERATORS : SemOperatorTable
    AST       : Tuple [Any]
    """

    def __init__ (
      self, 
      caller : Dict [str, str]
    ) -> None:
        """Create a SemReflect object for a given caller dictionary.
        
        Parameters
        ----------
        caller : Dict [str, str]
            The dictionary of module information, of the caller of this 
            script further up the call stack.
        
        """
        
        self.SDICT     = caller
        self.datatypes = None
        self.BOOLEANS  = None
        self.OPERATORS = None
  
    def get_datatypes (self) -> None:
        """Get all datatypes from the language.
        
        Set the value of self.datatypes to those types.
        
        Raises
        ------
        SemTypeListError
            If there is no list of datatypes defined.
        """    
        
        dt_strings = self.SDICT.get ("datatypes", None)
        
        if not dt_strings:
            raise SemTypeListError ()
        
        dts = SemTypeTable ()
                
        for (name, flag) in dt_strings:            
            dt = SemType (name, flag)
            dts.add (dt)
             
        self.datatypes = dts


    def get_boolean_info (self) -> None:
        """Get the boolean information from the language.
        
        Add the boolean type to self.datatypes. Set the value of 
        self.BOOLEANS to those values.
        
        Raises
        ------
        SemTypeBoolError
            If boolean type is defined incorrectly by user.
        """
        
        boolSpecs = self.SDICT.get ("booleans", None)
        
        if not boolSpecs:
            raise SemTypeBoolError
        
        try:
            trueVar  = boolSpecs [0]
            falseVar = boolSpecs [1]
            boolName = boolSpecs [2]
            boolFlag = boolSpecs [3]
        
            SemType.BOOL_TYPE = SemType (boolName, boolFlag)
            self.datatypes.add (SemType.BOOL_TYPE)

            self.BOOLEANS = (trueVar, falseVar)
        
        except IndexError:
            raise SemTypeBoolError
    
    
    def get_operators (self) -> None:
        """Get all operators from the language.    
        
        Set the value of self.operators to those types.
        
        Raises
        ------
        SemOperatorListError
            If the list of operators is missing.
        """
        op_info = self.SDICT.get ("operators", None)

        if not op_info:
            raise SemOperatorListError ()
        
        ops = SemOperatorTable ()
        
        for operator in op_info:
            op = SemOperator (*operator)
            ops.add (op)
             
        self.OPERATORS = ops


    def validate_operators (self) -> None:
        """Check that the operators' type lists make sense.
        
        Raises
        ------
        SemOperatorTypeError
            If there is any disparity in an operator's expeceted 
            datatypes.
        """

        for operator in self.OPERATORS.table:
            opTypess = operator.typess
            length   = None
            
            if (len (opTypess) == 0):
                length = 0
            else:
                length = len (opTypess [0])
        
            for opTypes in opTypess:
                if (len (opTypes) == length):
                    for opType in opTypes:
                        self.datatypes.retrieve (opType, 0)
                else:
                    raise SemOperatorTypeError (str (operator))


    def get_all (self) -> None:
        """Get all of the basic information.
        
        Raises
        ------
        SemTypeListError
            If there is no list of datatypes defined.
        SemTypeBoolError
            If the boolean type is incorrectly defined.
        SemOperatorListError
            If there is no list of operators defined.
        """
        
        self.get_datatypes    ()
        self.get_boolean_info ()
        self.get_operators    ()


    def validate_all (self) -> None:
        """Validate all of the basic information.    
        
        Raises
        ------
        SemOperatorTypeError
            If there is any disparity in any operator's expeceted 
            datatypes.
        """
        
        self.validate_operators ()


class SemAnalyser:
    """The semantic analyser for the given language.
    
    Attributes
    ----------
    BOOLEANS       : Tuple [str, str]
        The string literals corresponding to the boolean values, True
        and False.
    TYPE_TABLE     : SemTypeTable
        The table of valid datatypes.
    OPERATOR_TABLE : SemOperatorTable
        The table of valid operators.
    symbolTable    : SemSymbolTable
        The table of symbols currently in scope.
        
        The symbol table is the only mutable table.
    """
    
    def __init__ (
      self, 
      booleans  : Tuple [str, str],
      datatypes : SemTypeTable, 
      operators : SemOperatorTable
    ) -> None:
        """Create a semantic analyser for a given specification.
        
        The symbol table is the only mutable table.
        
        Parameters
        ----------
        booleans  : Tuple [str, str]
            The literals corresponding to the boolean values, True and 
            False.
        datatypes : SemTypeTable
            The table of valid datatypes.
        operators : SemOperatorTable
            The table of valid operators.
        """
        
        self.BOOLEANS       = booleans
        self.TYPE_TABLE     = datatypes
        self.OPERATOR_TABLE = operators
        self.symbolTable    = SemSymbolTable ()


    def processStatement (
      self, 
      s0     : Tuple [Any], 
      s1     : Tuple [Any], 
      lineNo : int
    ) -> Union [SemVariable, str]:
        """Interpret a statement from the AST.
        
        Parameters
        ----------
        s0     : Tuple [Any]
            The statement to read.
        s1     : Tuple [Any]
            The next statement.
        lineNo : int
            The line number of the statement.
        
        Returns
        -------
        Union [SemVariable, str]
            The result of interpreting the statement.
        
        Raises
        ------
        SemAnalysisError
            If either statement has a semantic issue. 
        """
        
        smt0   = self.interpret (s0, lineNo)
        smt1   = self.interpret (s1, lineNo + 1)
        result = ""
        
        if (smt0):
            result  = str (smt0) + "\n"
        if (smt1):
            result += str (smt1)

        return result

        
    def processDeclaration (
      self, 
      typeName : str, 
      varName  : str, 
      lineNo   : int
    ) -> None:
        """Interpret a declaration from the AST.
        
        Parameters
        ----------
        typeName : str
            The name of the datatype of the symbol being declared.
        varName  : str 
            The name of the symbol being declared.
        lineNo   : int
            The line number of the current statement.

        Raises
        ------
        SemTypeNotFoundError
            If there is no datatype in the table matching the type name 
            given.
        SemSymbolDeclaredError
            If the symbol is already in the table.
        """
        
        datatype = self.TYPE_TABLE.retrieve (typeName, lineNo)            
        self.symbolTable.declare (varName, datatype, lineNo)

    
    def processAssignment (
      self, 
      name     : str, 
      otherVar : SemVariable, 
      lineNo   : int
    ) -> str:
        """Interpret a symbol assignment from the AST.
        
        Parameters
        ----------
        name     : str
            The name of the symbol.
        otherVar : SemVar
            The variable holding the new value of the symbol.
        lineNo   : int
            The line number of the current statement.
        
        Raises
        ------
        SemSymbolNotDeclaredError
            If no symbol with that name has been declared yet.
        SemTypeMismatchError
            If the variable holding the new value does not match the
            datatype of the symbol.                    
        """
        self.symbolTable.assign (name, otherVar, lineNo)
        
        result     = "{} = {}".format (name, str (otherVar))
        return result

        
    def processOperator (
      self, 
      opString : str, 
      argASTs  : Tuple [Any], 
      lineNo   : int
    ) -> Union [SemVariable, str]:
        """Interpret an operator call from the AST.
        
        Parameters
        ----------
        opString : str
            The string of the operator.
        argASTs  : Tuple [Any]
            The operands, as an AST.
        lineNo   : int
            The line number of the current statement.
        
        Raises
        ------
        SemOperatorNotFoundError
            If there is no operator in the table matching the string 
            given.
        SemSymbolNotAssignedError
            If the symbol has not yet been assigned a value.
        SemTypeMismatchError
            If the types of the operands supplied do not match any of 
            the operator's accepted operand types.
        SemOperatorFStringError
            If the operator's format string is not valid for the 
            operands given.
        SemAnalysisError
            If any of the arguments has a semantic issue.
        """
    
        operator = self.OPERATOR_TABLE.retrieve (opString, lineNo)
        argVars = [None] * len (argASTs)
            
        for i in range (0, len (argASTs)):
            argVars [i] = self.interpret (argASTs [i], lineNo)
                
        result = operator.execute (argVars, lineNo)
        return result
    

    def processLiteral (
      self, 
      flag   : str, 
      value  : str, 
      lineNo : int
    ) -> SemVariable:
        """Interpret a variable literal from the AST.
        
        Parameters
        ----------
        flag   : str
            The literal flag of the variable. 
        value  : str
            The value of the variable.
        lineNo : int
            The line number of the current statement.
        
        Returns
        -------
        SemVariable
            The variable as a SemVar object.
        
        Raises
        ------
        SemTypeFlagNotFoundError
            If there is no datatype in the table matching the flag 
            given.
        """

        dtype = self.TYPE_TABLE.retrieveAlias (flag, lineNo)

        if (dtype == SemType.BOOL_TYPE):
            if (value == self.BOOLEANS [0]):
                value = "True"
            else:
                value = "False"
                
        result = SemVariable (value, dtype)
    
        return result


    def interpret (
      self, 
      ast    : Tuple [Any], 
      lineNo : int
    ) -> Union [SemVariable, str]:
        """Interpret an AST.
        
        Parameters
        ----------
        ast    : Tuple [Any]
            The AST to interpret.
        lineNo : int
            The line number of the current statement.
        
        Returns
        -------
        Union [SemVariable, str]
            The result of interpreting the AST.
        
        Raises
        ------
        SemAnalysisError
            If any statement has a semantic issue. 
        """
            
        result = None
                
        # End of programme.
        if (type (ast) != tuple):
            pass
        
        elif (ast [0] == FLAG_STATEMENT):
            s0     = ast [1]
            s1     = None
            if (len (ast) > 2):
                s1 = ast [2] 
            result = self.processStatement (s0, s1, lineNo)
            
        elif (ast [0] == FLAG_DECLARATION):
            typeName = ast [1]
            varName  = ast [2]
            self.processDeclaration (typeName, varName, lineNo)
                    
        elif (ast [0] == FLAG_ASSIGNMENT):
            name     = ast [1]
            otherVar = self.interpret (ast [2], lineNo) 
            result   = self.processAssignment (name, otherVar, lineNo)
        
        elif (ast [0] == FLAG_DECLARE_ASSIGN):
            typeName = ast [1]
            varName  = ast [2]
            otherVar = self.interpret (ast [3], lineNo)
            self.processDeclaration (typeName, varName, lineNo)
            result   = self.processAssignment (varName, otherVar, lineNo)
        
        elif (ast [0] == FLAG_IDENTIFIER):
            name   = ast [1]
            result = self.symbolTable.retrieve (name, lineNo, True)
            result.value = name
            return result
            
        elif (ast [0] == FLAG_OPERATOR):
            opString = ast [1]
            argASTs  = ast [2:]            
            result = self.processOperator (opString, argASTs, lineNo)
                            
        elif (ast [0] == FLAG_PRODUCTION):
            result = self.interpret (ast [1:], lineNo)
        
        elif (ast [0] == FLAG_EMPTY):
            pass
            
        else:
            try:
                # Variable literal.
                flag   = ast [0]
                value  = ast [1]
                result = self.processLiteral (flag, value, lineNo)
                
            except IndexError:
                errTemp = "Unable to read parser flag \"{}\"."
                errMsg  = errTemp.format (str (ast [0]))
                raise SemAnalysisError (errMsg, lineNo)
        
        return result
        
        
    def analyse (
      self, 
      ast    : Tuple [Any]
    ) -> str:
        """Analyse an AST.
        
        Parameters
        ----------
        ast    : Tuple [Any]
            The AST to analyse.
        
        Returns
        -------
        str
            The result of analysing the AST.
        
        Raises
        ------
        SemAnalysisError
            If any statement has a semantic issue. 
        SemASTError
            If the AST is not readable.
        """
        
        result = self.interpret (ast, 1)
        
        if (not result):
            raise SemASTError
        
        return str (result)


def get_caller_module_dict (
  levels : int
) -> Dict [str, str]:
    """This function returns a dictionary containing all of the symbols
    defined within a caller further down the call stack.  This is used 
    to get the environment associated with the sem () call if none was 
    provided.
    
    This function was sourced from PLY.yacc.py.
    
    Parameters
    ----------
    levels : int
        The number of levels up the call stack to go for the caller.
    
    Returns
    -------
    Dict [str, str]
        A dictionary containing all module information of the caller.
    
    Raises
    ------
    ValueError
        If the number of levels requested is larger than the call 
        stack.
    """
    
    frame = sys._getframe (levels)
    sdict = frame.f_globals.copy ()
    
    if frame.f_globals != frame.f_locals:
        sdict.update (frame.f_locals)
        
    return sdict
            
        
def get_module_dict (
  module : Any
) -> Dict [str, str]:
    """Get the module dictionary used for the semantic analyser.
    
    This function was sourced from PLY.yacc.py.
    
    Parameters
    ----------
    module : Any
        The module itself.
        
    Returns
    -------
    Dict [str, str]
        A dictionary containing all module information.
    
    Raises
    ------
    ValueError
        If the semantic analyser is unable to find the module.
    """
    
    sdict = None
    
    if module:
        contents = [(name, getattr (module, name)) for k in dir (module)]
        sdict    = dict (contents)
        
        # If no __file__ or __package__ attributes are available, try to 
        # obtain them from the __module__ instead.
        if ("__file__" not in sdict):
            sdict ["__file__"] = (
              sys.modules [sdict ["__module__"]].__file__
            )
            
        if "__package__" not in sdict and "__module__" in sdict:
            if (hasattr (sys.modules [sdict ["__module__"]], "__package__")):
                sdict ["__package__"] = (
                  sys.modules [sdict ["__module__"]].__package__ 
                )   
    else:
        try:
            sdict = get_caller_module_dict (3)
        except ValueError:
            raise SemCallerError
    
    return sdict
    

def sem (
    module : Any = None
) -> SemAnalyser:
    """Build a semantic analyser and execute its analysis.
    
    Parameters
    ----------
    module : Any, default = None
        The module containing the language-specific information.
    
    Returns
    -------
    SemAnalyser
        A semantic analyser for the language.
    
    Raises
    ------
    SemError
        If anything goes wrong during semantic analysis.
    """
    # Collect language-specific information from the module.
    sdict = get_module_dict (module)
    sinfo = SemReflect (sdict)
    sinfo.get_all      ()
    sinfo.validate_all ()

    # Build and return the semantic analyser.
    analyser = SemAnalyser (sinfo.BOOLEANS, sinfo.datatypes, sinfo.OPERATORS)
    return analyser

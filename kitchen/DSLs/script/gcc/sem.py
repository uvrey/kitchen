from enum import Enum
import sys
import os
import traceback

__version__    = '1.00'

#-----------------------------------------------------------------------------
#                     === User configurable parameters ===
#
# Change these to modify the default behavior of sem (if you wish)
#-----------------------------------------------------------------------------
FLAG_STATEMENT   = "STATEMENT"
FLAG_DECLARATION = "DECLARATION"
FLAG_OPERATOR    = "OPERATOR"
FLAG_IDENTIFIER  = "IDENTIFIER"
FLAG_EMPTY       = "EMPTY"
FLAG_PRODUCTION  = ""
#-----------------------------------------------------------------------------

# String type-checking compatibility
if sys.version_info[0] < 3:
    string_types = basestring
else:
    string_types = str

MAXINT = sys.maxsize

# Enumeration of datatypes accepted.
class SemEnumType (Enum):
    BOOLEAN = 1
    STRING  = 2
    NUMERIC = 3


# Exception raised for semantic analysis errors.
class SemError (Exception):
    pass

# Exception raised for type errors.
class SemTypeError (SemError):
    pass

# Exception raised for operator errors.
class SemOpError (SemError):
    pass

# Exception raised for symbol table errors.
class SemSymbolError (SemError):
    pass

# Exception raised for AST errors.
class SemASTError (SemError):
    pass

# Exception where no boolean type is defined.
class SemNoBoolTypeError (SemTypeError):
    pass

# Exception where no type list is defined.
class SemNoTypeListError (SemTypeError):
    pass

# Exception where two types are given the same name.
class SemTypeDuplicateError (SemTypeError):
    pass

# Type Mismatch Exception.
class SemTypeMismatchError (SemTypeError):
    def __init__ (self, strTypes):
        errormsg = "Unsupported operand type(s):"
        
        for strType in strTypes:
            errormsg += "\n\t" + strType
        
        errormsg += "."
          
        super ().__init__ (errormsg)

# Exception where type does not exist with given name.
class SemTypeNotFoundError (SemTypeError):
    def __init__ (self, type_string):
        error_msg = "Type {} is not defined.\n".format (type_string)
        
        super ().__init__ (error_msg)

# Exception where type does not exist with given enumeration.
class SemTypeEnumError (SemTypeError):
    def __init__ (self, type_string):
        error_msg = "Type {} is not defined. Choose from:\n".format (type_string)
                  
        for name, _ in SemEnumType.__members__.items ():
            error_msg += name + "\n"
                
        error_msg += "."
                 
        super ().__init__ (error_msg)         

# Exception where no operator list is defined.
class SemNoOpListError (SemOpError):
    pass

# Exception where an operator with a given symbol has already been defined.
class SemOpDuplicateError (SemOpError):
    pass

# Exception where operator does not exist with given symbol.
class SemOpNotFoundError (SemOpError):
    def __init__ (self, op_string):
        error_msg = "Operator {} is not defined.\n".format (op_string)
        
        super ().__init__ (error_msg)

# Exception where operator has a type list of the wrong size.        
class SemOpTypeListDisparityError (SemOpError):
    def __init__ (self, op_string):
        error_msg = "Operator {} has an incorrect type list size.\n".format (op_string)
        
        super ().__init__ (error_msg)

# Exception where a symbol has already been declared.
class SemDeclaredError (SemSymbolError):
    pass

# Exception where a symbol has not already been declared.
class SemNotDeclaredError (SemSymbolError):
    pass

# Exception whe

# Exception where the given AST is uninitialised.
class SemASTNoneError (SemASTError):
    pass
    
# Exception where the given AST is not a tuple.
class SemASTFormatError (SemASTError):
    pass
    
# Create a datatype.
class SemType:
    def __init__ (
      self, 
      strTypeName, 
      flag,
      enumType):
        self.typeName = strTypeName
        self.alias    = flag
        self.datatype = enumType
    
# There is only one boolean type.
SemType.BOOL_TYPE = SemType (None, None, SemEnumType ["BOOLEAN"].value)

class SemVar:    
    def __init__ (
      self,
      strValue,
      semType):
        self.value = strValue
        self.dtype = semType   
    
    @staticmethod
    def literal (strValue, semType):
        return SemVar (strValue, semType)
    
    @staticmethod
    def getInfo (args):
        values = []
        types  = []
        for arg in args:
            values.append (arg.value)
            types .append (arg.dtype.typeName)
        return (values, types)
        
    @staticmethod
    def checkTypes (numArgs, argTypes, types):
        valid  = (len (types) == 0)
        result = None
        
        for i in range (len (types)):
            check0 = True
            for j in range (numArgs):
                if (argTypes [j] != types [i] [j].typeName):
                    check0 = False
                break
            
            if (check0):
                valid  = True
                if (numArgs == len (argTypes)):
                    result = types [i] [-1]
                break
                
        return (valid, result)

    @staticmethod
    def customOperator (numArgs, formatString, args, types):
        argInfo  = SemVar.getInfo (args)
        argVals  = argInfo [0]
        argTypes = argInfo [1]
        
        check = SemVar.checkTypes (numArgs, argTypes, types)
        valid = check [0]
        rType = check [1]
        
        if (valid):
            result = formatString.format (*argVals)
            if (rType == None):
                return result
            else:
                return SemVar (result, rType)
        else:
            raise SemTypeMismatchError (argTypes)

dummyVar = SemVar (None, None)
SemVar.TYPE = type (dummyVar)

class SemOperator:
    def __init__ (
      self,
      strSymbol,
      argNum,
      typeList,
      formatString):
        if (len (typeList) == 0):
            length = 0
        else:        
            length = len (typeList [0])
        
        if ((length != argNum + 1) and (length != argNum)):
            raise SemOpTypeListDisparityError (strSymbol)

        self.symbol   = strSymbol        
        self.numArgs  = argNum
        self.typess   = typeList
        self.fString  = formatString

# Table of datatypes of type SemType.
class SemTypeTable:
    def __init__ (self):
        self.table = []
    
    def retrieve (self, strTypeName):
        if (strTypeName == None):
            return None
        for i in range (len (self.table)):
            if (
              (self.table [i].typeName == strTypeName) or
              (self.table [i].alias    == strTypeName)
            ):
                return self.table [i]
        raise SemTypeNotFoundError (strTypeName)
    
    def exists (self, strTypeName):
        try:
            self.retrieve (strTypeName)
            return True
        except SemTypeNotFoundError:
            return False
    
    def add (self, semType):
        if self.exists (semType.typeName):
            raise SemTypeDuplicateError
        else:
            self.table.append (semType)  

# Table of operators of type SemOperator.
class SemOperatorTable:
    def __init__ (self):
        self.table = []

    def retrieve (self, strSymbol):
        for i in range (len (self.table)):
            if (self.table [i].symbol == strSymbol):
                return self.table [i]
        raise SemOpNotFoundError (strSymbol)
    
    def exists (self, strSymbol):
        try:
            self.retrieve (strSymbol)
            return True
        except SemOpNotFoundError:
            return False
    
    def add (self, semOperator):
        if self.exists (semOperator.symbol):
            raise SemOpDuplicateError
        else:
            self.table.append (semOperator)  

# Table of symbols of type SemVar.
class SemSymbolTable:
    def __init__ (
      self, 
      symbols = []):
        self.table = symbols
        
    def retrieve (self, strVarName):
        for i in range (len (self.table)):
            if (self.table [i].value == strVarName):
                return self.table [i]
        raise SemNotDeclaredError
    
    def exists (self, strVarName):
        try:
            self.retrieve (strVarName)
            return True
        except SemNotDeclaredError:
            return False
    
    def add (self, strVarName, semType):
        if self.exists (strVarName):
            raise SemDeclaredError
        else:
            symbol = SemVar (strVarName, semType)
            self.table.append (symbol)


def stringType (o1):
    """Returns the input as a string""" 
    if (o1 == None):
        return ""
    elif (type (o1) == SemVar.TYPE):
        return o1.value
    else:
        return o1

# -----------------------------------------------------------------------------
#                               == SemAnalyser ==
#
# The semantic analyser for the given language.
# -----------------------------------------------------------------------------
class SemAnalyser:
    """Work in progress"""
    def __init__ (
      self, 
      booleans,
      datatypes, 
      operators):
        self.boolNames     = booleans
        self.typeTable     = datatypes
        self.operatorTable = operators
        self.symbolTable   = SemSymbolTable ()

    def interpret (self, ast, lineNo = 0):
        result = ""
                
        # End of programme.
        if (type (ast) != tuple):
            pass
        
        # Process statements one at a time.
        elif (ast [0] == FLAG_STATEMENT):
            if (len (ast) > 2):
                result = stringType (self.interpret (ast [1], lineNo))
                
                if (result != ""):
                    result += "\n"
                
                result += stringType (self.interpret (ast [2], lineNo + 1))
            else:
                result += stringType (self.interpret (ast [1], lineNo))

        # Variable declaration.
        elif (ast [0] == FLAG_DECLARATION):
            datatype = self.typeTable.retrieve (ast [1])            
            self.symbolTable.add (ast [2], datatype)
            result += ast [2] + " = "
            
            enumType = datatype.datatype
            
            if   (enumType == SemEnumType ["BOOLEAN"].value):
                result += "False"
            elif (enumType == SemEnumType ["STRING"].value):
                result += "\"\""
            else:
                result += "0"

        elif (ast [0] == FLAG_IDENTIFIER):
            variable = self.symbolTable.retrieve (ast [1])
            result = variable
            
        # Operation.
        elif (ast [0] == FLAG_OPERATOR):
            operator = self.operatorTable.retrieve (ast [1])
            
            argsIn  = ast [2:]
            argsOut = [None] * len (argsIn)
            
            for i in range (0, len (argsIn)):
                argIn  = argsIn [i]
                argOut = None
                
                if (type (argIn) == str):
                    argOut = self.symbolTable.retrieve (argIn)
                
                else:
                    argOut = self.interpret (argIn, lineNo)

                
                argsOut [i] = argOut
                
            result = SemVar.customOperator (operator.numArgs, operator.fString, argsOut, operator.typess)
                
        elif (ast [0] == FLAG_PRODUCTION):
            result = self.interpret (ast [1:])
        
        elif (ast [0] == FLAG_EMPTY):
            pass
            
        else:
            # Variable literal.
            try:
                dtype = self.typeTable.retrieve (ast [0])
                value = ast [1]
                
                if (dtype == SemType.BOOL_TYPE):
                    if (value == self.boolNames [0]):
                        value = "True"
                    else:
                        value = "False"
                
                result = SemVar.literal (value, dtype)
                
            except (IndexError, SemTypeNotFoundError):
                raise SemError ("The parser returned a bad result: " + str (ast [0]) + "\n Statement Number: " + repr(lineNo))
        
        return result
        
# -----------------------------------------------------------------------------
# get_caller_module_dict ()
#
# This function returns a dictionary containing all of the symbols defined within
# a caller further down the call stack.  This is used to get the environment
# associated with the sem () call if none was provided.
# -----------------------------------------------------------------------------
# Source:
# ply: yacc.py
#
# Copyright (C) 2001-2018
# David M. Beazley (Dabeaz LLC)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the David Beazley or Dabeaz LLC may be used to
#   endorse or promote products derived from this software without
#  specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------
def get_caller_module_dict (levels):
    f = sys._getframe (levels)
    sdict = f.f_globals.copy ()
    if f.f_globals != f.f_locals:
        sdict.update (f.f_locals)
    return sdict
    
# -----------------------------------------------------------------------------
# SemReflect ()
#
# This class represents information extracted for building a semantic analyser
# including start symbol, error function, tokens, precedence list, action 
# functions, etc.
# -----------------------------------------------------------------------------
class SemReflect (object):
    def __init__ (self, dict):
        self.sdict     = dict
        self.booleans  = None
        self.datatypes = None
        self.operators = None
        self.ast       = None

    # Get all of the basic information.
    def get_all (self):
        self.get_booleans  ()
        self.get_datatypes ()
        self.get_operators ()
        self.get_ast       ()

    # Validate all of the basic information.
    def validate_all (self):
        self.validate_operators ()
        self.validate_ast       ()

    # Get the boolean literal strings from the language.
    def get_booleans (self):
        lit_strings = self.sdict.get ("booleans", None)
        
        if not lit_strings:
            lit_strings = ("True", "False")
        
        self.booleans = lit_strings
  
    # Get all types from the language.
    def get_datatypes (self):        
        dt_strings = self.sdict.get ("datatypes", None)
        
        if not dt_strings:
            raise SemNoTypeListError ()
        
        dts = SemTypeTable ()
        
        boolFlag = True
        
        for (name, type_string, flag) in dt_strings:            
            enumType = None
            dt = None
            
            try:
                enumType = SemEnumType [type_string.upper ()].value
            except KeyError:
                raise SemTypeEnumError (type_string)
            
            try:
                if (enumType == SemEnumType ["BOOLEAN"].value):
                    assert boolFlag
                    boolFlag = False
                    SemType.BOOL_TYPE = SemType (name, flag, SemEnumType ["BOOLEAN"].value)
                    dt = SemType.BOOL_TYPE
                else:
                    dt = SemType (name, flag, enumType)
            
                dts.add (dt)
             
            except AssertionError:
                raise SemTypeDuplicateError ("You cannot have more than one STRING or BOOLEAN type.")
                 
        self.datatypes = dts
    
    # Convert a list of type strings to a list of types.
    def convert_types (self, typeStringss):
        semTypess = []
        
        # typeStrings is a tuple.
        for typeStrings in typeStringss:
            semTypes = []
            for typeString in typeStrings:
                semType = self.datatypes.retrieve (typeString)
                semTypes.append (semType)
            
            semTypess.append (tuple (semTypes))
        
        return semTypess
    
    # Get all operators from the language.    
    def get_operators (self):
        op_info = self.sdict.get ("operators", None)

        if not op_info:
            raise SemNoOpListError ()
        
        ops = SemOperatorTable ()
        
        for (symbol, arg_num, type_str_list, format_string) in op_info:
            type_list = self.convert_types (type_str_list)
            op = SemOperator (symbol, arg_num, type_list, format_string)  
            ops.add (op)
             
        self.operators = ops

    # Check that the operators' type lists make sense.
    def validate_operators (self):
        for operator in self.operators.table:
            opTypess = operator.typess
            length   = None
            
            if (len (opTypess) == 0):
                length = 0
            else:
                length = len (opTypess [0])
        
            for opTypes in opTypess:
                if (len (opTypes) == length):
                    for opType in opTypes:
                        self.datatypes.retrieve (opType.typeName)
                else:
                    raise SemOpTypeListDisparityError (symbol)
    
    # Get the ast from the parser.
    def get_ast (self):
        result = self.sdict.get ("ast", None)
        self.ast = result
    
    # Check that the ast is readable.    
    def validate_ast (self):
        if (type (self.ast) == None):
            raise SemASTNoneError
        elif (type (self.ast) != tuple):
            raise SemASTFormatError
            
        
# -----------------------------------------------------------------------------
# sem (module)
#
# Build a semantic analyser
# -----------------------------------------------------------------------------

def sem ():
    """Work in progress"""    
    sdict = get_caller_module_dict (2)

    # Collect semantic analyser information from the dictionary
    sinfo = SemReflect (sdict)
    sinfo.get_all ()
    sinfo.validate_all ()

    pythonCode = ""
    
    # Build the semantic analyser
    analyser = SemAnalyser (sinfo.booleans, sinfo.datatypes, sinfo.operators)
    
    pythonCode += analyser.interpret (sinfo.ast)
    
    return pythonCode
    

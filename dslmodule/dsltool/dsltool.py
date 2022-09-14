"""DSL Design Tool

This script prompts the user for a DSL specification file and an input 
script written in that DSL. It then generates a lexing, parsing, and 
semantic analysing script for that DSL and its input. The semantic
analysing script calls the other scripts, so can be immediately run as 
a compiler.

See Also
--------
dslSpecsTemplate
"""

#-----------------------------------------------------------------------------
#                     === User configurable parameters ===
#
# Change these to modify the default behavior of dsltool (if you wish)
#-----------------------------------------------------------------------------
DEF_T_LITERAL      = "True"
DEF_F_LITERAL      = "False"
DEF_BOOL_NAME      = "bool"
DEF_BOOL_FLAG      = "BOOL"
GCC_PATH           = "dslmodule.gcc"
#-----------------------------------------------------------------------------

# Important disclaimer for generated files.
disclaimer = (
"""# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ------------- This is an automatically generated file. -------------
# ---------------------------- Do NOT edit ---------------------------
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""
)

# Imports for generated files.
imports = (
"""import os
import sys

ROOT = os.path.abspath (
  os.path.join (
    os.path.dirname (__file__), 
    os.pardir
  )
)
sys.path.append (ROOT)"""
)

# Useful for type hinting.
from typing import List, Dict, Tuple
import sys

class FileFormatError (OSError):
    """Raised when the specification file is formatted incorrectly.
    """
    def __init__ (
      self, 
      lineNo   : int,
      expected : str,
      actual   : str
    ) -> None:
        """Creates a FileFormatError for the given specification file.
        
        Parameters
        ----------
        lineNo   : int
            The line of the specification file that is of the wrong
            format.
        expected : str
            The expected subportion of the line.
        actual   : str
            The actual subportion of the line.
        """
        
        errorMsg  = "Your input file is of the wrong format.\n"
        errorMsg += "    Line number     : {}.\n".format (lineNo)
        errorMsg += "    Expected string : {}.\n".format (expected)
        errorMsg += "    Actual line     : {}.\n".format (actual)
        
        super ().__init__ (errorMsg)


class FileInfo:
    """A helper class used to store information from a file and read it
    iteratively.
    
    Attributes
    ----------
    counter : int
        A line tracker for the file contents.
    content : [str]
        The contents of the file, split by line.
    
    Raises
    ------
    FileNotFoundError
        When the given file does not exist.
    """
    
    def __init__ (
      self, 
      infoFileName : str
    ) -> None:
        """Read all information from the file and store it in a list.
        
        Parameters
        ----------
        infoFileName : str
            The name of the file to read.
        """
        
        self.counter = 0
        
        infoFile = open (infoFileName, "r")
        self.content = infoFile.read ().split ("\n")
        
        infoFile.close ()
       
        
    def readLine (self) -> str:
        """Returns a new line of text from the file contents.
        
        If you want to read a previous line of text, just decrement the
        counter attribute.
        
        Returns
        -------
        str
            The next line of text.
        """
        
        nextLine = ""
        
        while (
          ((nextLine == "") or (nextLine [0] == "#")) and
          (self.counter < len (self.content))
        ):
            nextLine = self.content [self.counter].strip ()
            self.counter += 1
        
        if (self.counter < len (self.content)):
            return nextLine
            
        else:
            raise EOFError

    
    def readList (self) -> List [str]:
        """Returns a new line of tokens from the file contents.
        
        The tokens are strings within the line, separated by 
        whitespace.
        If you want to read a previous line of tokens, just decrement 
        the counter attribute.
        
        Returns
        -------
        List [str]
            The next line of tokens.
        """

        return self.readLine ().split ()
        

    def testInput (
      self,
      expected : str,
      actual   : str
    ) -> None:
        """Tests a given input from the file against its expectation.
    
        Parameters
        ----------
        expected : str
            The expected input from the file.
        actual   : str
            The actual input read from the file.
        """
        
        if (
            expected.upper () != actual [:len (expected)].upper ()
        ):
            raise FileFormatError (self.counter, expected, actual)
            

def lex (
  reserved       : Dict [str, str],
  tokenSpecs     : List [Tuple [str, str, bool, bool]], 
  inputFileName  : str, 
  outputFileName : str,
  gccFileName    : str
) -> None:
    """Generates a PLY lexing script for a specified DSL.
    
    Parameters
    ----------
    reserved       : Dict [str, str]
        A dictionary of reserved words, with their names as keys and 
        their symbol as values.
    tokenSpecs     : List [Tuple [str, str, bool, bool]]
        A list of tuples of form (token, spec, check, ignore), 
        specifying the token name, the regex of that token, whether 
        that token can contain a reserved word, and whether that token 
        should be ignored.
    inputFileName  : str
        The name of the file written in the DSL that you wish to lex.
    outputFileName : str
        The prefix of the name of the file that tokens will be written 
        to (to be followed by "_outlex").
    gccFileName    : str
        The prefix of the name of the lexing script (to be followed by 
        "_gcclex.py").
    """
    
    lexFileName    = "{}/{}_gcclex.py".format (GEN_PATH, gccFileName)
    lexOutFileName = "{}/{}_outlex"   .format (OUT_PATH, outputFileName) 
    
    lexFile = open (lexFileName, 'w')
    lexFile.write (disclaimer + "\n\n")
    lexFile.write (imports    + "\n\n")
    
    # Import the lexer.
    lexFile.write ("import {}.ply.lex as lex\n".format (GCC_PATH))
    lexFile.write ("\n")
    
    # List the tokens and their regexes. 
    tokenString   = "tokens = [\n"
    specString    = ""
    reserveString = "reserved = {\n"
    
    for (token, word) in reserved.items ():
        reserveString += "    \"{}\" : {},\n".format (token, word)
    
    for (token, spec, check, ignore) in tokenSpecs:
        if (ignore):
            specString += "def t_ignore_{} (t):\n    {}".format (token, spec)
            specString += "\n    pass\n\n"
        else:
            tokenString += "    \"" + token + "\",\n"
            specString  += "def t_{} (t):\n    {}\n".format (token, spec)
            
            if (check):
                specString += "    t.type = reserved.get (t.value, "
                specString += "\"{}\")\n".format (token)
            
            specString += "    return t\n\n"
            
    if (reserveString != "reserved = {\n"):
        reserveString = reserveString [:-2]
    reserveString += "\n}\n\n"
    
    if (tokenString != "tokens = [\n"):
        tokenString = tokenString [:-2]
    tokenString += "\n] + list (reserved.values ())\n\n"
    
    lexFile.write (reserveString)
    lexFile.write (tokenString)
    lexFile.write (specString)
    
    # Write the error function.
    lexFile.write ("def t_error (t):\n")
    lexFile.write ("    print (\"Unexpected character {}\"")
    lexFile.write (".format (t.value [0]))\n")
    lexFile.write ("    t.lexer.skip (1)\n")
    lexFile.write ("\n")
    
    # Write the end of file function.
    lexFile.write ("def t_eof (t):\n")
    lexFile.write ("    return None\n")
    lexFile.write ("\n")
    
    # Open the input file and send it to the lexer.
    lexFile.write (
      "inputFile = open (os.getcwd () + \"/{}\", \"r\")\n"
        .format (inputFileName)
    )    
    lexFile.write ("lexer = lex.lex ()\n")
    lexFile.write ("lexer.input (inputFile.read ())\n")
    lexFile.write ("inputFile.close ()\n")
    lexFile.write ("\n")
    
    # Output the tokens.
    lexFile.write (
      "outputFile = open (os.getcwd () + \"/{}\", \"w\")\n"
        .format (lexOutFileName)
    )
    lexFile.write ("hasNext = True\n")
    lexFile.write ("while hasNext:\n")
    lexFile.write ("    next = lexer.token ()\n")
    lexFile.write ("    if not next:\n")
    lexFile.write ("        hasNext = False\n")
    lexFile.write ("    else:\n")
    lexFile.write ("        outputFile.write (next.value + \"\\n\")\n")
    lexFile.write ("outputFile.close ()\n")
    lexFile.write ("\n")
    
    lexFile.close ()


def yacc (
  productions    : List [Tuple [
    str, 
    List [List [str]], 
    str, 
    List [int]
  ]], 
  inputFileName  : str, 
  outputFileName : str, 
  gccFileName    : str
) -> None:
    """Generates a PLY parsing script for a specified DSL.
    
    Parameters
    ----------
    productions    : List [Tuple [str, 
      List [List [str]], 
      str, 
      List [int]
    ]]
        A list of tuples of form (non_terminal, symbolss, flag, order), 
        specifying the starting symbol, a list of possible productions
        of that symbol (where each production is a list of symbols in 
        order), a string flag that will be relevant to the semantic 
        analyser (e.g. denoting an operator), and a list of the indexes 
        of each symbol you wish to be preserved in the AST. Symbols at
        the listed indexes are saved in the abstract syntax tree in the 
        order they appear. 
        For example:
               0              1       2    3      
          P EXPRESSION -> EXPRESSION plus TERM
          F OPERATOR
          I 2 1 3
          ...results in an AST entry of (OPERATOR, plus, p [1], p [3]).
    inputFileName  : str
        The name of the file written in the DSL that you wish to parse.
    outputFileName : str
        The prefix of the name of the file that the AST will be written 
        to (to be followed by "_outyacc").
    gccFileName    : str
        The prefix of the name of the parsing script (to be followed by
        "_gccyacc.py").
    """   
    
    lexFileName     = "{}.{}_gcclex"    .format (GEN_PATH, gccFileName)
    yaccFileName    = "{}/{}_gccyacc.py".format (GEN_PATH, gccFileName)
    yaccOutFileName = "{}/{}_outyacc"   .format (OUT_PATH, outputFileName)
    
    yaccFile = open (yaccFileName, 'w')
    yaccFile.write (disclaimer + "\n\n")
    yaccFile.write (imports    + "\n\n")
    
    # Import the parser.
    yaccFile.write ("import {}.ply.yacc as yacc\n".format (GCC_PATH))
    yaccFile.write ("\n")
    
    # Import the tokens from the lexer.
    yaccFile.write ("from {} import tokens\n".format (lexFileName))
    yaccFile.write ("\n")
    
    # Specify the user-given productions.
    for (non_terminal, symbolss, flag, order) in productions:
        funcName    = "p_" + non_terminal
        funcString  = "    \'\'\'" + non_terminal + " :"
        funcAction  = "    p [0] = ("
        
        for symbols in symbolss:
            if (symbols == []):
                funcName   += "_empty"
                funcString += " empty"
            else:
                for symbol in symbols:
                    funcName   += "_" + symbol
                    funcString += " " + symbol
            funcString += "\n    {}    |".format (" " * len (non_terminal))
        
        funcName = funcName [:50]
        
        if (funcString [-1] == "|"):
            funcString = funcString [:-(len (non_terminal) + 10)]
        funcString += "\'\'\'"

        if (flag != ""):
            funcAction += "\"" + flag + "\", "
        
        for index in order:
            funcAction += "p [{}]".format (index) + ", "
        
        if (funcAction == "    p [0] = ("):
            funcAction = "    pass"
        else:    
            funcAction = funcAction [:-2] + ")"
                
        if (funcAction [-7:] == "(p [1])"):
           funcAction = "    p [0] = p [1]"
        
        yaccFile.write ("def {} (p):\n".format(funcName))
        yaccFile.write (funcString + "\n")
        
        yaccFile.write (funcAction + "\n")
        
        yaccFile.write ("\n")
    
    # Specify the empty production.
    yaccFile.write ("def p_empty (p):\n")
    yaccFile.write ("    \'\'\'empty :\'\'\'\n")
    yaccFile.write ("    pass\n")
    yaccFile.write ("\n")
    
    # Specify the error handling.
    yaccFile.write ("def p_error (p):\n")
    yaccFile.write ("    if (p):\n")
    yaccFile.write ("        print (\"There is a syntax error in token {}\"")
    yaccFile.write (".format (p))\n")
    yaccFile.write ("\n")
    
    # Specify the function to print the AST out.
    yaccFile.write ("def writeAST (inputString, next, tabs):\n")
    yaccFile.write ("    outputString = \"\"\n")
    yaccFile.write ("    if (not next):\n")
    yaccFile.write ("        pass\n")
    yaccFile.write ("    elif (type (next) == tuple):\n")
    yaccFile.write ("        outputString += inputString + (\"  \" * tabs) ")
    yaccFile.write ("+ \"(\\n\"\n")
    yaccFile.write ("        for element in next:\n")
    yaccFile.write ("            outputString += writeAST (inputString, ")
    yaccFile.write ("element, tabs + 1)\n")
    yaccFile.write ("        outputString += inputString + (\"  \" * tabs) ")
    yaccFile.write ("+ \")\\n\"\n")
    yaccFile.write ("    else:\n")
    yaccFile.write ("        outputString += inputString + (\"  \" * tabs) ")
    yaccFile.write (" + next + \"\\n\"\n")
    yaccFile.write ("    return outputString\n")
    yaccFile.write ("\n")
    
    # Open the input file and send it to the parser.
    yaccFile.write (
      "inputFile = open (os.getcwd () + \"/{}\", \"r\")\n"
        .format (inputFileName)
    )    
    yaccFile.write ("parser = yacc.yacc ()\n")
    yaccFile.write ("ast = parser.parse (inputFile.read ())\n")
    yaccFile.write ("inputFile.close ()\n")
    yaccFile.write ("\n")
    
    # Output the AST.
    yaccFile.write (
      "outputFile = open (os.getcwd () + \"/{}\", \"w\")\n"
        .format (yaccOutFileName)
    )    
    yaccFile.write ("outputFile.write (writeAST (\"\", ast, 0))\n")
    yaccFile.write ("outputFile.close ()\n")
    yaccFile.write ("\n")
    
    yaccFile.close ()


def sem (
  datatypes      : List [Tuple [str, str]], 
  booleans       : Tuple [str, str, str, str],  
  operators      : List [Tuple [
    str, 
    int, 
    List [List [str]], 
    str
  ]], 
  outputFileName : str,
  gccFileName    : str
) -> None:
    """Generates a semantic analysis script for a specified DSL.
    
    The semantic analysis script calls the lexing and parsing scripts,
    so it can be run as a full compiler.
    
    Parameters
    ----------
    datatypes      : List [Tuple [str, str]]
        A list of accepted datatypes in the DSL of form (typeName, 
        typeAlias), specifying the symbol of that datatype and the flag
        used to denote its literals within the AST.
    booleans       : Tuple [str, str, str, str]
        A tuple corresponding to the boolean true and false literals, 
        the name of the boolean datatype, and the boolean literal flag
        used in the AST.
    operators      : List [Tuple [
      str, 
      int, 
      List [List [str]], 
      str
    ]]
        A list of accepted operators in the dsl of form (opSymbol, 
        numArgs, opTypess, opString), specifying the symbol of that 
        operator, the number of arguments it takes, a list of symbols
        of accepted datatypes for those arguments (and the return type
        if applicable), and a Python format string specifying what the 
        operator does.
        For example, the operator:
        ("add", 2, [[int, int, int], [float, float, float]], 
          "{0} + {1}")
        will map the AST ("add", ("int", "2"), ("int", "3")) to ("int", 
        "2 + 3").
    inputFileName  : str
        The name of the file written in the DSL that you wish to 
        analyse.
    outputFileName : str
        The prefix of the name of the file that corresponding Python
        script will be written to (to be followed by "_outsem.py").
    gccFileName    : str
        The prefix of the name of the semantic analysing script (to be
        followed by "_gccsem.py").
    """
    
    yaccFileName   = "{}.{}_gccyacc"  .format (GEN_PATH, gccFileName)
    semFileName    = "{}/{}_gccsem.py".format (GEN_PATH, gccFileName)
    semOutFileName = "{}/{}_outsem.py".format (OUT_PATH, outputFileName)
    
    semFile = open (semFileName, 'w')
    semFile.write (disclaimer + "\n\n")
    semFile.write (imports    + "\n\n")
    
    # Import the semantic analyser.
    semFile.write ("import {}.sem as sem\n".format (GCC_PATH))
    semFile.write ("\n")
    
    # Import the tokens from the lexer.
    semFile.write ("from {} import ast\n".format (yaccFileName))
    semFile.write ("\n")

    # Specify the user-given datatypes.
    dtsString = "datatypes = [\n"
    
    for (typeName, typeAlias) in datatypes:
        dtString  = "    (\"{}\", ".format (typeName)
        dtString += "\"{}\"),\n"   .format (typeAlias)
        
        dtsString += dtString

    if (dtsString != "datatypes = [\n"):
        dtsString = dtsString [:-2]
    dtsString += "\n]\n\n"
    
    semFile.write (dtsString)

    # Specify the user-given boolean variables.
    boolString  = "booleans = (\"{}\", ".format (booleans [0])
    boolString += "\"{}\", "            .format (booleans [1])
    boolString += "\"{}\", "            .format (booleans [2])
    boolString += "\"{}\")\n\n"         .format (booleans [3])
    
    semFile.write (boolString)
    
    # Specify the user-given operators.
    opsString = "operators = [\n"

    for (opSymbol, numArgs, opTypess, opString) in operators:
        typessString = "["
    
        for opTypes in opTypess:
            typesString = "("
            length = len (opTypes)
            
            if (length == 0):
                typesString = ""
            elif (length == 1):
                typesString += "\"" + opTypes [0] + "\",), "
            else:
                for opType in opTypes:
                    typesString += "\"" + opType + "\", "
                       
                typesString = typesString [:-2] + "), "
        
            typessString += typesString    

        if (typessString != "["):
            typessString = typessString [:-2]
        typessString += "]"
        
        # operString = "    ('{}', {}, {}, '{}'),\n"
        operString  = "    ('{}', ".format (opSymbol)
        operString += "{}, "       .format (numArgs)
        operString += "{}, "       .format (typessString)
        operString += "'{}'),\n"   .format (opString)
        
        opsString += operString

    if (opsString != "operators = [\n"):
        opsString = opsString [:-2]
    opsString += "\n]\n\n"
    
    semFile.write (opsString)
    
    # Call the semantic analyser.
    semFile.write ("analyser = sem.sem ()\n")
    semFile.write ("\n")
    
    # Run the semantic analyser.
    semFile.write ("pythonCode = analyser.analyse (ast)")
    semFile.write ("\n")
    
    # Output the pythonCode.
    semFile.write (
      "outputFile = open (os.getcwd () + \"/{}\", \"w\")\n"
        .format (semOutFileName)
    )    
    semFile.write ("outputFile.write (pythonCode)\n")
    semFile.write ("outputFile.close ()\n")
    semFile.write ("\n")
    
    semFile.close ()


def readReserved (
  fi : FileInfo
) -> Dict [str, str]:
    """Reads a specification file and builds a dictionary of reserved 
    words.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.
        
    Returns
    -------
    Dict [str, str]
        The dictionary of reserved words in the DSL.

    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.
        
    See Also
    --------
    lex
    """
    
    fi.testInput ("RESERVED", fi.readLine ())
    
    reserved   = {}
    nextList   = fi.readList ()
    
    while (nextList [0] [0] != "-"):
    
        if (len (nextList) != 3):
            raise FileFormatError (
              fi.counter,
              "R ... ...",
              " ".join (nextList)
            )
        
        fi.testInput ("R", nextList [0])
            
        name = nextList [1]
        word = repr (nextList [2])
        reserved.update ({name : word})

        nextList = fi.readList ()
    
    return reserved


def readTokens (
  fi : FileInfo
) -> List [Tuple [str, str, bool, bool]]:
    """Reads a specification file and builds a list of tokens and their 
    specifications.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.

    Returns
    -------
    List [Tuple [str, str, bool, bool]]
        The list of tokens and specifications in the DSL.

    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.
        
    See Also
    --------
    lex
    """
     
    fi.testInput ("TOKENS", fi.readLine ())
    
    tokenSpecs = []
    nextList   = fi.readList ()
        
    while (nextList [0] [0] != "-"):
    
        if (len (nextList) != 3):
            raise FileFormatError (
              fi.counter,
              "... ... ...",
              " ".join (nextList)
            )
        
        header = nextList [0].upper ()    
        token  = nextList [1]
        regex  = repr (nextList [2])
        check  = False
        ignore = False
        
        if (header == "C"):
            check = True
        elif (header == "I"):
            ignore = True                       
        else:
            fi.testInput ("T", header)
        
        tokenSpecs.append ((token, regex, check, ignore))
            
        nextList = fi.readList ()
    
    return tokenSpecs
    
    
def readProductions (
  fi : FileInfo
) -> List [Tuple [
  str, 
  List [List [str]], 
  str, 
  List [int]
]]:
    """Reads a specification file and builds a list of productions and 
    production rules for an AST.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.

    Returns
    -------
    List [Tuple [str, 
      List [List [str]], 
      str, 
      List [int]
    ]]
        The list of production rules of the DSL.
        
    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.
        
    See Also
    --------
    yacc        
    """
    
    fi.testInput ("PRODUCTIONS", fi.readLine ())
    
    productions = []
    nextList    = fi.readList ()

    while (nextList [0] [0] != "-"):
        if (len (nextList) < 3):
            raise FileFormatError (
              fi.counter,
              "P ... -> (...)*",
              " ".join (nextList)
            )

        fi.testInput ("P", nextList [0])
        
        non_terminal = nextList [1]
        allProds = []
        nextProd = []
        
        fi.testInput ("->", nextList [2])
        
        for i in range (3, len (nextList)):
            symbol = nextList [i]
            if (symbol == "|"):
                allProds.append (nextProd)
                nextProd = []
            else:
                nextProd.append (symbol)
        allProds.append (nextProd)
        
        nextList = fi.readList ()
        fi.testInput ("F", nextList [0])
        
        flag = ""
        
        try:
            flag = nextList [1]
        except IndexError:
            pass
        
        nextList = fi.readList ()
        fi.testInput ("I", nextList [0])
        
        indices = nextList [1:] 
            
        if (allProds == [[]]):
            indices.append (1)
            
        productions.append ((non_terminal, allProds, flag, indices))
    
        nextList = fi.readList ()
        
    return productions


def readDatatypes (
  fi : FileInfo
) -> Tuple [str, str]:
    """Reads a specification file and builds a list of datatypes.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.
    
    Returns
    -------
    Tuple [str, str]
        The list of datatypes used in that DSL.

    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.

    See Also
    --------
    sem        
    """
    
    fi.testInput ("DATATYPES", fi.readLine ())
    
    datatypes = []
    nextList  = fi.readList ()

    while (nextList [0] [0] != "-"):
        # Read in the type name.
        fi.testInput ("N", nextList [0])
        typeName = nextList [1]
        
        # Read in the literal flag.
        nextList = fi.readList ()
        fi.testInput ("L", nextList [0])
        typeAlias = nextList [1]
            
        datatypes.append ((typeName, typeAlias))
        
        nextList  = fi.readList ()
        
    return datatypes   


def readBooleans (
  fi : FileInfo
) -> Tuple [str, str, str, str]:
    """Reads a specification file to determine boolean specifications.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.

    Return
    ------
    Tuple [str, str, str, str]
        The boolean specifications of the DSL.

    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.

    See Also
    --------
    sem                
    """
    
    fi.testInput ("BOOLEANS", fi.readLine ())    
    
    # Set the default values.
    trueVar     = DEF_T_LITERAL
    falseVar    = DEF_F_LITERAL
    boolName    = DEF_BOOL_NAME
    boolLiteral = DEF_BOOL_FLAG
    
    # Read in the true literal.
    nextList = fi.readList ()
    if (len (nextList) < 2):
        raise FileFormatError (
          fi.counter,
          "T ... ",
          " ".join (nextList)
        )
    fi.testInput ("T", nextList [0])
    if (nextList [1] != "default"):
        trueVar     = nextList [1]
    
    # Read in the false literal.
    nextList = fi.readList ()
    if (len (nextList) < 2):
        raise FileFormatError (
          fi.counter,
          "F ... ",
          " ".join (nextList)
        )
    fi.testInput ("F", nextList [0])
    if (nextList [1] != "default"):
        falseVar    = nextList [1]

    # Read in the boolean datatype name.
    nextList = fi.readList ()        
    if (len (nextList) < 2):
        raise FileFormatError (
          fi.counter,
          "N ... ",
          " ".join (nextList)
        )
    fi.testInput ("n", nextList [0])
    if (nextList [1] != "default"):
        boolName    = nextList [1]

    # Read in the boolean literal flag.
    nextList = fi.readList ()        
    if (len (nextList) < 2):
        raise FileFormatError (
          fi.counter,
          "L ... ",
          " ".join (nextList)
        )
    fi.testInput ("L", nextList [0])
    if (nextList [1] != "default"):
        boolLiteral = nextList [1]
    
    fi.testInput ("-", fi.readLine ())    
    return (trueVar, falseVar, boolName, boolLiteral)
    
    
def readOperators (
  fi : FileInfo
) -> List [Tuple [
  str, 
  int, 
  List [List [str]], 
  str
]]:
    """Reads a specification file to determine operators and their 
    execution instructions.
    
    Parameters
    ----------
    fi            : FileInfo
        The extracted information from the DSL specification file.

    Return
    ------
    List [Tuple [
      str, 
      int, 
      List [List [str]], 
      str
    ]]
        The operators and their execution instructions of the DSL.

    Raises
    ------
    FileFormatError
        When the specification file is formatted incorrectly.

    See Also
    --------
    sem                
    """
    
    fi.testInput ("OPERATORS", fi.readLine ())
    
    operators = []
    nextList  = fi.readList ()

    while (nextList [0] [0] != "-"):
        # Read in operator symbol.
        fi.testInput ("S", nextList [0])
        opSymbol = repr (nextList [1]) [1:-1]

        # Read in number of arguments.       
        nextList = fi.readList ()
        fi.testInput ("A", nextList [0])   
        numArgs = int (nextList [1])
            
        # Read in datatypes.
        nextList = fi.readList ()
        fi.testInput ("T", nextList [0])
        opTypess  = []
            
        while (nextList [0].upper () == "T"):
            nextTypes = nextList [1:]
            
            if (len (nextTypes) + 1 < numArgs):
                raise FileFormatError (
                  fi.counter,
                  "T" + (" ..." * numArgs) + " (...)", 
                  " ".join (nextList)
                )

            opTypess.append (tuple (nextTypes))
            nextList = fi.readList ()
            
        # Read in specification string.
        fi.testInput ("F", nextList [0])
        opString = repr (" ".join (nextList [1:])) [1:-1]
       
        operators.append ((opSymbol, numArgs, opTypess, opString))
               
        nextList = fi.readList ()
        
    return operators


def build (
  infoFileName  : str,
  inputFileName : str,
  gccFileName   : str,
  outFileName   : str
) -> None:
    """Reads a specification file and builds a set of compiling scripts
    based on it.
    
    The generated scripts are for lexing, parsing, and semantic 
    analysis.
    
    Parameters
    ----------
    infoFileName  : str
        The name of the DSL specification file.
    inputFileName : str
        The name of the file written in the DSL that the user wishes
        to transpile to Python.
    gccFileName   : str
        The prefix of the names of the output compiling scripts (to be 
        followed by "_gcclex.py", "_gccyacc.py", and "_gccsem.py"
        respectively.
    outFileName   : str
        The prefix of the names of the output files of those scripts
        (to be followed by "_outlex", "_outyacc", and "_outsem.py"
        respectively.
        
    Raises
    ------
    FileNotFoundError
        When the specification file does not exist.
    FileFormatError
        When the specification file is formatted incorrectly.
    """
    
    fi          = FileInfo (infoFileName)
    
    # Specification document heading.
    fi.testInput ("LANGUAGE SPECIFICATION DOCUMENT", fi.readLine ())
    fi.testInput ("-", fi.readLine ())
    
    # Read lexer specifications.
    reserved    = readReserved    (fi)    
    tokens      = readTokens      (fi)
    lex (reserved, tokens, inputFileName, outFileName, gccFileName)
    
    # Read parser specifications.
    productions = readProductions (fi)    
    yacc (productions, inputFileName, outFileName, gccFileName)
    
    # Read sematic analyser specifications.
    datatypes   = readDatatypes   (fi)
    booleans    = readBooleans    (fi)
    operators   = readOperators   (fi)
    sem (datatypes, booleans, operators, outFileName, gccFileName)


def main (
  spec : str        = None
) -> None:
    """Prompts the user for the names of input and output files they want
    to build a compiler matching.
    
    If the input given is blank, default file names are used instead.
    """
    
    if spec:
        infoFileName   = spec
        print ("DSL specification file at {} is loaded.\n".format (spec))
    
    else:
        prompt = input (
          "What is the name of the DSL specification file?\n"
        ).strip ()
        infoFileName = prompt
        
    prompt = input (
      "What is the name of the DSL coded file?\n"
    ).strip ()
    inputFileName = prompt

    prompt = input (
      "What would you like to name the compiler files?\n"
    ).strip ()
    gccFileName = prompt

    prompt = input (
      "What would you like to name the output files?\n"
    ).strip ()    
    outputFileName = prompt
        
    build (infoFileName, inputFileName, gccFileName, outputFileName)

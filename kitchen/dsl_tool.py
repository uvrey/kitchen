"""
DSL Design Tool

This script prompts the user for a DSL specification file and an input 
script written in that DSL. It then generates a lexing, parsing, and 
semantic analysing script for that DSL and its input. The semantic
analysing script calls the other scripts, so can be immediately run as 
a compiler.

See Also
--------
dslSpecsTemplate
"""

from kitchen import SUCCESS

# Configurable variables.
defInfoFileName = "dslSpecs"
defInFileName   = "dslInput"
defGccFileName  = "dsl"
defOutFileName  = "dsl"
gccPath         = "gcc"

# Important disclaimer for generated files.
disclaimer  = "# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
disclaimer += "# ------------------- This is an automatically generated file. -------------------\n"
disclaimer += "# -------------------------------- Do NOT edit. ----------------------------------\n"
disclaimer += "# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"


class FileFormatError (OSError):
    """
    Raised when the specification file is formatted incorrectly.
    """
    def __init__ (
      self, 
      lineNo,
      expected,
      actual):
        """
        Creates a FileFormatError for the given specification file.
        
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
    """
    A helper class used to store information from a file and read it
    iteratively.
    
    ...
    
    Attributes
    ----------
    counter : int
        A line tracker for the file contents.
    content : [str]
        The contents of the file, split by line.
    
    Methods
    -------
    readLine  ()
        Returns a new line of text from the file contents.
    readList  ()
        Returns a new line of tokens from the file contents.
    testInput (expected, actual)
        Tests a given input from the file against its expectation.
    
    Raises
    ------
    FileNotFoundError
        When the given file does not exist.
    """
    
    def __init__ (self, infoFileName):
        """
        Read all information from the file and store it in a list.
        
        Parameters
        ----------
        infoFileName : str
            The name of the file to read.
        """
        
        self.counter = 0
        
        infoFile = open (infoFileName, "r")
        self.content = infoFile.read ().split ("\n")
        
        infoFile.close ()
        
    def readLine (self):
        """
        Returns a new line of text from the file contents.
        
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
    
    def readList (self):
        """
        Returns a new line of tokens from the file contents.
        
        The tokens are strings within the line, separated by 
        whitespace.
        If you want to read a previous line of tokens, just decrement 
        the counter attribute.
        
        Returns
        -------
        [str]
            The next line of tokens.
        """

        return self.readLine ().split ()
        

    def testInput (
      self,
      expected,
      actual):
        """
        Tests a given input from the file against its expectation.
    
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
  tokenSpecs, 
  reserved,
  inputFileName, 
  outputFileName,
  gccFileName):
    """
    Generates a PLY lexing script for a specified DSL.
    
    Parameters
    ----------
    tokenSpecs     : [(str, str, bool, bool)]
        A list of tuples of form (token, spec, check, ignore), 
        specifying the token name, the regex of that token, whether 
        that token can contain a reserved word, and whether that token 
        should be ignored.
    reserved       : dict
        A dictionary of reserved words, with their names as keys and 
        their symbol as values.
    inputFileName  : str
        The name of the file written in the DSL that you wish to lex.
    outputFileName : str
        The prefix of the name of the file that tokens will be written 
        to (to be followed by "_outlex").
    gccFileName    : str
        The prefix of the name of the lexing script (to be followed by 
        "_gcclex.py").
    """
    
    lexFileName    = gccFileName    + "_gcclex.py"
    lexOutFileName = outputFileName + "_outlex"
    
    lexFile = open (lexFileName, 'w')
    lexFile.write (disclaimer + "\n")
    
    # Import the lexer.
    lexFile.write ("import {}.ply.lex as lex\n".format (gccPath))
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
    lexFile.write ("inputFile = open (\"{}\", ".format (inputFileName))
    lexFile.write ("\"r\")\n")
    lexFile.write ("lexer = lex.lex ()\n")
    lexFile.write ("lexer.input (inputFile.read ())\n")
    lexFile.write ("inputFile.close ()\n")
    lexFile.write ("\n")
    
    # Output the tokens.
    lexFile.write ("outputFile = open (\"{}\", ".format (lexOutFileName))
    lexFile.write ("\"w\")\n")
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
  productions, 
  inputFileName, 
  outputFileName, 
  gccFileName):
    """
    Generates a PLY parsing script for a specified DSL.
    
    Parameters
    ----------
    productions     : [(str, [[str]], str, [int])]
        A list of tuples of form (non_terminal, symbolss, flag, order), 
        specifying the starting symbol, a list of possible productions
        of that symbol (where each production is a list of symbols in 
        order), token name, the regex of that token, a string flag that
        will be relevant to the semantic analyser (e.g. denoting an 
        operator), and a list of the indexes (numbered from 1, 0
        refers to the starting symbol) of each symbol you wish to be
        preserved in the AST.
        For example, in the production:
        ("START", [["CARRY", "ON"], ["or", "end"]], "flag", [1, 2]),
        the resulting AST will be:
        ("flag", "CARRY", "ON") or ("flag", "or", "end").
    inputFileName  : str
        The name of the file written in the DSL that you wish to parse.
    outputFileName : str
        The prefix of the name of the file that the AST will be written 
        to (to be followed by "_outyacc").
    gccFileName    : str
        The prefix of the name of the parsing script (to be followed by
        "_gccyacc.py").
    """   
    
    lexFileName     = gccFileName    + "_gcclex"
    yaccFileName    = gccFileName    + "_gccyacc.py"
    yaccOutFileName = outputFileName + "_outyacc"
    
    yaccFile = open (yaccFileName, 'w')
    yaccFile.write (disclaimer + "\n")
    
    # Import the parser.
    yaccFile.write ("import {}.ply.yacc as yacc\n".format (gccPath))
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
    yaccFile.write ("inputFile = open (\"{}\", ".format (inputFileName))
    yaccFile.write ("\"r\")\n")
    yaccFile.write ("parser = yacc.yacc ()\n")
    yaccFile.write ("ast = parser.parse (inputFile.read ())\n")
    yaccFile.write ("inputFile.close ()\n")
    yaccFile.write ("\n")
    
    # Output the AST.
    yaccFile.write ("outputFile = open (\"{}\", ".format (yaccOutFileName))
    yaccFile.write ("\"w\")\n")
    yaccFile.write ("outputFile.write (writeAST (\"\", ast, 0))\n")
    yaccFile.write ("outputFile.close ()\n")
    yaccFile.write ("\n")
    
    yaccFile.close ()

def sem (
  booleans, 
  datatypes, 
  operators, 
  outputFileName,
  gccFileName):
    """
    Generates a semantic analysis script for a specified DSL.
    
    The semantic analysis script calls the lexing and parsing scripts,
    so it can be run as a full compiler.
    
    Parameters
    ----------
    booleans  : (str, str)
        The string literals corresponding to the boolean values (True,
        False) in the DSL.
    datatypes : [(str, str, str)]
        A list of accepted datatypes in the DSL of form (typeName, 
        typeAlias, typeString), specifying the symbol of that datatype,
        the flag used to denote its literals within the AST, and its
        corresponding supported type string (only "BOOLEAN", "STRING",
        or "NUMERIC" are accepted).
    operators : [(str, int, [[str]], str)]
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
    
    yaccFileName   = gccFileName    + "_gccyacc"
    semFileName    = gccFileName    + "_gccsem.py"
    semOutFileName = outputFileName + "_outsem.py"
    
    semFile = open (semFileName, 'w')
    semFile.write (disclaimer + "\n")
    
    # Import the semantic analyser.
    semFile.write ("import {}.sem as sem\n".format (gccPath))
    semFile.write ("\n")
    
    # Import the tokens from the lexer.
    semFile.write ("from {} import ast\n".format (yaccFileName))
    semFile.write ("\n")

    # Specify the user-given boolean variables.
    # boolString = booleans = (\"{}\", \"{}\")\n"
    boolString  = "booleans = (\"{}\", ".format (booleans [0])
    boolString += "\"{}\")\n"           .format (booleans [1])
    semFile.write (boolString)
    semFile.write ("\n")
        
    # Specify the user-given datatypes.
    dtsString = "datatypes = [\n"
    
    for (typeName, typeAlias, typeString) in datatypes:
        # dtString = "    (\"{}\", \"{}\", \"{}\"),\n"
        dtString  = "    (\"{}\", ".format (typeName)
        dtString += "\"{}\", "     .format (typeString)
        dtString += "\"{}\"),\n"   .format (typeAlias)
        
        dtsString += dtString

    if (dtsString != "datatypes = [\n"):
        dtsString = dtsString [:-2]
    dtsString += "\n]\n\n"
    
    semFile.write (dtsString)
    
    # Specify the user-given operators.
    opsString = "operators = [\n"

    for (opSymbol, numArgs, opTypess, opString) in operators:
        typessString = "["
    
        for opTypes in opTypess:
            typesString = "("
        
            for opType in opTypes:
                typesString += "\"" + opType + "\", "
        
            if (typesString != "("):
                typesString = typesString [:-1] + "), "
            else:
                typesString = ""
        
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
    semFile.write ("pythonCode = sem.sem ()\n")
    semFile.write ("\n")
    
    # Output the pythonCode.
    semFile.write ("outputFile = open (\"{}\", \"w\")\n".format (semOutFileName))
    semFile.write ("outputFile.write (pythonCode)\n")
    semFile.write ("outputFile.close ()\n")
    semFile.write ("\n")
    
    semFile.close ()


def build (
  infoFileName,
  inputFileName,
  gccFileName,
  outFileName):
    """
    Reads a specification file and builds a set of compiling scripts
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
    tokenSpecs  = []
    reserved    = {}
    productions = []
    nextLine    = ""
    nextList    = []
    
    # Specification document heading.
    fi.testInput ("LANGUAGE SPECIFICATION DOCUMENT", fi.readLine ())
    fi.testInput ("-", fi.readLine ())
        
    # Read in tokens.  
    fi.testInput ("TOKENS", fi.readLine ())
    
    nextList = fi.readList ()
        
    while (nextList [0] [0] != "-"):
        if (len (nextList) != 3):
            raise FileFormatError (
              fi.counter,
              "... ... ...",
              " ".join (nextList)
            )
            
        token  = nextList [1].strip ()
        spec   = repr (nextList [2].strip ())
        check  = False
        ignore = False
        
        if (nextList [0].upper () == "R"):
            reserved.update ({token : spec})
        else:
            if (nextList [0].upper () == "C"):
                check = True
            elif (nextList [0].upper () == "I"):
                ignore = True                       
            else:
                fi.testInput ("T", nextList [0])
        
            tokenSpecs.append ((token, spec, check, ignore))
            
        nextList = fi.readList ()

    lex (tokenSpecs, reserved, inputFileName, outFileName, gccFileName)
        
    # Read in CFG.
    fi.testInput ("PRODUCTIONS", fi.readLine ())
    
    nextList = fi.readList ()
         
    while (nextList [0] [0] != "-"):
        fi.testInput ("P", nextList [0])
        
        terminal = nextList [1]
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
            
        productions.append ((terminal, allProds, flag, indices))
    
        nextList = fi.readList ()

    yacc (productions, inputFileName, outFileName, gccFileName)

    # Read in boolean literals.
    fi.testInput ("BOOLEANS", fi.readLine ())
    
    nextList = fi.readList ()
    fi.testInput ("T", nextList [0])
    trueVar = nextList [1]
    
    nextList = fi.readList ()
    fi.testInput ("F", nextList [0])
    falseVar = nextList [1]
    
    booleans = (trueVar, falseVar)
    
    fi.testInput ("-", fi.readLine ())
            
    # Read in datatypes.
    fi.testInput ("DATATYPES", fi.readLine ())
    datatypes = []
    
    nextList  = fi.readList ()
    
    while (nextList [0] [0] != "-"):
        fi.testInput ("N", nextList [0])
        typeName = nextList [1]
    
        nextList = fi.readList ()
        fi.testInput ("L", nextList [0])
        typeAlias = nextList [1]
            
        nextList = fi.readList ()
        fi.testInput ("T", nextList [0])
        typeString = nextList [1]
        
        datatypes.append ((typeName, typeAlias, typeString))
        
        nextList  = fi.readList ()
    
    # Read in operators.
    fi.testInput ("OPERATORS", fi.readLine ())
    operators = []
    
    nextList = fi.readList ()

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
        
    sem (booleans, datatypes, operators, outFileName, gccFileName)

def main ():
    """
    Prompts the user for the names of input and output files they want
    to build a compiler matching.
    
    If the input given is blank, default file names are used instead.
    """

    infoFileName   = defInfoFileName
    inputFileName  = defInFileName
    gccFileName    = defGccFileName
    outputFileName = defOutFileName

    defaults = input ("Use defaults (Y/N) :\n").strip ()
 
    if (defaults.upper () == "N"):
        prompt = input (
          "What is the name of the DSL specification file?\n"
        ).strip ()
        
        if (prompt != ""): 
            infoFileName = prompt
    
        prompt = input (
          "What is the name of the DSL coded file?\n"
        ).strip ()
        
        if (prompt != ""): 
            inputFileName = prompt
        
        prompt = input (
          "What would you like to name the compiler files?\n"
        ).strip ()
        
        if (prompt != ""): 
            gccFileName = prompt
        
        prompt = input (
          "What would you like to name the output files?\n"
        ).strip ()
        
        if (prompt != ""): 
            outputFileName = prompt
        
    build (infoFileName, inputFileName, gccFileName, outputFileName)
    return SUCCESS
    
if (__name__ == "__main__"):
    main ()
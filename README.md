#:woman_cook: Kitchen: A Compiler Visualiser and Teaching Tool
Kitchen is a tool that supports the learning and teaching of Compiler Theory.

##:hammer: Domain-Specific Language Tool and General-Compiler Compiler
Kitchen helps educators design and use Domain-Specific Languages in assignments, and allows students to verify the correctness of the compilers they build in class. 

##:eyes:Visualisation Engine
Kitchen's Visualisation Engine calculates, visualises and explains five algorithms in Compiler
Theory:

- First Set
- Follow Set 
- Parsing Table
- LL(1) Parse Tree
- Simplified Semantic Analysis

Kitchen is designed to perform each of these algorithms given
an arbitrary, but somewhat constrained Context-Free Grammar
(CFG) as input. 

Visualisations are created as .mp4 videos, and can be found inside the
`.\media\videos\<resolution>` directory, where `<resolution>` is 
`1080p60`, `720p30` or `480p15`. 

Sample CFGs are available in the `.\samples\example_cfgs` folder.

##:green_circle: Quick Start
Kitchen requires one argument, which is the path to a Context-Free Grammar (CFG) file. This CFG contains the structure of some small language- here's an example:
```
S -> a B D h
B -> b | #
D -> d | #
```
*Source:* `".\samples\example_cfgs\cfg_12.txt"`

Using this CFG unlocks all of the Visulisation Engine's functionality, except for visualising Semantic Analysis. To do this, and also to use the DSL Tool, a Language Specification file is needed. You can find an example at `".\samples\test_spec.txt"`.

Once all the dependencies are installed (See *Installation*), Kitchen may be run as follows:

### Using only a Context-Free Grammar
**When to use:**
- You are testing out the app for the first time
- You just want to generate simple parsing videos, which skip Lexical Analysis (so there is no mapping of an input string to a token stream).
```
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg.txt" 
python3 -m kitchen run
```

### Also using a Language Specification
**When to use:**
- You want to parse actual input; where the strings you type in are mapped to tokens.
- You just want to visualise Semantic Analysis.
- You want to use the Domain-Specific Language Design tool. 
```
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg_id_language.txt" ".\samples\test_spec.txt"
python3 -m kitchen run
```

### Only starting the DSL Tool
Once a Language Specification has been initialised, only the DSL tool may started using the following command:
```
python3 -m kitchen dsl-tool
```

##:black_circle: Installation
These instructions assume that a Windows system is used. Kitchen is compatible with Linux, but issues installing LaTeX for Manim may be experienced. This is because some style packages may be absent. It is recommended to install the complete LaTeX suite in this case, or install [MikTeX for Linux](https://miktex.org/howto/install-miktex-unx) to manage this.

For detailed instructions to install Manim for on your operating system, please see below:
https://docs.manim.community/en/v0.3.0/installation.html

In brief, to begin using Kitchen, you will need to install several packages.

### Setting up 
**Requirements:**
- Python3
- Pip
- Chocolatey: https://chocolatey.org/install

**0. Make sure your package managers are up to date.**

In this installation, we will use Pip and Chocolatey. Ensure Pip is upgraded by running:
```python -m pip install -–upgrade pip```

**1. Install `manim` and other dependencies; remembering to use Powershell as admin.**
  ```choco install manimce```  
  Alternatively:   ```python3 -m pip install manim```
  
  If manim is not detected, use the following command within your virtual environment to set it up:
  ```python3 -m pip install manim```
  
  Some packages may require a reboot, so please do this :)
  
**2. Install LaTeX**
  MikTeX is recommended: https://miktex.org/m.DOWNload
  It will also assist with installing extra style packages when you run the code for the first time.
  
### Getting going
**1. Set up virtual environment:**
Since Kitchen requires several dependencies, it is recommended to make use of a 
virtual environment. 

To do this, navigate to the ComVizTT directory and create a virtual environment, then activate it. Detailed instructions are provided here:
https://mothergeo-py.readthedocs.io/en/latest/development/how-to/venv-win.html

```python3 -m virtualenv <env_name>\```

Activate this environment.
```.\venv\Scripts\activate```

Then, install the requirements:
```python3 -m pip install -r requirements.txt```

**2. Exporting parse trees**
Exporting the parse trees to PNG files requires an additonal package called `graphviz`.

From an elevated command prompt, install `graphviz` via `choco install graphviz`

The parse trees will be exported to the `.\samples\tree_pngs` directory.
 
 **3. Using narration**
 The generation of narration is enabled by the gTTS library. Make sure you are
 connected to the internet when doing so, otherwise the video will not generate.

 For offline rendering, it is recommended to turn narration off. This is achieved
 by inserting the following command at Kitchen's prompt.

 `Input: \c -n n`

##:purple_circle: Compiling and Executing
  ### Running Kitchen
  To run the program, the Context-Free Grammar file needs to be specified.
  
  use the following command to do this (A CFG is provided for your 
  convience, but you can replace the last argument with your choice of path).
  
```
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg_12.txt" 
```

  If you would like to also include a language specification, please include it
  as an additional path. For example:

```
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg_12.txt" ".\samples\test_spec.txt"
```
  **Please Note:** This file needs to be supplied to use the DSL tool and General-Compiler Compiler.
  
  Now, to run the application, use:

```
python3 -m kitchen run
```

  From here, `\m` will display the menu, and `\tut' will take you through
  a quick tutorial.

  For your convenience, here is this menu. It contains all the commands which
  Kitchen supports :)

```
Use these commands to see what files are loaded
 and adjust the animation settings.
| Detail                         | Command    | Shortcut   |
|:-------------------------------|:-----------|:-----------|
| Exit app                       | \quit      | \q         |
| Configure animation settings   | \config    | \c         |
| Display Context-Free Grammar   | \show cfg  | \cfg       |
| Display Language Specification | \show spec | \spec      |

Use this command to open the domain-specific language design tool.
| Detail        | Command   | Shortcut   |
|:--------------|:----------|:-----------|
| Open DSL tool | \dsl tool | \dsl       |

Use these commands to check your calculations
| Detail                          | Command          | Shortcut   |
|:--------------------------------|:-----------------|:-----------|
| Display First Set               | \show first      | \fs        |
| Display Follow Set              | \show follow     | \fw        |
| Display Parse Table             | \show parsetable | \pt        |
| Display LL(1) Parse Tree        | \ll1 <input>     | <input>    |
| Export LL(1) Parse Tree as .png | \tree <input>    |            |
| Display Symbol Table            | \sem <input>     |            |

Use these commands to generate an explanation video.
| Detail                                  | Command         | Shortcut   |
|:----------------------------------------|:----------------|:-----------|
| Visualise Parsing Table calculation     | \vis parsetable | \vpt       |
| Visualise First Set calculation         | \vis first      | \vfs       |
| Visualise Follow Set calculation        | \vis follow     | \vfw       |
| Visualise LL(1) Parse Tree construction | \ll1 v <input>  | \v <input> |
| Visualise Semantic Analysis             | \vsem <input>   |            |
```
### Running the DSL Tool Independently
Kitchen allows the DSL Tool to be accessed as a standalone resource. This is 
achieved by running the following command:
```python3 -m kitchen dsl-tool```

##:grey_question: App Options
The application also contains several options. While `run` and `init` are most
helpful, you may view help, as well as the application version using the below 
commands. 

```python3 -m kitchen --help```
```python3 -m kitchen -v ```

To check which CFG is currently loaded without having to run Kitchen, use this command.
```python3 -m kitchen show-cfg```


##:books: Documentation
To view the complete documentation online, `pdoc` needs to be installed:

`pip install pdoc`

Once it is, simply run the following in the 
command-line at the root of the directory:
``` python3 -m pdoc --http localhost:8080 kitchen```
  
##:test_tube: Running tests
Kitchen makes use of several tests. To run these, the CFGs in the samples directory
(particularly in the `example_cfgs` and `expected_fs` etc. folders must not be removed. 

Execute `python -m pytest tests/` from the project’s root directory to 
initiate the tests. 


##:arrow_forward: Example Visualisations
### Follow Set calculation
![follow](https://user-images.githubusercontent.com/77244149/189752729-0e51d1dd-742d-4774-99d0-36c392bc5db9.png)
### Parsing Table calculation
![parse_table2](https://user-images.githubusercontent.com/77244149/189752702-e5bf107f-73cd-4559-ab38-97fceed93cec.png)

### LL1(Parsing)
####:crescent_moon: Dark Theme
![matching](https://user-images.githubusercontent.com/77244149/189752748-8bb6cb44-1189-4315-87a8-ba6a3661342e.png)
####:sunny:Light Theme
![light_1](https://user-images.githubusercontent.com/77244149/189753376-e248e159-0530-4b07-8c27-6c3eaf725d89.png)
### Semantic Analysis
![semantic](https://user-images.githubusercontent.com/77244149/189752534-89258b52-a816-4a64-9c3b-94a71eddffea.png)
![semantic 2](https://user-images.githubusercontent.com/77244149/189752817-ca53b906-66da-4c45-b9f2-881bac0e6216.png)




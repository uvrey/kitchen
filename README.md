# Kitchen: A Compiler Visualiser and Teaching Tool
Kitchen calculates, visualises and explains five algorithms in Compiler
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

## Example Visualisations
### Follow Set calculation
![follow](https://user-images.githubusercontent.com/77244149/189752729-0e51d1dd-742d-4774-99d0-36c392bc5db9.png)
### Parsing Table calculation
![parse_table2](https://user-images.githubusercontent.com/77244149/189752702-e5bf107f-73cd-4559-ab38-97fceed93cec.png)

### LL1(Parsing)
#### Dark Theme
![matching](https://user-images.githubusercontent.com/77244149/189752748-8bb6cb44-1189-4315-87a8-ba6a3661342e.png)
#### Light Theme
[light_1](https://user-images.githubusercontent.com/77244149/189753257-4a9a5545-8726-4ebe-9f63-31aa27e98b9d.png)
### Semantic Analysis!
![semantic](https://user-images.githubusercontent.com/77244149/189752534-89258b52-a816-4a64-9c3b-94a71eddffea.png)
![semantic 2](https://user-images.githubusercontent.com/77244149/189752817-ca53b906-66da-4c45-b9f2-881bac0e6216.png)

## Installation

### Windows
To run Kitchen on Windows, you will need to install several packages.

**Requirements:**
- Python3
- Pip
- Chocolatey: https://chocolatey.org/install

**0. Make sure your package managers are up to date.**

In this installation, we will use pip and Chocolatey. Ensure Pip is upgraded by running:
```python -m pip install -–upgrade pip```

**2. Install manim and other dependencies; remembering to use Powershell as admin. **
  ```choco install manimce```  
  Alternatively:   ```python3 -m pip install manim```
  
  If manim is not detected, use the following command within your virtual environment to set it up:
  ```python3 -m pip install manim```
  
  Some packages may require a reboot, so please do this :)
  
3. Install LaTeX on Windows
  MikTeX is recommended: https://miktex.org/m.DOWNload
  It will also assist with installing extra style packages when you run the code for the first time.
  

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
 
 **3. Using narration**
 The generation of narration is enabled by the gTTS library. Make sure you are
 connected to the internet when doing so, otherwise the video will not generate.

 For offline rendering, it is recommended to turn narration off. This is achieved
 by inserting the following command at Kitchen's prompt.

 `Input: \c -n n`
## Compiling and Executing
  
  To run the program, the Context-Free Grammar file needs to be specified.
  
  use the following command to do this (A CFG is provided for your 
  convience, but you can replace the last argument with your choice of path).
  
```python
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg_12.txt" 
```

  If you would like to also include a language specification, please include it
  as an additional path. For example:

```python
python3 -m kitchen init -cfg ".\samples\example_cfgs\cfg_12.txt" ".\samples\test_spec.txt"
```
  
  Now, to run the application, use:

```python
python3 -m kitchen run
```

  From here, `\m` will display the menu, and `\tut' will take you through
  a quick tutorial.

  For your convenience, here is this menu! It contains all the commands which
  kitchen supports. 

```python
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
| Detail                   | Command          | Shortcut   |
|:-------------------------|:-----------------|:-----------|
| Display First Set        | \show first      | \fs        |
| Display Follow Set       | \show follow     | \fw        |
| Display Parse Table      | \show parsetable | \pt        |
| Display LL(1) Parse Tree | \ll1 <input>     | <input>    |
| Display Symbol Table     | \sem <input>     | <input>    |

Use these commands to generate an explanation video.
| Detail                                  | Command         | Shortcut   |
|:----------------------------------------|:----------------|:-----------|
| Visualise Parsing Table calculation     | \vis parsetable | \vpt       |
| Visualise First Set calculation         | \vis first      | \vfs       |
| Visualise Follow Set calculation        | \vis follow     | \vfw       |
| Visualise LL(1) Parse Tree construction | \ll1 v <input>  | \v <input> |
| Visualise Semantic Analysis             | \vsem <input>   | \v <input> |
```

## App Options
The application also contains several options. While `run` and `init` are most
helpful, you may view help, as well as the application version using the below 
commands. 

```python3 -m kitchen --help```
```python3 -m kitchen -v ```

## Documentation
To view the complete documentation online, simply run the following in the 
command-line at the root of the directory:
``` python3 -m pdoc --http localhost:8080 kitchen```
  
## Running tests
Kitchen makes use of several tests. To run these, the CFGs in the samples directory
(particularly in the `example_cfgs` and `expected_fs` etc. folders must not be removed. 

Execute `python -m pytest tests/` from the project’s root directory to 
initiate the tests. 





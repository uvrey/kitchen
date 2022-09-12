# ComVizTT
Compiler Visualiser and Teaching Tool


python3 dsl-tool/dsltool.py to run DSL design tool. Defaults are fine.
python3 <generated file>_gccsem.py will generate python output code for your input.


## Installation

### Windows
To run Kitchen, you will need to install several packages.

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
 
 **3. 
## Compiling and Executing
  
  To run the program, use the following command:
  
  ``` python3 cli.py ```
  
  The regex and CLI file will need to be provided.
  
  From here, `\m` will display the menu. 

## App Options

```python3 -m kitchen --help```
```python3 -m kitchen -v ```

## Documentation
For complete documentation, run the following in the command-line:
``` python3 -m pdoc --http localhost:8080 kitchen```
  
## Running tests
Execute `python -m pytest tests/` from this project’s root directory.





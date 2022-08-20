""" Kitchen entry point script """
# kitchen/main.py
from kitchen import app, __app_name__

def main():
    """Entry point for the application.
    """    
    app.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()
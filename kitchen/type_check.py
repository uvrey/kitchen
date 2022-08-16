from logging import root
from manim import m
from kitchen import (RE_TERMINAL, RE_PRODUCTION, RE_NONTERMINAL, cli_helper, sounds, animation)
import typer

class SymbolTable:
    def __init__(self, cfg, root, g):
        self.cfg = cfg
        self.root = root
        self.g = g

# 1.	If a variable(identifier) is created/defined on the left hand side of an assignment, it should check if it has already been defined, in which case it should generate an appropriate semantic error. 
# 2.	If a variable(identifier) is used in the right hand side of an assignment it should check if it has been defined already, and if not it should generate an appropriate semantic error.
    def create_symbol_table(self):
        pass

    def traverse_tree(self):
        pass

    
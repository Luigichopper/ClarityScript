from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass

@dataclass
class Document(ASTNode):
    """Root node representing a complete Clarity document"""
    children: List[ASTNode]

@dataclass
class Element(ASTNode):
    """HTML element node"""
    name: str
    attributes: Dict[str, Any] = None
    children: List[ASTNode] = None
    content: Optional[str] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.children is None:
            self.children = []

@dataclass
class TextContent(ASTNode):
    """Text content node"""
    value: str

@dataclass
class VariableDeclaration(ASTNode):
    """Variable declaration node"""
    name: str
    value: Any

@dataclass
class VariableReference(ASTNode):
    """Variable reference node"""
    name: str

@dataclass
class ForLoop(ASTNode):
    """For loop node"""
    iterator: str
    iterable: str
    body: List[ASTNode]

@dataclass
class Conditional(ASTNode):
    """If/else conditional node"""
    condition: str
    if_body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None

@dataclass
class ComponentDefinition(ASTNode):
    """Component definition node"""
    name: str
    parameters: List[str]
    default_values: Dict[str, Any]
    body: List[ASTNode]

@dataclass
class ComponentUse(ASTNode):
    """Component use node"""
    name: str
    arguments: Dict[str, Any]

@dataclass
class StyleBlock(ASTNode):
    """CSS style block node"""
    content: str

@dataclass
class ScriptBlock(ASTNode):
    """JavaScript script block node"""
    content: str

@dataclass
class StringLiteral(ASTNode):
    """String literal node"""
    value: str
    is_formatted: bool = False  # True for f-strings

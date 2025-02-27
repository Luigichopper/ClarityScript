from typing import List, Dict, Any, Optional, Union, Tuple
from clarity_lexer import Lexer, Token, TokenType
from clarity_ast import *
import re


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.variables: Dict[str, Any] = {}
        self.components: Dict[str, ComponentDefinition] = {}

    def parse(self) -> Document:
        """Parse tokens into an AST"""
        document = Document(children=[])

        while not self._is_at_end() and self._peek().type != TokenType.EOF:
            node = self._parse_statement()
            if node:
                document.children.append(node)

        return document

    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a top-level statement"""
        token = self._peek()

        if token.type == TokenType.VARIABLE_DECL:
            return self._parse_variable_declaration()
        elif token.type == TokenType.COMPONENT_DEF:
            return self._parse_component_definition()
        elif token.type == TokenType.ELEMENT:
            return self._parse_element()
        elif token.type == TokenType.FOR_LOOP:
            return self._parse_for_loop()
        elif token.type == TokenType.IF_STATEMENT:
            return self._parse_conditional()
        elif token.type == TokenType.COMPONENT_USE:
            return self._parse_component_use()
        elif token.type in (TokenType.NEWLINE, TokenType.COMMENT):
            self._advance()  # Skip newlines and comments
            return None
        elif token.type == TokenType.MULTILINE_STRING:
            return self._parse_multiline_string()
        else:
            self._error(f"Unexpected token: {token}")
            self._advance()  # Skip the unexpected token
            return None

    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Parse a variable declaration statement"""
        token = self._consume(TokenType.VARIABLE_DECL)
        match = re.match(r'\$([\w_]+)\s*=\s*(.*)', token.value)

        if not match:
            self._error(f"Invalid variable declaration: {token.value}")
            return VariableDeclaration("error", "")

        var_name = match.group(1)
        var_value = match.group(2).strip()

        # Handle string literals
        if var_value.startswith('"') and var_value.endswith('"'):
            var_value = var_value[1:-1]

        # Store variable for later use
        self.variables[f"${var_name}"] = var_value

        return VariableDeclaration(var_name, var_value)

    def _parse_multiline_string(self) -> TextContent:
        """Parse a multiline string"""
        token = self._consume(TokenType.MULTILINE_STRING)
        return TextContent(token.value)

    def _parse_element(self) -> Element:
        """Parse an HTML element"""
        element_token = self._consume(TokenType.ELEMENT)
        element_name = element_token.value

        attributes = {}
        if self._check(TokenType.ATTRIBUTE):
            attr_token = self._consume(TokenType.ATTRIBUTE)
            attributes = self._parse_attributes(attr_token.value)

        # Expect a colon
        self._consume(TokenType.COLON)

        # Check for inline content
        content = None
        children = []

        if self._check(TokenType.STRING) or self._check(TokenType.VARIABLE_REF) or self._check(
                TokenType.CONTENT) or self._check(TokenType.MULTILINE_STRING):
            content = self._parse_content()
        else:
            # Check for block content (indented children)
            if self._check(TokenType.NEWLINE):
                self._consume(TokenType.NEWLINE)

                if self._check(TokenType.INDENT):
                    self._consume(TokenType.INDENT)
                    children = self._parse_block()
                    self._consume(TokenType.DEDENT)

        return Element(element_name, attributes, children, content)

    def _parse_attributes(self, attr_str: str) -> Dict[str, Any]:
        """Parse element attributes"""
        attributes = {}

        # Very simple attribute parsing (doesn't handle all edge cases)
        in_quotes = False
        quote_char = None
        current_attr = ""
        attr_parts = []

        for char in attr_str:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None

            current_attr += char

            if char == ' ' and not in_quotes:
                if current_attr.strip():
                    attr_parts.append(current_attr.strip())
                current_attr = ""

        if current_attr.strip():
            attr_parts.append(current_attr.strip())

        # Process each attribute
        for attr in attr_parts:
            if '=' in attr:
                key, value = attr.split('=', 1)
                key = key.strip()

                # Strip quotes from value if present
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                # Replace variable references
                for var_name, var_value in self.variables.items():
                    if var_name in value:
                        value = value.replace(var_name, var_value)

                attributes[key] = value
            else:
                # Boolean attribute
                attributes[attr.strip()] = True

        return attributes

    def _parse_content(self) -> str:
        """Parse inline content"""
        if self._check(TokenType.STRING):
            token = self._consume(TokenType.STRING)
            # Remove quotes
            content = token.value
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            return content
        elif self._check(TokenType.MULTILINE_STRING):
            token = self._consume(TokenType.MULTILINE_STRING)
            return token.value
        elif self._check(TokenType.VARIABLE_REF):
            token = self._consume(TokenType.VARIABLE_REF)
            var_name = token.value
            if var_name in self.variables:
                return self.variables[var_name]
            return f"{var_name}"
        elif self._check(TokenType.CONTENT):
            token = self._consume(TokenType.CONTENT)
            return token.value

        return ""

    def _parse_block(self) -> List[ASTNode]:
        """Parse a block of statements (after an indentation)"""
        statements = []

        while not self._is_at_end() and not self._check(TokenType.DEDENT):
            statement = self._parse_statement()
            if statement:
                statements.append(statement)

        return statements

    def _parse_for_loop(self) -> ForLoop:
        """Parse a for loop statement"""
        for_token = self._consume(TokenType.FOR_LOOP)

        # Extract iterator and iterable from the for statement
        match = re.match(r'for\s+(\w+)\s+in\s+(.+)', for_token.value)
        if not match:
            self._error(f"Invalid for loop syntax: {for_token.value}")
            return ForLoop("error", "error", [])

        iterator = match.group(1)
        iterable = match.group(2)

        # Expect a colon
        self._consume(TokenType.COLON)

        # Parse the loop body
        self._consume(TokenType.NEWLINE)
        self._consume(TokenType.INDENT)
        body = self._parse_block()
        self._consume(TokenType.DEDENT)

        return ForLoop(iterator, iterable, body)

    def _parse_conditional(self) -> Conditional:
        """Parse an if/else conditional statement"""
        if_token = self._consume(TokenType.IF_STATEMENT)

        # Extract condition from the if statement
        match = re.match(r'if\s+(.+)', if_token.value)
        if not match:
            self._error(f"Invalid if statement syntax: {if_token.value}")
            return Conditional("True", [])

        condition = match.group(1)

        # Expect a colon
        self._consume(TokenType.COLON)

        # Parse the if body
        self._consume(TokenType.NEWLINE)
        self._consume(TokenType.INDENT)
        if_body = self._parse_block()
        self._consume(TokenType.DEDENT)

        # Check for an else block
        else_body = None
        if self._check(TokenType.ELSE_STATEMENT):
            self._consume(TokenType.ELSE_STATEMENT)

            # Expect newline and indent
            self._consume(TokenType.NEWLINE)
            self._consume(TokenType.INDENT)
            else_body = self._parse_block()
            self._consume(TokenType.DEDENT)

        return Conditional(condition, if_body, else_body)

    def _parse_component_definition(self) -> ComponentDefinition:
        """Parse a component definition"""
        comp_token = self._consume(TokenType.COMPONENT_DEF)

        # Extract component name and parameters
        match = re.match(r'@component\s+(\w+)\s*\(([^)]*)\)\s*', comp_token.value)
        if not match:
            self._error(f"Invalid component definition: {comp_token.value}")
            return ComponentDefinition("error", [], {}, [])

        name = match.group(1)
        params_str = match.group(2)

        # Parse parameters
        parameters = []
        default_values = {}

        if params_str.strip():
            for param in params_str.split(','):
                param = param.strip()
                if '=' in param:
                    param_name, default = param.split('=', 1)
                    param_name = param_name.strip()
                    default = default.strip()

                    # Process default value
                    if (default.startswith('"') and default.endswith('"')) or \
                            (default.startswith("'") and default.endswith("'")):
                        default = default[1:-1]  # Remove quotes

                    parameters.append(param_name)
                    default_values[param_name] = default
                else:
                    parameters.append(param)

        # Expect a colon
        if not comp_token.value.endswith(':'):
            self._consume(TokenType.COLON)

        # Parse the component body
        self._consume(TokenType.NEWLINE)
        self._consume(TokenType.INDENT)
        body = self._parse_block()
        self._consume(TokenType.DEDENT)

        # Register this component
        component = ComponentDefinition(name, parameters, default_values, body)
        self.components[name] = component

        return component

    def _parse_component_use(self) -> ComponentUse:
        """Parse a component use statement"""
        comp_token = self._consume(TokenType.COMPONENT_USE)

        # Extract component name and arguments
        match = re.match(r'@(\w+)(?:\s*\(([^)]*)\))?', comp_token.value)
        if not match:
            self._error(f"Invalid component use: {comp_token.value}")
            return ComponentUse("error", {})

        name = match.group(1)
        args_str = match.group(2) if match.group(2) else ""

        # Parse arguments
        arguments = {}

        if args_str.strip():
            for arg in args_str.split(','):
                arg = arg.strip()
                if '=' in arg:
                    arg_name, value = arg.split('=', 1)
                    arg_name = arg_name.strip()
                    value = value.strip()

                    # Process value
                    if (value.startswith('"') and value.endswith('"')) or \
                            (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]  # Remove quotes

                    arguments[arg_name] = value
                else:
                    # Positional argument (not supported in this simplistic parser)
                    self._error(f"Positional arguments not supported: {arg}")

        return ComponentUse(name, arguments)

    def _consume(self, expected_type: TokenType) -> Token:
        """Consume and return the current token if it matches the expected type"""
        if self._check(expected_type):
            return self._advance()

        token = self._peek()
        self._error(f"Expected {expected_type} but got {token.type} at line {token.line}")
        return token

    def _check(self, type: TokenType) -> bool:
        """Check if the current token is of the given type"""
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self) -> Token:
        """Advance to the next token and return the previous one"""
        if not self._is_at_end():
            self.position += 1
        return self.tokens[self.position - 1]

    def _peek(self) -> Token:
        """Return the current token without consuming it"""
        return self.tokens[self.position]

    def _is_at_end(self) -> bool:
        """Check if we've reached the end of tokens"""
        return self.position >= len(self.tokens) or self._peek().type == TokenType.EOF

    def _error(self, message: str) -> None:
        """Report an error"""
        print(f"Parser Error: {message}")
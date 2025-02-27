from typing import List, Dict, Any, Optional, Tuple
from clarity_lexer import Lexer, Token, TokenType
from clarity_parser import Parser
from clarity_ast import *
import sys
import os


class Compiler:
    def __init__(self, ast: Document):
        self.ast = ast
        self.output_lines = []
        self.indentation = 0
        self.variables = {}
        self.components = {}

    def compile(self) -> str:
        """Compile AST to HTML"""
        # First pass: collect all component definitions
        self._collect_components(self.ast.children)

        # Second pass: compile all nodes
        for node in self.ast.children:
            self._compile_node(node)

        return '\n'.join(self.output_lines)

    def _collect_components(self, nodes: List[ASTNode]) -> None:
        """Pre-process to collect all component definitions"""
        for node in nodes:
            if isinstance(node, ComponentDefinition):
                self.components[node.name] = node
            elif isinstance(node, Element) and node.children:
                self._collect_components(node.children)

    def _compile_node(self, node: ASTNode) -> None:
        """Compile a node based on its type"""
        if isinstance(node, Element):
            self._compile_element(node)
        elif isinstance(node, TextContent):
            self._compile_text(node)
        elif isinstance(node, VariableDeclaration):
            self._compile_variable_declaration(node)
        elif isinstance(node, ForLoop):
            self._compile_for_loop(node)
        elif isinstance(node, Conditional):
            self._compile_conditional(node)
        elif isinstance(node, ComponentDefinition):
            # Already collected, no need to output anything
            pass
        elif isinstance(node, ComponentUse):
            self._compile_component_use(node)
        else:
            # Unknown node type
            pass

    def _compile_element(self, element: Element) -> None:
        """Compile an HTML element"""
        # Special handling for document element
        if element.name == 'document':
            self.output_lines.append('<!DOCTYPE html>')
            self.output_lines.append('<html>')

            for child in element.children:
                self._compile_node(child)

            self.output_lines.append('</html>')
            return

        # Special handling for style and script elements
        if element.name == 'style' or element.name == 'script':
            self._compile_special_element(element)
            return

        # Regular HTML element
        tag = element.name
        attrs = self._compile_attributes(element.attributes)

        # Opening tag
        if attrs:
            self.output_lines.append(' ' * self.indentation + f'<{tag} {attrs}>')
        else:
            self.output_lines.append(' ' * self.indentation + f'<{tag}>')

        # Add content if available
        if element.content:
            content = self._replace_variables(element.content)
            self.output_lines[-1] = self.output_lines[-1][:-1] + f'>{content}</{tag}>'
            return

        # Add children
        if element.children:
            self.indentation += 2
            for child in element.children:
                self._compile_node(child)
            self.indentation -= 2

        # Closing tag (if not self-closing)
        if element.children or not element.content:
            self.output_lines.append(' ' * self.indentation + f'</{tag}>')

    def _compile_special_element(self, element: Element) -> None:
        """Compile style and script elements with their content"""
        tag = element.name
        attrs = self._compile_attributes(element.attributes)

        # Opening tag
        if attrs:
            self.output_lines.append(' ' * self.indentation + f'<{tag} {attrs}>')
        else:
            self.output_lines.append(' ' * self.indentation + f'<{tag}>')

        # Process content
        multiline_content = None

        # First, look for direct multiline string content
        for child in element.children:
            if isinstance(child, TextContent):
                content = child.value
                if content.strip().startswith('"""') and content.strip().endswith('"""'):
                    multiline_content = content.strip()[3:-3]
                    break

        # If not found, look for MULTILINE_STRING token
        if not multiline_content:
            for i, child in enumerate(element.children):
                if isinstance(child, Element) and child.content:
                    content = child.content
                    if isinstance(content, str) and '"""' in content:
                        start_idx = content.find('"""') + 3
                        end_idx = content.rfind('"""')
                        if end_idx > start_idx:
                            multiline_content = content[start_idx:end_idx]
                            break

        # Output the content
        if multiline_content:
            lines = multiline_content.split('\n')
            for line in lines:
                self.output_lines.append(' ' * (self.indentation + 2) + line)

        # Closing tag
        self.output_lines.append(' ' * self.indentation + f'</{tag}>')

    def _compile_attributes(self, attributes: Dict[str, Any]) -> str:
        """Compile element attributes to HTML format"""
        attr_strs = []

        for key, value in attributes.items():
            if isinstance(value, bool) and value:
                # Boolean attribute
                attr_strs.append(key)
            else:
                # Regular attribute with value
                attr_strs.append(f'{key}="{value}"')

        return ' '.join(attr_strs)

    def _compile_text(self, text: TextContent) -> None:
        """Compile text content"""
        content = self._replace_variables(text.value)
        self.output_lines.append(' ' * self.indentation + content)

    def _compile_variable_declaration(self, var_decl: VariableDeclaration) -> None:
        """Process variable declaration (no output, just store for substitution)"""
        self.variables[f"${var_decl.name}"] = var_decl.value

    def _compile_for_loop(self, loop: ForLoop) -> None:
        """Process a for loop by expanding it"""
        # This is a simplistic implementation and doesn't handle complex iterables
        iterable = loop.iterable

        # Handle variable reference in iterable
        if iterable.startswith('$'):
            if iterable in self.variables:
                # Very basic handling - assumes it's a list-like string representation
                # In a real compiler, you'd have proper evaluation
                raw_value = self.variables[iterable]
                if raw_value.startswith('[') and raw_value.endswith(']'):
                    items = raw_value[1:-1].split(',')
                    items = [item.strip() for item in items]
                    if all(item.startswith('"') and item.endswith('"') for item in items):
                        items = [item[1:-1] for item in items]
                else:
                    # Fallback - treat as a single item
                    items = [raw_value]
            else:
                # Unknown variable, emit warning
                print(f"Warning: Unknown variable {iterable} in for loop")
                return
        else:
            # Direct iterable (not implemented in this simple version)
            print(f"Warning: Direct iterables not implemented in for loop: {iterable}")
            return

        # Process the loop body for each item
        for item in items:
            # Store the iterator variable
            temp_var = f"${loop.iterator}"
            self.variables[temp_var] = item

            # Process the loop body
            for node in loop.body:
                self._compile_node(node)

            # Clean up
            if temp_var in self.variables:
                del self.variables[temp_var]

    def _compile_conditional(self, cond: Conditional) -> None:
        """Process a conditional statement"""
        # This is a very simplistic implementation
        condition = cond.condition

        # Replace variables in the condition
        for var_name, var_value in self.variables.items():
            condition = condition.replace(var_name, f'"{var_value}"')

        # Evaluate the condition (using eval - never do this in production!)
        # In a real compiler, you'd have proper safe evaluation
        try:
            result = eval(condition)
        except Exception as e:
            print(f"Warning: Failed to evaluate condition {condition}: {e}")
            result = False

        if result:
            # Process the if body
            for node in cond.if_body:
                self._compile_node(node)
        elif cond.else_body:
            # Process the else body
            for node in cond.else_body:
                self._compile_node(node)

    def _compile_component_definition(self, comp_def: ComponentDefinition) -> None:
        """Store component definition for later use"""
        self.components[comp_def.name] = comp_def

    def _compile_component_use(self, comp_use: ComponentUse) -> None:
        """Process component use by expanding the component with arguments"""
        component_name = comp_use.name

        if component_name not in self.components:
            print(f"Warning: Unknown component: {component_name}")
            return

        component = self.components[component_name]

        # Set up component parameters as variables
        old_vars = self.variables.copy()

        # First apply default values
        for param, default in component.default_values.items():
            self.variables[f"${param}"] = default

        # Then apply provided arguments
        for param, value in comp_use.arguments.items():
            self.variables[f"${param}"] = value

        # Process the component body
        for node in component.body:
            self._compile_node(node)

        # Restore original variables
        self.variables = old_vars

    def _replace_variables(self, text: str) -> str:
        """Replace variable references in text"""
        if not isinstance(text, str):
            return text

        for var_name, var_value in self.variables.items():
            if var_name in text:
                text = text.replace(var_name, str(var_value))

        return text


def compile_clarity_file(input_file: str, output_file: Optional[str] = None) -> None:
    """Compile a Clarity file to HTML."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Lexical analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        # Code generation
        compiler = Compiler(ast)
        html_output = compiler.compile()

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            print(f"Compiled {input_file} to {output_file}")
        else:
            print(html_output)

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clarity_compiler.py input.clar [output.html]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    compile_clarity_file(input_file, output_file)
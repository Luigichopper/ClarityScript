#!/usr/bin/env python3
import sys
import os
from clarity_lexer import Lexer
from clarity_parser import Parser
from clarity_compiler import Compiler

def print_banner():
    """Print a banner for the Clarity compiler"""
    print("=" * 60)
    print("           CLARITY LANGUAGE COMPILER v0.1")
    print("      HTML with the readability of Python")
    print("=" * 60)
    print()

def compile_file(input_file, output_file=None):
    """Compile a Clarity file to HTML"""
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return False
    
    print(f"Compiling {input_file}...")
    
    try:
        # Auto-generate output file name if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.html"
        
        # Read the source file
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Lexical analysis
        print("  Tokenizing source code...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parsing
        print("  Parsing into AST...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Code generation
        print("  Generating HTML...")
        compiler = Compiler(ast)
        html_output = compiler.compile()
        
        # Write the output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"Successfully compiled to {output_file}")
        print(f"  Input: {len(source_code)} bytes")
        print(f"  Output: {len(html_output)} bytes")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    print_banner()
    
    if len(sys.argv) < 2:
        print("Usage: python clarity.py input.clar [output.html]")
        print()
        print("Options:")
        print("  -v, --version    Display version information")
        print("  -h, --help       Display this help message")
        return
    
    # Check for options
    if sys.argv[1] in ['-h', '--help']:
        print("Usage: python clarity.py input.clar [output.html]")
        print()
        print("Options:")
        print("  -v, --version    Display version information")
        print("  -h, --help       Display this help message")
        return
    
    if sys.argv[1] in ['-v', '--version']:
        print("Clarity Language Compiler v0.1")
        print("Created in 2025")
        return
    
    # Process files
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    compile_file(input_file, output_file)

if __name__ == "__main__":
    main()

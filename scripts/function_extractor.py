def escape_html(text: str) -> str:
    """Escape HTML-like syntax in text."""
    if not text:
        return text
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")


class FunctionInfo(NamedTuple):
    """Information about a function."""

    name: str
    is_async: bool
    decorators: List[str]
    params: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    imports: List[str]


def extract_imports(tree: ast.AST) -> List[str]:
    """Extract import statements from an AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append(f"{module}.{name.name}")
    return sorted(imports)


def extract_functions(file_path: str) -> List[FunctionInfo]:
    """Extract detailed function information from a Python file."""
    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())

        imports = extract_imports(tree)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get decorators
                decorators = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorators.append(dec.id)
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name):
                            decorators.append(dec.func.id)

                # Get parameters
                params = []
                for arg in node.args.args:
                    param = arg.arg
                    if arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
                            param += f": {arg.annotation.id}"
                        elif isinstance(arg.annotation, ast.Constant):
                            param += f": {arg.annotation.value}"
                    params.append(param)

                # Get return type
                returns = None
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        returns = node.returns.id
                    elif isinstance(node.returns, ast.Constant):
                        returns = str(node.returns.value)

                # Get docstring
                docstring = ast.get_docstring(node)

                functions.append(
                    FunctionInfo(
                        name=node.name,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                        decorators=decorators,
                        params=params,
                        returns=returns,
                        docstring=docstring,
                        imports=imports,
                    )
                )

        return sorted(functions, key=lambda x: x.name)
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []


def extract_js_functions(file_path: str) -> List[dict]:
    """Extract function information from a JavaScript/TypeScript file."""
    try:
        with open(file_path, "r") as file:
            content = file.read()

            # Extract imports
            import_pattern = r'^import\s+.*?[\'"].*?[\'"];?\s*$'
            imports = re.findall(import_pattern, content, re.MULTILINE)

            # Match function declarations with types
            functions = []
            patterns = [
                # Function declarations with type annotations
                r"(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:<([^>]+)>)?\s*\((.*?)\)(?:\s*:\s*([^{]+))?\s*{",
                # Arrow functions with type annotations
                r"(?:export\s+)?(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:<([^>]+)>)?\s*=\s*(?:async\s*)?\((.*?)\)(?:\s*:\s*([^=]+))?\s*=>",
                # Class methods with type annotations
                r"(?:async\s+)?(?:public|private|protected)?\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:<([^>]+)>)?\s*\((.*?)\)(?:\s*:\s*([^{]+))?\s*{",
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    name = match.group(1)
                    generic_types = match.group(2)
                    params = match.group(3)
                    returns = match.group(4)

                    is_exported = bool(re.search(r"export\s+", match.group(0)))
                    is_async = bool(re.search(r"async\s+", match.group(0)))

                    functions.append(
                        {
                            "name": name,
                            "is_async": is_async,
                            "is_exported": is_exported,
                            "generic_types": generic_types.strip() if generic_types else None,
                            "params": params.strip(),
                            "returns": returns.strip() if returns else None,
                            "imports": imports,
                        }
                    )

            return sorted(functions, key=lambda x: x["name"])
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []


def process_directories(root_dir: str, output_file: str):
    """Process app and frontend directories and write detailed function information to output file."""
    content = []
    content.append("# Function Details\n\n")

    def format_docstring(docstring: str) -> str:
        """Format docstring to avoid trailing spaces and maintain proper markdown formatting."""
        if not docstring:
            return ""

        # Split into lines and strip trailing spaces
        lines = [line.rstrip() for line in docstring.split("\n")]

        # Remove empty lines from start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            return ""

        # Join lines back together with proper line endings
        return "\n".join(lines)

    # Track used headings to avoid duplicates
    used_headings = {}

    def get_unique_heading(base_name: str, file_path: str) -> str:
        """Get a unique heading by appending a suffix if needed."""
        key = f"{base_name}|{file_path}"
        if key not in used_headings:
            used_headings[key] = 0
        else:
            used_headings[key] += 1

        # Format the file path for display
        file_context = file_path.replace("/", ".").replace("\\", ".")

        # Escape special function names that start and end with double underscores
        if base_name.startswith("__") and base_name.endswith("__"):
            # Use backticks to properly escape dunder methods
            base_name = f"`{base_name}`"

        # Always include file context for uniqueness
        if used_headings[key] == 0:
            return f"{base_name} ({file_context})"

        # Add counter for subsequent occurrences
        return f"{base_name} ({file_context} #{used_headings[key] + 1})"

    # Process Python files
    app_dir = os.path.join(root_dir, "app")
    if os.path.exists(app_dir):
        content.append("## Backend (Python)\n\n")
        for root, _, files in os.walk(app_dir):
            python_files = [f for f in files if f.endswith(".py")]

            for file in python_files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                functions = extract_functions(file_path)

                if functions:
                    content.append(f"### {relative_path}\n\n")
                    # List imports once per file if there are any, with unique heading
                    if functions and functions[0].imports:
                        content.append(f"#### Imports ({relative_path})\n\n")
                        content.append("- **Imports**:\n")
                        for imp in functions[0].imports:
                            content.append(f"  - `{escape_html(imp)}`\n")
                        content.append("\n---\n\n")

                    for func in sorted(functions, key=lambda x: x.name):
                        unique_name = get_unique_heading(func.name, relative_path)
                        content.append(f"#### {unique_name}\n\n")
                        if func.is_async:
                            content.append("- **Async**: Yes\n\n")
                        if func.decorators:
                            content.append("- **Decorators**:\n")
                            for dec in func.decorators:
                                content.append(f"  - `{escape_html(dec)}`\n")
                            content.append("\n")
                        if func.params:
                            content.append("- **Parameters**:\n")
                            for param in func.params:
                                content.append(f"  - `{escape_html(param)}`\n")
                            content.append("\n")
                        if func.returns:
                            content.append(f"- **Returns**: `{escape_html(func.returns)}`\n\n")
                        if func.docstring:
                            formatted_docstring = format_docstring(func.docstring)
                            if formatted_docstring:
                                content.append(f"- **Description**:\n{formatted_docstring}\n\n")
                        content.append("---\n\n")

    # Process JavaScript/TypeScript files
    frontend_dir = os.path.join(root_dir, "frontend")
    if os.path.exists(frontend_dir):
        content.append("## Frontend (JavaScript/TypeScript)\n\n")
        for root, dirs, files in os.walk(frontend_dir):
            if "node_modules" in dirs:
                dirs.remove("node_modules")

            js_files = [f for f in files if f.endswith((".js", ".jsx", ".ts", ".tsx"))]

            for file in js_files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                functions = extract_js_functions(file_path)

                if functions:
                    content.append(f"### {relative_path}\n\n")
                    # List imports once per file if there are any, with unique heading
                    if functions and functions[0]["imports"]:
                        content.append(f"#### Imports ({relative_path})\n\n")
                        content.append("- **Imports**:\n")
                        for imp in functions[0]["imports"]:
                            content.append(f"  - `{escape_html(imp)}`\n")
                        content.append("\n---\n\n")

                    for func in sorted(functions, key=lambda x: x["name"]):
                        unique_name = get_unique_heading(func["name"], relative_path)
                        content.append(f"#### {unique_name}\n\n")
                        if func["is_async"]:
                            content.append("- **Async**: Yes\n\n")
                        if func["is_exported"]:
                            content.append("- **Exported**: Yes\n\n")
                        if func["generic_types"]:
                            content.append(
                                f"- **Generic Types**: `{escape_html(func['generic_types'])}`\n\n"
                            )
                        if func["params"]:
                            content.append(f"- **Parameters**: `{escape_html(func['params'])}`\n\n")
                        if func["returns"]:
                            content.append(f"- **Returns**: `{escape_html(func['returns'])}`\n\n")
                        content.append("---\n\n")

    # Write content to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(content))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python function_extractor.py <output_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Root directory: {root_dir}")

    try:
        process_directories(root_dir, output_file)
        print(f"Function details have been written to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

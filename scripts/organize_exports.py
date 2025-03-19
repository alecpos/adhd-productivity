"""Script to organize and export files by functional grouping and features."""




class ExportError(Exception):
    """Custom exception for export errors."""



def setup_logging():
    """Configure logging for the export process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("exports/export.log"), logging.StreamHandler()],
    )


def safe_file_operation(func):
    """Decorator for safe file operations."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            raise ExportError(f"Failed to execute {func.__name__}: {str(e)}")



def get_file_type_config():
    """Configuration for supported file types and their export settings."""
    return {
        "BACKEND": {
            "extensions": [".py"],
            "export_template": "from .{module_name} import *\n",
            "consolidated_ext": ".py",
            "comment_symbol": "#",
        },
        "FRONTEND": {
            "extensions": [".ts", ".tsx", ".js", ".jsx"],
            "export_template": "export * from './{module_name}';\n",
            "consolidated_ext": ".ts",
            "comment_symbol": "//",
        },
        "STYLES": {
            "extensions": [".css", ".scss", ".less"],
            "export_template": "@import './{module_name}';\n",
            "consolidated_ext": ".scss",
            "comment_symbol": "//",
        },
    }


def load_config() -> Dict[str, Any]:
    """Load configuration from multiple sources."""
    config = {
        "exclude_patterns": [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
        ],
        "include_patterns": ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
        "export_settings": {
            "create_consolidated_files": True,
            "create_readme": True,
            "create_documentation": True,
            "analyze_dependencies": True,
        },
    }

    # Load from config file if exists
    if os.path.exists("export_config.json"):
        with open("export_config.json") as f:
            config.update(json.load(f))

    # Override with environment variables
    for key in os.environ:
        if key.startswith("EXPORT_"):
            config_key = key[7:].lower()
            config[config_key] = os.environ[key]



@safe_file_operation
def analyze_dependencies(file_path: str) -> List[str]:
    """Analyze file dependencies based on imports and requires."""
    dependencies = []
    with open(file_path, "r") as f:
        content = f.read()
        # Python imports
        if file_path.endswith(".py"):
            imports = re.findall(r"^(?:from|import)\s+([.\w]+)", content, re.MULTILINE)
            dependencies.extend(imports)
        # JavaScript/TypeScript imports
        elif file_path.endswith((".js", ".ts", ".tsx")):
            imports = re.findall(r'(?:import|require)\s*\(?[\'"]([^\'"\)]+)', content)
            dependencies.extend(imports)


def detect_circular_dependencies(files: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    """Detect circular dependencies between files."""
    dependency_graph = {}
    for file, deps in files.items():
        dependency_graph[file] = set(deps)

    circular_deps = []
    visited = set()
    path = []

    def dfs(node):
        if node in path:
            cycle = path[path.index(node) :]
            circular_deps.append(tuple(cycle))
        if node in visited:

        visited.add(node)
        path.append(node)

        for neighbor in dependency_graph.get(node, []):
            if dfs(neighbor):

        path.pop()

    for node in dependency_graph:
        if node not in visited:
            dfs(node)



def check_theme_alignment(file_path: str) -> Dict[str, Any]:
    """Check how well the frontend code aligns with rneui themed principles."""
    alignment_issues = []
    with open(file_path, "r") as f:
        content = f.read()
        if "makeStyles" not in content:
            alignment_issues.append("Missing makeStyles usage")
        if "theme." not in content:
            alignment_issues.append("Missing theme properties usage")
    return {"alignment_issues": alignment_issues}


@safe_file_operation
def check_code_quality(file_path: str) -> Dict[str, Any]:
    """Basic code quality checks, including theme alignment for frontend."""
    metrics = {
        "lines_of_code": 0,
        "comment_lines": 0,
        "empty_lines": 0,
        "todo_count": 0,
        "complexity_warnings": [],
        "theme_alignment": [],
    }

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            metrics["lines_of_code"] += 1

            if line.startswith(("#", "//")):
                metrics["comment_lines"] += 1
            elif not line:
                metrics["empty_lines"] += 1
            if "TODO" in line:
                metrics["todo_count"] += 1

            # Basic complexity warnings
            if line.count("if") + line.count("for") + line.count("while") > 2:
                metrics["complexity_warnings"].append(f"Complex line detected: {line}")

    # Check theme alignment for frontend files
    if file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        theme_alignment = check_theme_alignment(file_path)
        metrics["theme_alignment"].extend(theme_alignment["alignment_issues"])



def generate_documentation(categories: Dict[str, List[str]], features: Dict[str, List[str]]):
    """Generate comprehensive documentation."""
    docs_dir = "exports/docs"
    os.makedirs(docs_dir, exist_ok=True)

    # Generate main documentation
    with open(f"{docs_dir}/index.md", "w") as f:
        f.write("# Project Documentation\n\n")

        # Architecture Overview
        f.write("## Architecture Overview\n\n")
        f.write("### Backend Components\n")
        for category in ["CORE", "MODELS", "SERVICES", "ROUTES"]:
            if categories.get(category):
                f.write(f"#### {category}\n")
                for file in categories[category]:
                    f.write(f"- {file}\n")
                    # Add dependency information
                    try:
                        deps = analyze_dependencies(file)
                        if deps:
                            f.write("  Dependencies:\n")
                            for dep in deps:
                                f.write(f"    - {dep}\n")
                    except ExportError as e:
                        f.write(f"  Error analyzing dependencies: {str(e)}\n")

                    # Add code quality metrics
                    try:
                        metrics = check_code_quality(file)
                        f.write("  Metrics:\n")
                        f.write(f"    - Lines of code: {metrics['lines_of_code']}\n")
                        f.write(f"    - Comment lines: {metrics['comment_lines']}\n")
                        f.write(f"    - TODO count: {metrics['todo_count']}\n")
                    except ExportError as e:
                        f.write(f"  Error analyzing code quality: {str(e)}\n")

        # Feature Documentation
        f.write("\n## Features\n\n")
        for feature, files in features.items():
            if files:
                f.write(f"### {feature}\n")
                deps = set()
                for file in files:
                    try:
                        deps.update(analyze_dependencies(file))
                    except ExportError as e:
                        f.write(f"Error analyzing dependencies for {file}: {str(e)}\n")
                f.write("\nDependencies:\n")
                for dep in sorted(deps):
                    f.write(f"- {dep}\n")


def list_directories(start_path: str = "app") -> List[str]:
    """List all directories and subdirectories starting from start_path."""
    directories = []
    for root, dirs, _ in os.walk(start_path):
        for d in dirs:
            if not d.startswith("__") and not d.startswith("."):
                directories.append(os.path.join(root, d))


def group_files_by_category(start_path: str = "app") -> Dict[str, List[str]]:
    """Group files by their category (models, routes, services, etc.)."""
    categories = {
        "CORE": [],
        "MODELS": [],
        "SERVICES": [],
        "ROUTES": [],
        "SCHEMAS": [],
        "ENUMS": [],
        "ML": [],
        "TESTS": [],
        "UTILS": [],
        "HOOKS": [],
        "COMPONENTS": [],
        "CONTEXTS": [],
        "TYPES": [],
        "CONSTANTS": [],
        "CONFIG": [],
        "API": [],
        "ANIMATIONS": [],
        "THEME": [],
        "NAVIGATION": [],
        "ASSETS": [],
        "STORE": [],
        "ERRORS": [],
        "SECURITY": [],
        "MIDDLEWARE": [],
        "VALIDATORS": [],
        "MIGRATIONS": [],
        "LOCALIZATION": [],
    }

    for root, _, files in os.walk(start_path):
        # Skip node_modules directory
        if "node_modules" in root:

        for file in files:
            if not file.endswith((".py", ".ts", ".tsx")) or file.startswith("__"):

            file_path = os.path.join(root, file)

            # Backend categories
            if "models" in root:
                categories["MODELS"].append(file_path)
            elif "routes" in root:
                categories["ROUTES"].append(file_path)
            elif "services" in root:
                categories["SERVICES"].append(file_path)
            elif "schemas" in root:
                categories["SCHEMAS"].append(file_path)
            elif "enums" in root:
                categories["ENUMS"].append(file_path)
            elif "ml" in root:
                categories["ML"].append(file_path)
            elif "tests" in root:
                categories["TESTS"].append(file_path)
            elif "utils" in root:
                categories["UTILS"].append(file_path)
            elif "middleware" in root:
                categories["MIDDLEWARE"].append(file_path)
            elif "validators" in root:
                categories["VALIDATORS"].append(file_path)
            elif "migrations" in root:
                categories["MIGRATIONS"].append(file_path)
            # Frontend categories
            elif "hooks" in root:
                categories["HOOKS"].append(file_path)
            elif "components" in root:
                categories["COMPONENTS"].append(file_path)
            elif "contexts" in root:
                categories["CONTEXTS"].append(file_path)
            elif "types" in root:
                categories["TYPES"].append(file_path)
            elif "constants" in root:
                categories["CONSTANTS"].append(file_path)
            elif "config" in root:
                categories["CONFIG"].append(file_path)
            elif "api" in root:
                categories["API"].append(file_path)
            elif "animations" in root:
                categories["ANIMATIONS"].append(file_path)
            elif "theme" in root:
                categories["THEME"].append(file_path)
            elif "navigation" in root:
                categories["NAVIGATION"].append(file_path)
            elif "assets" in root:
                categories["ASSETS"].append(file_path)
            elif "store" in root:
                categories["STORE"].append(file_path)
            elif "errors" in root:
                categories["ERRORS"].append(file_path)
            elif "security" in root:
                categories["SECURITY"].append(file_path)
            elif "localization" in root:
                categories["LOCALIZATION"].append(file_path)
            elif "core" in root or root == start_path:
                categories["CORE"].append(file_path)



def group_files_by_feature(start_path: str = "app") -> Dict[str, List[str]]:
    """Group files by their feature (auth, scheduling, calendar, etc.)."""
    features = {
        "AUTH": [],
        "SCHEDULING": [],
        "CALENDAR": [],
        "BODY_DOUBLING": [],
        "HYPERFOCUS": [],
        "MENTAL_HEALTH": [],
        "ANALYTICS": [],
        "NOTIFICATIONS": [],
        "ADHD": [],
        "TASK_MANAGEMENT": [],
        "ENERGY_TRACKING": [],
        "FOCUS_TRACKING": [],
        "GAMIFICATION": [],
        "POMODORO": [],
        "MINDFULNESS": [],
        "TIME_MANAGEMENT": [],
        "VISUALIZATION": [],
        "USER_SETTINGS": [],
        "SYNC": [],
        "SOCIAL": [],
        "ACCESSIBILITY": [],
        "SECURITY": [],
        "CORE": [],
    }

    keywords = {
        "AUTH": ["auth", "user", "login", "register", "password", "security"],
        "SCHEDULING": ["schedul", "block", "time_block", "task", "calendar", "timeline"],
        "CALENDAR": ["calendar", "event", "appointment", "schedule", "sync"],
        "BODY_DOUBLING": ["body_doubling", "session", "pair", "accountability"],
        "HYPERFOCUS": ["hyperfocus", "focus_session", "deep_work", "concentration"],
        "MENTAL_HEALTH": ["mental", "health", "mindful", "wellness", "mood", "emotion"],
        "ANALYTICS": ["analytic", "stat", "metric", "track", "report", "insight"],
        "NOTIFICATIONS": ["notif", "remind", "alert", "message"],
        "TASK_MANAGEMENT": ["task", "todo", "checklist", "priority", "deadline"],
        "ENERGY_TRACKING": ["energy", "fatigue", "stamina", "productivity"],
        "FOCUS_TRACKING": ["focus", "attention", "concentration", "distraction"],
        "GAMIFICATION": ["game", "point", "badge", "achievement", "reward", "streak"],
        "POMODORO": ["pomodoro", "timer", "break", "session", "interval"],
        "MINDFULNESS": ["mindful", "meditation", "breathing", "calm"],
        "TIME_MANAGEMENT": ["time", "schedule", "planning", "organization"],
        "VISUALIZATION": ["visual", "chart", "graph", "display", "view"],
        "USER_SETTINGS": ["setting", "preference", "config", "profile"],
        "SYNC": ["sync", "integration", "connect", "external"],
        "SOCIAL": ["social", "share", "collaborate", "community"],
        "ACCESSIBILITY": ["accessibility", "a11y", "assist", "support"],
        "ADHD": [
            "adhd",
            "distraction",
            "medication",
            "executive_function",
            "focus",
            "accommodation",
            "gamification",
            "energy_management",
            "time_blindness",
            "working_memory",
            "task_initiation",
            "task_switching",
            "prioritization",
            "adhd_settings",
            "hyperfocus",
            "pomodoro",
            "body_doubling",
            "mindfulness",
            "mental_health",
            "attention",
            "concentration",
            "routine",
            "schedule",
            "reminder",
            "timer",
            "task_management",
            "productivity",
            "motivation",
            "procrastination",
            "organization",
            "planning",
            "time_management",
            "fidget",
            "stim",
            "sensory",
        ],
    }

    for root, _, files in os.walk(start_path):
        # Skip node_modules directory
        if "node_modules" in root:

        for file in files:
            if not file.endswith((".py", ".ts", ".tsx")) or file.startswith("__"):

            file_path = os.path.join(root, file)
            try:
                file_content = Path(file_path).read_text()
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

            # First try to match by directory name
            dir_matched = False
            for feature in features.keys():
                if feature.lower() in root.lower():
                    features[feature].append(file_path)
                    dir_matched = True

            if dir_matched:

            # Then try to match by keywords
            matched = False
            for feature, patterns in keywords.items():
                if any(
                    pattern in file_path.lower() or pattern in file_content.lower()
                ):
                    features[feature].append(file_path)
                    matched = True

            if not matched:
                features["CORE"].append(file_path)



def create_consolidated_file(files: List[str], output_path: str, category: str):
    """Create a single consolidated file for a category."""
    print(f"Creating consolidated file: {output_path}")
    with open(output_path, "w") as outfile:
        outfile.write(f"# Consolidated {category} File\n\n")

        for file_path in files:
            if os.path.exists(file_path):
                outfile.write(f"# From: {file_path}\n")
                try:
                    with open(file_path, "r") as infile:
                        content = infile.read()
                        outfile.write(content)
                        if not content.endswith("\n\n"):
                            outfile.write("\n\n")
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")


def create_exports(categories: Dict[str, List[str]], features: Dict[str, List[str]]):
    """Create export files organized by category and feature."""
    exports_dir = "exports"
    if os.path.exists(exports_dir):
        shutil.rmtree(exports_dir)
    os.makedirs(exports_dir)

    # Create category-based exports
    category_dir = os.path.join(exports_dir, "by_category")
    os.makedirs(category_dir)
    for category, files in categories.items():
        if files:
            category_path = os.path.join(category_dir, category.lower())
            os.makedirs(category_path)
            print(f"\nProcessing category: {category}")

            # Create individual files
            for file in files:
                if os.path.exists(file):
                    dest = os.path.join(category_path, os.path.basename(file))
                    print(f"  Copying: {file} -> {dest}")
                    shutil.copy2(file, dest)

            # Create consolidated file
            consolidated_path = os.path.join(category_path, f"{category.lower()}_all.py")
            create_consolidated_file(files, consolidated_path, category)

            # Create __init__.py
            init_path = os.path.join(category_path, "__init__.py")
            print(f"  Creating: {init_path}")
            with open(init_path, "w") as f:
                f.write(f"# {category} exports\n")
                for file in files:
                    module_name = os.path.splitext(os.path.basename(file))[0]
                    if file.endswith(".py"):
                        f.write(f"from .{module_name} import *\n")
                    elif file.endswith((".ts", ".tsx")):
                        f.write(f"export * from './{module_name}';\n")

    # Create feature-based exports
    feature_dir = os.path.join(exports_dir, "by_feature")
    os.makedirs(feature_dir)
    for feature, files in features.items():
        if files:
            feature_path = os.path.join(feature_dir, feature.lower())
            os.makedirs(feature_path)
            print(f"\nProcessing feature: {feature}")

            # Separate backend and frontend files
            backend_files = [f for f in files if f.endswith(".py")]
            frontend_files = [f for f in files if f.endswith((".ts", ".tsx"))]

            # Create backend directory if needed
            if backend_files:
                backend_path = os.path.join(feature_path, "backend")
                os.makedirs(backend_path)

                # Copy backend files
                for file in backend_files:
                    if os.path.exists(file):
                        dest = os.path.join(backend_path, os.path.basename(file))
                        print(f"  Copying: {file} -> {dest}")
                        shutil.copy2(file, dest)

                # Create consolidated backend file
                consolidated_path = os.path.join(backend_path, f"{feature.lower()}_backend_all.py")
                create_consolidated_file(backend_files, consolidated_path, f"{feature} Backend")

                # Create backend __init__.py
                init_path = os.path.join(backend_path, "__init__.py")
                print(f"  Creating: {init_path}")
                with open(init_path, "w") as f:
                    f.write(f"# {feature} backend exports\n")
                    for file in backend_files:
                        module_name = os.path.splitext(os.path.basename(file))[0]
                        f.write(f"from .{module_name} import *\n")

            # Create frontend directory if needed
            if frontend_files:
                frontend_path = os.path.join(feature_path, "frontend")
                os.makedirs(frontend_path)

                # Copy frontend files
                for file in frontend_files:
                    if os.path.exists(file):
                        dest = os.path.join(frontend_path, os.path.basename(file))
                        print(f"  Copying: {file} -> {dest}")
                        shutil.copy2(file, dest)

                # Create consolidated frontend file
                consolidated_path = os.path.join(
                    frontend_path, f"{feature.lower()}_frontend_all.ts"
                )
                create_consolidated_file(frontend_files, consolidated_path, f"{feature} Frontend")

                # Create frontend index.ts
                index_path = os.path.join(frontend_path, "index.ts")
                print(f"  Creating: {index_path}")
                with open(index_path, "w") as f:
                    f.write(f"// {feature} frontend exports\n")
                    for file in frontend_files:
                        module_name = os.path.splitext(os.path.basename(file))[0]
                        f.write(f"export * from './{module_name}';\n")

            # Create feature README.md
            readme_path = os.path.join(feature_path, "README.md")
            print(f"  Creating: {readme_path}")
            with open(readme_path, "w") as f:
                f.write(f"# {feature}\n\n")
                if backend_files:
                    f.write("## Backend Components\n\n")
                    for file in backend_files:
                        f.write(f"- {os.path.basename(file)}\n")
                if frontend_files:
                    f.write("\n## Frontend Components\n\n")
                    for file in frontend_files:
                        f.write(f"- {os.path.basename(file)}\n")


def main():
    """Main function to organize and export files."""
    try:
        # Setup logging
        setup_logging()
        logging.info("Starting export organization process...")

        # Load configuration
        config = load_config()
        logging.info("Configuration loaded successfully")

        # Process backend (app) directory
        logging.info("Processing backend directory...")
        backend_directories = list_directories("app")
        for d in backend_directories:
            logging.info(f"Found backend directory: {d}")

        backend_categories = group_files_by_category("app")
        logging.info("Backend categories processed")

        backend_features = group_files_by_feature("app")
        logging.info("Backend features processed")

        # Process frontend directory
        logging.info("Processing frontend directory...")
        frontend_directories = list_directories("frontend")
        for d in frontend_directories:
            logging.info(f"Found frontend directory: {d}")

        frontend_categories = group_files_by_category("frontend")
        logging.info("Frontend categories processed")

        frontend_features = group_files_by_feature("frontend")
        logging.info("Frontend features processed")

        # Analyze dependencies
        logging.info("Analyzing dependencies...")
        all_files = {}
        for category in backend_categories.values():
            for file in category:
                try:
                    deps = analyze_dependencies(file)
                    all_files[file] = deps
                except ExportError as e:
                    logging.warning(f"Could not analyze dependencies for {file}: {e}")

        # Check for circular dependencies
        logging.info("Checking for circular dependencies...")
        circular_deps = detect_circular_dependencies(all_files)
        if circular_deps:
            logging.warning("Circular dependencies detected:")
            for cycle in circular_deps:
                logging.warning(f"Cycle: {' -> '.join(cycle)}")

        # Merge backend and frontend files
        logging.info("Merging backend and frontend files...")
        all_categories = backend_categories.copy()
        for category, files in frontend_categories.items():
            if category in all_categories:
                all_categories[category].extend(files)
            else:
                all_categories[category] = files

        all_features = backend_features.copy()
        for feature, files in frontend_features.items():
            if feature in all_features:
                all_features[feature].extend(files)
            else:
                all_features[feature] = files

        # Create exports
        logging.info("Creating exports...")
        if config["export_settings"]["create_consolidated_files"]:
            create_exports(all_categories, all_features)

        # Generate documentation
        if config["export_settings"]["create_documentation"]:
            logging.info("Generating documentation...")
            generate_documentation(all_categories, all_features)

        # Code quality summary
        logging.info("Generating code quality metrics...")
        quality_metrics = {}
        for category, files in all_categories.items():
            quality_metrics[category] = {
                "total_lines": 0,
                "comment_lines": 0,
                "todo_count": 0,
                "complexity_warnings": [],
                "theme_alignment": [],
            }
            for file in files:
                try:
                    metrics = check_code_quality(file)
                    quality_metrics[category]["total_lines"] += metrics["lines_of_code"]
                    quality_metrics[category]["comment_lines"] += metrics["comment_lines"]
                    quality_metrics[category]["todo_count"] += metrics["todo_count"]
                    quality_metrics[category]["complexity_warnings"].extend(
                        metrics["complexity_warnings"]
                    )
                    quality_metrics[category]["theme_alignment"].extend(metrics["theme_alignment"])
                except ExportError as e:
                    logging.warning(f"Could not analyze code quality for {file}: {e}")

        # Write code quality summary
        with open("exports/code_quality_summary.md", "w") as f:
            f.write("# Code Quality Summary\n\n")
            for category, metrics in quality_metrics.items():
                f.write(f"## {category}\n")
                f.write(f"- Total lines of code: {metrics['total_lines']}\n")
                f.write(f"- Comment lines: {metrics['comment_lines']}\n")
                f.write(f"- TODO items: {metrics['todo_count']}\n")
                if metrics["complexity_warnings"]:
                    f.write("\nComplexity Warnings:\n")
                    for warning in metrics["complexity_warnings"]:
                        f.write(f"- {warning}\n")
                if metrics["theme_alignment"]:
                    f.write("\nTheme Alignment Issues:\n")
                    for issue in metrics["theme_alignment"]:
                        f.write(f"- {issue}\n")
                f.write("\n")

        logging.info("Export organization completed successfully!")

    except Exception as e:
        logging.error(f"Error during export organization: {str(e)}")


if __name__ == "__main__":
    main()

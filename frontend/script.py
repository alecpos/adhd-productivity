import os


def export_and_combine_folder_contents():
    """
    Traverse each folder and subfolder in the current directory (excluding 'node_modules' and specified directories),
    and combine all exports into a single consolidated file.
    """
    # Get the current working directory
    current_dir = os.getcwd()

    # Directories to exclude
    exclude_dirs = {"node_modules", ".git", ".expo", ".expo-shared", "__pycache__"}

    # File extensions to include
    include_extensions = {".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".html", ".md", ".txt"}

    # Get all items in the current directory
    items = os.listdir(current_dir)

    # Filter out files, keep only directories, excluding specified directories
    folders = [
        item
        for item in items
        if os.path.isdir(os.path.join(current_dir, item)) and item not in exclude_dirs
    ]

    # Create a single consolidated file
    consolidated_file = os.path.join(current_dir, "frontend_consolidated_export.txt")

    with open(consolidated_file, "w", encoding="utf-8") as consolidated_outfile:
        for folder in folders:
            # Recursively traverse directories and create a single export per top-level directory
            output_file = os.path.join(current_dir, f"{folder}_export.txt")
            with open(output_file, "w", encoding="utf-8") as outfile:
                for root, dirs, files in os.walk(os.path.join(current_dir, folder)):
                    # Exclude specified directories
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]

                    for file in files:
                        # Include only files with the allowed extensions
                        if any(file.endswith(ext) for ext in include_extensions):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r", encoding="utf-8") as infile:
                                    # Write the file content with a header indicating the relative path
                                    relative_file_path = os.path.relpath(
                                        file_path, start=current_dir
                                    )
                                    header = f"--- File: {relative_file_path} ---\n"
                                    content = infile.read()

                                    # Write to the folder-specific file
                                    outfile.write(header)
                                    outfile.write(content)
                                    outfile.write("\n\n")

                                    # Write to the consolidated file
                                    consolidated_outfile.write(header)
                                    consolidated_outfile.write(content)
                                    consolidated_outfile.write("\n\n")
                            except Exception as e:
                                print(f"Error reading file {file_path}: {e}")
            print(f"Exported contents of folder '{folder}' to '{output_file}'.")

        print(f"Consolidated all folder exports into '{consolidated_file}'.")


if __name__ == "__main__":
    export_and_combine_folder_contents()

import os

from src.config import Config

"""
TODO: Replace this with `code2prompt` - https://github.com/mufeedvh/code2prompt
"""

class ReadCode:
    def __init__(self, project_name: str):
        """        Initialize the project directory path.

        Args:
            project_name (str): The name of the project.
        """

        config = Config()
        project_path = config.get_projects_dir()
        self.directory_path = os.path.join(project_path, project_name.lower().replace(" ", "-"))

    def read_directory(self):
        """        Reads the files from the specified directory and returns a list of dictionaries containing file information.

        It iterates through the directory and reads the content of each file, then appends the file information to a list of dictionaries.

        Returns:
            list: A list of dictionaries containing file information, where each dictionary has keys 'filename' and 'code'.
        """

        files_list = []
        for root, _dirs, files in os.walk(self.directory_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as file_content:
                        files_list.append({"filename": file_path, "code": file_content.read()})
                except:
                    pass

        return files_list

    def code_set_to_markdown(self):
        """        Generate markdown content from a set of code snippets.

        This method reads a directory to obtain a set of code snippets and then generates markdown content
        by formatting each code snippet with filename and code, separated by a horizontal line.

        Returns:
            str: The generated markdown content.
        """

        code_set = self.read_directory()
        markdown = ""
        for code in code_set:
            markdown += f"### {code['filename']}:\n\n"
            markdown += f"```\n{code['code']}\n```\n\n"
            markdown += "---\n\n"
        return markdown

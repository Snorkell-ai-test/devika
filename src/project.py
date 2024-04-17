import os
import json
import zipfile
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from src.config import Config

class Projects(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    message_stack_json: str

class ProjectManager:
    def __init__(self):
        """        Initialize the database connection and create tables if they do not exist.

        It initializes the database connection using the SQLite database path obtained from the configuration.
        It also sets the project path and creates tables in the database if they do not exist.

        Args:
            self: The object instance.
        """

        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.project_path = config.get_projects_dir()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_message(self):
        """        Create a new message dictionary with a timestamp.

        This function creates a new message dictionary with a timestamp and returns it.

        Returns:
            dict: A dictionary containing the following keys:
                - "from_devika" (bool): True
                - "message" (NoneType): None
                - "timestamp" (str): The current timestamp in the format "%Y-%m-%d %H:%M:%S"
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "from_devika": True,
            "message": None,
            "timestamp": timestamp
        }

    def create_project(self, project: str):
        """        Create a new project in the database.

        This function creates a new project in the database with the given project name and an empty message stack.

        Args:
            project (str): The name of the project to be created.
        """

        with Session(self.engine) as session:
            project_state = Projects(project=project, message_stack_json=json.dumps([]))
            session.add(project_state)
            session.commit()

    def delete_project(self, project: str):
        """        Delete a project from the database.

        This function deletes the specified project from the database.

        Args:
            project (str): The name of the project to be deleted.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                session.delete(project_state)
                session.commit()

    def add_message_to_project(self, project: str, message: dict):
        """        Add a message to the message stack of a project.

        This function adds a message to the message stack of a project. If the project already exists, the message is appended
        to the existing message stack. If the project does not exist, a new project is created with the provided message.

        Args:
            project (str): The name of the project.
            message (dict): The message to be added to the project's message stack.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                message_stack.append(message)
                project_state.message_stack_json = json.dumps(message_stack)
                session.commit()
            else:
                message_stack = [message]
                project_state = Projects(project=project, message_stack_json=json.dumps(message_stack))
                session.add(project_state)
                session.commit()

    def add_message_from_devika(self, project: str, message: str):
        """        Add a message to a specific project.

        This method creates a new message and adds it to the specified project.

        Args:
            project (str): The name of the project to which the message will be added.
            message (str): The content of the message to be added.
        """

        new_message = self.new_message()
        new_message["message"] = message
        self.add_message_to_project(project, new_message)
        
    def add_message_from_user(self, project: str, message: str):
        """        Add a message from a user to the specified project.

        This method creates a new message with the provided content and sets the 'from_devika' flag to False before adding it to the specified project.

        Args:
            project (str): The name of the project to which the message will be added.
            message (str): The content of the message to be added.
        """

        new_message = self.new_message()
        new_message["message"] = message
        new_message["from_devika"] = False
        self.add_message_to_project(project, new_message)

    def get_messages(self, project: str):
        """        Retrieve the messages for a specific project.

        This function retrieves the messages for a specific project from the database.

        Args:
            project (str): The name of the project.

        Returns:
            dict: A dictionary containing the messages for the specified project.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                return json.loads(project_state.message_stack_json)
            return None
        
    def get_latest_message_from_user(self, project: str):
        """        Get the latest message from a user for a specific project.

        Retrieves the latest message from the message stack of a specific project.

        Args:
            project (str): The name of the project.

        Returns:
            dict or None: The latest message from a user if found, otherwise None.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in reversed(message_stack):
                    if not message["from_devika"]:
                        return message
            return None

    def validate_last_message_is_from_user(self, project: str):
        """        Validate if the last message is from the user in a specific project.

        This function checks the last message in the message stack of a project to determine if it is from the user.

        Args:
            project (str): The name of the project.

        Returns:
            bool: True if the last message is from the user, False otherwise.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                if message_stack:
                    return not message_stack[-1]["from_devika"]
            return False

    def get_latest_message_from_devika(self, project: str):
        """        Get the latest message from Devika for a specific project.

        This function retrieves the latest message sent by Devika for a specific project.

        Args:
            project (str): The name of the project.

        Returns:
            dict or None: The latest message sent by Devika for the specified project, or None if no message is found.
        """

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in reversed(message_stack):
                    if message["from_devika"]:
                        return message
            return None

    def get_project_list(self):
        """        Get the list of projects from the database.

        This function retrieves the list of projects from the database using a session and returns a list of project names.

        Returns:
            list: A list of project names.
        """

        with Session(self.engine) as session:
            projects = session.query(Projects).all()
            return [project.project for project in projects]
        
    def get_all_messages_formatted(self, project: str):
        """        Get all messages formatted for a specific project.

        This function retrieves all messages for a specific project from the database and formats them for display.

        Args:
            project (str): The name of the project.

        Returns:
            list: A list of formatted messages for the specified project.
        """

        formatted_messages = []
        
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in message_stack:
                    if message["from_devika"]:
                        formatted_messages.append(f"Devika: {message['message']}")
                    else:
                        formatted_messages.append(f"User: {message['message']}")
                        
            return formatted_messages

    def get_project_path(self, project: str):
        """        Returns the path of the specified project.

        This function takes a project name as input and returns the path of the project by joining it with the base project path
        after converting the project name to lowercase and replacing spaces with hyphens.

        Args:
            project (str): The name of the project.

        Returns:
            str: The path of the specified project.
        """

        return os.path.join(self.project_path, project.lower().replace(" ", "-"))
    
    def project_to_zip(self, project: str):
        """        Compresses the specified project directory into a zip file.

        Args:
            project (str): The name of the project directory to be zipped.

        Returns:
            str: The file path of the generated zip file.
        """

        project_path = self.get_project_path(project)
        zip_path = f"{project_path}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), os.path.join(project_path, '..'))
                    zipf.write(os.path.join(root, file), arcname=relative_path)
                    
        return zip_path
    
    def get_zip_path(self, project: str):
        """        Returns the path of the zip file for the specified project.

        Args:
            project (str): The name of the project.

        Returns:
            str: The path of the zip file for the specified project.
        """

        return f"{self.get_project_path(project)}.zip"
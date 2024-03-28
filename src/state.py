import json
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from src.config import Config

class AgentStateModel(SQLModel, table=True):
    __tablename__ = "agent_state"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    state_stack_json: str

class AgentState:
    def __init__(self):
        """        Initialize the database engine for the application.

        It initializes the database engine using the sqlite database path obtained from the application configuration.

        Args:
            self: The instance of the class.
        """

        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_state(self):
        """        Creates a new state object with default values for various attributes.

        Returns:
            dict: A dictionary representing the new state object with default values for various attributes.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "internal_monologue": None,
            "browser_session": {
                "url": None,
                "screenshot": None
            },
            "terminal_session": {
                "command": None,
                "output": None,
                "title": None
            },
            "step": None,
            "message": None,
            "completed": False,
            "agent_is_active": True,
            "token_usage": 0,
            "timestamp": timestamp
        }

    def delete_state(self, project: str):
        """        Delete the state of a project.

        This function deletes the state of a project from the database, if it exists.

        Args:
            project (str): The name of the project.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                session.delete(agent_state)
                session.commit()

    def add_to_current_state(self, project: str, state: dict):
        """        Add a state to the current state stack for a specific project.

        This function adds a state to the current state stack for a specific project. If the project already has a state stack,
        the new state is appended to the existing stack. If the project does not have a state stack, a new stack is created
        with the provided state.

        Args:
            project (str): The name of the project.
            state (dict): The state to be added to the stack.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack.append(state)
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [state]
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def get_current_state(self, project: str):
        """        Get the current state of the agent for a specific project.

        Retrieves the current state of the agent for the specified project from the database.

        Args:
            project (str): The name of the project.

        Returns:
            dict or None: A dictionary representing the current state of the agent if available,
                                  otherwise None.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)
            return None
 
    def update_latest_state(self, project: str, state: dict):
        """        Update the latest state of a project in the database.

        This function updates the latest state of a project in the database. If the project already has a state, it updates the state stack with the new state. If the project does not have a state, it creates a new state stack with the provided state.

        Args:
            project (str): The name of the project.
            state (dict): The new state to be updated.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1] = state
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [state]
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def get_latest_state(self, project: str):
        """        Get the latest state of a project's agent.

        This function retrieves the latest state of an agent for a specific project from the database.

        Args:
            project (str): The name of the project.

        Returns:
            dict or None: The latest state of the agent for the specified project as a dictionary, or None if no state is found.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]
            return None

    def set_agent_active(self, project: str, is_active: bool):
        """        Set the active state of an agent for a specific project.

        This function updates the active state of an agent for a specific project in the database.
        If the agent state for the project already exists, it updates the existing state. If not, it creates a new state.

        Args:
            project (str): The name of the project.
            is_active (bool): The new active state of the agent.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["agent_is_active"] = is_active
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["agent_is_active"] = is_active
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def is_agent_active(self, project: str):
        """        Check if the agent is active for a specific project.

        This function queries the database for the agent state of the specified project and returns
        the active status of the agent.

        Args:
            project (str): The name of the project.

        Returns:
            bool or None: The active status of the agent for the specified project. Returns None if no
            agent state is found for the project.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["agent_is_active"]
            return None

    def set_agent_completed(self, project: str, is_completed: bool):
        """        Set the completion status of an agent for a specific project.

        This function updates the completion status of an agent for a specific project in the database.
        If an agent state for the project already exists, it updates the completion status in the existing state stack.
        If not, it creates a new agent state with the completion status.

        Args:
            project (str): The name of the project.
            is_completed (bool): The completion status to be set.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["completed"] = is_completed
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["completed"] = is_completed
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()
                
    def is_agent_completed(self, project: str):
        """        Check if the agent has completed the project.

        This function checks the completion status of the agent for a specific project. It queries the database to retrieve
        the agent state for the given project and returns the completion status.

        Args:
            project (str): The name of the project.

        Returns:
            bool or None: The completion status of the agent for the specified project. Returns None if no agent state is found.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["completed"]
            return None
            
    def update_token_usage(self, project: str, token_usage: int):
        """        Update the token usage for a specific project in the agent state.

        This function updates the token usage for a specific project in the agent state. If the agent state for the project
        already exists, it updates the token usage in the existing state. If the agent state does not exist, it creates a new
        state for the project and sets the token usage.

        Args:
            project (str): The name of the project.
            token_usage (int): The amount of token usage to be updated.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            print(agent_state)
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["token_usage"] += token_usage
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["token_usage"] = token_usage
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def get_latest_token_usage(self, project: str):
        """        Get the latest token usage for a specific project.

        Retrieves the latest token usage for a specific project from the database.

        Args:
            project (str): The name of the project.

        Returns:
            int: The latest token usage for the specified project, or 0 if no token usage is found.
        """

        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["token_usage"]
            return 0
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import os
import logging
from threading import Thread

import tiktoken

from src.init import init_devika
from src.config import Config

from src.logger import Logger, route_logger
from src.project import ProjectManager
from src.state import AgentState

from src.agents import Agent
from src.llm import LLM

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.disabled = True
CORS(app)

logger = Logger()

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

os.environ["TOKENIZERS_PARALLELISM"] = "false"


@app.route("/api/create-project", methods=["POST"])
@route_logger(logger)
def create_project():
    """    Create a new project.

    This function creates a new project using the project name provided in the request data.

    Returns:
        dict: A JSON object with a message indicating the successful creation of the project.
    """

    data = request.json
    project_name = data.get("project_name")
    ProjectManager().create_project(project_name)
    return jsonify({"message": "Project created"})


@app.route("/api/execute-agent", methods=["POST"])
@route_logger(logger)
def execute_agent():
    """    Execute an agent to process a prompt using a specified base model and project name.

    This function takes in a JSON request containing a prompt, base model, and project name. It then creates a new thread to execute an Agent with the specified base model and project name.

    Returns:
        JSON: A message indicating that the Devika Agent has been started.
    """

    data = request.json
    prompt = data.get("prompt")
    base_model = data.get("base_model")
    project_name = data.get("project_name")

    if not base_model:
        return jsonify({"error": "base_model is required"})

    thread = Thread(
        target=lambda: Agent(base_model=base_model).execute(prompt, project_name)
    )
    thread.start()

    return jsonify({"message": "Started Devika Agent"})


@app.route("/api/get-browser-snapshot", methods=["GET"])
@route_logger(logger)
def browser_snapshot():
    """    Generate a snapshot of the browser.

    This function takes a snapshot path as input and returns the file as an attachment.

    Args:
        snapshot_path (str): The path to the snapshot file.

    Returns:
        file: The snapshot file as an attachment.
    """

    snapshot_path = request.args.get("snapshot_path")
    return send_file(snapshot_path, as_attachment=True)


@app.route("/api/download-project", methods=["GET"])
@route_logger(logger)
def download_project():
    """    Download a project as a zip file.

    This function takes the project name from the request arguments, converts the project to a zip file using ProjectManager,
    retrieves the path of the zip file, and sends the file as a response.

    Returns:
        File: The project zip file.
    """

    project_name = request.args.get("project_name")
    ProjectManager().project_to_zip(project_name)
    project_path = ProjectManager().get_zip_path(project_name)
    return send_file(project_path, as_attachment=False)


@app.route("/api/download-project-pdf", methods=["GET"])
@route_logger(logger)
def download_project_pdf():
    """    Download the PDF file for a specific project.

    This function retrieves the project name from the request arguments, constructs the path to the corresponding PDF file,
    and returns the PDF file as a response.

    Returns:
        response: A response object containing the requested PDF file.
    """

    project_name = request.args.get("project_name")
    pdf_dir = Config().get_pdfs_dir()
    pdf_path = os.path.join(pdf_dir, f"{project_name}.pdf")

    response = make_response(send_file(pdf_path))
    response.headers['Content-Type'] = 'application/pdf'
    return response


@app.route("/api/get-messages", methods=["POST"])
@route_logger(logger)
def get_messages():
    """    Get messages for a specific project.

    Retrieves messages for a specific project by extracting the project name from the JSON data
    and then fetching the messages using the ProjectManager class.

    Returns:
        dict: A dictionary containing the messages for the specified project.
    """

    data = request.json
    project_name = data.get("project_name")
    messages = ProjectManager().get_messages(project_name)
    return jsonify({"messages": messages})


@app.route("/api/send-message", methods=["POST"])
@route_logger(logger)
def send_message():
    """    Send a message to a project and trigger subsequent execution if the agent is completed.

    This function takes in a JSON request containing a message, project name, and base model. It then creates a new message
    and adds it to the specified project. If the agent for the project is completed, it triggers subsequent execution
    using a separate thread.

    Returns:
        dict: A JSON response indicating that the message has been sent.
    """

    data = request.json
    message = data.get("message")
    project_name = data.get("project_name")
    base_model = data.get("base_model")

    new_message = ProjectManager().new_message()
    new_message["message"] = message
    new_message["from_devika"] = False
    ProjectManager().add_message_to_project(project_name, new_message)

    if AgentState().is_agent_completed(project_name):
        thread = Thread(
            target=lambda: Agent(base_model=base_model).subsequent_execute(message, project_name)
        )
        thread.start()

    return jsonify({"message": "Message sent"})


@app.route("/api/project-list", methods=["GET"])
@route_logger(logger)
def project_list():
    """    Get the list of projects.

    This function retrieves the list of projects from the ProjectManager and returns it as a JSON response.

    Returns:
        dict: A JSON object containing the list of projects.
    """

    pm = ProjectManager()
    projects = pm.get_project_list()
    return jsonify({"projects": projects})


@app.route("/api/model-list", methods=["GET"])
@route_logger(logger)
def model_list():
    """    Returns a list of available models.

    This function retrieves a list of available models using the LLM class and returns the list in a JSON format.

    Returns:
        dict: A dictionary containing the list of available models.
    """

    models = LLM().list_models()
    return jsonify({"models": models})


@app.route("/api/is-agent-active", methods=["POST"])
@route_logger(logger)
def is_agent_active():
    """    Check if the agent is active for a given project.

    This function checks the activity status of an agent for a specific project by retrieving the project name from the request data and then calling the 'is_agent_active' method of the AgentState class.

    Returns:
        dict: A JSON object containing the activity status of the agent for the specified project.
    """

    data = request.json
    project_name = data.get("project_name")
    is_active = AgentState().is_agent_active(project_name)
    return jsonify({"is_active": is_active})


@app.route("/api/get-agent-state", methods=["POST"])
@route_logger(logger)
def get_agent_state():
    """    Get the latest state of an agent for a specific project.

    Retrieves the latest state of an agent for a specified project by using the project name from the request data.

    Returns:
        dict: A JSON object containing the state of the agent for the specified project.
    """

    data = request.json
    project_name = data.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    return jsonify({"state": agent_state})


@app.route("/api/calculate-tokens", methods=["POST"])
@route_logger(logger)
def calculate_tokens():
    """    Calculate the number of tokens used in a given prompt.

    It calculates the number of tokens used in the input prompt using the TIKTOKEN_ENC encoding.

    Returns:
        dict: A dictionary containing the token usage count.
    """

    data = request.json
    prompt = data.get("prompt")
    tokens = len(TIKTOKEN_ENC.encode(prompt))
    return jsonify({"token_usage": tokens})


@app.route("/api/token-usage", methods=["GET"])
@route_logger(logger)
def token_usage():
    """    Get the latest token usage for a specific project.

    This function retrieves the latest token usage for a specific project by querying the AgentState class.

    Returns:
        dict: A JSON object containing the token usage for the specified project.
    """

    project_name = request.args.get("project_name")
    token_count = AgentState().get_latest_token_usage(project_name)
    return jsonify({"token_usage": token_count})


@app.route("/api/real-time-logs", methods=["GET"])
def real_time_logs():
    """    Returns the real-time logs from the log file.

    This function reads the log file using the Logger class and returns the log file content in JSON format.

    Returns:
        dict: A dictionary containing the log file content.
    """

    log_file = Logger().read_log_file()
    return jsonify({"log_file": log_file})


@app.route("/api/get-browser-session", methods=["GET"])
@route_logger(logger)
def get_browser_session():
    """    Get the browser session for a specific project.

    Retrieves the latest agent state for the specified project and returns the browser session if available.

    Returns:
        dict: A dictionary containing the browser session information.
    """

    project_name = request.args.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    if not agent_state:
        return jsonify({"session": None})
    else:
        browser_session = agent_state["browser_session"]
        return jsonify({"session": browser_session})


@app.route("/api/get-terminal-session", methods=["GET"])
@route_logger(logger)
def get_terminal_session():
    """    Get the latest terminal session state for a given project.

    Retrieves the latest state of the agent for the specified project and returns the terminal session state if available.

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: A JSON object containing the terminal session state.
    """

    project_name = request.args.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    if not agent_state:
        return jsonify({"terminal_state": None})
    else:
        terminal_state = agent_state["terminal_session"]
        return jsonify({"terminal_state": terminal_state})


@app.route("/api/run-code", methods=["POST"])
@route_logger(logger)
def run_code():
    """    Run the provided code for a specific project.

    This function takes the project name and code as input and executes the code for the specified project.

    Args:
        project_name (str): The name of the project for which the code will be executed.
        code (str): The code to be executed.

    Returns:
        dict: A JSON object with a message indicating that the code execution has started.
    """

    data = request.json
    project_name = data.get("project_name")
    code = data.get("code")
    # TODO: Implement code execution logic
    return jsonify({"message": "Code execution started"})


@app.route("/api/set-settings", methods=["POST"])
@route_logger(logger)
def set_settings():
    """    Set the application settings based on the provided data.

    It updates the application configuration with the provided data and saves the configuration.

    Returns:
        dict: A JSON response indicating that the settings have been updated.
    """

    data = request.json
    config = Config()
    config.config.update(data)
    config.save_config()
    return jsonify({"message": "Settings updated"})


@app.route("/api/get-settings", methods=["GET"])
@route_logger(logger)
def get_settings():
    """    Get the settings from the configuration and return them as a JSON response.

    Returns:
        dict: A JSON object containing the settings from the configuration.
    """

    config = Config().get_config()
    return jsonify({"settings": config})


if __name__ == "__main__":
    logger.info("Booting up... This may take a few seconds")
    init_devika()
    app.run(debug=False, port=1337, host="0.0.0.0")

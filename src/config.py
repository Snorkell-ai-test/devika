import toml
from os import environ


class Config:
    _instance = None

    def __new__(cls):
        """        Create a new instance of the class.

        This method is responsible for creating a new instance of the class if it does not already exist.
        It loads the configuration from the "config.toml" file and assigns it to the instance.

        Returns:
            object: The instance of the class.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = toml.load("config.toml")
        return cls._instance

    def __init__(self):
        """        Initialize the object with configuration settings loaded from 'config.toml'.

        Loads the configuration settings from the 'config.toml' file and assigns them to the 'config' attribute.


        Raises:
            FileNotFoundError: If the 'config.toml' file is not found.
            toml.TomlDecodeError: If the 'config.toml' file is not a valid TOML file.
        """

        self.config = toml.load("config.toml")

    def get_config(self):
        """        Returns the configuration settings.

        This function returns the configuration settings stored in the 'config' attribute of the object.

        Returns:
            dict: A dictionary containing the configuration settings.
        """

        return self.config

    def get_bing_api_key(self):
        """        Returns the Bing API key from the environment variable or the configuration file.

        If the Bing API key is set as an environment variable, it returns the value of the environment variable.
        If the Bing API key is not set as an environment variable, it returns the Bing API key from the configuration file.

        Returns:
            str: The Bing API key.
        """

        return environ.get("BING_API_KEY", self.config["API_KEYS"]["BING"])

    def get_bing_api_endpoint(self):
        """        Returns the Bing API endpoint.

        This function retrieves the Bing API endpoint from the environment variables. If the environment variable is not set, it falls back to the default endpoint specified in the configuration.

        Returns:
            str: The Bing API endpoint.
        """

        return environ.get("BING_API_ENDPOINT", self.config["API_ENDPOINTS"]["BING"])

    def get_ollama_api_endpoint(self):
        """        Returns the OLLAMA API endpoint.

        This function retrieves the OLLAMA API endpoint from the environment variables or the configuration file.

        Returns:
            str: The OLLAMA API endpoint URL.
        """

        return environ.get(
            "OLLAMA_API_ENDPOINT", self.config["API_ENDPOINTS"]["OLLAMA"]
        )

    def get_claude_api_key(self):
        """        Returns the Claude API key from the environment variable or the configuration file.

        If the environment variable "CLAUDE_API_KEY" is set, it returns its value.
        Otherwise, it returns the API key from the configuration file under the "CLAUDE" section.

        Returns:
            str: The Claude API key.
        """

        return environ.get("CLAUDE_API_KEY", self.config["API_KEYS"]["CLAUDE"])

    def get_openai_api_key(self):
        """        Get the OpenAI API key.

        This function retrieves the OpenAI API key from the environment variables. If the key is not found in the environment variables, it falls back to using the key from the configuration file.

        Returns:
            str: The OpenAI API key.
        """

        return environ.get("OPENAI_API_KEY", self.config["API_KEYS"]["OPENAI"])

    def get_netlify_api_key(self):
        """        Get the Netlify API key from the environment variables or configuration file.

        Returns:
            str: The Netlify API key.
        """

        return environ.get("NETLIFY_API_KEY", self.config["API_KEYS"]["NETLIFY"])
    
    def get_groq_api_key(self):
        """        Returns the GROQ API key from the environment variable or the configuration file.

        If the GROQ_API_KEY environment variable is set, it returns the value of the environment variable.
        Otherwise, it returns the GROQ API key from the configuration file.

        Returns:
            str: The GROQ API key.
        """

        return environ.get("GROQ_API_KEY", self.config["API_KEYS"]["GROQ"])
      
    def get_sqlite_db(self):
        """        Returns the path of the SQLite database.

        This function returns the path of the SQLite database. If the environment variable "SQLITE_DB_PATH" is set, it returns
        the value of that variable; otherwise, it returns the path specified in the configuration under "STORAGE".

        Returns:
            str: The path of the SQLite database.
        """

        return environ.get("SQLITE_DB_PATH", self.config["STORAGE"]["SQLITE_DB"])

    def get_screenshots_dir(self):
        """        Get the directory path for storing screenshots.

        This function returns the directory path for storing screenshots. If the environment variable SCREENSHOTS_DIR is not set,
        it falls back to the value specified in the configuration file under STORAGE/SCREENSHOTS_DIR.

        Returns:
            str: The directory path for storing screenshots.
        """

        return environ.get("SCREENSHOTS_DIR", self.config["STORAGE"]["SCREENSHOTS_DIR"])

    def get_pdfs_dir(self):
        """        Returns the directory path for storing PDF files.

        This method retrieves the directory path for storing PDF files from the environment variable "PDFS_DIR"
        or from the configuration file under the "STORAGE" section with the key "PDFS_DIR".

        Returns:
            str: The directory path for storing PDF files.
        """

        return environ.get("PDFS_DIR", self.config["STORAGE"]["PDFS_DIR"])

    def get_projects_dir(self):
        """        Returns the projects directory path.

        This function retrieves the projects directory path from the environment variable "PROJECTS_DIR"
        or from the configuration file under the "STORAGE" section.

        Returns:
            str: The projects directory path.
        """

        return environ.get("PROJECTS_DIR", self.config["STORAGE"]["PROJECTS_DIR"])

    def get_logs_dir(self):
        """        Returns the logs directory path.

        This function retrieves the logs directory path from the environment variable "LOGS_DIR" or from the configuration
        file under the "STORAGE" section with the key "LOGS_DIR".

        Returns:
            str: The logs directory path.
        """

        return environ.get("LOGS_DIR", self.config["STORAGE"]["LOGS_DIR"])

    def get_repos_dir(self):
        """        Returns the directory path for storing repositories.

        This function retrieves the directory path for storing repositories from the environment variable "REPOS_DIR"
        or from the configuration file under the "STORAGE" section with the key "REPOS_DIR".

        Returns:
            str: The directory path for storing repositories.
        """

        return environ.get("REPOS_DIR", self.config["STORAGE"]["REPOS_DIR"])

    def get_logging_rest_api(self):
        """        Returns the value of the LOG_REST_API configuration from the logging settings.

        This method retrieves the value of the LOG_REST_API configuration from the logging settings
        and returns True if it is set to "true", otherwise returns False.

        Returns:
            bool: True if LOG_REST_API is set to "true", False otherwise.
        """

        return self.config["LOGGING"]["LOG_REST_API"] == "true"

    def get_logging_prompts(self):
        """        Return the logging prompts setting from the configuration.

        This function retrieves the logging prompts setting from the configuration and returns it.

        Returns:
            bool: The logging prompts setting from the configuration.
        """

        return self.config["LOGGING"]["LOG_PROMPTS"] == "true"

    def set_bing_api_key(self, key):
        """        Set the Bing API key in the configuration.

        This function sets the Bing API key in the configuration file and saves the configuration.

        Args:
            key (str): The Bing API key to be set.
        """

        self.config["API_KEYS"]["BING"] = key
        self.save_config()

    def set_bing_api_endpoint(self, endpoint):
        """        Set the Bing API endpoint in the configuration and save the changes.

        Args:
            endpoint (str): The new endpoint URL for the Bing API.
        """

        self.config["API_ENDPOINTS"]["BING"] = endpoint
        self.save_config()

    def set_ollama_api_endpoint(self, endpoint):
        """        Set the OLLAMA API endpoint in the configuration.

        This function sets the OLLAMA API endpoint in the configuration and saves the updated configuration.

        Args:
            endpoint (str): The new OLLAMA API endpoint to be set.
        """

        self.config["API_ENDPOINTS"]["OLLAMA"] = endpoint
        self.save_config()

    def set_claude_api_key(self, key):
        """        Set the API key for the Claude service.

        This function sets the API key for the Claude service in the configuration and saves the configuration.

        Args:
            key (str): The API key for the Claude service.
        """

        self.config["API_KEYS"]["CLAUDE"] = key
        self.save_config()

    def set_openai_api_key(self, key):
        """        Set the OpenAI API key in the configuration and save it.

        This function sets the OpenAI API key in the configuration and saves the updated configuration.

        Args:
            key (str): The OpenAI API key to be set.
        """

        self.config["API_KEYS"]["OPENAI"] = key
        self.save_config()

    def set_netlify_api_key(self, key):
        """        Set the Netlify API key in the configuration.

        This function sets the Netlify API key in the configuration file and saves the updated configuration.

        Args:
            key (str): The Netlify API key to be set.
        """

        self.config["API_KEYS"]["NETLIFY"] = key
        self.save_config()

    def set_sqlite_db(self, db):
        """        Set the SQLite database path in the configuration and save the updated configuration.

        Args:
            db (str): The path to the SQLite database.
        """

        self.config["STORAGE"]["SQLITE_DB"] = db
        self.save_config()

    def set_screenshots_dir(self, dir):
        """        Set the directory for storing screenshots.

        This method sets the directory path for storing screenshots in the configuration and saves the updated configuration.

        Args:
            dir (str): The directory path for storing screenshots.
        """

        self.config["STORAGE"]["SCREENSHOTS_DIR"] = dir
        self.save_config()

    def set_pdfs_dir(self, dir):
        """        Set the directory for storing PDF files.

        This method sets the directory path for storing PDF files in the configuration and saves the updated configuration.

        Args:
            dir (str): The directory path for storing PDF files.
        """

        self.config["STORAGE"]["PDFS_DIR"] = dir
        self.save_config()

    def set_projects_dir(self, dir):
        """        Set the directory for storing projects.

        This method sets the directory path for storing projects in the configuration and saves the updated configuration.

        Args:
            dir (str): The directory path for storing projects.
        """

        self.config["STORAGE"]["PROJECTS_DIR"] = dir
        self.save_config()

    def set_logs_dir(self, dir):
        """        Set the directory for storing logs.

        This method sets the directory path for storing logs in the configuration and saves the updated configuration.

        Args:
            dir (str): The directory path for storing logs.
        """

        self.config["STORAGE"]["LOGS_DIR"] = dir
        self.save_config()

    def set_repos_dir(self, dir):
        """        Set the directory for storing repositories.

        This method sets the directory path for storing repositories in the configuration and saves the updated configuration.

        Args:
            dir (str): The directory path for storing repositories.
        """

        self.config["STORAGE"]["REPOS_DIR"] = dir
        self.save_config()

    def set_logging_rest_api(self, value):
        """        Set the configuration for logging the REST API.

        This function sets the configuration for logging the REST API by updating the value in the configuration file.

        Args:
            value (bool): A boolean value indicating whether to log the REST API.
        """

        self.config["LOGGING"]["LOG_REST_API"] = "true" if value else "false"
        self.save_config()

    def set_logging_prompts(self, value):
        """        Set the logging prompts configuration.

        This function sets the logging prompts configuration in the application configuration file.

        Args:
            value (bool): The value to set for the logging prompts configuration.
        """

        self.config["LOGGING"]["LOG_PROMPTS"] = "true" if value else "false"
        self.save_config()

    def save_config(self):
        """        Save the configuration to a TOML file.

        This function saves the configuration to a TOML file named "config.toml".

        Args:
            self: The instance of the class containing the configuration to be saved.
        """

        with open("config.toml", "w") as f:
            toml.dump(self.config, f)

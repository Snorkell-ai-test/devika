import requests
from src.config import Config

class BingSearch:
    def __init__(self):
        """        Initialize the class with configuration settings and API information.

        It initializes the class with configuration settings such as Bing API key and endpoint,
        and sets the query result to None.

        Args:
            self: The class instance.
        """

        self.config = Config()
        self.bing_api_key = self.config.get_bing_api_key()
        self.bing_api_endpoint = self.config.get_bing_api_endpoint()
        self.query_result = None

    def search(self, query):
        """        Perform a search using the Bing Search API.

        This method sends a search query to the Bing Search API and stores the result in the 'query_result' attribute.

        Args:
            query (str): The search query to be sent to the API.

        Returns:
            dict: The JSON response from the Bing Search API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to the API fails.
        """

        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "mkt": "en-US"}

        try:
            response = requests.get(self.bing_api_endpoint, headers=headers, params=params)
            response.raise_for_status()
            self.query_result = response.json()
            return self.query_result
        except Exception as err:
            return err

    def get_first_link(self):
        """        Returns the first URL link from the query result.

        This function retrieves the first URL link from the query result obtained from the web search.

        Returns:
            str: The first URL link from the query result.
        """

        return self.query_result["webPages"]["value"][0]["url"]


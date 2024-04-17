import os

from playwright.sync_api import sync_playwright
from markdownify import markdownify as md
from pdfminer.high_level import extract_text

from src.config import Config
from src.state import AgentState

class Browser:
    def __init__(self):
        """        Initialize a new instance of the class.

        This method initializes a new instance of the class and sets up the Playwright environment,
        launching a new Chromium browser and creating a new page for interaction.
        """

        self.playwright = sync_playwright().start()
        chromium = self.playwright.chromium
        self.browser = chromium.launch()
        self.page = self.browser.new_page()

    def new_page(self):
        """        Open a new page in the browser.

        Returns:
            Page: A new page object representing the newly opened page.
        """

        return self.browser.new_page()

    def go_to(self, url):
        """        Navigates to the specified URL.

        Args:
            url (str): The URL to navigate to.
        """

        self.page.goto(url)

    def screenshot(self, project_name):
        """        Takes a screenshot of the current web page and saves it.

        Args:
            project_name (str): The name of the project for which the screenshot is being taken.

        Returns:
            str: The path where the screenshot is saved.
        """

        screenshots_save_path = Config().get_screenshots_dir()

        page_metadata = self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
        page_url = page_metadata['url']
        random_filename = os.urandom(20).hex()
        filename_to_save = f"{random_filename}.png"
        path_to_save = os.path.join(screenshots_save_path, filename_to_save)

        self.page.emulate_media(media="screen")
        self.page.screenshot(path=path_to_save)

        new_state = AgentState().new_state()
        new_state["internal_monologue"] = "Browsing the web right now..."
        new_state["browser_session"]["url"] = page_url
        new_state["browser_session"]["screenshot"] = path_to_save
        AgentState().add_to_current_state(project_name, new_state)        

        return path_to_save
    
    def get_html(self):
        """        Returns the HTML content of the page.

        Returns:
            str: The HTML content of the page.
        """

        return self.page.content()

    def get_markdown(self):
        """        Returns the markdown content of the page.

        This function retrieves the markdown content of the page using the 'content' method and returns it.

        Returns:
            str: The markdown content of the page.
        """

        return md(self.page.content())

    def get_pdf(self):
        """        Save the current web page as a PDF and return the file path.

        This method saves the current web page as a PDF file in the specified directory and returns the file path.

        Returns:
            str: The file path where the PDF is saved.
        """

        pdfs_save_path = Config().get_pdfs_dir()
        
        page_metadata = self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
        filename_to_save = f"{page_metadata['title']}.pdf"
        save_path = os.path.join(pdfs_save_path, filename_to_save)
        
        self.page.pdf(path=save_path)        
        
        return save_path

    def pdf_to_text(self, pdf_path):
        """        Extract text content from a PDF file.

        Args:
            pdf_path (str): The file path of the PDF to extract text from.

        Returns:
            str: The extracted text content from the PDF.
        """

        return extract_text(pdf_path).strip()

    def get_content(self):
        """        Get the content from a PDF file.

        This method retrieves the text content from a PDF file by first obtaining the path to the PDF file and then converting
        it to text.

        Returns:
            str: The text content extracted from the PDF file.
        """

        pdf_path = self.get_pdf()
        return self.pdf_to_text(pdf_path)

    def extract_text(self):
        """        Extracts the text content from the web page.

        Returns:
            str: The text content of the web page.
        """

        return self.page.evaluate("() => document.body.innerText")    

    def close(self):
        """        Close the page, browser, and playwright instance.

        This method closes the current page, browser, and playwright instance.
        """

        self.page.close()
        self.browser.close()
        self.playwright.stop()

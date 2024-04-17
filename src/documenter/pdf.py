import os
from io import BytesIO
from markdown import markdown
from xhtml2pdf import pisa

from src.config import Config

class PDF:
    def __init__(self):
        """        Initialize the object with the PDF path from the configuration.

        It initializes the object with the PDF path obtained from the configuration settings.

        Args:
            self: The object instance.
        """

        config = Config()
        self.pdf_path = config.get_pdfs_dir()
    
    def markdown_to_pdf(self, markdown_string, project_name):
        """        Convert a markdown string to a PDF file.

        This function takes a markdown string as input, converts it to HTML, and then generates a PDF file from the HTML content.

        Args:
            markdown_string (str): A string containing markdown content.
            project_name (str): The name of the project for which the PDF is being generated.

        Returns:
            str: The file path of the generated PDF.

        Raises:
            Exception: If there is an error generating the PDF.
        """

        html_string = markdown(markdown_string)
        
        out_file_path = os.path.join(self.pdf_path, f"{project_name}.pdf")
        with open(out_file_path, "wb") as out_file:
            pisa_status = pisa.CreatePDF(html_string, dest=out_file)

        if pisa_status.err:
            raise Exception("Error generating PDF")

        return out_file_path
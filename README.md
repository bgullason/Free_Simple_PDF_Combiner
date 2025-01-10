# Free Simple PDF Combiner
Combine and split PDF files for free!  

#### Build Requirements:
PySimpleGUI 4.60.5  
PyPDF2 2.12.1  

#### Install the requirements:
- Download and extract the repository into a folder.
- Next I reccomend setting up a Python virtual environement to install the Python packages https://docs.python.org/3/library/venv.html
- Make sure to install the required python packages listed under "Build Requirements".
  - You can specify the version like this: `pip install PyPDF2==2.12.1`
#### Run the application with Python
`python ./free_simple_pdf_combiner.pyw`
#### Create an executable file with pyinstaller
- Install pyinstaller with pip.
- To make a one file executable run `pyinstaller -F ./free_simple_pdf_combiner.pyw`
- The executable will be created in the ./dist folder.
- You should be able to run the application using the standalone executable file now.

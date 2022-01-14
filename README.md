
# PythonWebKitGoogle - Embed Google Docs Pages in your Application 

## To Configure
The demo is configured to run with python 3.8, but should work in any version:
- Follow the instructions in [webextension](https://github.com/aperezdc/webkit2gtk-python-webextension-example) repository to install the dependencies
- Follow the instructions in (**https://developers.google.com/sheets/api/quickstart/python**) to create the `credentials.json`
## To Run
- To execute, just run:
`./SheetDemo.sh http://docs.google.com/spreadsheets/d/<spreadsheetNumber>`

After the login, the credentials are saved. So every time that you open the application, it will open directly in the spreadsheet.

![](video.gif)

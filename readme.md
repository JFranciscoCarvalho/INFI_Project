# INFI project

## Program execution

To run the program, follow the steps:

1. Open Codesys project
2. Open sfs simulation program
3. Run the Codesys project (Build->Login->Download->Start)
4. Open a terminal and execute the ERP program, by typing "python erp.py"
5. Open a terminal and execute the MES program, by typing "python mes.py"
(Note: You can also open firstly the MES and then the ERP)
6. Execute the file II_commands.bat

## Code Requirements

1. Python

2. Codesys v3.5 SP18 Patch3

3. Virtual Environment (Optional)

Python isn’t great at dependency management. If you’re not specific, then pip will place all the external packages that you install in a folder called site-packages/ in your base Python installation.

So in order to keep track of the dependencies, we can use a Virtual Environment.

In order to do so, you need to install the venv package. Open the cmd and install it as following:

```sh
>pip install virtualenv
```

4. Create the Virtual Environment (Optional)

To use the virtual environment, you first need to create it.

In the VSCode, if you open the `requirements.txt` file, there is a button that appears in the bottom right corner of the window `Create Environment...`. Click it, then select the Venv option, the Python interpreter (should only appear one, the global one from `C:\Programs...`). Finally, it will appear a checkbox and select the `requirements.txt` file.

The virtual environment will be created in a folder named `.venv` and all the libraries will be installed inside it.



In order to use the venv, you type the following command:

```sh
>.venv\Scripts\activate
```

You should always open the venv before running the code.

To deactivate the venv, you type:

```sh
>deactivate
```
5. Install dependencies

If you followed the previous step, you're done.
Otherwise, you need to manually install the needed dependencies. So execute the following command:

```sh
>pip install -r requirements.txt
```

**Credits**

José Carvalho

Henrique Martins

Manuel Silva

Pedro Amaral

Sixto González

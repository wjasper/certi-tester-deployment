# Project Deployment

This guide will help you deploy your project. Ensure you have Python, MySQL, and VSCode installed.

All commands should be executed in the root directory of your project folder.

## Recommended Steps

1. **Create a Virtual Environment**:

   ``` 
   python -m venv certi_testor_deployement_env
   ```

2. **Activate the Virtual Environment**:
   - **Linux/macOS**:
     ```bash
     source certi_testor_deployement_env/bin/activate
     ```
   - **Windows**:
     ```bash
     certi_testor_deployement_env\Scripts\activate
     ```

## Mandatory Steps

3. **Install Required Packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Verify MySQL Root User Password**:
   - Ensure the MySQL root user's password is correct in `app.py`.

5. **Run the Application**:
   ```bash
   python3 app.py
   ```

## Access the Application

Open your browser and navigate to [http://127.0.0.1:7784](http://127.0.0.1:7784).


## Added shell scripting

start_certi_testor

Entering this command anywhere works in the terminal
(Only after this command has added in your zshrc profile
)
alias start_certi_testor='/Users/sunday/brainfuck/certi_testor_deployement/start_certi_testor.sh'  

- Need to check it with windows.
- Also the virtual env name needs to be certi_testor_deployement_env
- Work on schedular on Windows
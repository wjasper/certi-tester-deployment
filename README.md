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

# Use the Python 3.9 slim image as base
FROM python:3.9-slim AS python-base

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy just the app.py file from your local directory into the container
COPY app.py /app/

# Uncomment and use this line if you have a requirements.txt file
# COPY requirements.txt /app/
# RUN pip install -r requirements.txt

# Build stage for MySQL
FROM mysql:latest AS mysql-base

# Allow connections from any IP address
RUN sed -i 's/^\(bind-address\s.*\)/# \1/' /etc/mysql/my.cnf

# Set MySQL root password
ENV MYSQL_ROOT_PASSWORD=c3rt1test3r

# Final stage
# Start a new build stage using Python base and MySQL base
FROM python-base AS final

# Install MySQL client in the Python image
RUN apt-get update && apt-get install -y default-mysql-client

# Example of how to run your application (adjust according to your needs)
CMD ["python", "app.py"]

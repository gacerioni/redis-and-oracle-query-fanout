#!/bin/bash

# Define installation paths
ORACLE_CLIENT_DIR="/root/something/instantclient_19_24"

# Update package list and install necessary packages
sudo apt-get update && sudo apt-get install -y python3.12 python3.12-dev python3.12-venv unzip

# Check if Oracle Instant Client directory already exists
if [ ! -d "$ORACLE_CLIENT_DIR" ]; then
    # Unzip the Oracle Instant Client
    echo "Unzipping Oracle Instant Client..."
    unzip ./oracle_dependencies/instantclient-basic-linux.x64-19.24.0.0.0dbru.zip -d /root/something/
    if [ $? -ne 0 ]; then
        echo "Failed to unzip Oracle Instant Client."
        exit 1
    fi
else
    echo "Oracle Instant Client directory already exists."
fi

# Set the LD_LIBRARY_PATH environment variable
export LD_LIBRARY_PATH="$ORACLE_CLIENT_DIR:$LD_LIBRARY_PATH"
echo "LD_LIBRARY_PATH set to $LD_LIBRARY_PATH"

# Optionally, add to .bashrc for persistence across sessions
echo "export LD_LIBRARY_PATH=\"$ORACLE_CLIENT_DIR:\$LD_LIBRARY_PATH\"" >> ~/.bashrc

# Create a virtual environment for Python 3.12
echo "Creating virtual environment..."
python3.12 -m venv venv && source venv/bin/activate

# Upgrade pip and install required packages from requirements.txt
python3.12 -m pip install --upgrade pip && python3.12 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install Python packages."
    exit 1
fi

# Inform the user that the setup is complete
echo "Setup complete. The virtual environment is ready and the Oracle Instant Client path is set."

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate

# Run the Flask application
echo "Running the Flask application..."
python3.12 -m flask run --host=0.0.0.0
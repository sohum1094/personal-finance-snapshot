#!/usr/bin/env bash

# Define the Backend server URL (replace with actual URL if fixed)
BACKEND_SERVER_URL="http://localhost:2020"  # Change port if necessary

# Start the Backend server
echo "Starting Backend server..."
python backend_server.py  # Run the server in the foreground to show requests and print statements

# Inform the user where the backend server is running
echo "Backend server is running at $BACKEND_SERVER_URL"

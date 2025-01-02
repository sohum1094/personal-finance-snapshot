#!/usr/bin/env bash

# Define the server URLs (replace with actual URLs if they are fixed)
PLAID_SERVER_URL="http://localhost:3000"  # Change port if necessary
BACKEND_SERVER_URL="http://localhost:2020"  # Change port if necessary

# Start the Plaid server
echo "Starting Plaid server..."
python plaid_server.py > plaid_server.log 2>&1 &  # Run in the background and log output
PLAID_PID=$!  # Store the process ID of the Plaid server

# Start the Backend server
echo "Starting Backend server..."
python backend_server.py > backend_server.log 2>&1 &  # Run in the background and log output
BACKEND_PID=$!  # Store the process ID of the Backend server

# Wait for both servers to start
sleep 2

# Check if the servers are running
if ps -p $PLAID_PID > /dev/null; then
    echo "Plaid server is running (PID: $PLAID_PID)"
    echo "Plaid server URL: $PLAID_SERVER_URL"
else
    echo "Failed to start Plaid server. Check plaid_server.log for details."
fi

if ps -p $BACKEND_PID > /dev/null; then
    echo "Backend server is running (PID: $BACKEND_PID)"
    echo "Backend server URL: $BACKEND_SERVER_URL"
else
    echo "Failed to start Backend server. Check backend_server.log for details."
fi

# Keep the script running to manage servers
echo "Press Ctrl+C to stop both servers."
wait $PLAID_PID $BACKEND_PID

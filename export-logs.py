#!/usr/bin/env python3

import os
import requests
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from .env-local file
load_dotenv('.env-local')

# Access the API token
api_token = os.getenv('API_TOKEN')

# defining authentication headers
headers = {"Authorization": f"Token {api_token}"}

# API-endpoint for environments
ENV_URL = "https://api.divio.com/apps/v3/environments/"

# Function to truncate microseconds from a timestamp
def truncate_microseconds(timestamp):
    """
    Truncates the microseconds part from a timestamp string.

    Parameters:
        timestamp (str): The timestamp string to be truncated.

    Returns:
        str: The truncated timestamp without microseconds (up to milliseconds precision).
    """
    if "." in timestamp:
        return timestamp[:timestamp.index(".") + 3]  # Truncate to two decimal places
    return timestamp

# Function to export and display logs from a Divio environment
def get_all_logs():
    """
    Retrieves and displays logs from a specified Divio environment for a given date range.

    The function first defines the date range for the logs, then identifies the target Divio environment
    using environment slug and application UUID. It constructs the URL with the specified date range
    and queries the Divio API to fetch the logs.

    The logs are displayed in reverse chronological order, printing each log's timestamp and message.
    The function paginates through the log data to fetch all the available logs.

    Parameters:
        None

    Returns:
        None
    """
    # Setting the date and time to export the logs, 
    from_ts = "YYYY-MM-DDThh:mm"
    to_ts = "YYYY-MM-DDThh:mm"

    # Defining Environment variables

    # environment slug, for example "live" or "test"
    env_slug = ""

    # application uuid, from the application url after the /app/ part
    app_uuid = ""

    # Getting the environment uuid

    # Defining a params dictionary with the application UUID
    env_params = {"application": app_uuid}

    # Listing the environments of the given application
    env_response = requests.get(url=ENV_URL, params=env_params, headers=headers)

    # Getting the uuid of the environment

    # Iterating through the list of environments to get the uuid with the given env slug
    for env in env_response.json()["results"]:
        if env["slug"] == env_slug: 
            env_uuid = env["uuid"]  

    # Construct the URL with query parameters
    logs_params = {
        'from_ts': from_ts,
        'to_ts': to_ts,
    }
    query_string = urllib.parse.urlencode(logs_params)
    url = f"https://api.divio.com/apps/v3/environments/{env_uuid}/logs/?{query_string}"

    response = requests.get(url=url, headers=headers)

    # Open a file to save the logs (replace 'logs.txt' with your desired file name)
    with open('logs.txt', 'w') as log_file:

        # Main loop to retrieve and display logs
        while True:
            # Fetch the log data from the current URL
            data = response.json()

            # Check for any error messages in the response
            if not "results" in data:
                print(data)

            # Print each log entry in reverse chronological order and save to the file
            for line in data["results"][::-1]:
                # Truncate the microseconds part of the timestamp
                timestamp = truncate_microseconds(line["timestamp"])
                log_entry = f"{timestamp} - {line['message']}\n"
                print(log_entry, end='')  # Print the log entry without a newline
                log_file.write(log_entry)  # Write the log entry to the file

            # Check if there are more log entries in the previous page
            if url != data["previous"]:
                # Update the URL to fetch the previous page
                url = data["previous"]
                # Fetch the log data from the updated URL
                response = requests.get(url=url, headers=headers)
            else:
                # End the loop if there are no more log entries
                return

# Call the function to retrieve and display logs and save them to a file
get_all_logs()

from flask import Flask, request, abort
import requests

app = Flask(__name__)

# Azure DevOps organization and project details
organization = "sawantsajay"
project = "AJAY_TEST"

# Personal Access Token (PAT) with Work Items scope
pat = "z6vvwpmzvqp55sl3qrtkx66db5imymbtgbdic6udfvlcxqwaif6a"

# Azure DevOps REST API base URL
base_url = f"https://dev.azure.com/{organization}/{project}/_apis/"

# Webhook endpoint to receive Azure DevOps events
webhook_endpoint = "/webhook"

# Function to validate the event payload
def validate_event(payload):
    # Add any additional validation logic as needed
    return True

# Function to handle work item state change events
def handle_state_change_event(data):
    # Extract relevant information from the event payload
    work_item_id = data['resource']['workItemId']
    new_state = data['resource']['revision']['fields']['System.State']['newValue']

    # Check if the state is changed to "Doing"
    if new_state.lower() == "doing":
        # Check if there is at least one related link
        related_links = get_related_links(work_item_id)
        if not related_links:
            # Add your logic to enforce the requirement (e.g., raise an error)
            raise ValueError("A related link is required when changing the state to 'Doing'.")

# Function to get related links for a work item
def get_related_links(work_item_id):
    url = f"{base_url}wit/workitems/{work_item_id}?api-version=7.1"
    headers = {"Authorization": f"Basic {pat}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        work_item = response.json()
        related_links = work_item.get('fields', {}).get('System.Links-Related', [])
        return related_links
    else:
        # Handle error (e.g., log or raise an exception)
        return None

# Flask route to handle Azure DevOps webhook events
@app.route(webhook_endpoint, methods=['POST'])
def webhook_listener():
    try:
        payload = request.get_json()

        if validate_event(payload):
            event_type = payload['eventType']

            if event_type == 'workitem.updated':
                handle_state_change_event(payload['resource'])
            
            return '', 200
        else:
            abort(400)
    except Exception as e:
        # Handle exceptions (e.g., log or send notifications)
        print(f"Error: {e}")
        abort(500)

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)

import os
from datetime import datetime, timedelta

from slack_bolt import App
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def get_user_info(user_id):
    try:
        user_info = app.client.users_info(user=user_id)
        return user_info["user"]
    except Exception as e:
        print(f"Error fetching user info for {user_id}: {e}")
        return None


# A simple relevance filter
def is_relevant(message_text):
    keywords = ["relevant", "urgent", "needs action"]
    return any(keyword in message_text.lower() for keyword in keywords)


def build_relevant_message(source_channel_id, message):
    user_info = get_user_info(message["user"])
    user_name = user_info.get('real_name', 'Unknown User') if user_info else 'Unknown User'

    # Format the timestamp for readability
    message_time = datetime.fromtimestamp(float(message["ts"]))
    message_time_str = message_time.strftime("%Y-%m-%d %H:%M:%S")

    message_link_ts = message["ts"].replace('.', '')
    # Ensure SLACK_WORKSPACE_NAME is in your .env file
    workspace_name = os.environ.get("SLACK_WORKSPACE_NAME", "yourworkspace")
    message_link = f"https://{workspace_name}.slack.com/archives/{source_channel_id}/p{message_link_ts}"

    # Build the message content using Block Kit
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Relevant Comment from <#{source_channel_id}>*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{user_name}* posted at *{message_time_str}*:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message["text"]
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🔗 <{message_link}|View original message>"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]

    # This will be the fallback text for notifications
    fallback_text = f"Relevant comment from {user_name}: {message['text']}"

    return blocks, fallback_text


def pull_and_post_relevant_comments(source_channel_id, destination_channel_id):
    oldest_ts = (datetime.now() - timedelta(hours=24)).timestamp()

    try:
        result = app.client.conversations_history(
            channel=source_channel_id,
            oldest=str(oldest_ts)
        )

        messages = result.get("messages", [])
        for message in reversed(messages):  # Reverse to post in chronological order
            if "user" in message and "text" in message and is_relevant(message["text"]):
                blocks_payload, fallback_text = build_relevant_message(source_channel_id, message)

                app.client.chat_postMessage(
                    channel=destination_channel_id,
                    blocks=blocks_payload,
                    text=fallback_text
                )

    except Exception as e:
        print(f"Error fetching or posting messages: {e}")


if __name__ == "__main__":
    source_channel = os.environ.get("SOURCE_CHANNEL_ID")
    destination_channel = os.environ.get("DESTINATION_CHANNEL_ID")

    if not all([source_channel, destination_channel]):
        print("Error: SOURCE_CHANNEL_ID and DESTINATION_CHANNEL_ID must be set in your .env file.")
    else:
        print("Running bot to check for relevant messages...")
        pull_and_post_relevant_comments(source_channel, destination_channel)
        print("Bot finished.")

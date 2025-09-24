This Slack bot will pull messages from the past 24 hours in one channel, identify messages with specific keywords, and repost those messages with user information and timestamps in another channel. This is based on a Slack bot I built while at Atlassian, recreated to be customizable. Add a cron job or a task schedule to run this at a set time a day.

Requirements:
in your .env file, add the following with your own values:

SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SOURCE_CHANNEL_ID=
DESTINATION_CHANNEL_ID=
SLACK_WORKSPACE_NAME=

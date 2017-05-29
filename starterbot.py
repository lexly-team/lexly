import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
BOT_NAME="starterbot"
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
GENERAL_CHANNEL="#general"
WELCOME_MESSAGE="Hi guys! I'm connected and running. You can try interacting with me by typing: @" + BOT_NAME + " do <something> (The applicable <something>: hi)"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(user, command, sub_command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print("\nuser=" + user + ", command=" + command + ", sub_command=" + sub_command + ", channel=" + channel + "\n")
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        if command.split(" ")[1] == "hi":
            response = "Oh, hi! How are you, " + user + " today?"
        else:
            response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print("Got a message from Slack: " + output.__str__())
            if output and 'text' in output and 'user' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                command = output['text'].split(AT_BOT)[1].strip().lower()
                sub_command = ""
                return "<@{}>".format(output['user']), command, sub_command, output['channel']
    return None, None, None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        slack_client.api_call("chat.postMessage", channel=GENERAL_CHANNEL, text=WELCOME_MESSAGE, as_user=True)
        while True:
            user, command, sub_command, channel = parse_slack_output(slack_client.rtm_read())
            if user and command and channel:
                handle_command(user, command, sub_command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


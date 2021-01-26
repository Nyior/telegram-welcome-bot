import requests
from decouple import config
from bottle import (  
    run, post, response, request as bottle_request
)

from os import environ


TOKEN = config('TOKEN') #retrieving the env var TOKEN
ENV = config('ENV')
BOT_URL = f"https://api.telegram.org/bot{TOKEN}/" 


def get_user_first_name(data):  
    """
    Method to extract a newly added user's first name
    from telegram request
    """
    try:
        first_name = data['message']['new_chat_member']['first_name']
        return first_name
    except KeyError:
        pass


def get_group_name(data):  
    """
    Method to extract a newly name of group a user has been added to
    """
    try:
        group_name = data['message']['chat']['title']
        return group_name
    except KeyError:
        pass


def get_chat_id(data):  
    """
    Method to extract chat id from telegram request.
    """
    chat_id = data['message']['chat']['id']

    if not isinstance(chat_id, int):
        raise TypeError('Please chat_id must be an integer')
    return chat_id


def prepare_welcome_text(data):  
    user_name = get_user_first_name(data)
    group = get_group_name(data) 

    group_name = f"the @{group}" if group is not None else "this our"

    welcome_text = f""" 
                    *Hi {user_name}, welcome to {group_name} Family*\nwe are _very_ glad to have you here :)\n\nNot required, but if you can, introduce yourself just so other members of this community get to know you.\n\n_no fear, e no dey too serious_  :-))\n\nJust tell us who you are, what you do, and your interests in the tech space and beyond if you want.
                   """

    json_data = {
        "chat_id": get_chat_id(data),
        "text": welcome_text,
        "parse_mode": "Markdown"
    }

    return json_data


def send_message(prepared_data):  
    """
    Prepared data should be json which includes at least `chat_id` and `text`
    """ 
    message_url = BOT_URL + 'sendMessage'
    requests.post(
                    message_url, 
                    json=prepared_data,
                    ) #import the requests lib first


@post('/')
def main():  
    data = bottle_request.json
    user = get_user_first_name(data)
    
    if user is not None: #only send a reply when a new user has
        welcome_text = prepare_welcome_text(data)
        send_message(welcome_text)

    return response  # status 200 OK by default


if __name__ == '__main__': 
    if ENV == "development":
        run(host='0.0.0.0', port=8080, debug=True)
    run(
        server='gunicorn', 
        host='0.0.0.0', 
        port=int(environ.get("PORT", 5000))
        )
    
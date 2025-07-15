import os
import json
from typing import TypedDict

from dotenv import load_dotenv
from imap_tools import MailBox, AND

from langchain.chat_models import init_chat_model
from langchain.core.tools import tool

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_FOLDER = "INBOX"

MAYAN = 'gemma3'

class ChatState(TypedDict):
    messages: list
    
def connect():
    mail_box = MailBox(IMAP_HOST)
    mail_box.login(IMAP_USER, IMAP_PASS, initial_folder=IMAP_FOLDER)
    return mail_box

@tool
def list_unread_email():
    """Return a list of unread emails UID, subject, date and sender"""
    
    print('List Unread Emails tool called')
    
    with connect() as mb:
        unread = list(mb.fetch(AND(seen=False), headers=True, mark_seen=False))
        
    if not unread:
        return "No unread emails found."

    response = json.dumps([
        {
            "uid": mail.uid,
            "date": mail.date.astimezone().strftime("%d-%m-%Y %H:%M:%S"),
            "subject": mail.subject,
            "sender": mail.from_
        }
        for mail in unread
    ])

    return response

def summarize_email(uid):
    """Summarize the email with the given UID"""
    
    print(f'Summarizing email with UID: {uid}')
    
    with connect() as mb:
        mail = next(mb.fetch(AND(uid=uid), mark_seen=False), None)
        if not mail:
            return f"No email found with UID: {uid}"  
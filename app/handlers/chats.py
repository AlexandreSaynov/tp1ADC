import xml.etree.ElementTree as ET
from datetime import datetime
import time
import os
import threading
from app.handlers._helper import helper_select_users

CHATS_FILE = "./vars/dev/chats.xml"
RELOAD_INTERVAL = 0.5  # seconds

def handle_create_chat(db, logged_user):
    print("\n=== Create New Chat ===")

    name = input("Chat name: ").strip()
    if not name:
        print("Chat name cannot be empty.")
        return

    print("\nSelect participants:")
    participant_ids = helper_select_users(db, allow_multiple=True, exclude_ids={logged_user.id})

    participants = []
    for uid in participant_ids:
        user = db.get_user_by_id(uid)
        if user:
            participants.append(user.username)

    create_chat_in_xml(name, participants, logged_user.username)

    print(f"\nChat '{name}' created successfully!")


def create_chat_in_xml(name, participants, owner_username):
    if os.path.exists(CHATS_FILE):
        tree = ET.parse(CHATS_FILE)
        root = tree.getroot()
    else:
        root = ET.Element("chats")
        tree = ET.ElementTree(root)

    existing_ids = [
        int(chat.get("id").replace("chat_", ""))
        for chat in root.findall("chat")
    ]
    next_id = max(existing_ids, default=0) + 1
    chat_id = f"chat_{next_id:03}"

    chat_elem = ET.SubElement(root, "chat")
    chat_elem.set("id", chat_id)

    ET.SubElement(chat_elem, "name").text = name
    ET.SubElement(chat_elem, "owner").text = owner_username

    if owner_username not in participants:
        participants.append(owner_username)

    for p in participants:
        ET.SubElement(chat_elem, "participant").text = p

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(chat_elem, "latest_timestamp").text = now

    tree.write(CHATS_FILE)



def load_user_chats(logged_user):
    if not os.path.exists(CHATS_FILE):
        return []
    
    tree = ET.parse(CHATS_FILE)
    root = tree.getroot()
    user_chats = []
    
    for chat in root.findall("chat"):
        participants = [p.text for p in chat.findall("participant")]
        if logged_user.username in participants:
            chat_id = chat.get("id")
            chat_name = chat.findtext("name", f"Chat {chat_id}")
            owner = chat.findtext("owner", "")
            
            user_chats.append({
                "id": chat_id,
                "name": chat_name,
                "participants": participants,
                "owner": owner
            })
    
    return user_chats

def display_chat_menu(chats, page=0, page_size=5):
    total_pages = (len(chats) + page_size - 1) // page_size
    start = page * page_size
    end = start + page_size
    
    print("\n" + "="*50)
    print("AVAILABLE CHATS")
    print("="*50)
    
    for idx, chat in enumerate(chats[start:end], 1):
        print(f"{idx}. {chat['name']} ({', '.join(chat['participants'])})")
    
    print("\n" + "-"*50)
    print(f"Page {page + 1}/{total_pages}")
    
    if page > 0:
        print("'P' - Previous Page")
    if page < total_pages - 1:
        print("'N' - Next Page")
    
    print("'Q' - Exit to Main Menu")
    print("-"*50)
    
    return page, total_pages

def chat_selection_loop(logged_user, db):
    chats = load_user_chats(logged_user)
    
    if not chats:
        print("\nNo chats available.")
        return
    
    page = 0
    page_size = 5
    
    while True:
        page, total_pages = display_chat_menu(chats, page)
        start = page * page_size
        end = start + page_size
        
        choice = input("\nSelect chat (1-5) or command (P/N/Q): ").upper().strip()
        
        if choice == 'Q':
            break
        elif choice == 'N' and page < total_pages - 1:
            page += 1
        elif choice == 'P' and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(chats[start:end]):
                selected_chat = chats[start + idx]
                
                if logged_user.username == selected_chat["owner"]:
                    print(f"\nYou are the owner of '{selected_chat['name']}'")
                    print("1. Enter chat")
                    print("2. Manage chat")
                    sub_choice = input("Choose option: ").strip()
                    if sub_choice == '2':
                        manage_chat(logged_user, selected_chat, db)
                        chats = load_user_chats(logged_user)
                        continue
                chat_viewer(logged_user, selected_chat)


def load_chat_messages(chat_id):
    if not os.path.exists(CHATS_FILE):
        return [], None
    
    tree = ET.parse(CHATS_FILE)
    root = tree.getroot()
    
    for chat in root.findall("chat"):
        if chat.get("id") == chat_id:
            messages = []
            for msg in chat.findall("message"):
                messages.append({
                    "sender": msg.findtext("sender"),
                    "content": msg.findtext("content"),
                    "timestamp": msg.findtext("timestamp")
                })
            
            latest_timestamp = chat.findtext("latest_timestamp")
            return messages, latest_timestamp
    
    return [], None

def display_chat(chat_info, messages):
    print("\n" + "="*50)
    print(f"CHAT: {chat_info['name']}")
    print("="*50 + "\n")
    
    if not messages:
        print("No messages yet.\n")
    else:
        for msg in messages:
            print(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}")
    
    print("\n" + "-"*50)
    print("Type 'M' to send a message, 'Q' to quit chat.")

def add_message_to_chat(logged_user, chat_id, content):
    if not os.path.exists(CHATS_FILE):
        return False
    
    tree = ET.parse(CHATS_FILE)
    root = tree.getroot()
    
    for chat in root.findall("chat"):
        if chat.get("id") == chat_id:
            new_msg = ET.SubElement(chat, "message")
            ET.SubElement(new_msg, "sender").text = logged_user.username
            ET.SubElement(new_msg, "content").text = content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(new_msg, "timestamp").text = timestamp
            
            latest = chat.find("latest_timestamp")
            if latest is not None:
                latest.text = timestamp
            else:
                ET.SubElement(chat, "latest_timestamp").text = timestamp
            
            tree.write(CHATS_FILE)
            return True
    
    return False

def chat_viewer(logged_user, chat_info):
    last_timestamp = None
    user_choice = None
    user_message = None
    input_event = threading.Event()
    
    def get_user_input():
        nonlocal user_choice, user_message
        choice = None
        while choice != 'Q':
            choice = input().upper().strip()
            if choice == 'M':
                message = input("Enter message: ").strip()
                user_message = message
                add_message_to_chat(logged_user, chat_info["id"], user_message)
                print("Message sent.")
            elif choice == 'Q':
                user_choice = 'Q'
            else:
                print("Invalid option. Type 'M' to send a message or 'Q' to quit.")
            input_event.set()
    
    input_thread = threading.Thread(target=get_user_input, daemon=True)
    input_thread.start()
    
    while user_choice != 'Q':
        messages, latest_timestamp = load_chat_messages(chat_info["id"])
        
        if latest_timestamp != last_timestamp:
            display_chat(chat_info, messages)
            last_timestamp = latest_timestamp
        
        time.sleep(RELOAD_INTERVAL)
    input_thread.join(0)

def chat_loop(logged_user):
    chat_selection_loop(logged_user)

def manage_chat(logged_user, chat_info, db):
    if logged_user.username != chat_info["owner"]:
        print("\nOnly the chat owner can manage this chat.")
        return

    while True:
        print("\n" + "="*50)
        print(f"MANAGE CHAT: {chat_info['name']}")
        print("="*50)
        print("1. Edit chat name")
        print("2. Delete chat")
        print("Q. Quit to previous menu")
        print("-"*50)
        
        choice = input("Select option: ").upper().strip()
        
        if choice == '1':
            new_name = input("Enter new chat name: ").strip()
            if new_name:
                edit_chat_name(chat_info["id"], new_name)
                chat_info["name"] = new_name
                print("Chat name updated.")
            else:
                print("Chat name cannot be empty.")
        
        elif choice == '2':
            confirm = input("Are you sure you want to delete this chat? (Y/N): ").upper().strip()
            if confirm == 'Y':
                if delete_chat(chat_info["id"]):
                    print("Chat deleted.")
                    break
                else:
                    print("Error deleting chat.")
        
        elif choice == 'Q':
            break
        else:
            print("Invalid option.")

def delete_chat(chat_id):
    if not os.path.exists(CHATS_FILE):
        return False
    
    tree = ET.parse(CHATS_FILE)
    root = tree.getroot()
    chat_to_delete = None
    
    for chat in root.findall("chat"):
        if chat.get("id") == chat_id:
            chat_to_delete = chat
            break
    
    if chat_to_delete is not None:
        root.remove(chat_to_delete)
        tree.write(CHATS_FILE)
        return True
    
    return False


def edit_chat_name(chat_id, new_name):
    if not os.path.exists(CHATS_FILE):
        return False
    
    tree = ET.parse(CHATS_FILE)
    root = tree.getroot()
    
    for chat in root.findall("chat"):
        if chat.get("id") == chat_id:
            chat.find("name").text = new_name
            tree.write(CHATS_FILE)
            return True
    return False
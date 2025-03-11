# WhatsApp Message Scheduler

🚀 A Python script that allows users to schedule and send WhatsApp messages automatically at a specific time.

📌 Project Overview

This script uses Selenium WebDriver to interact with WhatsApp Web and send messages at predefined times. The script ensures that the user is logged in and automates the message-sending process while handling login detection, scheduled tasks, and error handling.

🔧 Features

✅ Automates WhatsApp messages at a scheduled time✅ Works with personal and group chats✅ Uses Selenium WebDriver to interact with WhatsApp Web✅ Detects login status and waits for QR code scanning if necessary✅ Supports message scheduling using schedule library✅ Logs all activities for debugging and monitoring

🛠️ Technology Stack

- Python – Core programming language

- Selenium – For automating WhatsApp Web interaction

- Schedule – For scheduling message execution

- Datetime & Pytz – For handling time zones and scheduling

- Logging – For efficient error handling and debugging

🚀 How It Works

1. The script initializes Selenium WebDriver and opens WhatsApp Web.

2. It checks if the user is logged in or waits for the QR code to be scanned.

3. The user specifies a contact name and a message to be sent.

4. The script finds the contact, opens the chat, types the message, and sends it.

5. Messages are scheduled using the schedule library and run in a loop.

6. The script logs all actions and retries if sending fails.

📩 Installation & Setup

Prerequisites

Ensure you have Python installed. Then, install the required libraries:

pip install selenium schedule pytz

You also need to download the Chrome WebDriver matching your Chrome version.

Running the Script

1. Open a terminal and navigate to the script's directory.

2. Run the script:

python wapp.py

3. Scan the QR code in WhatsApp Web if not already logged in.

4. The script will schedule and send messages at the predefined time.

⚠️ Important Notes

- The script requires WhatsApp Web to be logged in.

- The browser must remain open for message execution.

- The message will be sent at the exact scheduled time if conditions are met.

- Keep the system running to ensure the script executes properly.

📩 Contact

For any questions or improvements, feel free to reach out:

Email: cristian.trifan@student.nhlstenden.com


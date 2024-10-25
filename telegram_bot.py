import requests
import logging

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()  # Raises an error for bad responses (4xx/5xx)
            
            logging.info(f"Message sent successfully to chat_id {self.chat_id}: {message}")
            return response.json()  # Return response data if needed for further handling
            
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred while sending message: {http_err} - Response: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred: {req_err}")

        return None  # Return None if an error occurred

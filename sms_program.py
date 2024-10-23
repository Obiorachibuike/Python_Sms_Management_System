import sys
import time
from metrics import Metrics

metrics = Metrics()  # Instantiate the Metrics class

def send_sms(phone_number, proxy):
    # Implement your SMS sending logic here, using the proxy if provided
    try:
        # Simulate sending SMS
        time.sleep(5)  # Simulate a delay for sending
        print(f"SMS sent to {phone_number} via {proxy}")  # Print success message
        metrics.update_metrics("example_country_operator", True)  # Update metrics on success
    except Exception as e:
        print(f"Error sending SMS: {e}")  # Print error message
        metrics.update_metrics("example_country_operator", False)  # Update metrics on failure

if __name__ == "__main__":
    phone_number = sys.argv[1]  # Get phone number from command line argument
    proxy = sys.argv[2] if len(sys.argv) > 2 else None  # Get proxy from command line argument
    send_sms(phone_number, proxy)  # Call the function to send SMS

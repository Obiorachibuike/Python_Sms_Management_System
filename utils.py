from time import time

rate_limits = {}

def rate_limit(country):
    current_time = time()
    if country not in rate_limits:
        rate_limits[country] = current_time
        return True
    elif current_time - rate_limits[country] >= 6:  # 10 SMS per minute = 1 SMS every 6 seconds
        rate_limits[country] = current_time
        return True
    return False
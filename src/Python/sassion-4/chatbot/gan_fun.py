import random
import json

with open ("C:/Users/New Star Computer 26/Desktop/Depi/BNS_AIS2_S2_ML/src/Python/sassion-4/chatbot/Data.json","r") as file:
    responses = json.load(file)

    
    

def get_response(user_input):
    for key in responses:
        if key in user_input:
            return random.choice(responses[key])
    return random.choice(responses["default"])
from gan_fun import get_response

def main_bot():
    print("chatbot: Hi How can i assust you ? my name yousef hussein ")

    while True:
        user_input = input("user:   ").lower()
        response = get_response(user_input)
        print("chatpot:",response)

        if user_input == "Goodbye":
            break
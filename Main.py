from features_module import process_command, listen, say  # Importing features

def main():
    while True:
        try:
            text = listen().lower()
            if not text:
                continue
            response = process_command(text)
            print(response)
            say(response)
        except Exception as e:
            print(f"Error: {e}")
            say("Sorry, something went wrong.")
            
if __name__ == "__main__":
    main()




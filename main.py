from ai.agent import ask_ai

CLI_SESSION_ID = "cli:local"

while True:
    msg = input("\n나 : ")

    if msg == "exit":
        break

    answer = ask_ai(msg, CLI_SESSION_ID)

    print("\nAI :")
    print(answer)

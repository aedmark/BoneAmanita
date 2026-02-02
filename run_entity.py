from bone_entity import ConversationalEntity
import sys

def main():
    # Initialize the entity (creates the engine instance)
    print("--- Waking the Entity ---")
    entity = ConversationalEntity(user_name="Architect")

    print("\n(Type 'exit' to quit)\n")

    while True:
        try:
            user_input = input("You > ")
            if user_input.lower() in ["exit", "quit"]:
                # Save state on exit
                print(entity.save())
                break

            # The core interaction
            response = entity.talk(user_input)

            # Display the clean text and the hidden state
            print(f"Entity > {response['text']}")
            print(f"[META] > Mood: {response['mood']} | Voltage: {response['voltage']:.1f}v | Loc: {response['location']}")

        except KeyboardInterrupt:
            print("\nDisconnected.")
            break

if __name__ == "__main__":
    main()
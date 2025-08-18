import random

def play_game():
    print("Welcome to Rock-Paper-Scissors!")
    print("Enter your choice: rock, paper or scissors")
    
    choices = ["rock", "paper", "scissors"]
    user_choice = input("Your choice: ").lower()
    
    if user_choice not in choices:
        print("Invalid choice! Please choose rock, paper or scissors.")
        return
    
    computer_choice = random.choice(choices)
    print(f"Computer chose: {computer_choice}")
    
    if user_choice == computer_choice:
        print("It's a tie! 🤝")
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "scissors" and computer_choice == "paper") or \
         (user_choice == "paper" and computer_choice == "rock"):
        print("You win! 🎉")
    else:
        print("You lose! 😢")

# Play in loop
while True:
    play_game()
    again = input("Do you want to play again? (yes/no): ").lower()
    if again != "yes":
        print("Thanks for playing! 👋")
        break

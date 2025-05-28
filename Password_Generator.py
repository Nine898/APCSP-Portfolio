import random
import string

def generate_password(name, pet_name, birth_year, special_char):
    combined_string = name + pet_name + str(birth_year) + special_char  # Combine user input
    shuffled_string = ''.join(random.sample(combined_string, len(combined_string)))  # Shuffle characters

    password = ""  # Initialize password string
    for char in shuffled_string:
        if random.random() < 0.3:  # 30% chance to convert to uppercase
            password += char.upper()
        elif random.random() < 0.2:  # 20% chance to add a random digit
            password += str(random.randint(0, 9))
        else:
            password += char  # Otherwise, keep the original character

    # Ensure password contains at least one digit
    if not any(char.isdigit() for char in password):
        password += str(random.randint(0, 9)) 

    # Ensure password contains at least one uppercase letter
    if not any(char.isupper() for char in password):
        password += random.choice(string.ascii_uppercase) 

    return password  # Return the generated password

while True:
    name = input("Enter your name: ")  # Get user's name
    pet_name = input("Enter your pet's name: ")  # Get pet's name
    birth_year = input("Enter your birth year: ")  # Get user's birth year
    special_char = input("Enter a special character (!@#$...): ")  # Get special character

    password = generate_password(name, pet_name, birth_year, special_char)  # Generate password
    print("Generated Password:", password)  # Display the password

    repeat = input("Do you want to generate another password? (yes/no): ")  # Ask if user wants another
    if repeat.lower() != 'yes':  # Exit loop if user enters anything other than 'yes'
        break

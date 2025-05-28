import random
import string

def generate_password(name, pet_name, birth_year, special_char):
    combined_string = name + pet_name + str(birth_year) + special_char
    shuffled_string = ''.join(random.sample(combined_string, len(combined_string)))
    password = ""
    for char in shuffled_string:
        if random.random() < 0.3:  
            password += char.upper()
        elif random.random() < 0.2:  
            password += str(random.randint(0, 9))
        else:
            password += char
    if not any(char.isdigit() for char in password):
        password += str(random.randint(0, 9)) 
    if not any(char.isupper() for char in password):
        password += random.choice(string.ascii_uppercase) 
    return password

while True:
    name = input("Enter your name: ")
    pet_name = input("Enter your pet's name: ")
    birth_year = input("Enter your birth year: ")
    special_char = input("Enter a special character (!@#$...): ")
    password = generate_password(name, pet_name, birth_year, special_char)
    print("Generated Password:", password)
    repeat = input("Do you want to generate another password? (yes/no): ")
    if repeat.lower() != 'yes':
        break

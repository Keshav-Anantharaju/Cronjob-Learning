import os


def main():

    secret_key = os.getenv('MY_SECRET')  # Fetch the secret key from environment variable
    print(secret_key)
    if secret_key:
        print(f"Hello, World! The secret key is: I wont show")

if __name__ == '__main__':
    main()

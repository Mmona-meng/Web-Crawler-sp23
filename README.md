# Web-Crawler-sp23

This is a web crawler project for a computer networking class. The goal of the project is to find all secret flag messages from all pages on the "/fakebook/" website.

The program uses a TCP socket connection to send HTTP requests and receive responses. It logs in to the website using the provided username and password, retrieves cookies, and then crawls the website using breadth-first search. The program extracts the secret flags and the csrfmiddlewaretoken using an HTML parser class.

## Usage

To execute the program, you can run either of the following commands in your terminal:

`python3 webcrawler.py [username] [password]`

`./webcrawler [username] [password]`

The first command is for running the program on a Windows or Unix-based system, while the second command is a executable for running it on a Unix-based system.

The username is the prefix of your northeastern.edu email address, and password is your NUID.

For test purposes, you can use the following credentials:

*hidden

The program can handle various HTTP status codes, such as 301, 403, 404, and 500, depending on the situation. If there are any issues with the program, you can add print functions to each step of the main() function to see the status code and actual content.

After running the program, you will see a list of secret flags, which match the content of the file "secret_flags.txt".

## License

MIT License

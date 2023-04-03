#!/usr/bin/env python3

# author: Xiaoqing Meng

import socket
import sys
import ssl
from collections import deque
from html.parser import HTMLParser

# use a set to track unique URLs already crawled
visited_urls = set()
# use deque to track URLs to be crawled, and append the base URL /fakebook/ to be crawled
to_be_crawled = deque(['/fakebook/'])
# use a set to store unique secret flags found on the pages
secret_flags = set()
# use a list to hold the middlewaretoken
middlewaretoken = ""


class FakebookHTMLParser(HTMLParser):
    """
    The FakebookHTMLParser extends the HTML Parser to parse through the server response for tags in search of more URLs and/or secret flags respectively.
    """

    def __init__(self):
        super().__init__()
        self.csrfmiddlewaretoken = None

        """
        Method called by HTML Parser when start of new tag is encountered.
        Looks for anchor tags and extracts their href attribute as the next URL to be crawled.
        Looks for the secret_flag class and extracts the secret flag from the inner text.
        Looks for the csrfmiddlewaretoken and extracts the token value.
        """

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                # Looks for anchor tags and extracts their href attribute as the next URL to be crawled.
                if name == 'href' and '/fakebook/' in value and len(attrs) == 1:
                    to_be_crawled.append(value)

        elif tag == 'input':
            for name, value in attrs:
                # Looks for the csrfmiddlewaretoken and extracts the token value.
                if name == 'name' and value == 'csrfmiddlewaretoken':
                    for name, value in attrs:
                        if name == 'value':
                            self.csrfmiddlewaretoken = value

    def handle_data(self, data):
        # Looks for the secret_flag class and extracts the secret flag from the inner text.
        if "FLAG" in data:
            secret_flags.add(data.strip().split(":")[-1])
            print("Secret flag found: {}".format(data.strip().split(":")[-1]))


def parse_cmd_line():
    """ Parses the command line arguments for username and password. Throws error for invalid info. """

    username = ""
    password = ""

    try:
        username = sys.argv[1]
        password = sys.argv[2]
        return username, password

    except:
        if username == "":
            sys.exit("Please provide appropriate user name.")
        if password == "":
            sys.exit("Please provide appropriate password.")


def create_socket():
    """Creates a TLS wrapped socket to create a connection to http server. """
    port = 443
    host_name = 'project2.5700.network'

    # building connection
    try:
        context = ssl.create_default_context()
        sock = socket.create_connection((host_name, port))
        wrapped_socket = context.wrap_socket(
            sock, server_hostname=host_name)
        return wrapped_socket
    except socket.error as e:
        sys.exit("Connection error.: {}".format(str(e)))


def send_get_request(path, sock, host, cookie1=None, cookie2=None):
    """
    Sends GET request to the server with appropriate header fields, and handles cookies. Sends this header file to the server using socket
    """
    headers = f"GET {path} HTTP/1.1\r\n{host}\r\n"
    cookies = ""
    # add cookies to the header if they exist, and separate them with a semicolon
    if cookie1:
        cookies += f"{cookie1}"
    if cookie2:
        cookies += f"; {cookie2}"
    if cookies:
        headers += f"Cookie: {cookies}\r\n"
    headers += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36\r\n"
    headers += "\r\n"
    sock.sendall(headers.encode('utf-8'))


def receive_msg(sock):
    """
    Receives message from the server for any request sent by the client
    Receives message in a loop based on the content length given in the header
    """
    buffer_size = 4096  # Use a larger buffer size
    content_length = 0
    received_msg = bytearray()  # Use a bytearray to store the received data

    while True:  # keep receiving data until the content length is reached
        response = sock.recv(buffer_size)
        if response:
            received_msg += response

            # extract the content length from the header if it is not already extracted
            if not content_length:
                # find the end of the header
                header_end = received_msg.find(b"\r\n\r\n")
                # if the header is found
                if header_end != -1:
                    # extract the content length from the header
                    header = received_msg[:header_end]
                    content_length = getContent_length(header.decode())
                    if content_length == 0:
                        break

            if content_length:
                # check if the content length has been reached
                if len(received_msg) >= content_length + header_end + 4:
                    # all the data has been received
                    break
        else:
            break
    # convert the bytearray to a string
    received_msg = received_msg.decode('utf-8')
    return received_msg


def getContent_length(msg):
    # extract the content length from the header
    header_list = msg.split("\r\n")
    for header in header_list:
        if header.startswith("Content-Length: "):
            return int(header[16:])


def cookie_jar(msg):
    """
    Extract cookies from the response message
    Stores the session and/or the csrf cookies, return cookies
    """
    cookies = {}
    header_list = msg.split("\r\n")
    for header in header_list:
        if header.startswith("Set-Cookie: "):
            cookie = header[12:].split(";")[0]
            if cookie.startswith("sessionid") or cookie.startswith("csrftoken"):
                cookies[cookie.split("=")[0]] = cookie.split("=")[1]
    return cookies


def login_user(sock, path, host, body_len, body, cookie1=None, cookie2=None):
    """
    Creates a POST request and sends it to login to the fakebook site
    """
    request = f"POST {path} HTTP/1.1\r\n{host}\r\nContent-Length: {body_len}\r\nContent-Type: application/x-www-form-urlencoded\r\n"
    cookies = ""
    if cookie1:
        cookies += f"{cookie1}"
    if cookie2:
        cookies += f"; {cookie2}"
    if cookies:
        request += f"Cookie: {cookies}\r\n"
    request += "\r\n"
    request += body
    sock.sendall(request.encode('utf-8'))


def start_crawling(msg, sock, host, cookie3, cookie4):
    """
    Uses the HTML Parser object to parse through the current URL in search for more URLs and/or secret flags until all secret flags are found for the user.
    Accounts for and appropriately handles different errors received when parsing through pages.
    Use breadth-first search to crawl URLs, and keep track of visited URLs to avoid infinite loops.
    """
    parser = FakebookHTMLParser()
    parser.csrfmiddlewaretoken = middlewaretoken
    parser.feed(msg)

    while to_be_crawled and len(secret_flags) < 5:
        # Use breadth-first search to crawl URLs
        new_url = to_be_crawled.popleft()

        if new_url not in visited_urls:
            visited_urls.add(new_url)

            send_get_request(new_url, sock, host, cookie3, cookie4)
            response = receive_msg(sock)

            # Handle HTTP status codes
            if "HTTP/1.1 200 OK" not in response:
                status_code = response.split()[1]

                if status_code == "301":
                    # HTTP redirect, try again with new URL
                    new_url = response.split("Location: ")[1].split("\r\n")[0]
                    if new_url not in visited_urls:
                        to_be_crawled.append(new_url)
                elif status_code in ("403", "404"):
                    # Forbidden or not found, skip this URL
                    print(f"Error: Could not fetch URL - {new_url}")
                elif status_code == "500":
                    # Internal server error, try again
                    to_be_crawled.append(new_url)
                else:
                    print(
                        f"Error: Unexpected status code - {status_code} for URL - {new_url}")
                    continue
                continue

            # Parse the response for URLs and secret flags
            parser.feed(response)
            print("Crawled URL -", new_url)

    if len(secret_flags) == 5:
        print("All flags found!")
        for flag in secret_flags:
            print(flag)
    else:
        print("Could not find all flags.")


def main():
    host = "Host: project2.5700.network"
    root_path = "/"
    fakebook = "/fakebook/"
    login_path = "/accounts/login/?next=/fakebook/"

    # Parse the username and password from the command line
    username, password = parse_cmd_line()

    # Create TLS wrapped socket
    sock = create_socket()

    # Get the root page
    send_get_request(root_path, sock, host)
    response = receive_msg(sock)

    # Store session cookie
    cookies = cookie_jar(response)
    cookie1 = "sessionid=" + cookies["sessionid"]

    # Send GET request for login page
    send_get_request(login_path, sock, host, cookie1=cookie1)
    response = receive_msg(sock)

    # Check message for login page
    if "HTTP/1.1 200 OK" not in response:
        sys.exit("Error: Could not fetch login page.")

    # Retrieving csrf cookie and middleware token
    cookies = cookie_jar(response)
    cookie2 = "csrftoken=" + cookies["csrftoken"]
    parser = FakebookHTMLParser()
    parser.feed(response)
    middlewaretoken = parser.csrfmiddlewaretoken

    # Creating login body for user
    body = "username=" + username + "&password=" + \
        password + "&csrfmiddlewaretoken=" + middlewaretoken
    body_len = len(body)

    # Login user
    login_user(sock, login_path, host, body_len, body, cookie1, cookie2)

    # Store new cookies
    response_login = receive_msg(sock)
    cookies = cookie_jar(response_login)
    cookie3 = "sessionid=" + cookies["sessionid"]
    cookie4 = "csrftoken=" + cookies["csrftoken"]

    # Send request to go to my fakebook page
    send_get_request(fakebook, sock, host, cookie3, cookie4)
    response = receive_msg(sock)

    # Start your crawler
    start_crawling(response, sock, host, cookie3, cookie4)

    # close the socket - program end
    sock.close()


if __name__ == "__main__":
    main()

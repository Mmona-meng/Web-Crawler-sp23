# Web Crawler project

Group member:

Name: Xiaoqing Meng  NUID: 002983054

Name: Wenqiao Xu  NUID: 002978212

Name: Huazhou Liu  NUID: 002197947

High-level approach (all steps involved in logging in, crawling and getting the secret Flags):

Basically, it follows the steps

- builds the TCP socket connection
- send GET request to root page to retrieve session cookie
- send GET request to login page to retrieve session and CSRF cookie
- send POST request to login
- use the HTML parser class to look for anchor tags and extracts their href attribute as the next URL to be crawled, look for the secret flags and extracts the secret flag from the inner text, look for the csrfmiddlewaretoken and extracts the token value
- use Breath first search to crawl the website.
- return all the secret flags

Challenges faced:

Two biggest challenges as follows

- How to handle the cookies - sessionid and crvftoken. Since we're using the same `send_get_request` function for every GET request, some of them don't need cookies, some need one cookie, some need two cookies, I spent some time to figure out which one need what kind of cookies. Also, since the header have strict formatting requirements, I tested many times to pass the cookies in correct format.
- Increament buffer size and check for content length in the `receive_msg` function, I tested thousands of time to process any response from the server.

Overview of how to test the code:

You can add print function to each step in the `main()` fucntion, especially for each response message to see the status code and actual content, you can also print out the header info in the `send_get_request` function to see the cookie value. For example, add `print(headers + "---HEADER HERE")` after the `headers += "\r\n"` line in the `send_get_request` function.
Based on these prints, you can see each step clearly.

Who worked on what part(s) of the code:

All three of us discussed on how to start the project and provided solutions. After discussion, we decided to use breadth first search to crawl the website.
Xiaoqing did the majority of the code development, including solving the problems with the cookies, testing on user login and set GET and POST requests, optimizing the `receive_msg` funciton to process the request.
Wenqiao and Huazhou helped on testing the code, including debugging the send_get_request function, based on the request header and corresponding response message.

Steps on how to run your code:

For MacOS, simply run `python3 webcrawler.py [username] [password]`, you can pass in [name] and [NUID] of any of the three group members at the top.
Now that the file trun into a executable file, you can run `./webcrawler [username] [password]` to run the code.

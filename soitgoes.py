import bs4, requests, smtplib, re
import string, email
import sys, thread, time
from email.mime.text import MIMEText

# Number of threads currently executing
num_threads = 0
# If any thread has started
thread_started = False
# Lock for critical section
lock = thread.allocate_lock()

def send_email(email, title, link_param, server):
    # Get access to global variables
    global num_threads, thread_started

    # Lock the memory to do nonatomic operations
    lock.acquire()
    num_threads += 1
    thread_started = True
    #print 'THREAD CREATED: ' + str(num_threads) + ' ' + title
    # Release the lock so other threads can have access
    lock.release()

    # Set up the email   
    body_text = title + " is now on SIG: www.soitgo.es" + link_param
    msg = MIMEText(body_text.encode('utf-8'))
    msg['Subject'] = title
    msg['From'] = email
    msg['To'] = email

    # The actual mail send  
    # Sent from email to email with msg as the headers and body
    server.sendmail(email, email, msg.as_string()) 
    # Close server connection
    server.quit()
    
    # Acquire the lock for nonatomic operations
    lock.acquire()
    num_threads -= 1
    #print 'Thread for ' + title + ' is over '
    #release the lock so of threads can have access
    lock.release()

def main(argv):
    print "RUNNING!"
    # Get access to global variables
    global num_threads, thread_started
    
    # Variable to control writing to first found file
    first_title_saved = False
    
    # This is the title of the first item read during the last run
    last_read = [item for item in open('lastread.txt', 'r')]
    last_read_found = False
    
    # Login URL and parameters for SIG
    LOGIN_URL = 'https://soitgo.es/?i=redirect&r=YToxOntzOjE6ImkiO3M6NDoibWFpbiI7fQ=='
    PARAMS = {'user':argv[0], 'pass':argv[1]}
    
    # set up the username and password for the email account
    email_username = argv[2]
    email_password = argv[3]
    
    # Get homepage to get session cookie
    home_req = requests.get('https://soitgo.es')
    
    # Log into the website
    login_req = requests.post(LOGIN_URL, data=PARAMS, cookies=home_req.cookies)

    # Create a BeautifulSoup object using the HTML contents after logging in
    page = bs4.BeautifulSoup(login_req.content)
    
    # Create a list of wanted items from wanted.txt
    wanted = [item for item in open('wanted.txt', 'r')]
    
    # Loop through all the rows on the home page
    for row in page.find_all('div', class_='row'):
        # Get the category, title, and query string for link
        category = row.find(class_='category').text
        title = row.find(class_='title').text
        link_param = row.find_all('a')[1].get('href')

        # Filters out the porn
        if category != 'XXX':
            # Save the first non-Featured link we find
            if first_title_saved == False and category != 'Featured':
                # Open the file, write the title, the close
                write_title = open('lastread.txt', 'w')
                write_title.write(title)
                write_title.close()
                first_title_saved = True
                
            # Check to see if the current title hasn't been seen before
            if not title in last_read:
                # Skip the featured link
                if category != 'Featured':
                    # Loop through wanted items
                    for item in wanted:
                        # Remove the newline at the end of string
                        i = item[:-1]
                        # See if i is a substring in title
                        if re.search(i.lower(), title.lower()):
                            # Create a new server connection for each thread
                            server = smtplib.SMTP('smtp.gmail.com:587')  
                            server.starttls()
                            server.login(email_username, email_password)
                            # Create a new thread that will send the email out
                            thread.start_new_thread( send_email, (email_username, title, link_param, server,) )
                            #print title
                    
            # If the currently title has already been read
            else:
                # We found the first title read during the last run
                #   so break from the loop
                last_read_found = True
                break
            '''
            # Prints out all the category, title, and info
            row_text = ''
            for child in row.contents[:3]:
               row_text += child.text + ' '

            print row_text.encode('utf-8')
            '''
    # Idle this thread to allow any spawned threads to properly increment num_threads
    time.sleep(1)
    # Loops if we've found the last_read_item or num_threads > 0
    while ((not last_read_found) and thread_started == False) or (num_threads > 0):
        print "HERE IT IS"
        # print 'Waiting. Threads: ' + str(num_threads)
        pass  



if __name__ == '__main__':
    #Pass command line args to main
    main(sys.argv[1:])
import bs4, requests, smtplib, re
import string, email
import sys, thread, time
from email.mime.text import MIMEText

def main(argv):
    print "RUNNING!"
    # Variable to control writing to first found file
    first_title_saved = False
    
    # Set up body_text for later use
    body_text = ""
    
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
                            # Add it to the body of the email.
                            body_text = body_text + '\n' + title + " is now on SIG: www.soitgo.es" + link_param + '\n'
                    
            # If the currently title has already been read
            else:
                # We found the first title read during the last run
                #   so break from the loop
                break
    
    
    # Create a new server connection for each thread
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()
    server.login(email_username, email_password)
    
    # Set up the email   
    msg = MIMEText(body_text.encode('utf-8'))
    msg['Subject'] = "Matches found on SIG!"
    msg['From'] = email_username
    msg['To'] = email_username


    # The actual mail send  
    # Sent from email to email with msg as the headers and body
    server.sendmail(email_username, email_username, msg.as_string()) 
    # Close server connection
    server.quit()



if __name__ == '__main__':
    #Pass command line args to main
    main(sys.argv[1:])
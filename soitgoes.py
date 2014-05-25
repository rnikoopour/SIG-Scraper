import bs4, requests, smtplib, re
import string, email
import sys, thread, time
from email.mime.text import MIMEText

# This will hold our cookie gloablly
sig_cookies = None

def login_to_sig(sig_un, sig_pass):
    global sig_cookies
    
    # Login URL and parameters for SIG
    LOGIN_URL = 'https://soitgo.es/?i=redirect&r=YToxOntzOjE6ImkiO3M6NDoibWFpbiI7fQ=='
    PARAMS = {'user':sig_un, 'pass':sig_pass}
    
    # Get homepage to get session cookie
    home_req = requests.get('https://soitgo.es')
    
    # Store session cookie for later use in global variabele
    sig_cookies = home_req.cookies
    
    # Log into the website
    login_req = requests.post(LOGIN_URL, data=PARAMS, cookies=sig_cookies)
    return login_req
    
def scrape(sig_un, sig_pass, email_un, email_pass):
    print "\nScraping!\n"
    
    # Variable to control writing to first found file
    first_title_saved = False
    
    # Set up body_text for later use
    body_text = ""
    
    # This is the title of the first item read during the last run
    last_read = [item for item in open('lastread.txt', 'r')]
    last_read_found = False
    
    home_page = login_to_sig(sig_un, sig_pass)

    # Create a BeautifulSoup object using the HTML contents after logging in
    page = bs4.BeautifulSoup(home_page.content)
    
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
                lastread_file = open('lastread.txt', 'w')
                lastread_file.write(title)
                lastread_file.close()
                first_title_saved = True
                
            # Check to see if the current title hasn't been seen before
            if not title in last_read:
                # Skip the featured link
                if category != 'Featured':
                    # Loop through wanted items
                    for item in wanted:
                        # Remove the newline at the end of string
                        i = item.strip('\n')
                        # Remove any leading or trailing spaces
                        i = i.strip()
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
    server.login(email_un, email_pass)
    
    # Set up the email   
    msg = MIMEText(body_text.encode('utf-8'))
    msg['Subject'] = "Matches found on SIG!"
    msg['From'] = email_un
    msg['To'] = email_un


    # The actual mail send  
    # Sent from email to email with msg as the headers and body
    server.sendmail(email_un, email_un, msg.as_string()) 
    # Close server connection
    server.quit()
    
    print "\nDone Scraping!\n"
    
def search(sig_un, sig_pass, search_term):
    print "\nSearching!\n"
    
    # Get global reference so we can use the cookie provided to us
    global sig_cookies
    
    # Lets us know if we find results
    result_found = False
    
    # Log into the website
    login_to_sig(sig_un, sig_pass)

    # Set up the search url 
    search_url = 'https://soitgo.es/?i=' + search_term + '&do=search'
    
    # Get search results page and turn it into Beautiful Soup
    search_results = requests.get(search_url, cookies=sig_cookies)
    page = bs4.BeautifulSoup(search_results.content)
    
    # This grabs the blank row that is at the top of the search area
    blank_row = page.find_all('div', class_='row header')
    
    # Open searchresults.txt in write mode. This overwrites previous search results.
    results_file = open('results.txt', 'w')
    results_file.write('Category\tTitle\t\t\t\t\t\t\t\tLink\n')
    
    # Loop through all the rows
    for row in page.find_all('div', class_='row'):
        # If we found the blank row go ahead and go to the next item in the list
        if row in blank_row:
            pass
        else:
            # Result was found
            result_found = True
            # Get the category, title, and query string for link
            category = row.find(class_='category').text
            title = row.find(class_='title').text
            link_param = row.find_all('a')[1].get('href')
            if len(title) < 60:
                title = title + ' ' * (60 - len(title))
            print title[:60] + ' is on SIG: www.soitgo.es' + link_param
            results_file.write(category + '\t\t' + title[:55] + '\t\twww.soitgo.es' + link_param + '\n')
            
    if result_found == False:
        print "No Results Found."
        results_file.write("\nNo Results Found.\n")
    
    results_file.close()
    print "\nDone Searching. Information stored in results.txt\n"

def main(argv):
    if argv[0] == "scrape":
        scrape(argv[1], argv[2], argv[3], argv[4])
    elif argv[0] == "search":
        search(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    #Pass command line args to main
    main(sys.argv[1:])
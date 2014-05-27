SIG-Scrape
=========
SIG-Scrape can:

Scrape the homepage of SIG.  Send an email (only with gmail account) with the matching results as the body.
Search for a specific item.  Displays the results in the console and writes them to results.txt

Must have wanted.txt in the same directory
Must have lastread.txt in the same directory


Results of pip freeze:
=========
beautifulsoup4==4.3.2
requests==2.3.0
wsgiref==0.1.2

Add this to your bash profile to make searching easier:
=========
sigsearch() { 
    if [ "$1" == "-h" ]; then
        echo "sigsearch \"Search Term\""
        return
    fi
    
    if [ $# -eq 1 ]; then
        source /Location/To/Virtual/Env
        python /Path/To/soitgoes.py search SIG_UN SIG_PW "$@"
        deactivate
        return
    else
        echo "sigsearch \"Search Term\""
    fi
}

Use:
=========
This command scrapes the homepage
--
python soitgoes.py scrape SIG-username SIG-password email-username email-pass
--

This command searches SIG
--
python soitgoes.py search SIG-username SIG-password "Search Term"
--
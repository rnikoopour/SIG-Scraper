SIG-Scrape
=========
SIG-Scrape can:

Scrape the homepage of SIG.  Send an email with the matching results as the body.
Search for a specific item.  Displays the results in the console and writes them to results.txt

Must have wanted.txt in the same directory
Must have lastread.txt in the same directory

Use:
This command scrapes the homepage
--
python soitgoes.py scrape SIG-username SIG-password email-username email-pass
--

This command searches SIG
==
python soitgoes.py search SIG-username SIG-password "Search Term"
==
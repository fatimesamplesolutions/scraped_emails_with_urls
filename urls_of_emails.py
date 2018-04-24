import urllib.request
import re
import codecs
import pandas as pd
import requests
import socket
import lxml.html

working_urls = []
urls_to_scrape = []
scraped_emails = []
email_link = []

fileurls = codecs.open('urls-to-scrape.csv', 'r', 'latin-1')
filename = "scraped-emails-with-urls.csv"

try:
    f = open(filename, "a")
    f.seek(0)
    f.truncate()
except IOError:
    print("Close the .csv file in order for changes to append and re-execute")


# The function to verify URLs
def verify_urls(file):
    linelist = file.readlines()
    for url in linelist:
        url = url.strip('\r\n')
        try:
            socket.setdefaulttimeout(8000)
            req = requests.get("http://" + url)
            r = req.status_code
            request = str(r)

            if (request[0] == '2'):
                working_url = req.url
                working_urls.append(working_url)
            else:
                continue

        except urllib.error.URLError as e:

            continue

        except requests.exceptions.SSLError as q:
            continue

        except requests.exceptions.ConnectionError:
            continue


# The function to find top 50 internal links of a URL
def internal_links():
    for url in working_urls:
        fi = urllib.request.urlopen(url)
        s = fi.read().decode('utf-8')

        nlines = 0
        dom = lxml.html.fromstring(s)
        for link in dom.xpath('//a/@href'):
            # print(link)
            nlines += 1
            # working_urls.append(link)
            if nlines >= 50:
                break
            urls_to_scrape.append(link)


# The function to scrape emails
def scrape_emails():
    # sleep(30)
    for url in urls_to_scrape:
        if (len(url) == 0):
            continue
        try:
            fi = urllib.request.urlopen(url)
            s = fi.read().decode('utf-8')

            emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", s)
            for email in emails:
                if (email[-3:] == 'gif' or email[-3:] == 'png' or email[-3:] == 'jpg' or email[-3:] == 'tif' or email[
                                                                                                                -3:] == 'svg'):
                    continue
                else:
                    # print(email)
                    scraped_emails.append(email)
                    email_link.append(url)

        except urllib.error.URLError:
            # The reason for this error. It can be a message string or another exception instance.
            continue

        except requests.exceptions.ConnectionError:
            # print("Connection Refused")
            continue

        except:
            continue


# Calling functions
verify_urls(fileurls)
internal_links()
scrape_emails()

# Creating dataframe and saving the result
raw_data = {'Scraped e-mails': scraped_emails, 'Url': email_link}
df = pd.DataFrame(raw_data, columns=['Scraped e-mails', 'Url'])
df.to_csv(f, index=False)

f.close()

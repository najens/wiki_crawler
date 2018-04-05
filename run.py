import requests
from bs4 import BeautifulSoup

from time import sleep
from urllib.parse import urljoin

start_url = "https://en.wikipedia.org/wiki/Special:Random"
target_url = "https://en.wikipedia.org/wiki/Philosophy"

def download_article(url):
    """
    Downloads the html from the internet
        url: is the url of the last article in the article chain
    """
    response = requests.get(url)
    html = response.text
    return html

def find_first_link(html):
    """
    Finds the first link in a wikipedia article
        soup: is the soup object created after downloading and parsing the html
    """
    soup = BeautifulSoup(html, 'html.parser')

    # This div contains the article's body
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    # stores the first link found in the article, if the article contains no
    # links this value will remain None
    article_link = None

    # Find all the direct children of content_div that are paragraphs
    for element in content_div.find_all("p", recursive=False):

        # Find the first anchor tag that's a direct child of a paragraph.
        # It's important to only look at direct children, because other types
        # of link, e.g. footnotes and pronunciation, could come before the
        # first link to an article. Those other link types aren't direct
        # children though, they're in divs of various classes.
        if element.find("a", recursive=False):
            article_link = element.find("a", recursive=False).get('href')
            break

    if not article_link:
        return

    # Build a full url from the relative article_link url
    first_link = urljoin("https://en.wikipedia.org/", article_link)
    return first_link

def continue_crawl(search_history, target_url, max_steps = 25):
    """
    Determines whether or not we should keep crawling
        search_history: is a list of strings which are urls of Wikipedia
                        articles. The last item in the list is the most
                        recently found url.
        target_url: is a string, the url of the article that the search
                    should stop at if it is found.
    """
    if search_history[-1] == target_url:
        print("Congratulations! You reached the target Url. The article chain was {} article(s) long.".format(len(search_history)))
        return False
    elif len(search_history) > max_steps:
        print("The article chain has exceeded 25 articles so we are giving up.")
        return False
    elif search_history[-1] in search_history[:-1]:
        print("Uh oh! You got caught in an endless loop of articles.")
        return False
    else:
        return True

article_chain = [start_url]

while continue_crawl(article_chain, target_url):
    print(article_chain[-1])

    first_link = find_first_link(download_article(article_chain[-1]))
    if not first_link:
        print("We've arrived at an article with no links, aborting search!")
        break

    article_chain.append(first_link)

    sleep(2) # Slow things down so as to not hammer Wikipedia's servers

# Test to see if find_first_link works as expected
print(find_first_link(download_article("https://en.wikipedia.org/wiki/Taco")))

# Tests to see if continue_crawl function works as expected
test1 = continue_crawl(["1","2","3"], "3")
print("TEST 1: expected result \"Congratulations...\" and False, actual result {}".format(test1))

test2 = continue_crawl(["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26"], "27")
print("TEST 2: expected result \"The article chain has exceeded...\" and False, actual result {}".format(test2))

test3 = continue_crawl(["1","2","2"], "3")
print("TEST 3: expected result \"Uh oh! You got...\" and False, actual result {}".format(test3))

test4 = continue_crawl(["1","2","3"], "4")
print("TEST 4: expected result True, actual result {}".format(test4))

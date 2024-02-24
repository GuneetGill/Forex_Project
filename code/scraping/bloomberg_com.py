from bs4 import BeautifulSoup
import cloudscraper

#this is really from website reuters which gives finanical news 

# take in article card and return dictionary
def get_article(card):
    if card:
        return dict(
            #key is headline
            headline=card.get_text(strip=True),
            # link to headline so main url + card url stuff
            link='https://www.reuters.com' + card.get('href')
        )
    else:
        return None

def bloomberg_com():
    # create scraper
    s = cloudscraper.create_scraper()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
    }

    # url for website and send in headers
    resp = s.get("https://www.reuters.com/business/finance/", headers=headers)

    soup = BeautifulSoup(resp.content, 'html.parser')

    #print(soup)

    links = []

    # select items that begin with media story card body that tells us there will be a media story
    # this will find elements that begin with that name
    cards = soup.select('[class^="media-story-card__body"]')
    for card in cards:
        # after we found all those cards, we need to find headings so loop through all
        # and find those with the keyword heading
        ca = card.find('a', {'data-testid': 'Heading'})
        # add that article for the given card to the list
        article = get_article(ca)

        #only add if something is retuened
        if article:
            # Ensure that the headline and link are simple data types
            links.append({
                'headline': str(article['headline']),
                'link': str(article['link'])
            })
    
    return links




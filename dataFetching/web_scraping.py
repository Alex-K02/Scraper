import requests, vars, re, datetime
from bs4 import BeautifulSoup
from urllib import robotparser
import cohere, time
#for multiple looping
import itertools

## Robots exclusion standard
def can_fetch(url, user_agent='*'):
    domain = url.split('/')[2]
    robots_url = f"https://{domain}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        response.encoding = 'utf-8'  # Try utf-8 encoding first
        rp.parse(response.text.splitlines())
    except UnicodeDecodeError:
        try:
            response.encoding = 'ISO-8859-1'  # Fallback to ISO-8859-1 encoding
            rp.parse(response.text.splitlines())
        except UnicodeDecodeError:
            response.encoding = 'windows-1252'  # Fallback to windows-1252 encoding
            rp.parse(response.text.splitlines())
    return rp.can_fetch(user_agent, url)

##TODO: site scraping from different websites 
# Mb stick with this idea: scan website for all <a> elemets
# and then just search through them finding the searched links
## data base or mb other options
def tag_splitting(data):
    client = cohere.Client(
        vars.COHERE_API_KEY
    )
    response = client.chat(
        message = f"""You are a language model trained to analyze text and identify important keywords. Your task is to extract a list of the most relevant keywords from the given article. A keyword is defined as a significant word or phrase that represents the main topics or themes of the article. Please provide a list of 10 keywords separated by commas.
            Article: {data}
            Keywords:
            """
    )
    for key in response.text.split(", "):
        print(f"{str.lower(key)}\n")

def web_scraping(current_datetime:str, urls, max_result:int):
    search_URLs = ["https://thehackernews.com/"]
    for link in search_URLs:
        if can_fetch(link):
            #for a sraping only current date needed
            #datetime.today().strftime('%Y-%m-%d')
            if not current_datetime:
                #current_datetime = datetime.datetime.now.isoformat()
                current_datetime = "2024-06-19T16:19:00%2B05:30"
            if not max_result:
                max_result = 9
            
            ## TODO: check idea with scraping all the "a" elements and then defining the links that are searched

            #updated-max={datetime}&max-result={max_result}
            for day in range(19, 20):
                jql_query = f"{search_URLs[0]}search?updated-max=2024-06-{day}T16:19:00%2B05:30&max-result={max_result}"
                request = requests.get(jql_query)
                #check if query was succesful
                if request.status_code == 200:
                    soup = BeautifulSoup(request.content, 'html.parser')
                    pages = soup.find_all('div', class_='body-post')
                    story_links = [page.find('a', class_='story-link') for page in pages] 
                    links = [link['href'] for link in story_links]
                    print(links)
                    #page_scraping
                else:
                    print(request.status_code)
                time.sleep(5)
                print("\n")
        else:
            print(f"Fetching is not allowed by robots.txt: {link}")
            return None
        
        

def page_scraping(link):
    #only for test(can be removed)
    if can_fetch(link):
        request = requests.get(link)
        soup = BeautifulSoup(request.content, 'html.parser')

        title_text_elements = []
        article_text_elements = []
        
        for (text_filter, title_filter) in itertools.zip_longest(vars.article_text_filters, vars.title_text_filters):
            #filter by some filters
            text_elements = soup.find_all('div', class_=text_filter)
            title_elems = soup.find_all(vars.title_tags)
            if soup.find_all(vars.title_tags) and not title_text_elements:
                title_text_elements = page_elements_filtering(title_elems, vars.title_text_filters, vars.title_tags)
            #go through the filtered element and find text
            if soup.find_all('div', class_=text_filter) and not article_text_elements:
                article_text_elements = page_elements_filtering(text_elements, vars.article_text_filters, vars.text_tags)

        ##
        article_text_elements = [item.get_text().strip() for sublist in article_text_elements for item in sublist]
        title_text_elements = [item.get_text().strip() for sublist in title_text_elements for item in sublist]
            

        return title_text_elements + article_text_elements
    else:
        print(f"Fetching is not allowed by robots.txt: {link}")
        return None
    # tag_splitting(article_text)

def page_elements_filtering(page_elements, filters, tags):
    output = []
    check = []
    for element in page_elements:
        for new_filter in filters:
            res = element.find_all(tags, class_=new_filter)
            if res:
                output.extend(res)
                return output
        res = element.find_all(tags)
        if res and not check:
            check.extend(res)
        elif not check:
            check.append(element)

    return output if output else check
        
def main():
    #web_scraping(None,None, 9)
    # check ny times(it didnt work)https://www.nytimes.com/2024/06/26/technology/ai-consultants.html
    #https://www.wired.com/story/labgenius-antibody-factory-machine-learning/

    ## check this one (the author text is also copied) => https://www.techradar.com/computing/artificial-intelligence/this-new-ai-voice-assistant-beat-openai-to-one-of-chatgpts-most-anticipated-features
    # and this one https://www.pcworld.com/article/2387530/hacker-leaked-10-billion-passwords-heres-what-to-do.html
    print(page_scraping("https://www.pcworld.com/article/2387530/hacker-leaked-10-billion-passwords-heres-what-to-do.html"))

if __name__ == "__main__":
    main()

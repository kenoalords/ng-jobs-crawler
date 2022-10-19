import requests
from datetime import datetime
import time
from bs4 import BeautifulSoup


JOB_LINKS = [{
    "name": "naijahotjobs",
    "url": "https://www.hotnigerianjobs.com/category/legal/legal-jobs-in-nigeria"
}]

def crawler():
    if len(JOB_LINKS) > 0:
        start_time = time.time()
        for job in JOB_LINKS:
            request = requests.get(job["url"])
            if job["name"] == "naijahotjobs" and request.status_code == 200:
                results = parse_naijahotjobs(request)
                if results is not None:
                    # Send post request to API
                    print(results)
        print("Crawler executed in: ", time.time() - start_time)    


def parse_naijahotjobs(request):
    bs = BeautifulSoup(request.content, "html.parser")
    results = bs.find_all("div", class_="mycase")

    if len(results) > 0:
        post_body = []
        for result in results:
            title = result.find("h1")
            if title != None:
                link = ""
                description = ""
                date_posted = ""
                description_tag = result.find("div", class_="mycase4")
                anchor_tag = result.find_all("a")[0]
                date_tag = result.find_all("span", class_="semibio")[0]
                
                if date_tag is not None:
                    date_text = date_tag.text.replace("Posted on ", "").replace(" - ", "").split(" ")
                    formatted_date_text = "{day}/{month}/{year}".format(day=date_text[1][:2], month=date_text[2].replace(",", ""), year=date_text[3])
                    try:
                        date_posted = str(datetime.strptime(formatted_date_text, '%d/%b/%Y'))
                    except Exception as e:
                        print(e)
                        pass

                if anchor_tag != None:
                    link = anchor_tag["href"]

                if description_tag is not None:
                    description = description_tag.text.strip()
                
                job_object = {
                    "title": title.text.strip(),
                    "description": description,
                    "link": link,
                    "date_posted": date_posted,
                    "source": {
                        "name": "naijahotjobs",
                        "url": "https://naijahotjobs.com"
                    }
                }
                post_body.append(job_object)
            return post_body
            break
    return None

if __name__ == "__main__":
    crawler()
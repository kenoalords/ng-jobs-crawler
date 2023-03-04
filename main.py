import os
import requests
from datetime import datetime
import time
from bs4 import BeautifulSoup

# https://www.myjobmag.com/jobs-by-field/legal

JOB_LINKS = [{
    "name": "myjobmag",
    "url": "https://www.myjobmag.com/jobs-by-field/legal"
},{
    "name": "naijahotjobs",
    "url": "https://www.hotnigerianjobs.com/category/legal/legal-jobs-in-nigeria"
}]

settings = {}

dir = os.path.abspath(os.getcwd())

with open(os.path.join(dir, "app.txt"), mode="r") as cred:
    for x in cred:
        parts = x.split("=")
        settings[parts[0]] = parts[1].strip()

# print(settings)
# print(path)

def crawler():
    if len(JOB_LINKS) > 0:
        start_time = time.time()
        
        crawled_jobs = []
        for job in JOB_LINKS:
            request = requests.get(job["url"])

            # Fetch jobs from naijahotjobs
            if job["name"] == "naijahotjobs" and request.status_code == 200:
                results = parse_naijahotjobs(request)
                if results is not None:
                    # Send post request to API
                    crawled_jobs.extend(results)
                    # print(results)

            # Fetch jobs from myjobmag.com
            if job["name"] == "myjobmag" and request.status_code == 200:
                results = parse_myjobmag(request)
                if results is not None:
                    # Send post request to API
                    crawled_jobs.extend(results)
        print("Crawler executed in: ", time.time() - start_time)   
        # print(crawled_jobs) 

        # Post currated jobs to API
        if len(crawled_jobs) > 0:
            for job in crawled_jobs:
                payload = {
                        "title": job["title"], 
                        "description": job["description"], 
                        "link": job["link"],
                        "source": job["source"]["name"]
                    }
                request = requests.post("{endpoint}/api/cms/jobs/".format(endpoint=settings["API_ENDPOINT"]), json=payload, headers={"Authorization": settings["ACCESS_TOKEN"]})
            print("Jobs posted successfully")


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
            
    return None


def parse_myjobmag(request):
    bs = BeautifulSoup(request.content, "html.parser")
    results = bs.find_all("li", class_="job-info")

    if len(results) > 0:
        post_body = []
        for result in results:
            title = result.find("h2")
            if title is not None:
                link = ""
                description = ""
                date_posted = ""
                description_tag = result.find("div", class_="job-desc")
                anchor_tag = result.find_all("a")[0]
                date_tag = result.find("li", id="job-date")
                
                if date_tag is not None:
                    date_text = date_tag.text.strip()
                    try:
                        date_posted = str(datetime.strptime(date_text, '%d %B'))
                    except Exception as e:
                        print(e)
                        pass

                if anchor_tag != None:
                    link = "https://www.myjobmag.com{link}".format(link=anchor_tag["href"])

                if description_tag is not None:
                    description = description_tag.text.strip()
                
                job_object = {
                    "title": title.text.strip(),
                    "description": description,
                    "link": link,
                    "date_posted": date_posted,
                    "source": {
                        "name": "myjobmag",
                        "url": "https://www.myjobmag.com"
                    }
                }
                post_body.append(job_object)
        return post_body
            
    return None

if __name__ == "__main__":
    crawler()
    # pass

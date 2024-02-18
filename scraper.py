import requests
from tkinter import filedialog


headers = {'User-Agent': 'Mozilla/5.0'}

# /html/body/center[3]/div/p/img

def scrapeCover(comicLink, session): 
    coverImage = ""
    imageRequest = session.get(comicLink, headers=headers)
    print(comicLink)
    print(imageRequest)
    images = imageRequest.html.xpath('/html/body/center[3]/div/p/img')
    for image in images:
         coverImage = image.attrs['src']
    return coverImage

def scrapeTitles(url):
        comicTitles = [] 
        parsedTitles = url.html.xpath("/html/body/div[2]/div/div/ul/li")
        for child in parsedTitles:
            comicTitles.append(child.text)
        return comicTitles

def scrapeIssues(url):
    comicIssues = []
    parsedIssues = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li")
    for child in parsedIssues:
        comicIssues.append(child.text)
    return comicIssues


def scrapePages(issueName, session, oddChars):
     pageNum = 0 
     for char in oddChars:
            issueName = issueName.replace(char, "-")

     issueBase = "https://readallcomics.com/"
     issueLink = (issueBase + issueName).lower()

     print(issueLink)
    
     issueRequest = session.get(issueLink, headers=headers)
     images = issueRequest.html.xpath('.//img')
     
     directory = filedialog.askdirectory()
     for image in enumerate(images):
        pageNum += 1     
                       

     for idx, image in enumerate(images):
        src = image.attrs['src']
        pageResponse = requests.get(src)

        with open(f"{directory}/#{idx + 1}.jpg", 'wb') as f:
            f.write(pageResponse.content)
        
     print(f"{pageNum} page(s)")
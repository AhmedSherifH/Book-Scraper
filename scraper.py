import requests
from tkinter import filedialog
import re


headers = {'User-Agent': 'Mozilla/5.0'}
issueHref = ''
comicDownloads = []


def scrapeCover(comicLink, session, selectedHost): 

    coverImage = ""
    imageRequest = session.get(comicLink, headers=headers)
    print(comicLink)
    print(imageRequest)

    if selectedHost == "readallcomics.com":
        images = imageRequest.html.xpath('/html/body/center[3]/div/p/img')
        for image in images:
            coverImage = image.attrs['src']
        return coverImage
            

    if selectedHost == "readcomiconline.li":
        coverImage = imageRequest.html.xpath('//img')
        print(f"{selectedHost}{coverImage[1].attrs['src']} ---- > IMAGE")
        coverImage =  f"https://{selectedHost}{coverImage[1].attrs['src']}"
        return coverImage
        
def scrapeTitles(url, selectedHost, requestedComic):

        requestedComic = requestedComic.replace(" ", "-")
        
        comicTitles = {}
        if selectedHost == "readallcomics.com":
            parsedTitles = url.html.xpath("/html/body/div[2]/div/div/ul/li/a")
            for child in parsedTitles:
             
             titleHref = child.attrs['href']
             titleName = child.text
             comicTitles[titleName] = titleHref

            print(comicTitles)
            return comicTitles

        


def scrapeIssues(url, selectedHost):    
    comicIssues = {}
    if selectedHost == "readallcomics.com":
        parsedIssues = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li/a")
        for child in parsedIssues:
            issueName = child.text
            issueHref =  child.attrs['href']
            comicIssues[issueName] = issueHref
        return comicIssues
    
    
   

          
def scrapePages(issueLink, session, selectedHost, issueNameDownload,  downloads):
     
     pageNum = 0 
     directory = filedialog.askdirectory()
    
     if directory != '':
        comicDownloads.append(issueNameDownload)
        downloads.configure(text=", ".join(comicDownloads))

        if selectedHost == "readallcomics.com":
                
                issueRequest = session.get(issueLink, headers=headers)
                images = issueRequest.html.xpath('.//img')  
                
                for image in enumerate(images):
                    pageNum += 1     

                for idx, image in enumerate(images):
                    src = image.attrs['src']
                    pageResponse = requests.get(src)

                    with open(f"{directory}/#{idx + 1}.jpg", 'wb') as f:
                        f.write(pageResponse.content)
                
                print(f"{pageNum} page(s)")

        comicDownloads.remove(issueNameDownload)
        downloads.configure(text=",".join(comicDownloads))
import requests
from tkinter import filedialog


headers = {'User-Agent': 'Mozilla/5.0'}
issueHref = ''


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
        
        comicTitles = [] 
        if selectedHost == "readallcomics.com":
            parsedTitles = url.html.xpath("/html/body/div[2]/div/div/ul/li")
            for child in parsedTitles:
             comicTitles.append(child.text)
            return comicTitles

        
        if selectedHost == "readcomiconline.li":
            links = url.html.find('a')

            for link in links:
                comicName = link.attrs['href'].lower()
                comicName = comicName.replace("/comic/", "")
                requestedComic = requestedComic.replace("\n", "")
        
                if str(requestedComic).lower() in comicName:
                    comicTitles.append(comicName.title())
            
            comicTitles = list(set(comicTitles))
            return comicTitles
        


           


def scrapeIssues(url, selectedHost):    
    comicIssues = []
    if selectedHost == "readallcomics.com":
        parsedIssues = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li")
        for child in parsedIssues:
            comicIssues.append(child.text)
        return comicIssues
    
    
    if selectedHost == "readcomiconline.li":
        issues = url.html.xpath('//ul[@class="list"]/li//a')
        print(issues)

        for issue in issues:
            comicIssue = issue.attrs['href']  
            issueHref = comicIssue
            comicIssues.append(comicIssue)
            comicIssue = comicIssue.replace('/Comic/', '')  
            comicIssue = comicIssue.split('?')[0]  
            comicIssues.append(comicIssue)

        return comicIssues



          


def scrapePages(issueName, session, oddChars, selectedHost, issueHrefComic):
     
     pageNum = 0 
     directory = filedialog.askdirectory()

     for char in oddChars:
            issueName = issueName.replace(char, "-")
            
     if selectedHost == "readallcomics.com":
            issueBase = "https://readallcomics.com/"
            issueLink = (issueBase + issueName).lower()

            print(issueLink)
            
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

     elif selectedHost == "readcomiconline.li":
         issueBase = "https://readcomiconline.li"

         issueLink = (f"{issueBase}{issueHrefComic}&s=&readType=1").lower()
         print(issueLink)
         issueRequest = session.get(issueLink, headers=headers)
         images = issueRequest.html.xpath('/html/body/div[1]/div[4]/div[5]/p[1]')
         """  
         images = issueRequest.html.xpath('.//img')
         for image in enumerate(images):
                pageNum += 1     

         for idx, image in enumerate(images):
                src = image.attrs['src']
                 #   pageResponse = requests.get(src)
         #       print(src)

                #with open(f"{directory}/#{idx + 1}.jpg", 'wb') as f:
                 #       f.write(pageResponse.content)
             
         """
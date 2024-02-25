import requests
from tkinter import filedialog


headers = {'User-Agent': 'Mozilla/5.0'}
issueHref = ''
bookDownloads = []


def scrapeCover(bookLink, session, selectedHost): 

    coverImage = ""
    imageRequest = session.get(bookLink, headers=headers)
    print(bookLink)
    print(imageRequest)

    if selectedHost == "readallcomics.com":
        images = imageRequest.html.xpath('/html/body/center[3]/div/p/img')
        for image in images:
            coverImage = image.attrs['src']
        return coverImage
            


def scrapeTitles(url, selectedHost, requestedBook):

        requestedBook = requestedBook.replace(" ", "-")
        
        bookTitles = {}
        if selectedHost == "readallcomics.com":
            parsedTitles = url.html.xpath("/html/body/div[2]/div/div/ul/li/a")
            for child in parsedTitles:
             
             titleHref = child.attrs['href']
             titleName = child.text
             bookTitles[titleName] = titleHref

            print(bookTitles)
            return bookTitles

        

def scrapeIssues(url, selectedHost):    
    bookChapters = {}
    if selectedHost == "readallcomics.com":
        parsedIssues = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li/a")
        for child in parsedIssues:
            chapterName = child.text
            chapterHref =  child.attrs['href']
            bookChapters[chapterName] = chapterHref
        return bookChapters
    
    
   

          
def scrapePages(chapterLink, session, selectedHost, bookName, downloads, isMassDownload, directory):
     
     pageNum = 0 
     if isMassDownload == False:
        chosenDir = filedialog.askdirectory()
     else:
        chosenDir = directory
     if chosenDir != '': 
            bookDownloads.append(bookName)
            downloads.configure(text=", ".join(list(set(bookDownloads))))
            if selectedHost == "readallcomics.com":
                       
                issueRequest = session.get(chapterLink, headers=headers)
                images = issueRequest.html.xpath('.//img')  
                    
                for image in enumerate(images):
                        pageNum += 1     

                for idx, image in enumerate(images):
                        src = image.attrs['src']
                        pageResponse = requests.get(src)

                        print(f"{chosenDir}/#{idx + 1}.jpg")
                        with open(f"{chosenDir}/#{idx + 1}.jpg", 'wb') as f:
                            f.write(pageResponse.content)
                    
                print(f"{pageNum} page(s)")
            bookDownloads.remove(bookName)
            downloads.configure(text=",".join(list(set(bookDownloads))))

     
            
           

 
  

        
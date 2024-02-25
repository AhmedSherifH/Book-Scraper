import requests
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox



headers = {'User-Agent': 'Mozilla/5.0'}
issueHref = ''
bookDownloads = []


def scrapeCover(bookLink, session, selectedHost): 

    print(bookLink)
    coverImage = ""
    imageRequest = session.get(bookLink, headers=headers)
    print(bookLink)
    print(imageRequest)

    if selectedHost == "readallcomics.com":
        images = imageRequest.html.xpath('/html/body/center[3]/div/p/img')
        for image in images:
            coverImage = image.attrs['src']
        return coverImage
    
    if selectedHost == "mangakakalot.com":  
        images = imageRequest.html.xpath('//img[@class="img-loading"]')
        for image in images: 
            alt = image.attrs.get('alt', 'No alt attribute')
            if image.attrs['alt'] == alt:
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
        
        if selectedHost == "mangakakalot.com":
            divs = url.html.find('.story_item')
            for div in divs:
                titleHref = div.find('.story_name a', first=True).attrs['href']
                titleName = div.find('.story_name a', first=True).text
                bookTitles[titleName] = titleHref

            return bookTitles
            
        

def scrapeIssues(url, selectedHost):    
    bookChapters = {}

    if selectedHost == "readallcomics.com":
        parsedChapters = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li/a")
        for child in parsedChapters:
            chapterName = child.text
            chapterHref =  child.attrs['href']
            bookChapters[chapterName] = chapterHref
        return bookChapters
    
    if selectedHost == "mangakakalot.com":
        parsedChapters = url.html.find('.chapter-name')
        for chapter in parsedChapters:
            chapterName = chapter.text
            chapterHref = chapter.attrs['href']
            bookChapters[chapterName] = chapterHref 
        
        return bookChapters


        
    
   

          
def scrapePages(chapterLink, session, selectedHost, bookName, downloads, isMassDownload, directory, downloading):
     
     pageNum = 0 
     if isMassDownload == False:
        chosenDir = filedialog.askdirectory()
     else:
        chosenDir = directory
     try:
        if chosenDir != '':
            bookDownloads.append(bookName)
            downloading.configure(text="Downloading: ")
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
            downloads.configure(text=", ".join(list(set(bookDownloads))))
     except:
        messagebox.showerror("Error", "There was a problem while downloading. Make sure your directory path is correct.")

     if len(bookDownloads) == 0:
        downloading.configure(text="")
    
     
            
           

 
  

        
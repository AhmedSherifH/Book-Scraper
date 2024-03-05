import requests
from tkinter import filedialog
from pathlib import Path
from tkinter import messagebox
from format_manager import *



headers = {'User-Agent': 'Mozilla/5.0'}
issueHref = ''
bookDownloads = []
compressedChapters = []


def scrapeCover(bookLink, session, selectedHost): 

    coverImage = ""
    imageRequest = session.get(bookLink, headers=headers)

   # Get coverImage from the website source code, xpath differs across different websites
    if selectedHost == "readallcomics.com":
        images = imageRequest.html.xpath('/html/body/center[3]/div/p/img')
        for image in images:
            coverImage = image.attrs['src']
        return coverImage
    
    if selectedHost == "mangakomi.io":  
        images = imageRequest.html.xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[3]/div[1]/a/img')
        img_tag = images[0] 
        coverImage = img_tag.attrs['data-src']
        return coverImage
    
    if selectedHost == "mangafire.to":
        div = imageRequest.html.find('div.poster', first=True)
        if div:
            img = div.find('img', first=True)
            if img:
                coverImage = img.attrs.get('src')
                return coverImage
        
            


def scrapeTitles(url, selectedHost, requestedBook):
        
        requestedBook = requestedBook.replace(" ", "-")
        bookTitles = {}

   # Retrieve all book titles that contain the same words as those entered by the user
        if selectedHost == "readallcomics.com":
            parsedTitles = url.html.xpath("/html/body/div[2]/div/div/ul/li/a")
            for child in parsedTitles:
             titleHref = child.attrs['href']
             titleName = child.text
             bookTitles[titleName] = titleHref
        
        if selectedHost == "mangakomi.io":
            links = url.html.find('.post-title a')
            for link in links:
                titleHref = link.attrs['href']
                titleName = link.text
                bookTitles[titleName] = titleHref

        # While searching for titles in mangafire.to, several chapter links are included so any link with the word 'chapter' in it gets filtered as we only want to get book titles
        if selectedHost == "mangafire.to":
            div = url.html.find('div.original.card-lg', first=True)
            if div:
                hrefs = div.find('a')
                for href in hrefs:
                    if 'chapter' not in href.attrs['href']:
                        if href.text not in [""]:
                            titleHref = href.attrs['href']
                            titleName = href.text
                            bookTitles[titleName] = titleHref
        return bookTitles



def scrapeChapters(url, selectedHost):    
    bookChapters = {}

  # Get all chapters within a book
    if selectedHost == "readallcomics.com":
        parsedChapters = url.html.xpath("/html/body/center[3]/div/div[2]/ul/li/a")
        for child in parsedChapters:
            chapterName = child.text
            chapterHref =  child.attrs['href']
            bookChapters[chapterName] = chapterHref
    
    if selectedHost == "mangakomi.io":
      chapters = url.html.find('li.wp-manga-chapter')
      for chapter in chapters:
        href = chapter.find('a', first=True).attrs['href']
        title = chapter.find('a', first=True).text
        bookChapters[title] = href

    if selectedHost == "mangafire.to":
        div = url.html.find('div.list-body', first=True)
        if div:
            elements = div.find('li.item')  
            for element in elements:
                a_tag = element.find('a', first=True)
                if a_tag:
                    href = a_tag.attrs.get('href')
                    title = a_tag.find('span', first=True).text.strip()
                    bookChapters[title] = href

    return bookChapters


        
    
          
def scrapePages(chapterLink, session, selectedHost, bookName, downloads, isMassDownload, directory, downloading, format, numberofLoops, cbzVerification, zipCompression):
     
     
     pageNum = 0 
     imageContents = []
     global compressedChapters

  # If isMassDownload is True, we don't ask for the directory because the user has already chosen the directory in user_interface.py
     if isMassDownload == False:
        chosenDir = filedialog.askdirectory()
     else:
        chosenDir = directory
     try:
        if chosenDir != '' and chosenDir is not None:
            print(chapterLink)
            print(f'SELECTED HOST {selectedHost}')
            bookDownloads.append(bookName)
            downloading.configure(text="Downloading: ")
            downloads.configure(text=", ".join(list(set(bookDownloads))))
            if selectedHost == "readallcomics.com":
                       
                issueRequest = session.get(chapterLink, headers=headers)
                images = issueRequest.html.xpath('.//img')  
                    
                for pageNum, image in enumerate(images, 1):
                        if pageNum == 1:
                            continue
                        src = image.attrs['src']
                        pageResponse = requests.get(src)
                        print(f"{chosenDir}/#{pageNum}.jpg")
                        imageContents.append(pageResponse.content)


            if selectedHost == "mangakomi.io":
                issueRequest = session.get(chapterLink, headers=headers)
                images = issueRequest.html.xpath('//img')  
                
                if selectedHost == "mangakomi.io":
                    issueRequest = session.get(chapterLink, headers=headers)
                    images = issueRequest.html.xpath('//img')  
                                
                    for image in images:
                        if 'data-src' in image.attrs:
                         src = image.attrs.get('data-src')
                         src = src.strip()
                         if 'cdn' in src:
                             pageNum += 1 
                             print(f"#{pageNum}: {src}")            
                             pageResponse = requests.get(src) 
                             imageContents.append(pageResponse.content)

            if format == ".cbz":
                for page in imageContents:
                    compressedChapters.append(page)

                if cbzVerification == numberofLoops:
                    createCbz(compressedChapters, f"{chosenDir}/{bookName}.cbz")
                    if len(compressedChapters) > 0:
                        compressedChapters = []
 
            if format == ".zip":
                for page in imageContents:
                    compressedChapters.append(page)

                if cbzVerification == numberofLoops:
                    createZip(compressedChapters, f"{chosenDir}/{bookName}.zip", zipCompression)
                    if len(compressedChapters) > 0:
                        compressedChapters = []
 
            if format == ".jpg":
                createJpg(imageContents, chosenDir)

            bookDownloads.remove(bookName)
            downloads.configure(text=", ".join(list(set(bookDownloads))))
     except:
        messagebox.showerror("Error", "There was a problem while downloading. Make sure your directory path is correct.")

     if len(bookDownloads) == 0:
        downloading.configure(text="")
    
     
            
           

 
  

        
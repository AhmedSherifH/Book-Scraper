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
    
    if selectedHost == "mangakomi.io":  
        images = imageRequest.html.xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[3]/div[1]/a/img')
        img_tag = images[0]  # Access the first element of the list
        coverImage = img_tag.attrs['data-src']
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
        
        if selectedHost == "mangakomi.io":
            links = url.html.find('.post-title a')

            # Extract href attributes and titles
            for link in links:
                titleHref = link.attrs['href']
                titleName = link.text
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
    
    if selectedHost == "mangakomi.io":
  
      chapters = url.html.find('li.wp-manga-chapter')
      for chapter in chapters:
        href = chapter.find('a', first=True).attrs['href']
        title = chapter.find('a', first=True).text
        bookChapters[title] = href
        
      return bookChapters


        
    
   

          
def scrapePages(chapterLink, session, selectedHost, bookName, downloads, isMassDownload, directory, downloading):
     
     pageNum = 0 
     if isMassDownload == False:
        chosenDir = filedialog.askdirectory()
     else:
        chosenDir = directory
     try:
        if chosenDir != '':
            print(chapterLink)
            print(f'SELECTED HOST {selectedHost}')
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

            if selectedHost == "mangakakalot.com":
                print("SOOOOOOOOOOLO")
              #  imageRequest = session.get(chapterLink, headders=headers)
               # images = imageRequest.html.xpath('//div[@class="container-chapter-reader"]//img')
               # for image in images:
                #    print(image.get('src'))

            bookDownloads.remove(bookName)
            downloads.configure(text=", ".join(list(set(bookDownloads))))
     except:
        messagebox.showerror("Error", "There was a problem while downloading. Make sure your directory path is correct.")

     if len(bookDownloads) == 0:
        downloading.configure(text="")
    
     
            
           

 
  

        
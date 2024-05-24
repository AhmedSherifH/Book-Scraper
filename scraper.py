import requests
from tkinter import filedialog
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
    match selectedHost:
        case "readallcomics.com":
            images = imageRequest.html.xpath('/html/body/center[4]/center/center[1]/div/p/img')
            for image in images:
                coverImage = image.attrs['src']
        
        case "comixextra.com":
            images = imageRequest.html.xpath('/html/body/main/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/img')
            for image in images:
                coverImage = image.attrs['src']

        case "mangakomi.io":  
            images = imageRequest.html.xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[3]/div[1]/a/img')
            img_tag = images[0] 
            coverImage = img_tag.attrs['data-src']

        case "mangaread.org":
            images = imageRequest.html.xpath('/html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div[3]/div[1]/a/img')
            img_tag = images[0] 
            coverImage = img_tag.attrs['src']

        case "mangakatana.com":
            images = imageRequest.html.xpath('/html/body/div[3]/div/div/div[1]/div/div[1]/div/img')
            img_tag = images[0] 
            coverImage = img_tag.attrs['src']

        case "mangakakalot.tv":
            images = imageRequest.html.find('div.manga-info-pic', first=True)
            coverImage = "https://ww8.mangakakalot.tv/" + (images.find('img', first=True).attrs.get('src'))

    return coverImage
    
def scrapeInformation(bookLink, session, selectedHost):
    information = {}
    request = session.get(bookLink, headers=headers)
    genresList = []

    match selectedHost:
        case "readallcomics.com":
            information['Title'] = request.html.xpath('/html/body/center[4]/center/center[1]/div/h1/b')[0].text
            information['Author/Publisher'] = request.html.xpath('/html/body/center[4]/center/center[1]/div/div[1]/p/strong[2]')[0].text
            information['Genres'] = request.html.xpath('/html/body/center[4]/center/center[1]/div/div[1]/p/strong[1]')[0].text

        case "comixextra.com":
            information["Title"] = request.html.xpath('/html/body/main/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div[2]/h1/span')[0].text
            information["Author/Publisher"] = request.html.xpath('/html/body/main/div/div/div/div[1]/div[1]/div[1]/div[1]/div/div[2]/div/dl/dd[4]')[0].text
            genres = request.html.find('.movie-dd')[0]
            genreLinks = genres.find('a')
            for link in genreLinks:
                genre = link.text
                genresList.append(genre)
            information['Genres'] = "\n".join(genresList)

        case "mangakomi.io":
            information['Title'] = request.html.xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[2]/h1')[0].text
            authors = request.html.find('.author-content')
            if authors:
                for author in authors:
                        information['Author/Publisher'] = author.text
            else:
                information['Author/Publisher'] = "N/A"
            genreLinks = request.html.find('.genres-content')
            for link in genreLinks:
                genre = (link.text).replace(",", "\n")
                genresList.append(genre)
            information['Genres'] = "\n".join(genresList)

        case "mangaread.org":
            information['Title'] = request.html.xpath('/html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div[2]/h1')[0].text
            information['Author/Publisher'] = request.html.xpath('/html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div[3]/div[2]/div/div[1]/div[6]/div[2]/div/a')[0].text
            genreLinks = request.html.find('.genres-content')
            for genreLink in genreLinks:
                genre = (genreLink.text).replace(',', "\n")
                genresList.append(genre)
            information['Genres'] = "\n".join(genresList)

        case "mangakatana.com":
            information['Title'] = request.html.xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/div/h1')[0].text
            information['Author/Publisher'] = request.html.xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/div/ul/li[2]/div[2]/a')[0].text
            genreLinks = request.html.find('div.genres a.text_0')
            if genreLinks:
                for genre in genreLinks:
                    genreName = genre.text
                    genresList.append(f"{genreName}")
            information['Genres'] = "\n".join(genresList)

        case "mangakakalot.tv":
            information['Title'] = request.html.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/ul/li[1]/h1')[0].text
            information['Author/Publisher'] = request.html.xpath('/html/body/div[1]/div[2]/div[1]/div[3]/ul/li[2]/a')[0].text
            genres = request.html.find('li', containing='Genres :')[0].find('a[rel="nofollow"]')
            for genre in genres:
                genreName = genre.text
                genresList.append(f"{genreName}")
            information['Genres'] = "\n".join(genresList)

    return information

def scrapeTitles(url, selectedHost, requestedBook): 
    requestedBook = requestedBook.replace(" ", "-")
    bookTitles = {}
   # Retrieve all book titles that contain the same words as those entered by the user
    match selectedHost:
        case "readallcomics.com":
            parsedTitles = url.html.xpath("/html/body/section/div/div/div/ul/li/a") #
            for child in parsedTitles:
             titleHref = child.attrs['href']
             titleName = child.text
             print(titleName)
             bookTitles[titleName] = titleHref      

        case "comixextra.com":
            parsedTitles = url.html.find('div.cartoon-box a')
            for title in parsedTitles:
                if "https://comixextra.com/comic/" in title.attrs['href'] and title.text:
                    titleHref = title.attrs['href']
                    titleName = title.text
                    print(titleName)
                    bookTitles[titleName] = titleHref

        case "mangakomi.io":
            links = url.html.find('.post-title a')
            for link in links:
                titleHref = link.attrs['href']
                titleName = link.text
                bookTitles[titleName] = titleHref

        case "mangaread.org":
            h3Elements = url.html.find('h3.h4 a')
            for h3 in h3Elements:
                titleHref = h3.attrs['href']
                titleName = h3.text
                bookTitles[titleName] = titleHref
        
        case "mangakatana.com":
            requestedBookList = url.html.xpath('//*[@id="book_list"]//div[@class="item"]')
            for item in requestedBookList:
                titleClass = item.find('h3.title', first=True)
                if titleClass:
                    titleHref = titleClass.find('a', first=True).attrs['href']
                    titleName = titleClass.find('a', first=True).text
                    bookTitles[titleName] = titleHref
        
        case "mangakakalot.tv":
            requestedBookList = url.html.find('.story_item')
            for book in requestedBookList:
                aTag = book.find('a', first=True)
                imgTag = aTag.find('img', first=True)
                if imgTag:
                    titleName = imgTag.attrs.get('alt', '')
                    titleHref = "https://ww8.mangakakalot.tv/" + aTag.attrs.get('href', '')
                    bookTitles[titleName] = titleHref

    return bookTitles

def scrapeChapters(url, selectedHost):    
    bookChapters = {}
  # Get all chapters within a book
    match selectedHost: 
        case "readallcomics.com":
            parsedChapters = url.html.xpath("//ul[@class='list-story']/li/a")
            for chapter in parsedChapters:
                chapterName = chapter.text
                chapterHref = chapter.attrs['href']
                bookChapters[chapterName] = chapterHref

        case "comixextra.com":
            issues = url.html.find('#list a')
            for issue in issues:
                chapterHref = issue.attrs['href']
                chapterName = issue.text
                bookChapters[chapterName] = chapterHref + "/full"
        
        case "mangakomi.io":
            chapters = url.html.find('li.wp-manga-chapter')
            for chapter in chapters:
                chapterHref = chapter.find('a', first=True).attrs['href']
                chapterName = chapter.find('a', first=True).text
                bookChapters[chapterName] = chapterHref 

        case "mangaread.org":
            chapters = url.html.find('.wp-manga-chapter')
            for chapter in chapters:
                chapterName = chapter.find('a', first=True).text
                chapterHref = chapter.find('a', first=True).attrs['href']
                bookChapters[chapterName] = chapterHref
        
        case "mangakatana.com":
            chapters = url.html.find('div.chapter')
            for chapter in chapters:
                chapterName = chapter.find('a', first=True).text
                chapterHref = chapter.find('a', first=True).attrs['href']
                bookChapters[chapterName] = chapterHref

        case "mangakakalot.tv":
            chapters= url.html.find('div.row')
            for chapter in chapters:
                aTag = chapter.find('a', first=True)
                if aTag:
                    chapterHref = aTag.attrs.get('href')
                    chapterName = aTag.attrs.get('title')
                    bookChapters[chapterName] = "https://ww8.mangakakalot.tv/" + chapterHref

    return bookChapters

def scrapePages(chapterLink, session, selectedHost, bookName, isMassDownload, directory, format, numberofLoops, loopVerification, zipCompression):
     pageNum = 0 
     imageContents = []
     global compressedChapters
     chapterRequest = session.get(chapterLink, headers=headers)
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

            match selectedHost:
                case "readallcomics.com":                       
                    images = chapterRequest.html.xpath('.//img')                     
                    for pageNum, image in enumerate(images, 1):
                            if pageNum == 1:
                                continue
                            src = image.attrs['src']
                            pageResponse = requests.get(src)
                            print(f"{chosenDir}/#{pageNum}.jpg")
                            imageContents.append(pageResponse.content)

                case "comixextra.com":
                    images = chapterRequest.html.find('div.chapter-container img')
                    for image in images:
                        pageNum += 1
                        src = image.attrs['src']
                        print(f"{chosenDir}/#{pageNum}.jpg")
                        pageResponse = requests.get(src) 
                        imageContents.append(pageResponse.content)

                case "mangakomi.io":
                    images = chapterRequest.html.xpath('//img')  
                    for image in images:
                            if 'data-src' in image.attrs:
                                src = image.attrs.get('data-src')
                                src = src.strip()
                                if 'cdn' in src:
                                    pageNum += 1 
                                    print(f"#{pageNum}: {src}")            
                                    pageResponse = requests.get(src) 
                                    imageContents.append(pageResponse.content)

                case "mangaread.org":
                    images = chapterRequest.html.find('.page-break.no-gaps')
                    for div in images:
                        pageNum += 1
                        image = div.find('img', first=True)
                        src = image.attrs['src']
                        print(f"#{pageNum}: {src}")            
                        pageResponse = requests.get(src) 
                        imageContents.append(pageResponse.content)
                
                case "mangakatana.com":
                    thzqScript = chapterRequest.html.find('script', containing='var thzq=')[0].text
                    thzqStart = thzqScript.find('var thzq=')
                    thzqEnd = thzqScript.find('];function kxat', thzqStart) + 1
                    thzqArray = thzqScript[thzqStart:thzqEnd]
                    pageLinks = thzqArray.replace('var thzq=', '').split(',')
                    for pageLink in pageLinks:
                        pageLink = pageLink.replace("[", "",).replace(",", "").replace("'", "").replace("]", "")
                        print(pageLink)
                        if pageLink:
                            pageResponse = requests.get(pageLink) 
                            imageContents.append(pageResponse.content)
                    
                case "mangakakalot.tv":
                    pages = chapterRequest.html.find('div.vung-doc img')
                    for div in pages:
                        pageNum += 1
                        if div.attrs.get('data-src'):
                            page = div.attrs.get('data-src')
                            print(f"#{pageNum}: {page}")          
                            pageResponse = requests.get(page) 
                            imageContents.append(pageResponse.content)  
                
            match format: 
                case ".cbz":
                    for page in imageContents:
                        compressedChapters.append(page)

                    if loopVerification == numberofLoops:
                        createCbz(compressedChapters, f"{chosenDir}/{bookName}.cbz")
                        if len(compressedChapters) > 0:
                            compressedChapters = []
    
                case ".zip":
                    for page in imageContents:
                        compressedChapters.append(page)
                    if loopVerification == numberofLoops:
                        createZip(compressedChapters, f"{chosenDir}/{bookName}.zip", zipCompression)
                        if len(compressedChapters) > 0:
                            compressedChapters = []
                    
                case ".pdf":
                    for page in imageContents:
                        compressedChapters.append(page)
                    if loopVerification == numberofLoops:
                        createPdf(compressedChapters, f"{chosenDir}/{bookName}.pdf")
                        if len(compressedChapters) > 0:
                            compressedChapters = []

                case ".jpg":
                    createJpg(imageContents, chosenDir)

                case "Read":
                    bookDownloads.remove(bookName)
                    return imageContents
        
            bookDownloads.remove(bookName)
     except:
        messagebox.showerror("Error", "There was a problem while downloading. Make sure your directory path is correct.")


def getDownloads():
    downloads = ", ".join(list(set(bookDownloads)))
    if downloads == "":
        messagebox.showinfo(title="Downloads", message=f"Nothing is being downloaded!")
    else:
        messagebox.showinfo(title="Downloads", message=f"You're currently downloading: {downloads}")
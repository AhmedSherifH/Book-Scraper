from reader import *
import customtkinter
from functools import *
from requests_html import HTMLSession
from scraper import *
import threading
from PIL import Image
from io import BytesIO
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path
import signal
import os
import json

# The main window
root = customtkinter.CTk()
root.protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), signal.SIGTERM))
root.geometry("800x400")
root.resizable(False, False)
root.iconbitmap("visual/bookscraper-icon.ico")
root.title("Book Scraper")


# The images for the buttons
downloadButtonIcon = customtkinter.CTkImage(light_image=Image.open("./resources/download.png"),
                                            dark_image=Image.open("./resources/download.png"))
historyLabelIcon = customtkinter.CTkImage(light_image=Image.open("./resources/history.png"),
                                          dark_image=Image.open("./resources/history.png"))
bookmarkIcon = customtkinter.CTkImage(light_image=Image.open("./resources/bookmark.png"),
                                      dark_image=Image.open("./resources/bookmark.png"))
loadingIcon = customtkinter.CTkImage(light_image=Image.open("./resources/loading.png"),
                                      dark_image=Image.open("./resources/loading.png"))
infoIcon = customtkinter.CTkImage(light_image=Image.open("./resources/info.png"),
                                      dark_image=Image.open("./resources/info.png"))

# Global variables
selectedHost = ""
selectedFormat = ""
oddChars = [" ", ":", "/","?", "(", ")"]
hostBase = ""
bookmarkedBooks = []
hostValues = ["Select a Host", "readallcomics.com", "comicextra.me" , "mangakomi.io", "mangaread.org"] 
formatValues = ["Select a Format", "Read", ".jpg", ".cbz", ".zip", ".pdf"]
bookChapterNames = {}
globalBookName = ''
# The user agent is needed for some websites
headers = {'User-Agent': 'Mozilla/5.0'}
session = HTMLSession()
# The path to the history and bookmarks json files
historyJsonPath = Path('./cache/history/history.json')
bookmarksJsonPath = Path('./cache/bookmark/bookmarks.json')
# Check if the cache folders exist, if not, create them
os.makedirs('./cache/history', exist_ok=True)
os.makedirs('./cache/bookmark', exist_ok=True)


def selectHost(choice):
      global selectedHost
      global hostBase
      selectedHost = choice
      
      # Remove "Select a Host" after selecting a website, and assign hostBase to the correct value
      if choice != "Select a Host":
       if "Select a Host" in hostValues:
            hostValues.remove("Select a Host")
      
       hostSelector.configure(values=hostValues)
       match choice:
            case "readallcomics.com":
                  hostBase = "https://readallcomics.com/?story="
            case "comicextra.me":
                  hostBase = "https://comicextra.me/search?keyword={}"
            case "mangakomi.io":
                  hostBase = "https://mangakomi.io/?s={}&post_type=wp-manga"
            case "mangaread.org":
                  hostBase = "https://www.mangaread.org/?s={}&post_type=wp-manga"
      
def selectFormat(choice):
      global selectedFormat
      # Remove "Select a Format" after selecting a format, and assign selectedFormat to the correct value
      if choice != "Select a Format":
            if "Select a Format" in formatValues:
                  formatValues.remove("Select a Format")
            selectedFormat = choice
            formatSelector.configure(values=formatValues)
            # Only show the compression method menu if the selected format is .zip
            if selectedFormat == ".zip":
                  compressionMethodMenu.place(x=480, y=368)
            else:
                  compressionMethodMenu.place_forget()
       
 
def getPages(chapterLink, session, selectedHost, bookName, isMassDownload, directory, numberofLoops, cbzVerification): 
      zipCompressionMethod = compressionMethodMenu.get()
      if selectedFormat not in ["Read", ".jpg", ".cbz", ".zip", ".pdf"]:
            messagebox.showerror("Error", "Please select the format you'd like to download the pages in.")
      
      elif selectedFormat in ["Read"]:
            # !READING ONLY! isMassDownload is set to True to bypass asking for the directory
            isMassDownload = True
            # Directory variable is set to "directory" to avoid throwing an error
            directory = "directory" 
            imageContent = scrapePages(chapterLink, session, selectedHost, bookName, isMassDownload, directory, selectedFormat, numberofLoops, cbzVerification, zipCompressionMethod)
            createReaderWindow(imageContent)

      elif selectedFormat in [".jpg", ".cbz", ".zip", ".pdf"]:
            scrapePages(chapterLink, session, selectedHost, bookName, isMassDownload, directory, selectedFormat, numberofLoops, cbzVerification, zipCompressionMethod)


def getAllChapters():
      global bookChapterNames
      global globalBookName   

      isMassDownload = True      
      # Prevent the program from asking for directory if the selected format is "Read"
      if selectedFormat not in ["Read"]:
            baseDirectory = filedialog.askdirectory()
      else:
            messagebox.showerror("Error", "This button cannot be used for the selected format.")
      directory = ''
      folderNum = 0
      compressedVerification = 0

      # This option is mainly for .png and .jpg. The number of folders made equals the number of chapters inside a book.
      # The folder name is decided by the number of the chapter
      if selectedFormat in [".jpg"]:
            numberofLoops = 0
            compressedVerification = 0
            for Chapter in bookChapterNames:
                  folderNum = folderNum + 1
                  directory = f"{baseDirectory}/#{folderNum}"
                  Path(directory).mkdir(parents=True, exist_ok=True)

            for bookChapter in bookChapterNames:
                  directory = f"{baseDirectory}/#{folderNum}"
                  threading.Thread(target=getPages, args=(bookChapterNames[bookChapter], session, selectedHost, globalBookName, isMassDownload, directory, numberofLoops, compressedVerification)).start()
                  folderNum = folderNum - 1

      # A .cbz file is only made after compressedVerification = numberofLoops, where numberofLoops equals the number of chapters found in a book
      elif selectedFormat in [".zip", ".cbz", ".pdf"]:
            numberofLoops = len(bookChapterNames)
            for bookChapter in bookChapterNames:
                  compressedVerification = compressedVerification + 1 
                  getPages(bookChapterNames[bookChapter], session, selectedHost, globalBookName, isMassDownload, baseDirectory, numberofLoops, compressedVerification)
      
      if selectedFormat not in ["Read", ".jpg", ".cbz", ".zip", ".pdf"]:
            messagebox.showerror("Error", "Please select the format you'd like to download the pages in.")
                  
                  
def displayChapters(href, bookName, isHistory):
      global bookChapterNames
      global globalBookName
      
      coverLink = href 
      isMassDownload = False
      directory = ''
      bookIndividualRequest = session.get(href, headers=headers)
      numberofLoops = 0
      cbzVerification = 0
      bookChapterNames = {}
      globalBookName = bookName

      print(f"Displaying Chapters --> {href}, {bookName}")

      # Call scrapeChapters function from scraper.py to get all chapters in a book
      # After the function is finished, it will create a button for each chapter
      bookChapterNames = scrapeChapters(bookIndividualRequest, selectedHost)
      for chapterName in bookChapterNames:
            chapterButton = customtkinter.CTkButton(bookChapters, width=500, height=30, text=chapterName,
                                                      fg_color="#581845", command = lambda title=bookChapterNames[chapterName], bookName=bookName: 
                                                      threading.Thread(target=getPages, args=(title, session, selectedHost, 
                                                      bookName, isMassDownload, directory, numberofLoops, cbzVerification)).start())
            chapterButton.pack()


      # Get Cover Display, If it throws an error: Ignore cover completely     
      try:   
            coverLink = scrapeCover(coverLink, session, selectedHost)
            coverResponse = requests.get(coverLink)
            cover = Image.open(BytesIO(coverResponse.content))
            coverImage = customtkinter.CTkImage(light_image=cover, dark_image=cover,size=(166, 256))
            coverImageLabel.configure(image=coverImage)
      except:
            messagebox.showerror("Error", "Couldn't load cover image.")

      # Change the function and text of the bookmark button depending on whether the book is bookmarked or not
      if href not in bookmarkedBooks:
            bookmarkButton.configure(text="Bookmark", command=lambda cover=cover, href=href, bookName=bookName: saveBookmark(cover, href, bookName))
      else: 
            bookmarkButton.configure(text="Bookmarked" , command=lambda cover=cover, href=href, bookName=bookName: removeBookmark(href, bookName))

      # If the book was accessed via history, don't save it to history again; display the return to history button 
      if not isHistory:
            returnToList.place(x=700, y=5)
            os.makedirs(f'./cache/history/{selectedHost}', exist_ok=True)
            cover.save(f"./cache/history/{selectedHost}/{bookName}.png")
            saveBookToHistory(href, bookName)
      else:
            returnToHistory.place(x=700, y=5)

      # Manage Placement of Widgets
      loadingFrame.place_forget()
      displayInformationButton.place(x=609, y=301)
      downloadallChapters.place(x=608, y=336)
      formatSelector.place(x=624, y=368)
      bookmarkButton.place(x=5, y=365)
      searchButton.place_forget()
      bookList.place_forget()
      historyList.place_forget()
      historyFrame.place_forget()
      bookmarkList.place_forget()
      bookmarkFrame.place_forget()
      coverImageLabel.place(x=610, y=40)
      bookChapters.place(x=0, y=35) 


def searchProcess():
    historyList.place_forget()
    historyFrame.place_forget()
    bookmarkList.place_forget()
    bookmarkFrame.place_forget()
    bookTitles = {}
    searchBookURL = ""

    try:
      # Set searchBookURL according to the selected host, and get the text entered in the search bar
      if selectedHost == "readallcomics.com":
            requestedBook = searchBar.get("0.0", "end").replace(' ', "-").replace('\n', "")
            searchBookURL = hostBase + requestedBook + "&s=&type=comic"
            searchBookURL = searchBookURL.replace("\n", "").replace(" ", "")  
      if selectedHost in ["mangakomi.io", "mangaread.org", "comicextra.me"]:
            requestedBook = searchBar.get("0.0", "end").replace(' ', "+").replace('\n', "")
            searchBookURL = hostBase.format(requestedBook)

      searchBookRequest = session.get(searchBookURL,
                                          headers={'User-Agent': 'Mozilla/5.0'})
      
      
      # Get all titles that include the same keywords as the ones entered by the user
      bookTitles = scrapeTitles(searchBookRequest, selectedHost, requestedBook)
      for title in bookTitles:
            bookButton = customtkinter.CTkButton(bookList, width=780, height=30, text=title, 
                                                      fg_color="#581845", command=lambda href=bookTitles[title], bookName = title, isHistory=False: 
                                                      (bookList.place_forget(), 
                                                       displayChaptersCheck(href, bookName, isHistory)))
            bookButton.pack()

      bookList.place(x=0, y=35)
      searchButton.place(x=700, y=5)
    except: 
       messagebox.showerror("Error", "Please select a host from the dropdown menu.")


# Create History widgets
historyList = customtkinter.CTkScrollableFrame(root, width=200, height=340, 
                                               fg_color="#242424")
historyFrame = customtkinter.CTkFrame(root)
historyImage = customtkinter.CTkLabel(historyFrame, image=historyLabelIcon, text="", fg_color="#242424")
historyImage.grid(row=0, column=0)
labelFont = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=14)
historyText = customtkinter.CTkLabel(historyFrame, 
                                     text="History:",
                                     font=labelFont,
                                     anchor="center",
                                     fg_color="#242424")
historyText.grid(row=0, column=4)
returnToHistory = customtkinter.CTkButton(root, width=70, height=30, 
                                          fg_color="#581845", text="Back",
                                          command=lambda: (returnToHistory.place_forget(),
                                                           bookChapters.place_forget(), 
                                                           bookmarkButton.place_forget(),
                                                           coverImageLabel.place_forget(),
                                                           downloadallChapters.place_forget(),
                                                           formatSelector.place_forget(), 
                                                           compressionMethodMenu.place_forget(),
                                                           displayInformationButton.place_forget(),
                                                           searchButton.place(x=700, y=5),
                                                           historyFrame.place(x=60, y=45),
                                                           historyList.place(x=130, y=40),
                                                           displayBookmarks(),
                                                           searchButton.place(x=700, y=5),
                                                           showDownloads.place(x=700, y=360)
                                                           ))

def displayHistory():
    historyList.place(x=130, y=40) 
    historyFrame.place(x=60,y=45) 
    
    # Check if the history file exists, if not, create it
    if not historyJsonPath.exists():
        historyJsonPath.touch()
        base = {"books": []}
        with open(historyJsonPath, 'w') as jsonFile:
            json.dump(base, jsonFile, indent=4)  

    # Load the history JSON file assign the JSON keys to their corresponding variables
    # We're reversing the list to display the most recent history first
    with open(historyJsonPath, "r") as jsonFile:
            data = json.load(jsonFile)
    if data['books']:        
      for book in reversed(data['books']):
            bookLink = book.get('bookLink')  
            bookName = book.get('bookName')  
            historyHost = book.get('selectedHost')
            if bookLink and bookName:
                  # Don't display the book if its cover image doesn't exist
                  if os.path.exists(f"./cache/history/{historyHost}/{bookName}.png"):
                        coverImage = Image.open(f"./cache/history/{historyHost}/{bookName}.png")
                        bookNameButton = customtkinter.CTkButton(historyList, 
                                                                  image=customtkinter.CTkImage(light_image=coverImage
                                                                                               ,dark_image=coverImage,size=(166, 256)),
                                                                  text=f"{historyHost}",
                                                                  compound="top",
                                                                  font=labelFont,
                                                                  fg_color="#581845", 
                                                                  command=lambda href=bookLink, name=bookName, isHistory=True, historyHost=historyHost:                                                          
                                                                  (selectHost(historyHost), historyList.place_forget(), historyFrame.place_forget(),
                                                                   bookmarkList.place_forget(), bookmarkFrame.place_forget(),
                                                                   displayChaptersCheck(href, name, isHistory)))
                        bookNameButton.pack()
    if len(data['books']) == 0:
            # Display a button if the history is empty (Keys inside JSON = 0)
            emptyJsonButton = customtkinter.CTkButton(historyList, 
                                                      width=170, 
                                                      height=30, 
                                                      text="History is empty!", 
                                                      fg_color="#581845")
            emptyJsonButton.pack()
                                                      
                                                  
def saveBookToHistory(bookLink, bookName):
      print("Saving")
      with open("./cache/history/history.json", "r") as jsonFile:
            data = json.load(jsonFile)

      newBook = { "bookLink": bookLink, "bookName": bookName, "selectedHost": selectedHost}
      
      if len(data["books"]) >= 10:
        # Limit the number of history books to 10
        bookNameToRemove = data["books"][0].get('bookName')
        bookHostToRemove = data["books"][0].get('selectedHost')
        os.remove(f"./cache/history/{bookHostToRemove}/{bookNameToRemove}.png")
        data["books"].pop(0)  


      for book in data["books"]:
            # Check if the book already exists in the history, if so, don't add it
            if book == newBook:
                  return

      data["books"].append(newBook)
      with open("./cache/history/history.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4) 
displayHistory()

# Create Bookmark widgets
bookmarkList = customtkinter.CTkScrollableFrame(root, width=200, height=340, 
                                               fg_color="#242424")                                 
bookmarkFrame = customtkinter.CTkFrame(root)
bookmarkImage = customtkinter.CTkLabel(bookmarkFrame, image=bookmarkIcon, 
                                       text="", fg_color="#242424")
bookmarkImage.grid(row=0, column=0)
bookmarkText = customtkinter.CTkLabel(bookmarkFrame, 
                                     text="Bookmarks:",
                                     font=labelFont,
                                     anchor="center",
                                     fg_color="#242424")
bookmarkText.grid(row=0, column=4)

def displayBookmarks():
    for widget in bookmarkList.winfo_children():
        # Destroy the children of the bookmarkList widget
        # Once they're destroyed, they'll be readded again after loading the data from the JSON file
        # This is done to update bookmarkList after a book has been added or removed
        widget.destroy()

    bookmarkList.place(x=470, y=40) 
    bookmarkFrame.place(x=370,y=45) 

    if not bookmarksJsonPath.exists():
        # Create a new JSON file if it doesn't exist
        bookmarksJsonPath.touch()
        base = {"books": []}
        with open(bookmarksJsonPath, 'w') as jsonFile:
            json.dump(base, jsonFile, indent=4)  

    with open(bookmarksJsonPath, "r") as jsonFile:
            data = json.load(jsonFile)

    if data['books']:        
      for book in reversed(data['books']):
            # Reversed so the most recent book is at the top
            bookLink = book.get('bookLink')  
            bookName = book.get('bookName')  
            historyHost = book.get('selectedHost')
                  
            bookmarkedBooks.append(bookLink)
            
            if bookLink and bookName:
                  # If the cover image does not exist, the book is not going to be added to bookmarkList
                  if os.path.exists(f"./cache/bookmark/{historyHost}/{bookName}.png"):
                        coverImage = Image.open(f"./cache/bookmark/{historyHost}/{bookName}.png")
                        bookNameButton = customtkinter.CTkButton(bookmarkList, 

                                                                  image=customtkinter.CTkImage(light_image=coverImage
                                                                                               ,dark_image=coverImage,size=(166, 256)),
                                                                  text=f"{historyHost}",
                                                                  compound="top",
                                                                  font=labelFont,
                                                                  fg_color="#581845", 
                                                                  command=lambda href=bookLink, name=bookName, isHistory=True, historyHost=historyHost:                                                          
                                                                  (selectHost(historyHost), bookmarkFrame.place_forget(), bookmarkList.place_forget(),
                                                                   historyFrame.place_forget(), historyList.place_forget(),
                                                                   displayChaptersCheck(href, name, isHistory)))
                        bookNameButton.pack()
    if len(data['books']) == 0:
            # If there are no bookmarks, display a button telling the user
            emptyJsonButton = customtkinter.CTkButton(bookmarkList, 
                                                      width=170, 
                                                      height=30, 
                                                      text="No bookmarks!", 
                                                      fg_color="#581845")
            emptyJsonButton.pack()


def saveBookmark(cover, link, name):
      with open("./cache/bookmark/bookmarks.json", "r") as jsonFile:
         data = json.load(jsonFile)

      # Check if the directory exists, if not, create it and save the cover image inside of it
      os.makedirs(f'./cache/bookmark/{selectedHost}', exist_ok=True)
      cover.save(f"./cache/bookmark/{selectedHost}/{name}.png")

      newBook = { "bookLink": link, "bookName": name, "selectedHost": selectedHost}
      if len(data["books"]) >= 10:
        # The limit of bookmarkList is 10 books, if the list is full, remove the oldest book
        bookNameToRemove = data["books"][0].get('bookName')
        bookHostToRemove = data["books"][0].get('selectedHost')
        os.remove(f"./cache/bookmark/{bookHostToRemove}/{bookNameToRemove}.png")
        data["books"].pop(0)  

      for book in data["books"]:
            # if the book already exists, don't add it
            if book == newBook:
                  return

      data["books"].append(newBook)
      with open("./cache/bookmark/bookmarks.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4) 

def removeBookmark(link, name):
      selectedHost = ""
      bookmarkedBooks.remove(link)

      with open(bookmarksJsonPath, "r") as jsonFile:
            data = json.load(jsonFile)

      for book in data["books"]:
            if book["bookLink"] == link:
                  # The bookLink contains both the host and the name of the book so we're using it to check for duplicates
                  # eg. https://mangakomi.io/manga/chainsaw-man 
                  selectedHost = book["selectedHost"]
                  data["books"].remove(book)
                  break
            
      os.remove(f"./cache/bookmark/{selectedHost}/{name}.png")
      with open(bookmarksJsonPath, "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)      
displayBookmarks()


def searchProcessCheck():
      if selectedHost not in ["readallcomics.com", "comicextra.me" , "mangakomi.io", "mangaread.org"]:
            messagebox.showerror("Error", "Please select a host from the dropdown menu.")
      else: 
            searchButton.place_forget()
            bookList.place_forget()
            for widget in bookList.winfo_children():
                  if isinstance(widget, customtkinter.CTkButton):
                        widget.destroy()
            threading.Thread(target=searchProcess).start()
            

def displayChaptersCheck(href, bookName, isHistory):
      showDownloads.place_forget()
      searchButton.place_forget()
      returnToHistory.place_forget()
      loadingFrame.place(x=350, y=170)
      for widget in bookChapters.winfo_children():
            widget.destroy()
      threading.Thread(target=displayChapters, args=(href, bookName, isHistory)).start()


searchButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Search", command=searchProcessCheck)
searchButton.place(x=700, y=5)

showDownloads = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Downloads", command=getDownloads)
showDownloads.place(x=700, y=360)
 
downloadallChapters = customtkinter.CTkButton(master=root, image=downloadButtonIcon, text="Download All Chapters", width=170, fg_color="#581845", command=lambda: threading.Thread(target=getAllChapters).start())

coverImageLabel = customtkinter.CTkLabel(root, text="", image=None)


returnToList = customtkinter.CTkButton(master=root, width=70, height=30, 
                                       fg_color="#581845", text="Back",
                                       command=lambda: (bookList.place(x=0, y=35), returnToList.place_forget(),
                                                        showDownloads.place(x=700, y=360),
                                                        bookChapters.place_forget(), searchButton.place(x=700, y=5), 
                                                        coverImageLabel.place_forget(),
                                                        downloadallChapters.place_forget(),
                                                        formatSelector.place_forget(), 
                                                        displayInformationButton.place_forget(),
                                                        bookmarkButton.place_forget(),
                                                        compressionMethodMenu.place_forget()))

hostSelector = customtkinter.CTkOptionMenu(root, values=hostValues, fg_color="#581845", button_color="#581845", command=selectHost)
hostSelector.place(x=20, y=5)
                                   
formatSelector = customtkinter.CTkOptionMenu(root, values=formatValues, fg_color="#581845",
                                              button_color="#581845", command=selectFormat, anchor="center")
compressionMethodMenu = customtkinter.CTkOptionMenu(root, values=["Stored", "BZIP2", "LZMA", "Deflate"], button_color="#581845",
                                                    fg_color="#581845", anchor="center")
                                         
searchBar = customtkinter.CTkTextbox(master=root, width=500, height=30)
searchBar.place(x=180, y=5)
searchBar.bind('<Return>', lambda event: "break")
 

bookList = customtkinter.CTkScrollableFrame(root, width=770, height=300 , fg_color="#242424")
bookChapters = customtkinter.CTkScrollableFrame(root, width=570, height=320, fg_color="#242424")

bookmarkButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Bookmark", image=bookmarkIcon)
displayInformationButton = customtkinter.CTkButton(master=root, width=170, height=30, fg_color="#581845", text="Information", image=infoIcon)

loadingFont = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=25)
loadingFrame = customtkinter.CTkFrame(master=root)
loadingText = customtkinter.CTkLabel(loadingFrame, text="Loading...", font=loadingFont, fg_color="#242424")
loadingImage = customtkinter.CTkLabel(loadingFrame, text="", image=loadingIcon, fg_color="#242424")
loadingImage.grid(row=0, column=0)
loadingText.grid(row=0, column=4)
                                     

root.mainloop() 



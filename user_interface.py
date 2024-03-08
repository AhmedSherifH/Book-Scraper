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


root =  customtkinter.CTk()
root.protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), signal.SIGTERM))
root.geometry("800x400")
root.resizable(False, False)
root.iconbitmap("visual/bookscraper-icon.ico")
root.title("Book Scraper")





selectedHost = ""
selectedFormat = ""
oddChars = [" ", ":", "/","?", "(", ")"]
hostBase = ""
hostValues = ["Select a Host", "readallcomics.com", "comicextra.me" , "mangakomi.io", "mangaread.org"] 
formatValues = ["Select a Format", ".jpg", ".cbz", ".zip"]
bookChapterNames = {}
globalBookName = ''
headers = {'User-Agent': 'Mozilla/5.0'}
session = HTMLSession()
jsonPath = Path('./history.json')




def selectHost(choice):
      global selectedHost
      global hostBase
      selectedHost = choice
      
      # Remove "Select a Host" after selecting a website, and assign hostBase to the correct value
      if choice != "Select a Host":
       if "Select a Host" in hostValues:
            hostValues.remove("Select a Host")
      
       hostSelector.configure(values=hostValues)
       if choice == "readallcomics.com":
                  hostBase = "https://readallcomics.com/?story="
       if choice == "comicextra.me":
                  hostBase = "https://comicextra.me/search?keyword={}"
       if choice == "mangakomi.io":
                  hostBase = "https://mangakomi.io/?s={}&post_type=wp-manga"
       if choice == "mangaread.org":
                  hostBase = "https://www.mangaread.org/?s={}&post_type=wp-manga"
      
def selectFormat(choice):
      global selectedFormat
      
      # Remove "Select a Format" after selecting a format, and assign selectedFormat to the correct value
      if choice != "Select a Format":
            if "Select a Format" in formatValues:
                  formatValues.remove("Select a Format")
            selectedFormat = choice
            formatSelector.configure(values=formatValues)
            if selectedFormat == ".zip":
                  compressionMethodMenu.place(x=624, y=360)
            else:
                  compressionMethodMenu.place_forget()
       
 

def getPages(title, session, selectedHost, bookName, isMassDownload, directory, numberofLoops, cbzVerification): 
      # Get all pages inside a chapter
      if selectedFormat not in [".jpg", ".cbz", ".zip"]:
            messagebox.showerror("Error", "Please select the format you'd like to download the pages in.")
      else: 
            zipCompressionMethod = compressionMethodMenu.get()
            scrapePages(title, session, selectedHost, bookName, downloads, isMassDownload, directory, numberofDownloadsIndicator, selectedFormat, numberofLoops, cbzVerification, zipCompressionMethod)


def getAllChapters():
      global bookChapterNames
      global globalBookName   

      # Assign Variables
      isMassDownload = True
      baseDirectory = filedialog.askdirectory()
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
      elif selectedFormat in [".zip", ".cbz"]:
            numberofLoops = len(bookChapterNames)
            for bookChapter in bookChapterNames:
                  compressedVerification = compressedVerification + 1 
                  getPages(bookChapterNames[bookChapter], session, selectedHost, globalBookName, isMassDownload, baseDirectory, numberofLoops, compressedVerification)
      
      if selectedFormat not in [".jpg", ".cbz", ".zip"]:
            messagebox.showerror("Error", "Please select the format you'd like to download the pages in.")
                   
                  
def displayChapters(href, bookName, isHistory):
      global bookChapterNames
      global globalBookName

      if not isHistory:
            returnToList.place(x=700, y=5)
            saveBook(href, bookName)
      else:
            returnToHistory.place(x=700, y=5)
      
      print(f"Displaying Chapters --> {href}, {bookName}")
      # Empty Arrays and Frames
      bookChapterNames = {}
      globalBookName = bookName
      for widget in bookChapters.winfo_children():
          widget.destroy()


      # Assigns Variables
      coverLink = href 
      isMassDownload = False
      directory = ''
      bookIndividualRequest = session.get(href, headers=headers)
      numberofLoops = 0
      cbzVerification = 0
  

      # Get all Chapters in a book
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

      # Manage Placement of Widgets
      downloadallChapters.place(x=608, y=300)
      formatSelector.place(x=624, y=330)
      if selectedFormat == ".zip":
            compressionMethodMenu.place(x=624, y=360)
      searchButton.place_forget()
      bookList.place_forget()
      downloads.place_forget()
      historyDescription.place_forget()
      historyList.place_forget()
      historyText.place_forget()
      numberofDownloadsIndicator.place_forget()
      coverImageLabel.place(x=610, y=40)
      bookChapters.place(x=0, y=35) 


     
def searchProcess():
    # Empty Arrays and Assign Variables
    historyList.place_forget()
    historyDescription.place_forget()
    historyText.place_forget()
    bookList.place(x=0, y=35)  
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
      
      for widget in bookList.winfo_children():
            widget.destroy()
      
      # Get all books that were found in the search
      bookTitles = scrapeTitles(searchBookRequest, selectedHost, requestedBook)
      for title in bookTitles:
            bookButton = customtkinter.CTkButton(bookList, width=780, height=30, text=title, 
                                                      fg_color="#581845", command=lambda href=bookTitles[title], bookName = title, isHistory=False: 
                                                      (displayChapters(href, bookName, isHistory), downloads.place_forget(), numberofDownloadsIndicator.place_forget()))
            bookButton.pack()

    except: 
      messagebox.showerror("Error", "Please select a host from the dropdown menu.")



historyList = customtkinter.CTkScrollableFrame(root, width=570, height=320, fg_color="#242424")
historyText = customtkinter.CTkLabel(root, 
                                     text="History",
                                     font=('bold', 30),
                                     anchor="center")

historyDescription = customtkinter.CTkLabel(root,
                                            text="This page will display all books that you have recently visited.",
                                            font=('bold', 15),
                                            wraplength=250)
historyDescription.place(x=5, y=90)                                     
historyText.place(x=70,y=50)
historyList.place(x=200, y=35)  




def displayHistory():
    historyList.place(x=200, y=35)  
    
    # Check if the history file exists
    if not jsonPath.exists():
        jsonPath.touch()
        base = {"books": []}
        with open(jsonPath, 'w') as jsonFile:
            json.dump(base, jsonFile, indent=4)  
    else:
        with open(jsonPath, "r") as jsonFile:
            data = json.load(jsonFile)
        
        for book in reversed(data['books']):
            bookLink = book.get('bookLink')  
            bookName = book.get('bookName')  
            historyHost = book.get('selectedHost')
            
            if bookLink and bookName:
                bookNameButton = customtkinter.CTkButton(historyList, 
                                                         width=500, 
                                                         height=30, 
                                                         text=bookName, 
                                                         fg_color="#581845", 
                                                         command=lambda href=bookLink, name=bookName, isHistory=True, historyHost=historyHost:                                                          
                                                         (selectHost(historyHost), displayChapters(href, name, isHistory)))
                
            
                bookNameButton.pack()
            else:
                print("Error: Incomplete data for a book in history.")

def saveBook(bookLink, bookName):
      with open("history.json", "r") as jsonFile:
         data = json.load(jsonFile)

      newBook = { "bookLink": bookLink, "bookName": bookName, "selectedHost": selectedHost}
      data["books"].append(newBook)

      # Write the updated data back to the JSON file
      with open("history.json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)


displayHistory()
# Manage placement of widgets 
searchBar = customtkinter.CTkTextbox(master=root, width=500, height=30)
searchBar.place(x=180, y=5)
searchBar.bind('<Return>', lambda event: "break")
 

bookList = customtkinter.CTkScrollableFrame(root, width=770, height=300 , fg_color="#242424")
bookChapters = customtkinter.CTkScrollableFrame(root, width=570, height=320, fg_color="#242424")

searchButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Search", command=lambda: threading.Thread(target=searchProcess).start())
searchButton.place(x=700, y=5)


numberofDownloadsIndicator = customtkinter.CTkLabel(master=root, text="")
downloads = customtkinter.CTkLabel(master=root, text="")

      
downloadallChapters = customtkinter.CTkButton(master=root, text="Download All Chapters", width=170, fg_color="#581845", command=lambda: threading.Thread(target=getAllChapters).start())

coverImageLabel = customtkinter.CTkLabel(root, text="", image=None)


returnToList = customtkinter.CTkButton(master=root, width=70, height=30, 
                                       fg_color="#581845", text="Back",
                                       command=lambda: (bookList.place(x=0, y=35), returnToList.place_forget(),
                                                        bookChapters.place_forget(), searchButton.place(x=700, y=5), 
                                                        coverImageLabel.place_forget(),
                                                        downloadallChapters.place_forget(),
                                                        formatSelector.place_forget(), 
                                                        compressionMethodMenu.place_forget(),
                                                        downloads.place(x=83, y=350),
                                                        numberofDownloadsIndicator.place(x=0, y=350)
                                                        ))

returnToHistory = customtkinter.CTkButton(root, width=70, height=30, 
                                          fg_color="#581845", text="Back",
                                          command=lambda: (returnToHistory.place_forget(),
                                                           bookChapters.place_forget(), 
                                                           coverImageLabel.place_forget(),
                                                           downloadallChapters.place_forget(),
                                                           formatSelector.place_forget(), 
                                                           compressionMethodMenu.place_forget(),
                                                           searchButton.place(x=700, y=5),
                                                           downloads.place(x=83, y=350),                                                           
                                                           historyText.place(x=70, y=50),
                                                           historyDescription.place(x=5, y=90),
                                                           historyList.place(x=200, y=30)
                                                           ))

               

hostSelector = customtkinter.CTkOptionMenu(root, values=hostValues, fg_color="#581845", button_color="#581845", command=selectHost)
hostSelector.place(x=20, y=5)
                                   

formatSelector = customtkinter.CTkOptionMenu(root, values=formatValues, fg_color="#581845",
                                              button_color="#581845", command=selectFormat, anchor="center")
compressionMethodMenu = customtkinter.CTkOptionMenu(root, values=["Stored", "BZIP2", "LZMA", "Deflate"], button_color="#581845",
                                                    fg_color="#581845", anchor="center")
                                         



root.mainloop() 



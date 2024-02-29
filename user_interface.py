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


root =  customtkinter.CTk()
root.geometry("800x350")
root.resizable(False, False)
root.iconbitmap(None)
root.title("Book Scraper")

labelFont = customtkinter.CTkFont(family='Helvetica', size=12, weight='bold')

selectedHost = ""
selectedFormat = ""
oddChars = [" ", ":", "/","?", "(", ")"]
hostBase = ""
hostValues = ["Select a Host", "readallcomics.com", "mangakomi.io"] 
formatValues = ["Select a Format", ".jpg", ".cbz"]
bookChapterNames = {}
globalBookName = ''
session = HTMLSession()


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
       if choice == "mangakomi.io":
                  hostBase = "https://mangakomi.io/?s={}&post_type=wp-manga"
      
def selectFormat(choice):
      global selectedFormat
      
      # Remove "Select a Format" after selecting a format, and assign selectedFormat to the correct value
      if choice != "Select a Format":
            if "Select a Format" in formatValues:
                  formatValues.remove("Select a Format")
            selectedFormat = choice
            formatSelector.configure(values=formatValues)
       
 

def getPages(title, session, selectedHost, bookName, isMassDownload, directory, numberofLoops, cbzVerification): 
      # Get all pages inside a chapter
      print(bookName)
      scrapePages(title, session, selectedHost, bookName, downloads, isMassDownload, directory, numberofDownloadsIndicator, selectedFormat, numberofLoops, cbzVerification)


def getAllChapters():
      global bookChapterNames
      global globalBookName   

      # Assign Variables
      isMassDownload = True
      baseDirectory = filedialog.askdirectory()
      directory = ''
      folderNum = 0
      cbzVerification = 0

      # This option is mainly for .png and .jpg. The number of folders made equals the number of chapters inside a book.
      # The folder name is decided by the number of the chapter
      if selectedFormat != ".cbz":
            numberofLoops = 0
            cbzVerification = 0
            for Chapter in bookChapterNames:
                  folderNum = folderNum + 1
                  directory = f"{baseDirectory}/#{folderNum}"
                  Path(directory).mkdir(parents=True, exist_ok=True)

            for bookChapter in bookChapterNames:
                  directory = f"{baseDirectory}/#{folderNum}"
                  threading.Thread(target=getPages, args=(bookChapterNames[bookChapter], session, selectedHost, globalBookName, isMassDownload, directory, numberofLoops, cbzVerification)).start()
                  folderNum = folderNum - 1
      # A .cbz file is only made after cbzVerification = numberofLoops, where numberofLoops equals the number of chapters found in a book
      else:
            numberofLoops = len(bookChapterNames)
            for bookChapter in bookChapterNames:
                  cbzVerification = cbzVerification + 1 
                  getPages(bookChapterNames[bookChapter], session, selectedHost, globalBookName, isMassDownload, baseDirectory, numberofLoops, cbzVerification)
                   
                  
def displayChapters(href, bookName):
      global bookChapterNames
      global globalBookName


      # Empty Arrays and Frames
      bookChapterNames = {}
      globalBookName = bookName
      for widget in bookChapters.winfo_children():
          widget.destroy()


      # Assigns Variables
      headers = {'User-Agent': 'Mozilla/5.0'}
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
      formatSelector.place(x=455, y=300)
      searchButton.place_forget()
      bookList.place_forget()
      downloads.place_forget()
      numberofDownloadsIndicator.place_forget()
      coverImageLabel.place(x=610, y=40)
      returnToList.place(x=700, y=5)
      bookChapters.place(x=0, y=35) 


     
def searchProcess():
    # Empty Arrays and Assign Variables
    bookTitles = {}
    searchBookURL = ""
    searchBookRequest = session.get(searchBookURL,
                                    headers={'User-Agent': 'Mozilla/5.0'})
 
   # Set searchBookURL according to the selected host, and get the text entered in the search bar
    if selectedHost == "readallcomics.com":
          requestedBook = searchBar.get("0.0", "end").replace(' ', "-").replace('\n', "")
          searchBookURL = hostBase + requestedBook + "&s=&type=comic"
          searchBookURL = searchBookURL.replace("\n", "").replace(" ", "")  
    if selectedHost == "mangakomi.io":
          requestedBook = searchBar.get("0.0", "end").replace(' ', "+").replace('\n', "")
          searchBookURL = hostBase.format(requestedBook)
          print(searchBookURL)

    for widget in bookList.winfo_children():
           widget.destroy()
    
    # Get all books that were found in the search
    bookTitles = scrapeTitles(searchBookRequest, selectedHost, requestedBook)
    for title in bookTitles:
           bookButton = customtkinter.CTkButton(bookList, width=500, height=30, text=title, 
                                                 fg_color="#581845", command=lambda href=bookTitles[title], bookName = title: 
                                                 (displayChapters(href, bookName), downloads.place_forget(), numberofDownloadsIndicator.place_forget()))
           bookButton.pack()



# Manage placement of widgets 
searchBar = customtkinter.CTkTextbox(master=root, width=500, height=30)
searchBar.place(x=180, y=5)
searchBar.bind('<Return>', lambda event: "break")
 

bookList = customtkinter.CTkScrollableFrame(root, width=770, height=250, fg_color="#242424")
bookList.place(x=0, y=35)  
bookChapters = customtkinter.CTkScrollableFrame(root, width=570, height=250, fg_color="#242424")

searchButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Search", command=searchProcess)
searchButton.place(x=700, y=5)


numberofDownloadsIndicator = customtkinter.CTkLabel(master=root, text="", font=labelFont)
downloads = customtkinter.CTkLabel(master=root, text="", font=labelFont)

      
downloadallChapters = customtkinter.CTkButton(master=root, text="Download All Chapters", width=170, fg_color="#581845", command=lambda: threading.Thread(target=getAllChapters).start())

coverImageLabel = customtkinter.CTkLabel(root, text="", image=None, font=labelFont)


returnToList = customtkinter.CTkButton(master=root, width=70, height=30, 
                                       fg_color="#581845", text="Back",
                                       command=lambda: (bookList.place(x=0, y=35), returnToList.place_forget(),
                                                        bookChapters.place_forget(), searchButton.place(x=700, y=5), 
                                                        coverImageLabel.place_forget(),
                                                        downloadallChapters.place_forget(),
                                                        formatSelector.place_forget(), 
                                                        downloads.place(x=83, y=300),
                                                        numberofDownloadsIndicator.place(x=0, y=300)
                                                        ))
                                                        

hostSelector = customtkinter.CTkOptionMenu(root, values=hostValues, 
                                           fg_color="#581845", button_color="#581845", command=selectHost)
hostSelector.place(x=20, y=5)
                                   

formatSelector = customtkinter.CTkOptionMenu(root, values=formatValues, 
                                             fg_color="#581845", button_color="#581845", command=selectFormat)
                                         
root.mainloop() 



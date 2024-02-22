import customtkinter
from functools import *
from requests_html import HTMLSession
from scraper import *
import threading
from PIL import Image
from io import BytesIO
from tkinter import messagebox



root =  customtkinter.CTk()
root.geometry("800x350")
root.resizable(False, False)
root.iconbitmap(None)
root.title("Book Scraper")

selectedHost = ""
oddChars = [" ", ":", "/","?", "(", ")"]
comicBase = ""
optionMenuValues = ["Select a Host", "readallcomics.com"] 
comicIndividualLink = ""
session = HTMLSession()

                



def selectHost(choice):
      global selectedHost
      selectedHost = choice

      global comicBase

      if choice != "Select a Host":
       optionMenuValues.pop(0)
       optionMenu.configure(values=optionMenuValues)
       if choice == "readallcomics.com":
                  comicBase = "https://readallcomics.com/?story="

 

def getPages(title, session, selectedHost, issueNameDownload): 
      comicList.place_forget()
      searchButton.place_forget()
      
      print(issueNameDownload)
      scrapePages(title, session, selectedHost, issueNameDownload, downloads, numberofDownloadsIndicator)


      




def confirmDownload(href):
      # Empty Arrays and Frames
      comicIssueNames = {}
      for widget in comicIssues.winfo_children():
          widget.destroy()

      # Get Issues
      headers = {'User-Agent': 'Mozilla/5.0'}

      coverLink = href 
      comicIndividualRequest = session.get(href, headers=headers)

      comicIssueNames = scrapeIssues(comicIndividualRequest, selectedHost)
      for issueName in comicIssueNames:

            
            issueButton = customtkinter.CTkButton(comicIssues, width=500, height=30, text=issueName,
                                                      fg_color="#581845", command = lambda title=comicIssueNames[issueName], issueNameDownload=issueName: threading.Thread(target=getPages, args=(title, session, selectedHost, issueNameDownload)).start())
            issueButton.pack()


      # Get Cover Display, If it throws an error: Ignore cover completely  
      try:
            coverLink = scrapeCover(coverLink, session, selectedHost)
            coverResponse = requests.get(coverLink)
            cover = Image.open(BytesIO(coverResponse.content))
            coverImage = customtkinter.CTkImage(light_image=cover, dark_image=cover,size=(166, 256))
            coverImageLabel.configure(image=coverImage)
      except:
            messagebox.showerror("Error", "Couldn't load cover image.")



      # Manage Placement of Buttons
      searchButton.place_forget()
      comicList.place_forget()
      coverImageLabel.place(x=610, y=40)
      returnToList.place(x=700, y=5)
      comicIssues.place(x=0, y=35) 


     

def searchProcess():
    # Empty Arrays and Assign Variables
    comicTitles = {}
    searchComicURL = ""

    requestedComic = searchBar.get("0.0", "end")
    if selectedHost == "readallcomics.com":
      searchComicURL = comicBase + requestedComic + "&s=&type=comic"
      searchComicURL = searchComicURL.replace("\n", "").replace(" ", "")

    for widget in comicList.winfo_children():
           widget.destroy()
    
    # Get Comics
    searchComicRequest = session.get(searchComicURL,
                                       headers={'User-Agent': 'Mozilla/5.0'})
 
    
    comicTitles = scrapeTitles(searchComicRequest, selectedHost, requestedComic)
    
    for title in comicTitles:
           comicButton = customtkinter.CTkButton(comicList, width=500, height=30, text=title, 
                                                 fg_color="#581845", command=lambda title=comicTitles[title]: confirmDownload(title))
           comicButton.pack()


searchBar = customtkinter.CTkTextbox(master=root, width=500, height=30)
searchBar.place(x=180, y=5)
searchBar.bind('<Return>', lambda event: "break")
 

comicList = customtkinter.CTkScrollableFrame(root, width=770, height=250, fg_color="#242424")
comicList.place(x=0, y=35)  
comicIssues = customtkinter.CTkScrollableFrame(root, width=570, height=250, fg_color="#242424")

searchButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Search", command=searchProcess)
searchButton.place(x=700, y=5)


coverImageLabel = customtkinter.CTkLabel(root, text="", image=None)

numberofDownloadsIndicator = customtkinter.CTkLabel(master=root, text=f"Downloading: ")

downloads = customtkinter.CTkLabel(master=root, text="")


returnToList = customtkinter.CTkButton(master=root, width=70, height=30, 
                                       fg_color="#581845", text="Back",
                                       command=lambda: (comicList.place(x=0, y=35), returnToList.place_forget(),
                                                        comicIssues.place_forget(), searchButton.place(x=700, y=5), coverImageLabel.place_forget()))

optionMenu = customtkinter.CTkOptionMenu(root, values=optionMenuValues, 
                                         fg_color="#581845", button_color="#581845", command=selectHost)
optionMenu.place(x=20, y=5)
                                   


root.mainloop() 



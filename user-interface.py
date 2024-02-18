import customtkinter
from functools import *
from requests_html import HTMLSession
from scraper import *
import threading
from PIL import Image
from io import BytesIO

root =  customtkinter.CTk()
root.geometry("800x300")
root.resizable(False, False)

oddChars = [" ", ":", "/","?", "(", ")"]
comicBase = "https://readallcomics.com/?story="
session = HTMLSession()
                

def getPages(title, session, oddChars): 
      comicList.place_forget()
      returnToList.place_forget()
      searchButton.place_forget()
      
      scrapePages(title, session, oddChars)

def confirmDownload(button_name):
      # Empty Arrays and Frames
      comicIssueNames = []
      for widget in comicIssues.winfo_children():
          widget.destroy()

      # Get Issues
      comicIndividualLink = "https://readallcomics.com/category/"
      headers = {'User-Agent': 'Mozilla/5.0'}
      comicName = button_name 

      for char in oddChars:
            comicName = comicName.replace(char, "-")

      coverLink = comicIndividualLink + comicName

      comicIndividualRequest = session.get(comicIndividualLink + comicName, headers=headers)

      print(comicName)
      comicIssueNames = scrapeIssues(comicIndividualRequest) 
      for x in range(len(comicIssueNames)):
       issueButton = customtkinter.CTkButton(comicIssues, width=500, height=30, text=comicIssueNames[x],
                                              fg_color="#581845", command = lambda title=comicIssueNames[x]: threading.Thread(target=getPages, args=(title, session, oddChars)).start())
       issueButton.pack()


      # Get Cover Display    
      coverLink = scrapeCover(coverLink, session)
      coverResponse = requests.get(coverLink)
      cover = Image.open(BytesIO(coverResponse.content))
      coverImage = customtkinter.CTkImage(light_image=cover, dark_image=cover,size=(166, 256))
      coverImageLabel.configure(image=coverImage)


      # Manage Placement of Buttons
      searchButton.place_forget()
      comicList.place_forget()
      coverImageLabel.place(x=610, y=40)
      returnToList.place(x=700, y=5)
      comicIssues.place(x=0, y=35)  

   

def searchProcess():
    # Empty Arrays and Assign Variables
    comicTitles = []
    requestedComic = searchBar.get("0.0", "end")
    searchComicURL = comicBase + requestedComic + "&s=&type=comic"
    searchComicURL = searchComicURL.replace("\n", "").replace(" ", "")

    for widget in comicList.winfo_children():
           widget.destroy()
    
    # Get Comics
    searchComicRequest = session.get(searchComicURL,
                                       headers={'User-Agent': 'Mozilla/5.0'})
    comicTitles = scrapeTitles(searchComicRequest)
    
    for x in range(len(comicTitles)):
           comicButton = customtkinter.CTkButton(comicList, width=500, height=30, text=comicTitles[x], 
                                                 fg_color="#581845", command=lambda title=comicTitles[x]: confirmDownload(title))
           comicButton.pack()


searchBar = customtkinter.CTkTextbox(master=root, width=670, height=30)
searchBar.place(x=15, y=5)
searchBar.bind('<Return>', lambda event: "break")
 

comicList = customtkinter.CTkScrollableFrame(root, width=770, height=250, fg_color="#242424")
comicList.place(x=0, y=35)  
comicIssues = customtkinter.CTkScrollableFrame(root, width=570, height=250, fg_color="#242424")

searchButton = customtkinter.CTkButton(master=root, width=70, height=30, fg_color="#581845", text="Search", command=searchProcess)
searchButton.place(x=700, y=5)


coverImageLabel = customtkinter.CTkLabel(root, text="", image=None)


returnToList = customtkinter.CTkButton(master=root, width=70, height=30, 
                                       fg_color="#581845", text="Back",
                                       command=lambda: (comicList.place(x=0, y=35), returnToList.place_forget(),
                                                        comicIssues.place_forget(), searchButton.place(x=700, y=5), coverImageLabel.place_forget()))




root.mainloop() 



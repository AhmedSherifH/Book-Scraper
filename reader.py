from io import BytesIO
from tkinter import BOTTOM, LEFT, RIGHT
import customtkinter
from PIL import Image
from tkinter import filedialog


resamplingMethods = {"Nearest": Image.NEAREST,
                       "Bilinear": Image.BILINEAR,
                       "Bicubic": Image.BICUBIC,
                       "Lanczos": Image.LANCZOS,
                       "Hamming": Image.HAMMING}

fgColor = "#581845"
headers = {'User-Agent': 'Mozilla/5.0'}
currentPage = 0
readingPage = 1
pageLabelText = "Page {} of {} "
pageSize = (0 , 0)
resamplingMethod = None

leftButtonImage = customtkinter.CTkImage(light_image=Image.open("./resources/left.png"),
                                            dark_image=Image.open("./resources/left.png"))
rightButtonImage = customtkinter.CTkImage(light_image=Image.open("./resources/left.png"),
                                                dark_image=Image.open("./resources/right.png"))
zoomInButtomImage = customtkinter.CTkImage(light_image=Image.open("./resources/zoom in.png"),
                                                dark_image=Image.open("./resources/zoom in.png"))
zoomOutButtomImage = customtkinter.CTkImage(light_image=Image.open("./resources/zoom out.png"),
                                                dark_image=Image.open("./resources/zoom out.png"))
downloadImage = customtkinter.CTkImage(light_image=Image.open("./resources/download.png"),
                                            dark_image=Image.open("./resources/download.png"))


def changeResamplingMethod(choice):
    global resamplingMethod
    resamplingMethod = resamplingMethods[choice] 
    print(resamplingMethod)

def downloadPage(pages):
    directory = filedialog.asksaveasfilename(defaultextension=".png",
                                        filetypes=[("PNG", ".png"), ("JPG", ".jpg")])
    imageToDownload = Image.open(BytesIO(pages[currentPage]))
    imageToDownload.save(directory)

    
def createReaderWindow(imageContent):
    global readingPage

    readerWindow = customtkinter.CTkToplevel()
    readerWindow.geometry("600x600")
    readerWindow.wm_iconbitmap("visual/bookscraper-icon.ico")
    readerWindow.title("Book Scraper")

    labelFont = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=12)
    readingPage = 1

    controlFrame = customtkinter.CTkFrame(readerWindow, width=10)
    controlFrame.pack(side=BOTTOM)

    pageNumberDisplay = customtkinter.CTkLabel(controlFrame, width=70, height=40, 
                                               text=pageLabelText.format("1", len(imageContent)), 
                                               fg_color=fgColor,
                                               font=labelFont)
    
    resamplingMenu = customtkinter.CTkOptionMenu(controlFrame, width=70, height=40, 
                                                 values=list(resamplingMethods.keys()),
                                                 fg_color=fgColor,
                                                 button_color=fgColor,
                                                 font=labelFont,
                                                 command=changeResamplingMethod)
    resamplingMenu.pack(side='left', anchor='sw')
    
    downloadPageButton = customtkinter.CTkButton(controlFrame, width=70, height=40,
                                                 text="",
                                                 image=downloadImage,
                                                 fg_color=fgColor,
                                                 font=labelFont,
                                                 command= lambda pages = imageContent: downloadPage(pages))
    downloadPageButton.pack(side='right', anchor='se')

    pageFrame = customtkinter.CTkScrollableFrame(readerWindow)
    pageFrame.pack(anchor='center', fill="both", expand=True)
    pageLabel = customtkinter.CTkLabel(pageFrame, text="", image=None)
    pageLabel.pack(anchor='center', fill="x")


    leftButton = customtkinter.CTkButton(controlFrame, width=70, height=40, 
                                          image=leftButtonImage,
                                          text="", 
                                          fg_color=fgColor,
                                          command= lambda pages = imageContent, 
                                          pageLabel = pageLabel,
                                          pageNumberDisplay = pageNumberDisplay: getLastPage(pages, pageLabel, pageNumberDisplay))
    leftButton.pack(side=LEFT)

    rightButton = customtkinter.CTkButton(controlFrame, width=70, height=40, 
                                          image=rightButtonImage,
                                          text="", 
                                          fg_color=fgColor,
                                          command= lambda pages = imageContent, 
                                          pageLabel = pageLabel,
                                          pageNumberDisplay = pageNumberDisplay: getNextPage(pages, pageLabel, pageNumberDisplay))
    rightButton.pack(side=RIGHT)

    zoomInButton = customtkinter.CTkButton(controlFrame, width=70, height=40, 
                                           image=zoomInButtomImage, 
                                           text="", 
                                           fg_color=fgColor,
                                           command= lambda pageLabel = pageLabel, pages = imageContent: zoomIn(pageLabel, pages))
    zoomInButton.pack(side=LEFT)

    zoomOutButton = customtkinter.CTkButton(controlFrame, width=70, height=40, 
                                            image=zoomOutButtomImage, 
                                            text="",
                                            fg_color=fgColor,
                                            command= lambda pageLabel = pageLabel, pages= imageContent: zoomOut(pageLabel, pages))
    zoomOutButton.pack(side=RIGHT)

    pageNumberDisplay.pack(side=RIGHT)
                                            
    pageDisplay(imageContent, pageLabel)


def getNextPage(pages, pageLabel, pageNumberDisplay):
    global currentPage
    global readingPage
    global resamplingMethod

    if currentPage == len(pages) - 1:
        pass
    else:
        page = Image.open(BytesIO(pages[currentPage+1]))
        pageSize = (page.width, page.height)
        page.resize((page.width, page.height), resamplingMethod)
        pageLabel.configure(image=(customtkinter.CTkImage(light_image=page,
                              dark_image=page,
                              size=pageSize)))
                             
        currentPage += 1
        readingPage += 1
        pageNumberDisplay.configure(text=pageLabelText.format(readingPage, len(pages)))
        print(currentPage)
    
def getLastPage(pages, pageLabel, pageNumberDisplay):
    global currentPage
    global readingPage
    global resamplingMethod

    if currentPage == 0:
        pass
    else:
        page = Image.open(BytesIO(pages[currentPage-1]))
        page.resize((page.width, page.height), resamplingMethod)
        pageSize = (page.width, page.height)
        pageLabel.configure(image=(customtkinter.CTkImage(light_image=page,
                              dark_image=page,
                              size=pageSize)))
                              
        currentPage -= 1
        readingPage -= 1
        pageNumberDisplay.configure(text=pageLabelText.format(readingPage, len(pages)))
        print(currentPage)



def zoomIn(pageLabel, pages):
    global pageSize
    global resamplingMethod

    page = Image.open(BytesIO(pages[currentPage]))
    pageSize = (page.width / 0.7, page.height / 0.7)
    page.resize((page.width, page.height), resamplingMethod)
    pageLabel.configure(image=(customtkinter.CTkImage(light_image=page,
                                                      dark_image=page,
                                                      size=pageSize)))
                                                      

def zoomOut(pageLabel, pages):
    global pageSize
    global resamplingMethod

    page = Image.open(BytesIO(pages[currentPage]))
    pageSize = (page.width * 0.7, page.height * 0.7)
    page.resize((page.width, page.height), resamplingMethod)
    pageLabel.configure(image=(customtkinter.CTkImage(light_image=page,
                                                      dark_image=page,
                                                      size=pageSize)))
    

def pageDisplay(imageContent, pageLabel):
    global currentPage
    global pageSize
    firstPage = Image.open(BytesIO(imageContent[0]))
    firstPage.resize((firstPage.width, firstPage.height), Image.NEAREST)
    pageSize = ((firstPage.width), (firstPage.height))
    currentPage = 0
    pageLabel.configure(image=(customtkinter.CTkImage(light_image=firstPage,
                                                     dark_image=firstPage,
                                                     size=pageSize)))

    
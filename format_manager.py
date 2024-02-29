import zipfile

def createCbz(imageContent, outputCbz):
    with zipfile.ZipFile(outputCbz, 'w') as cbz_file:
        for pageNum, imageContent in enumerate(imageContent, 1):
            cbz_file.writestr(f'{pageNum}.jpg', imageContent)

def createJpg(imageContent, chosenDir):
    for pageNum, image in enumerate(imageContent, 1):
        print(pageNum)
        with open(f"{chosenDir}/#{pageNum}.jpg", 'wb') as f:
                f.write(image)



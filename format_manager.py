import zipfile

compressionMethods = {"Stored": zipfile.ZIP_STORED,
                       "BZIP2": zipfile.ZIP_BZIP2,
                       "LZMA": zipfile.ZIP_LZMA,
                       "Deflate": zipfile.ZIP_DEFLATED}

def createCbz(imageContent, outputCbz):
    with zipfile.ZipFile(outputCbz, 'w') as cbz_file:
        for pageNum, imageContent in enumerate(imageContent, 1):
            cbz_file.writestr(f'{pageNum}.jpg', imageContent)

def createZip(imageContent, outputZip, zipCompression): 
    with zipfile.ZipFile(outputZip, 'w', compression=compressionMethods[zipCompression]) as zipFile:
        for pageNum, imageContent in enumerate(imageContent, 1):
            zipFile.writestr(f'{pageNum}.jpg', imageContent)

def createJpg(imageContent, chosenDir):
    for pageNum, image in enumerate(imageContent, 1):
        print(pageNum)
        with open(f"{chosenDir}/#{pageNum}.jpg", 'wb') as f:
                f.write(image)




import easyocr
import cv2
import imutils
import skimage
import os

#  packages: - python 3.7.1
#            - opencv 4.5.4.60


def getPlateChars(foundPlate):

    foundPlate_gray = cv2.cvtColor(foundPlate, cv2.COLOR_BGR2GRAY)

    thresh_foundPlate = cv2.threshold(foundPlate_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
    thresh_foundPlate = cv2.morphologyEx(thresh_foundPlate, cv2.MORPH_OPEN, kernel)

    contours, hierarchy = cv2.findContours(thresh_foundPlate, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # array of none-s
    contours_poly = [None] * len(contours)

    # The Bounding Rectangles will be stored here:
    boundRect = []

    # look for the outer bounding boxes:
    for i, c in enumerate(contours):

        if hierarchy[0][i][3] == -1:
            contours_poly[i] = cv2.approxPolyDP(c, 3, True)
            boundRect.append(cv2.boundingRect(contours_poly[i]))

    # Draw the bounding boxes on the input image:
    for i in range(len(boundRect)):
        color = (0, 255, 0)
        cv2.rectangle(foundPlate, (int(boundRect[i][0]), int(boundRect[i][1])), \
                  (int(boundRect[i][0] + boundRect[i][2]), int(boundRect[i][1] + boundRect[i][3])), color, 2)


    cv2.imshow('bounding boxes', foundPlate)
    #cv2.waitKey(0)

    # sorting:
    n = len(boundRect)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            xj = boundRect[j]
            xi = boundRect[j + 1]
            if xi < xj:
                boundRect[j], boundRect[j + 1] = boundRect[j + 1], boundRect[j]


    # Crop the characters:
    counter = 1
    finalPlateNumber = ""
    for i in range(len(boundRect)):
        # Get the roi for each bounding rectangle:
        x, y, w, h = boundRect[i]

        # Crop the roi:
        croppedImg = thresh_foundPlate[y:y + h, x:x + w]

        # print(x, y, w, h)
        if w > 10 and h > 10 and len(croppedImg) and w < 300:
            croppedImg = cv2.resize(croppedImg, (40, 40))

            cv2.imshow("Cropped Character: " + str(i), croppedImg)

            folder_dir = ""
            if counter <= 3:
                folder_dir = "SampleLetters/letters"
            else:
                folder_dir = "SampleLetters/numbers"
            maxScore = -10
            letter = ""

            for image in os.listdir(folder_dir):

                path = folder_dir + "/" + image
                #print(path)
                charToCompare = cv2.imread(path)
                charToCompare = cv2.resize(charToCompare, (40, 40))
                charToCompare = cv2.cvtColor(charToCompare, cv2.COLOR_BGR2GRAY)

                charToCompare = cv2.threshold(charToCompare, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
                charToCompare = cv2.morphologyEx(charToCompare, cv2.MORPH_OPEN, kernel)

                score = skimage.metrics.structural_similarity(croppedImg, charToCompare, full=True)

                if score > maxScore:
                    maxScore = score
                    letter = image

            img = cv2.imread(folder_dir + "/" + letter)
            img = cv2.resize(img, (40, 40))
            #cv2.imshow("vizsgalt", img)
            counter += 1
            finalPlateNumber += letter[0]
            #cv2.waitKey(0)

    return finalPlateNumber




img = cv2.imread('resources/car43.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # noise reduction
cv2.imshow("bilateral", bfilter)
imgCanny = cv2.Canny(bfilter, 30, 200)  # edge detection
cv2.imshow('canny', imgCanny)
points = cv2.findContours(imgCanny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(points)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]


while True:
    location = None
    foundRectangle = False

    if not bool(contours):
        break

    # for contour in contours:
    #     approx = cv2.approxPolyDP(contour, 10, True)
    #     if len(approx) == 4:
    #         print('megvan')

    print('length:', len(contours))
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            print('bent')
            foundRectangle = True
            (x, y) = approx[1][0]
            (x3, y3) = approx[3][0]
            (x2, y2) = approx[2][0]
            (x0, y0) = approx[0][0]
            height = y3 - y
            width = x0 - x2
            aspectRatio = width / height
            if aspectRatio >= 2 and aspectRatio <= 8:
                location = approx
                contours.remove(contour)
                break
            contours.remove(contour)
            break

    if not foundRectangle:
        print("License plate not found.")
        break

    #contours.pop(idx)

    cv2.imshow('gray+edge', imgCanny)



    if(location is not None):
        rect = cv2.rectangle(img, (location[0][0]), (location[2][0]), color=(0, 255, 0))
        cv2.imshow('asd', img)
        #  cropping (hosszt kell még hozzáadni.)
        (x, y) = location[1][0]
        (x3, y3) = location[3][0]
        (x2, y2) = location[2][0]
        (x0, y0) = location[0][0]
        height = y3 - y
        width = x0 - x2
        #print('-----')
        #print(height, width)
        #print(abs(width) / abs(height))
        plate = cv2.boundingRect(location)
        x, y, w, h = plate
        print("loc: ", plate)

        roi = img[y:y+abs(h), x:x+abs(w)]  # height, width

        cv2.imshow('region of interest', roi)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(roi)

        if bool(result):
            print("License plate found!")
            print(result)
            break

    #cv2.waitKey(0)

print("OCR Program end.")

#  --------------------------------------------------------------------------------------------------

print("now trying without OCR.")
points = cv2.findContours(imgCanny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(points)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

result = ""
while True:
    location = None
    foundRectangle = False

    if not bool(contours):
        break

    print('length:', len(contours))
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            print('bent')
            foundRectangle = True
            (x, y) = approx[1][0]
            (x3, y3) = approx[3][0]
            (x2, y2) = approx[2][0]
            (x0, y0) = approx[0][0]
            height = y3 - y
            width = x0 - x2
            aspectRatio = width / height
            if aspectRatio >= 2 and aspectRatio <= 8:
                location = approx
                contours.remove(contour)
                break
            contours.remove(contour)
            break

    if not foundRectangle:
        print("License plate not found without OCR.")
        break

    cv2.imshow('gray+edge', imgCanny)



    if(location is not None):
        rect = cv2.rectangle(img, (location[0][0]), (location[2][0]), color=(0, 255, 0))
        cv2.imshow('asd', img)
        #  cropping (hosszt kell még hozzáadni.)
        (x, y) = location[1][0]
        (x3, y3) = location[3][0]
        (x2, y2) = location[2][0]
        (x0, y0) = location[0][0]
        height = y3 - y
        width = x0 - x2
        #print('-----')
        #print(height, width)
        #print(abs(width) / abs(height))
        plate = cv2.boundingRect(location)
        x, y, w, h = plate
        print("loc: ", plate)

        roi = img[y:y+abs(h), x:x+abs(w)]  # height, width

        cv2.imshow('region of interest', roi)
        result = getPlateChars(roi)

        if bool(result):
            print("License plate found without OCR!")
            print(result)
            break

    #cv2.waitKey(0)

if result == "":
    print("License not found without OCR!")

cv2.imshow('asd', img)
cv2.waitKey(0)




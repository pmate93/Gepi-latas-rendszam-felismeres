
import easyocr
import cv2
import imutils

#  packages: - python 3.7.1
#            - opencv 4.5.4.60


img = cv2.imread('resources/car3.jpg')
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

        roi = img[y:y+abs(height), x:x+abs(width)]  # height, width

        cv2.imshow('region of interest', roi)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(roi)

        if bool(result):
            print("License plate found!")
            print(result)
            break

    #cv2.waitKey(0)

print("Program end.")
cv2.imshow('asd', img)
cv2.waitKey(0)


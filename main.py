
import easyocr
import cv2
import imutils



img = cv2.imread('resources/car5.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # noise reduction
imgCanny = cv2.Canny(bfilter, 30, 200)  # edge detection

points = cv2.findContours(imgCanny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = imutils.grab_contours(points)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

location = None
for contour in contours:
    approx = cv2.approxPolyDP(contour, 10, True)
    if len(approx) == 4:
        location = approx
        break
cv2.imshow('gray+edge', imgCanny)
print('asd')
print(location)


rect = cv2.rectangle(img, (location[0][0]), (location[2][0]), color=(0, 255, 0))

#  cropping (hosszt kell még hozzáadni.)
(x, y) = location[1][0]
print(location)
(x3, y3) = location[3][0]
(x2, y2) = location[2][0]
(x0, y0) = location[0][0]
height = y3 - y
width = x0 - x2

print(x)
roi = img[y:y+height, x:x+width]  # height, width

cv2.imshow('region of interest', roi)
reader = easyocr.Reader(['en'])
result = reader.readtext(roi)

print(result)

cv2.waitKey(0)


import cv2
import numpy as np
from datetime import datetime, timedelta


debug = True
# Load the images

def add_to_canvas(canvas, img_to_add, guess_coords, debug):
    guess = canvas[guess_coords[1]:guess_coords[3], guess_coords[0]:guess_coords[2], :] 
    

    gray1 = cv2.cvtColor(img_to_add, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(guess, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)

    index_params = dict(algorithm=0, trees=5)  # KDTREE index with 5 trees
    search_params = dict(checks=50)  # Number of times to traverse the tree for checks

    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
        
    if len(good_matches) > 4:
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.flatten().tolist()

        ones = np.ones((img_to_add.shape[0], img_to_add.shape[1]), dtype=np.uint8) * 255

        warped_image = cv2.warpPerspective(img_to_add, H, (img_to_add.shape[1]*2, img_to_add.shape[0]*2, ))
        warped_mask = cv2.warpPerspective(ones, H, (img_to_add.shape[1]*2, img_to_add.shape[0]*2, ))

        print("matches found")
        print(datetime.now() - start_time)

        
        toreplace = canvas[guess_coords[1]:guess_coords[3] *2, guess_coords[0]:guess_coords[2] * 2, :]

        
        if debug:
            matchesimage = cv2.drawMatches(img_to_add, keypoints1, guess, keypoints2, good_matches, None)
            cv2.imshow('Matches', cv2.resize(matchesimage, (800, 600)))
            cv2.imshow('warped_image', cv2.resize( warped_image, (800, 600)))
            cv2.imshow('warped_mask', cv2.resize( warped_mask, (800, 600)))
            cv2.imshow('canvas', cv2.resize( canvas, (800, 600)))
            cv2.imshow('guess', cv2.resize( guess, (800, 600)))
            cv2.imshow('img_to_add', cv2.resize( toreplace, (800, 600)))
            cv2.waitKey(0)

        toreplace[np.where(warped_mask > 1)] = warped_image[np.where(warped_mask > 1)]

        canvas[guess_coords[1]:guess_coords[3] *2, guess_coords[0]:guess_coords[2] * 2, :] = toreplace

        print("canvas updated")
        print(datetime.now() - start_time)

        if debug:
            cv2.imshow('canvas', cv2.resize( canvas, (800, 600)))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return canvas

    else:
         canvas[guess_coords[1]:guess_coords[3], guess_coords[0]:guess_coords[2], :] = img_to_add
         print("not enough matches found - fallback to guess")
         return canvas




img2 = cv2.imread('./images/level0/2-0.jpg')
canvas = np.zeros((img2.shape[0] * 2, img2.shape[1] * 2, 3), dtype=np.uint8) 
canvas[0:img2.shape[0] , 0:img2.shape[1], :] = img2

guess_coords = (0, int(img2.shape[0]*0.5), img2.shape[1] , int(img2.shape[0] * 1.5))
img1 = cv2.imread('./images/level0/1-0.jpg')



start_time = datetime.now()
returned = add_to_canvas(canvas, img1, guess_coords, True )

img3 = cv2.imread('./images/level0/0-0.jpg')
returned = add_to_canvas(returned, img3, (0, img2.shape[0], img2.shape[1], img2.shape[0]*2), False)
cv2.imshow('result.png', cv2.resize( returned, (800, 600))) # (img_to_add, returned)
cv2.waitKey(0)
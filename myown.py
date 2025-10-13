import cv2
import numpy as np


# Load the images
img1 = cv2.imread('./images/level0/0-0.jpg')
img2 = cv2.imread('./images/level0/1-0.jpg')


# Convert the images to grayscale
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# Detect keypoints and compute descriptors
sift = cv2.SIFT_create()
keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)


index_params = dict(algorithm=0, trees=5)  # KDTREE index with 5 trees
search_params = dict(checks=50)  # Number of times to traverse the tree for checks

# Match the descriptors
matcher = cv2.FlannBasedMatcher(index_params, search_params)
matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

# Filter the matches
good_matches = []
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good_matches.append(m)
       

# Compute the transform
if len(good_matches) > 4:
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.flatten().tolist()
else:
    raise Exception("Not enough matches")

# Draw the matches
img3 = cv2.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, None)
# cv2.imshow('Matches', img3)
# cv2.waitKey(0)
# cv2.destroyAllWindows()





# Create a new image with the same size as the second image
stitched_image = np.zeros_like(img2)

# Warp the first image onto the second image using the homography matrix
print(H)
stitched_image = cv2.warpPerspective(img1, H, (img2.shape[1], img2.shape[0]))
cv2.imshow('Stitched Image', stitched_image)
cv2.waitKey(0)

# Create a mask based on the overlap area
mask = np.zeros_like(stitched_image)
mask[np.where((stitched_image != [0, 0, 0]).all(axis=2))] = 1

# Blend the first and second images together while preserving non-overlapping areas
alpha = 0.5  # Adjust this value to control the blending strength
blended_image = cv2.addWeighted(stitched_image, alpha, img2, 1-alpha, 0)
blended_image[mask == 0] = img2[mask == 0]

# Display the blended image
cv2.imshow('Blended Image', blended_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
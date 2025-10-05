from stitching import AffineStitcher
import cv2
import os

stitcher = AffineStitcher( )



rangex = (0, 4)
rangey = (0, 4)
level = 0

for level in range(0, 4):
    level_path = "./level{}/".format(level)
    next_level_path = "./level{}/".format(level + 1)

    os.makedirs(level_path, exist_ok=True)
    os.makedirs(next_level_path, exist_ok=True)

    if not os.path.exists( level_path + "{}-{}.jpg".format(1,0)):
        y = 0
        while os.path.exists( level_path + "{}-{}.jpg".format(0,y + 1)):
            x = 0
            imageApath = level_path + "{}-{}.jpg".format(x, y)
            imageBpath = level_path + "{}-{}.jpg".format(x, y + 1)
            print("stitching", imageApath, imageBpath, "to", combined_path)


            combined = stitcher.stitch_verbose([imageApath, imageBpath])

            combined_path = next_level_path + "{}-{}.jpg".format(x, int(y // 2))
            cv2.imwrite(combined_path, combined)
            y = y + 2
    else:

        for y in range(rangey[0], rangey[1] ):
            
            for x in range(rangex[0], max(2, rangex[1] // (level + 1)), 2):

                imageApath = level_path + "{}-{}.jpg".format(x, y)
                imageBpath = level_path + "{}-{}.jpg".format(x + 1, y)
                print("stitching", imageApath, imageBpath)

                combined = stitcher.stitch_verbose([imageApath, imageBpath])

                combined_path = next_level_path + "{}-{}.jpg".format(int(x // 2), y)
                print("stitched", imageApath, imageBpath, "to", combined_path)
                cv2.imwrite(combined_path, combined)
            if rangex[1] % 2 == 1:
                trailing = level_path + "{}-{}.jpg".format(rangex[1], y)
                if os.path.exists(trailing):
                    imageBpath = level_path + "{}-{}.jpg".format(rangex[1] - 1, y)

                    combined_path = next_level_path + "{}-{}.jpg".format(int(rangex[1] // 2 + 1), y)
                    print("stitched trailing ", trailing, "to", combined_path)
                    cv2.imwrite(combined_path, cv2.imread(trailing))

            
            




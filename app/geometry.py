import time
import numpy as np 

from utils.filters import OneEuroFilter


# mediapipe facial landmarks parameters
INDEX_TOP = 10
INDEX_BOT = 152
INDEX_LEFT = 234
INDEX_RIGHT = 454
INDEX_CENTER = 6
IDX = [(0, INDEX_TOP), (1, INDEX_BOT), (2, INDEX_LEFT), (3, INDEX_RIGHT), (4, INDEX_CENTER)]

POSITION_FACTOR = 30

"""
3d point with OneEuroFilter
"""
class Point():
    def __init__(self, x, y, z) -> None:
        t = time.time()
        self.xFilter = OneEuroFilter(t, x)
        self.yFilter = OneEuroFilter(t, y)
        self.zFilter = OneEuroFilter(t, z)

        self.x = x
        self.y = y
        self.z = z

        self.color = (np.random.randint(0, 255), 
                      np.random.randint(0, 255), 
                      np.random.randint(0, 255))

    def update(self, x, y, z):
        self.prev_x = self.x
        self.prev_y = self.y
        self.prev_z = self.z

        t = time.time()
        self.x = self.xFilter(t, x)
        self.y = self.yFilter(t, y)
        self.z = self.zFilter(t, z)

    def get(self):
        return np.array([self.x, self.y, self.z])


# midpoint in n dimensional space
def midpoint(p1, p2):
    return (p1 + p2) / 2

"""
6 DOF head tracking with landmarks
"""
class Head():
    def __init__(self, landmarkList) -> None:
        self.points = []
        self.origins = []

        landmarks = landmarkList.landmark
        for _, i in IDX:
            landmark = landmarks[i]
            px = landmark.x
            py = landmark.y
            pz = landmark.z
            self.points.append(Point(px, py, pz))
            self.origins.append(np.array([px, py, pz]))
        
        # set rotation
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        # set position
        self.x = 0
        self.y = 0
        self.z = 0

    def get_points(self, landmarkList):
        # points array
        landmarks = landmarkList.landmark
        for i, j in IDX:
            landmark = landmarks[j]
            px = landmark.x
            py = landmark.y
            pz = landmark.z
            self.points[i].update(px, py, pz)

        return self.points

    def update_rotation(self):
        # get current points
        current = []
        for point in self.points:
            current.append(point.get())
        
        # compute centroids
        co = np.mean(self.origins, axis=0)
        cc = np.mean(current, axis=0)
        # Compute covariance matrix
        H = np.dot((self.origins - co).T, current - cc)
        # Compute SVD
        U, S, Vt = np.linalg.svd(H)
        # Compute rotation matrix
        R = np.dot(Vt.T, U.T)

        # Compute Euler angles
        yaw = np.arctan2(R[1,0], R[0,0])
        pitch = np.arctan2(-R[2,0], np.sqrt(R[2,1]**2 + R[2,2]**2))
        roll = np.arctan2(R[2,1], R[2,2])

        # Convert angles to degrees
        yaw = np.degrees(yaw)
        pitch = np.degrees(pitch)
        roll = np.degrees(roll)

        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw

    def update_position(self):
        # get position difference
        origin = midpoint(self.origins[2], self.origins[3])
        current = midpoint(self.points[2].get(), self.points[3].get())
        dPos = origin - current
        # scale up movement
        self.x = dPos[0] * POSITION_FACTOR
        self.y = dPos[1] * POSITION_FACTOR
        self.z = dPos[2] * POSITION_FACTOR

    def center(self):
        # set origins
        for i in range(len(self.points)):
            self.origins[i] = self.points[i].get() 

        self.pitch = 0
        self.roll = 0
        self.yaw = 0

        self.x = 0
        self.y = 0 
        self.z = 0

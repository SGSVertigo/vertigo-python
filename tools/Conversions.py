import numpy as np
import math
import quaternion


class RollPitchYaw(object):
    def __init__(self):
        pass

    @staticmethod
    def to_eul(q: np.quaternion) -> np.array:
        q = quaternion.as_float_array(q)
        t0 = -2 * (q[2] * q[2] + q[3] * q[3]) + 1
        t1 = 2 * (q[1] * q[2] - q[0] * q[3])
        t2 = -2 * (q[1] * q[3] + q[0] * q[2])
        t3 = 2 * (q[2] * q[3] - q[0] * q[1])
        t4 = -2 * (q[1] * q[1] + q[2] * q[2]) + 1

        if t2 > 1:
            t2 = 1

        if t2 < -1:
            t2 = -1

        pitch = math.asin(t2) * 2
        roll = math.atan2(t3, t4)
        yaw = math.atan2(t1, t0)

        pitch = pitch * (180.0 / math.pi)
        roll = roll * (180.0 / math.pi)
        yaw = yaw * (180.0 / math.pi)

        eul = np.array([roll, pitch, yaw])
        return eul
    
    @staticmethod
    def transform(vector, quatdata) -> np.array:
        """
        Convert vectors in board frame into the world fram by using
        the IMU's quaternion vector in the world frame.
        :param np.array vector: The vector converted in board reference frame
        :param np.array quatdata: The quaternion data
        :returns np.array: The vector converted into world frame
        """
        quat = quaternion.as_quat_array(quatdata)
        return quaternion.rotate_vectors(quat, vector)
        

    @staticmethod
    def convert(quatdata: np.array) -> np.array:
        """
        Convert the quaternion data into Euler (roll/pitch/yaw)

        :param np.array quatdata: The quaternion data
        :returns np.array: The data converted into Euler
        """
        # Create a new numpy array for the results
        results = np.empty([len(quatdata), 3])

        for i, row in enumerate(quatdata):
            # Extract the 
            my_q = np.quaternion(row[2],row[3],row[4],row[5])
            eul = RollPitchYaw.to_eul(my_q)
            results[i, :] = eul
        return results
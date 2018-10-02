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
    def transform(vectors, quatdata) -> np.array:
        """
        Convert vectors in board frame into the world fram by using
        the IMU's quaternion vector in the world frame.
        :param np.array vector: The vector converted in board reference frame
        :param np.array quatdata: The quaternion data
        :returns np.array: The vector converted into world frame
        """
        rotated_vectors = vectors.copy()
        for i in range(len(quatdata)):
            rotated_vector = np.array([0.0,rotated_vectors[i][0],rotated_vectors[i][1],rotated_vectors[i][2]])
            rotated_vector = RollPitchYaw.hamiltonian(quatdata[i],rotated_vector)
            rotated_vector = RollPitchYaw.hamiltonian(rotated_vector,RollPitchYaw.quaternionConjugate(quatdata[i]))
            rotated_vector = np.array([rotated_vector[1],rotated_vector[2],rotated_vector[3]])
            rotated_vectors[i] = rotated_vector
        return rotated_vectors
    
    @staticmethod
    def quaternionConjugate(quat: np.array) -> np.array:
        return np.array([quat[0],-quat[1],-quat[2],-quat[3]])
    
    @staticmethod
    def hamiltonian(q: np.array, r: np.array) -> np.array:
        return np.array([
            q[0]*r[0] - q[1]*r[1] - q[2]*r[2] - q[3]*r[3],
            q[0]*r[1] + r[0]*q[1] + q[2]*r[3] - q[3]*r[2],
            q[0]*r[2] + r[0]*q[2] + q[3]*r[1] - q[1]*r[3],
            q[0]*r[3] + r[0]*q[3] + q[1]*r[2] - q[2]*r[1]
        ])
        

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
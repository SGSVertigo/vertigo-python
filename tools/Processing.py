import numpy as np
import math
import quaternion
import pandas as pd


class Processing(object):
    def __init__(self):
        pass

    #https://stackoverflow.com/questions/21201618/pandas-merge-match-the-nearest-time-stamp-the-series-of-timestamps
    @staticmethod
    def matchIMUtoQuat(imu, quat):
        idx = np.searchsorted(quat['TimeStamp'], imu['TimeStamp']) - 1
        mask = idx >= 0

        quat_matched_imu = pd.DataFrame({
            "TimeStamp":imu['TimeStamp'].values[mask],
            "q0":quat['q0'].values[idx][mask],
            "q1":quat['q1'].values[idx][mask],
            "q2":quat['q2'].values[idx][mask],
            "q3":quat['q3'].values[idx][mask],
            "ax":imu['ax'].values[mask],
            "ay":imu['ay'].values[mask],
            "az":imu['az'].values[mask],
            "rx":imu['rx'].values[mask],
            "ry":imu['ry'].values[mask],
            "rz":imu['rz'].values[mask]
        })
        return quat_matched_imu
    
    @staticmethod
    def matchIMUtoGPS(imu, gps):
        idx = np.searchsorted(gps['TimeStamp'], imu['TimeStamp']) - 1
        mask = idx >= 0

        gps_matched_imu = pd.DataFrame({
            "TimeStamp":imu['TimeStamp'].values[mask],
            "x":gps['x'].values[idx][mask],
            "y":gps['y'].values[idx][mask],
            "z":gps['z'].values[idx][mask],
            "ax":imu['ax'].values[mask],
            "ay":imu['ay'].values[mask],
            "az":imu['az'].values[mask],
            "rx":imu['rx'].values[mask],
            "ry":imu['ry'].values[mask],
            "rz":imu['rz'].values[mask]
        })
        return gps_matched_imu
import csv
import utm
import numpy as np
from scipy import interpolate


class Kalman3d:
    def __init__(self, imutime, an, ae, ad, gpstime, lat, lon, alt) -> None:
        # Arrays of data

        # IMU
        self.imutime = np.array(imutime)
        self.an = np.array(an)  # accel north
        self.ae = np.array(ae)  # accel east
        self.ad = np.array(ad)  # accel down

        # GPS
        self.gpstime = np.array(gpstime)
        self.lat = np.array(lat)
        self.lon = np.array(lon)
        self.alt = np.array(alt)
        self.eastings = []
        self.northings = []
        self.datum = ()
        self.alt_relative = []

    def llm2utm(self):
        self.datum = utm.from_latlon(self.lat, self.lon)
        altitudes = np.array(self.alt)
        eastings = np.array(self.datum[0])
        northings = np.array(self.datum[1])
        self.alt_relative = (
            altitudes - altitudes[0]
        ) * -1.0  # convert to relative, down is positive
        self.easting_datum = eastings[0]
        self.northing_datum = northings[0]
        self.eastings = eastings - eastings[0]  # convert to relative
        self.northings = northings - northings[0]  # convert to relative

    """Interpolate the GPS to the same timescales as the imu data"""

    def interpolate_gps(self):
        self.eastings = interpolate.interp1d(
            self.gpstime, self.eastings, kind="previous", fill_value="extrapolate"
        )(self.imutime)
        self.northings = interpolate.interp1d(
            self.gpstime, self.northings, kind="previous", fill_value="extrapolate"
        )(self.imutime)
        self.alt_relative = interpolate.interp1d(
            self.gpstime, self.alt_relative, fill_value="extrapolate",
        )(self.imutime)
        self.eastings = np.nan_to_num(self.eastings, nan=0)
        self.northings = np.nan_to_num(self.northings, nan=0)
        self.alt_relative = np.nan_to_num(self.alt_relative, nan=0)

    def process(self):
        self.llm2utm()
        self.interpolate_gps()
        self.filter()

    def filter(self):
        # Process the kalman filter
        n_steps = len(self.imutime)

        # State vector: [s_n, s_e, s_d, v_n, v_e, v_d, a_n, a_e, a_d]
        x = np.zeros((9, 1))
        P = 1e-3 * np.identity(9)

        # Quick and hacky estimation of timestep
        dt = self.imutime[1] - self.imutime[0]

        # Process noise
        Q = np.diag([1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-9, 1e-3, 1e-3, 1e-3])
        # Measurement noise
        gps_var = 1e-5
        imu_var = 1e-3
        #Error definitions
        R = np.diag([gps_var, gps_var, gps_var * 10, imu_var, imu_var, imu_var])

        # Discrete time model
        # s_n(k+1) = s_n(k) + v_n(k) * dt
        # v_n(k+1) = v_n(k) + a_n(k) * dt
        # a_n(k+1) = a_n(k)
        #Relationship between states
        F = np.array(
            [
                [1, 0, 0, dt, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, dt, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, dt, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, dt, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, dt, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, dt],
                [0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1],
            ]
        )

        #Sensor to state mapping
        H = np.array(
            [
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 1],
            ]
        )

        # Remove gravity from NED accel, leaving linear accels in NED frame
        self.ad = self.ad - 1
        # Convert to ms^-2
        self.an = self.an * 9.81
        self.ae = self.ae * 9.81
        self.ad = self.ad * 9.81
        sensors = np.stack(
            (
                self.northings,
                self.eastings,
                self.alt_relative,
                self.an,
                self.ae,
                self.ad,
            )
        )
        kal_x_stor = np.zeros((9, n_steps))

        for i in range(0, n_steps - 1):
            # Predict
            xp = F @ x  # no inputs
            Pp = F @ P @ F.T + Q
            # Update
            sensor_step = np.array(
                [sensors[:, i]]
            ).T  # Re-arranging the array to get the element dimentsions right and conver to 2d array
            y = sensor_step - H @ x
            S = H @ P @ H.T + R
            K = Pp @ H.T @ np.linalg.inv(S)
            x = xp + K @ y
            P = (np.identity(9) - K @ H) @ Pp
            # Store
            kal_x_stor[:, i] = x[:, 0]
        self.kal_x_store = kal_x_stor

    def result(self):
        return self.kal_x_store

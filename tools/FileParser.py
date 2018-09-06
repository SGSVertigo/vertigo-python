import pandas as pd

class FileParser:

    @staticmethod
    def openFile(file_path):
        data = FileParser.parse(file_path)
        data = FileParser.fixRolloverError(data)
        gpsData = FileParser.getDataType(data,1)
        gpsData.columns = ["TimeStamp", "Data_Type", "x", "y","z","","",""]
        imuData = FileParser.getDataType(data,2)
        imuData.columns = ["TimeStamp", "Data_Type", "ax", "ay","az","rx","ry","rz"]
        quatData = FileParser.getDataType(data,3)
        quatData.columns = ["TimeStamp", "Data_Type", "q0", "q1","q2","q3","",""]
        return [gpsData,imuData,quatData]

    @staticmethod
    def parse(file_path):
        data = pd.read_csv(file_path,header=None)
        return data

    @staticmethod
    def getDataType(dataFrame, type_interger_identifier):
        return dataFrame.loc[dataFrame[dataFrame.columns[1]] == type_interger_identifier]

    @staticmethod
    def fixRolloverError(dataFrame):
        rollover_value = 2.0**32/1e4
        delta_times = dataFrame.diff()[dataFrame.columns[0]]
        negative_delta_times = delta_times.loc[delta_times < -10000]
        times = dataFrame[dataFrame.columns[0]]
        for row in negative_delta_times.index:
            times[row:len(times.index)] += rollover_value
        dataFrame[dataFrame.columns[0]] = times
        return dataFrame
            




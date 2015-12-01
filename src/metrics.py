import matplotlib.pyplot as plt
import constants
import numpy as np

class Metrics:
    def __init__(self, log, flows, links):
        """Logs the metrics. The simulation calls this whenever
        it wishes to record some data for a particular link, or flow.
        Currently, both links and flows have three (exclusive) metrics:
        Link                        Flow
        Link Rate (Mbps)            Flow Rate (Mbps)
        Buffer Occupancy (pkts)     Window Size (pkts)
        Packet Loss (pkts)          Packet Delay (ms)

        :param log: Data can be logged in different frequencies.
            if 'less': data is to be logged once per
            LOG_TIME_INTERVAL (roughly average).
            if 'avg': data is to be collected over LOG_TIME_INTERVAL,
            and then averaged for that time interval
            if 'more': data is to be logged whenever relevant
        :type log: str

        :param flows: the flows that are to be tracked (if any)
        :type flows: list<str>

        :param links: the links that are to be tracked (if any)
        :type links: list<str>
        """

        self.log = log
        self.links = links
        self.flows = flows

        # for each metric we wish to measure (link rate, flow rate, etc),
        # give indices denoting the current time interval's
        # lower bound [0] and upper bound [1]
        # contains also the sum of values found so far [2],
        # as well as the number of events that occurred in this time interval [3]
        self.CURRENT_TIME_INTERVAL = [
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
                [0, constants.LOG_TIME_INTERVAL, 0, 0],
        ]

        # container containing relevant for all the links/flows AS we log
        self.logData = {}
        # container containing information for all the links/flows we have 
        # ACCUMULATED so far
        self.totalData = {}
        for link in links:
            self.logData[str(link)] = self.CURRENT_TIME_INTERVAL
            self.totalData[str(link)] = [open(str(link) + '_linkRate.log', 'w'),
                    open(str(link) + '_bufferOccupancy.log', 'w'),
                    open(str(link) + '_packetLoss.log', 'w')]
        for flow in flows:
            self.logData[str(flow)] = self.CURRENT_TIME_INTERVAL
            self.totalData[str(flow)] = [open(str(flow) + '_flowRate.log', 'w'),
                    open(str(flow) + '_windowSize.log', 'w'),
                    open(str(flow) + '_packetDelay.log', 'w')]

    def done(self):
        """ Closes the log files, Then reads them and graphs the data.
        """
        for key, value in self.totalData.iteritems():
            value[0].close()
            value[1].close()
            value[2].close()
        self.run()

    def logMetric(self, time, value, type, ID):
        if str(ID) not in self.links and str(ID) not in self.flows:
            return
        metricType = self.logData[str(ID)]
        metricFileData = self.totalData[str(ID)]
        if self.log == 'avg':
            lowerTimeInterval = metricType[type][0]
            upperTimeInterval = metricType[type][1]
            # if past the previous time interval,
            # aggregate the values for that interval and log it
            if time >= upperTimeInterval:
                # if there were no previous events, don't log anything
                count = metricType[type][3]
                if count > 0:
                    data = metricType[type][2] \
                        / count
                    # if this is a packet loss, don't average it. Just
                    # return the total number of packets dropped during this period
                    if 'L' in ID and type == 2:
                        data = metricType[type][2]
                    metricFileData[type].write(str(upperTimeInterval)
                        + " " + str(data) + "\n")

                # update the upper/lower bounds
                while time > upperTimeInterval:
                    metricType[type][1] += constants.LOG_TIME_INTERVAL
                    upperTimeInterval = metricType[type][1]
                metricType[type][0] \
                    = metricType[type][1] \
                    - constants.LOG_TIME_INTERVAL
                # reset
                metricType[type][2] = 0
                metricType[type][3] = 0
            # update the aggregate buffer link found so far
            metricType[type][2] \
                += value
            metricType[type][3] \
                += 1
        elif self.log == 'less':
            lowerTimeInterval = metricType[type][0]
            upperTimeInterval = metricType[type][1]
            # if no event of this type occurred in the last time interval(s),
            # have to move up the current time interval
            while time > upperTimeInterval:
                metricType[type][1] += constants.LOG_TIME_INTERVAL
                upperTimeInterval = metricType[type][1]
            if time >= lowerTimeInterval:
                metricFileData[type].write(str(upperTimeInterval)
                    + " "
                    + str(value) + "\n")
                # update the lower bound
                metricType[type][0] \
                    = metricType[type][1]
        else: # self.log == 'more'
            metricFileData[type].write(str(time)
            + " "
            + str(value) + "\n")

    def linkRate(self, fig, ID, file, ax):
        try:
            time, linkRate = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for link rate"
            return

        ax.plot(time, linkRate, label=ID)
        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def bufferOccupancy(self, fig, ID, file, ax):
        try:
            time, buffer = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for buffer occupancy"
            return

        ax.plot(time, buffer, label=ID)
        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def packetLoss(self, fig, ID, file, ax):
        try:
            time, packetLoss = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for packet loss"
            return

        ax.plot(time, packetLoss, label=ID)

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def flowRate(self, fig, ID, file, ax):
        try:
            time, flowRate = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for flow rate"
            return

        ax.plot(time, flowRate, label=ID)

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def windowSize(self, fig, ID, file, ax):
        try:
            time, windowSize = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for window size"
            return

        ax.plot(time, windowSize, label=ID)

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


    def packetDelay(self, fig, ID, file, ax):
        try:
            time, packetDelay = np.loadtxt(file, delimiter=' ',
                    usecols = (0, 1), unpack = True)
        except ValueError as e:
            print str(e) + " for packet delay"
            return


        ax.plot(time, packetDelay, label=ID)

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    def run(self):
        # Starting the metric logging.
        fig = plt.figure(figsize=(10, 6))
        fig2 = plt.figure(figsize=(10, 6))

        ax1= fig.add_subplot(311)
        ax1.set_xlabel('Time (sec)')
        ax1.set_ylabel('Link rate (Mbps)')
        # Shrink current axis by 20%
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax2= fig.add_subplot(312)
        ax2.set_xlabel('Time (sec)')
        ax2.set_ylabel('Buffer Occupancy (pkts)')
        # Shrink current axis by 20%
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax3= fig.add_subplot(313)
        ax3.set_xlabel('Time (sec)')
        ax3.set_ylabel('Packet loss (pkts)')
        # Shrink current axis by 20%
        box = ax3.get_position()
        ax3.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax4= fig2.add_subplot(311)
        ax4.set_xlabel('Time (sec)')
        ax4.set_ylabel('Flow rate (Mbps)')
        # Shrink current axis by 20%
        box = ax4.get_position()
        ax4.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax5= fig2.add_subplot(312)
        ax5.set_xlabel('Time (sec)')
        ax5.set_ylabel('Window size (pkts)')
        # Shrink current axis by 20%
        box = ax5.get_position()
        ax5.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        ax6= fig2.add_subplot(313)
        ax6.set_xlabel('Time (sec)')
        ax6.set_ylabel('Packet delay (ms)')
        # Shrink current axis by 20%
        box = ax6.get_position()
        ax6.set_position([box.x0, box.y0, box.width * 0.8, box.height])


        for key, value in self.totalData.iteritems():
            if "L" in key:
                self.linkRate(fig, key, value[0].name, ax1)
                self.bufferOccupancy(fig, key, value[1].name, ax2)
                self.packetLoss(fig, key, value[2].name, ax3)
            elif "F" in key:
                self.flowRate(fig2, key, value[0].name, ax4)
                self.windowSize(fig2, key, value[1].name, ax5)
                self.packetDelay(fig2, key, value[2].name, ax6)
        fig.subplots_adjust(left = 0.08, right = 0.87, hspace = 0.78)
        fig2.subplots_adjust(left = 0.08, right = 0.87, hspace = 0.78)

        plt.show()

if __name__ == "__main__":
    metric = Metrics('avg')
    metric.run()

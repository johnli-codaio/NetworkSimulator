import argparse
import json
import pprint
import metrics
import classes
import constants
import simulation


def main():
    # parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    # parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name',
    #                     help = 'Store JSON file name')
    # options for parsing a JSON file
    parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name',
                        help = 'Store JSON file name')

    # options for graphing metrics
    parser.add_argument('--m', dest = 'metrics',
            action = 'store_true', help = 'Print graphs for metrics')

    # TODO: options for method of congestion control?
    #

    # TODO: options for verbose? for debugging purposes

    args = parser.parse_args()

    f = open(args.json_file_name)

    print "JSON DATA:"
    parsed_data = json.loads(f.read())
    print "Parsed:"
    pprint.pprint(parsed_data)

    devices = {}
    links = {}
    flows = {}

    print "\n\n"

    print "Iterating over hosts:"
    for host_name in parsed_data['hosts']:
        print "Host ", host_name, "has data: ", parsed_data['hosts'][host_name]
        host = classes.Host(str(host_name))
        devices[str(host_name)] = host

    print "Iterating over routers:"
    print "TEST:"
    for router_name in parsed_data['routers']:
        print "Router ", router_name, "has data: ", parsed_data['routers'][router_name]
        router = classes.Router(str(router_name))
        devices[str(router_name)] = router
        #just added this, see if it works
        router.find_neighbors()
        print "asdfasdf"
        for router in router.neighbors:
            print "asdf"
            print router
    print "Hosts and routers instantiated. ", "\n\n"

    print "Iterating over links and adding to hosts/routers:"
    for link_name in parsed_data['links']:
        link_data = parsed_data['links'][link_name]
        print "Link ", link_name, "has data: ", link_data

        link = classes.Link(str(link_name), link_data['link_rate'], link_data['link_delay'],
                            link_data['link_buffer'],
                            devices[link_data['devices'][0]], devices[link_data['devices'][1]])
        links[str(link_name)] = link



    print "Links instantiated.", "\n\n"

    print "Iterating over flows:"
    for flow_name in parsed_data['flows']:
        flow_data = parsed_data['flows'][flow_name]
        print "Flow ", flow_name, "has data: ", flow_data

        flow = classes.Flow(str(flow_name), devices[flow_data['flow_src']],
                            devices[flow_data['flow_dest']],
                            flow_data['data_amt'], flow_data['flow_start'])
        flows[str(flow_name)] = flow
    print "Flows instantiated: ", "\n\n"

    print "Creating network..."
    network = classes.Network(devices, links, flows)

    print "----------DEVICE DETAILS----------"
    for device_name in devices:
        print "Device is: ", "HOST" if isinstance(devices[device_name], classes.Host) else "ROUTER"
        print "Name is: ", device_name
        print "Links: ", [l.linkID for l in devices[device_name].links]
        print "\n"

    print "----------LINK DETAILS----------"
    for link_name in links:
        print "Link name is: ", link_name
        print "Connects devices: ", links[link_name].device1.deviceID, links[link_name].device2.deviceID
        print "Link rate: ", links[link_name].rate
        print "Link delay", links[link_name].delay
        print "Link buffer size: ", links[link_name].linkBuffer.maxSize
        print "\n"

    print "----------FLOW DETAILS----------"
    for flow_name in flows:
        print "Flow name is: ", flow_name
        print "Source is: ", flows[flow_name].src
        print "Destination is: ", flows[flow_name].dest
        print "Data amount in bytes is: ", flows[flow_name].data_amt
        print "Flow start time in ms is: ", flows[flow_name].flow_start


    print "----------STARTING SIMULATION------------"

    simulator = simulation.Simulator(network)

    # Have flows create sending events...

    for flow_name in flows:
        flow = flows[flow_name]

        counter = 0
        timer = flow.flow_start

        newGenEvent = simulation.Event(None, None, "INITIALIZEFLOW", timer, flow)
        simulator.insertEvent(newGenEvent)


    while not simulator.q.empty():
        print "QUEUE SIZE: " + str(simulator.q.qsize())
        simulator.processEvent()

    for flow_name in flows:
        flow = flows[flow_name]
        print "DATA ACKNOWLEDGED: " + str(flow.data_acknowledged)
        print "DATA MADE: " + str(flow.data_amt)

    print "Simulation done!"

    simulator.done()

    # log the metrics
    if args.metrics:
        m = metrics.Metrics()
        m.run()



if __name__ == "__main__":
    main()



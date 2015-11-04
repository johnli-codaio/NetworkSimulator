import argparse
import json
import pprint


import classes
import simulation

def main():
    parser = argparse.ArgumentParser(description = 'Run simulation on JSON file.')
    parser.add_argument('--json', '-j', action = 'store', dest = 'json_file_name', 
                        help = 'Store JSON file name')
    # TODO: options for method of congestion control?
    # 

    args = parser.parse_args()

    f = open(args.json_file_name) 

    # TODO: uncomment above, this  line below is for testing
    # f = open("test0.json")
    print "JSON DATA:"
    parsed_data = json.loads(f.read())

    pprint.pprint(parsed_data)

    devices = {}
    links = {}
    flows = {}

    print "\n\n"

    print "Iterating over hosts:"
    for host_name in parsed_data['hosts']:
        print "Host ", host_name, "has data: ", parsed_data['hosts'][host_name]
        host = classes.Host(host_name)
        devices[host_name] = host

    print "Iterating over routers:"
    for router_name in parsed_data['routers']:
        print "Router ", router_name, "has data: ", parsed_data['routers'][router_name]
        router = classes.Router(router_name)
        devices[router_name] = router
    print "Hosts and routers instantiated: ", devices, "\n\n"

    print "Iterating over links and adding to hosts/routers:"
    for link_name in parsed_data['links']:
        link_data = parsed_data['links'][link_name]
        print "Link ", link_name, "has data: ", link_data

        link = classes.Link(link_name, link_data['link_rate'], link_data['link_delay'], 
                            link_data['link_buffer'], 
                            link_data['devices'][0], link_data['devices'][1])
        links[link_name] = link

        devices[link_data['devices'][0]].attachLink(link)
        devices[link_data['devices'][1]].attachLink(link)

    print "Links instantiated: ", links, "\n\n"

    print "Iterating over flows:"
    for flow_name in parsed_data['flows']:
        flow_data = parsed_data['flows'][flow_name]
        print "Flow ", flow_name, "has data: ", flow_data

        flow = classes.Flow(flow_name, flow_data['flow_src'], flow_data['flow_dest'],
                            flow_data['data_amt'], flow_data['flow_start'])
        flows[flow_name] = flow
    print "Flows instantiated: ", flows, "\n\n"

    # Have flows create sending events...










if __name__ == "__main__":
    main()



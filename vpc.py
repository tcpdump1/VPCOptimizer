def region(x):

    import json
    import boto3

    sns = boto3.client('sns')
    topicArn = 'arn:aws:sns:eu-west-1:AccountNumber:testSNS' # Fill in the ARN for the topic
    vpc_client = boto3.client('ec2', region_name = x)

##CODE FOR CHECKING IP ADDRESS USAGE IN VPCS
    list_vpc = vpc_client.describe_vpcs()
    vpc_list = []
    for i in list_vpc['Vpcs']:
        vpc_list.append(i['VpcId']) #Append all the VPCs in the region into a list called vpc_list. 
    list_of_vpc = sorted(vpc_list)


#This section calculates all the reserved IPs for each subnet in a VPC and appends that to a list. 
    len_of_subnet = []
    for eachvpc in list_of_vpc:
        number_of_subnet = []
        for subnetdetails in vpc_client.describe_subnets(Filters=[{'Name': 'vpc-id','Values': [eachvpc]}])['Subnets']:
            number_of_subnet.append(subnetdetails["SubnetId"])
        len_of_subnet.append(len(number_of_subnet) * 5) #Five IPs are reserved in each subnet




#Using the list gotten in the previous section, this section calculates 70% of available IP address in a VPC. The available IP address does not include the five reserved IP address of each VPC.
    totalIP = [] #Define a list that shows 70% of the available IP addresses from each VPC CIDR into a list
    for eachvpc in list_of_vpc:
        ip_address = vpc_client.describe_vpcs(Filters=[{'Name': 'vpc-id','Values': [eachvpc]}])
        for vpc in ip_address['Vpcs']:
            private = [] #The private list checks for all the CIDRs associated to a VPC and then appends the available IP addresses in those CIRS to a list for futher summation.
        
            for j in vpc['CidrBlockAssociationSet']:
                ava = int(j['CidrBlock'][-2:])
                final = (2**(32 - ava))
                private.append(final)
            totalIPadd = sum(i for i in private) #Sums all the IP addresses in the CIDRs associated to each VPC. The values are gotten from the private list.
    
   
        totalIP.append(int(totalIPadd)) #Finally append 70% of the values gotten in totatIPadd to a list called totalIP
    reserved_difference = [x1 - x2 for (x1, x2) in zip(totalIP, len_of_subnet)]
    final_difference = [int(0.7 * i) for i in reserved_difference]


    vpcs_totalIP = dict(zip(list_of_vpc, final_difference)) #Created a dictionary using vpc_list as the key and totalIP list as the values.
#print vpcs_totalIP




    
#This section calculates the current list of IP address in use for each vpc
    len_of_usedIP = [] #Created a list that shows the current number of used IP addresses in each VPC.
    for eachvpc in list_of_vpc:
        eni = vpc_client.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [eachvpc]}])

        IP_in_use =  [] #Creates a list that appends all the current IP addresses that are assosicated with network interfaces.
        
        for i in eni['NetworkInterfaces']:
            IP_in_use.append(i['PrivateIpAddress'])
       
        len_of_usedIP.append(len(IP_in_use)) 
    vpcs_usedIP = dict(zip(list_of_vpc, len_of_usedIP)) #Create a dictionary containing VPCs and the current number of IP address in use.
#print vpcs_usedIP




#To get the remaining available IP address in each VPC, subtract current IP usage from available IP usage. If we get a negative value, it means more than 70% of the IPs in that VPC is currently  used
    difference =  [x1 - x2 for (x1, x2) in zip(vpcs_totalIP.values(), vpcs_usedIP.values())] #Subtract both values in dictionary and if you get a negative value, it means the user has exceeded 70% usage in one of the VPCs
#print difference
    for i in range(len(difference)):
        if difference[i] < 0:
            vpc_message = "The current number of IP addresses in use for " + vpcs_totalIP.keys()[i] + " in " + x + " region has passed 70% of the available IP address space for this VPC. Please plan to scale the VPC.\n\nFor more information on scaling the VPC, please visit this link: https://aws.amazon.com/about-aws/whats-new/2017/08/amazon-virtual-private-cloud-vpc-now-allows-customers-to-expand-their-existing-vpcs/ ."
            sns.publish(TopicArn = topicArn, Message = vpc_message, Subject = 'VPC IP Address Space Limit')
            print vpc_message, "\n"



##CODE FOR CHECKING IP ADDRESS USAGE IN SUBNETS
    check_subnet = vpc_client.describe_subnets()

    for i in check_subnet["Subnets"]:
        subnet_cidr = int(i['CidrBlock'][-2:])
        subnet_total_IP = (2**(32 - subnet_cidr)) - 5
        subnet_benchmark = (int(subnet_total_IP * 0.30))

        if i["AvailableIpAddressCount"] < subnet_benchmark:
            subnet_message = "The current number of IP addresses in use for " + i["SubnetId"] + " in " + i["VpcId"] + " for " + x + " region has passed 70% of the available IP address space. You have " + str(i["AvailableIpAddressCount"]) + " IP addresses left in this subnet. Please delete unused elastic network interfaces (ENIs) to free up IP addresses in the subnet or create a new subnet in the VPC.\n\nFor more information, please visit this link: https://docs.aws.amazon.com/vpc/latest/userguide/working-with-vpcs.html#AddaSubnet ."
            sns.publish(TopicArn = topicArn, Message = subnet_message, Subject = 'Subnet IP Address Space Limit')
            print subnet_message, "\n"



##CODE FOR ELASTIC IP ADDRESS USAGE IN VPC
    elastic_IP = vpc_client.describe_addresses()
    for i in elastic_IP['Addresses']:
        if "AssociationId" not in i:
            elastic_message = "The Elastic IP address " + i['PublicIp'] + " in " + x + " region is not in use. Please associate it with an instance or network interface to save cost. Elastic IPs are totally free, as long as they are being used by an instance. "
            sns.publish(TopicArn = topicArn, Message = elastic_message, Subject='Elastic IP Address not in use')
            print elastic_message, "\n"



##CODE FOR CHECKING VALID ROUTE TABLE ENTRIES IN THE VPC       
    route_table = vpc_client.describe_route_tables()
    for i in route_table["RouteTables"]:
        for j in i["Routes"]:
            if "blackhole" == j["State"]:
                route_message = "The route " + j["DestinationCidrBlock"] + " in " + x + " region is in a blackhole state. Please review the configurations on route table " + i["Associations"][0]["RouteTableId"] + " and ensure the route target is active. The blackhole state indicates that the route's target isn't available (for example, the specified gateway isn't attached to the VPC, the specified NAT instance has been terminated, and so on)."
                sns.publish(TopicArn = topicArn, Message = route_message, Subject='Invalid Route Table Entry')
                print route_message, "\n"

region("eu-west-1")
region("us-east-1")
region("us-west-2")
region("us-west-1")
region("ap-southeast-1")
region("ap-southeast-2")
region("ca-central-1")
region("ap-northeast-1")
region("ap-northeast-2")
region("sa-east-1")
region("eu-central-1")
region("us-east-2")
region("ap-south-1")
region("eu-west-3")
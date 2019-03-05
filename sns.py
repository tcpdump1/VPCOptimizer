import json
import boto3

sns = boto3.client('sns')
create_sns = sns.create_topic(Name='testSNS')

subscribe = sns.subscribe(
    TopicArn='', # Fill in the ARN for the topic
    Protocol='Email',
    Endpoint='') #Fill in the email address that receives the email.


number_of_subnet = []
len_of_subnet = []
for eachvpc in sorted(vpc_list):
    for me in vpc_client.describe_subnets(Filters=[{'Name': 'vpc-id','Values': [eachvpc]}])['Subnets']:
        number_of_subnet.append(me["SubnetId"])
    len_of_subnet.append(len(number_of_subnet) * 5)
    
    
    
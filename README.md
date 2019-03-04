# VPCOptimizer

SUMMARY
The function of this template is to inform the account holder about the following: 

70% of IP address in a VPC or subnet is used up so the user can plan accordingly.
There are unused Elastic IP address in an account (save some cost for AWS users).
Blackhole routes in a route table (save some time troubleshooting basic issues).

The Cloudformation template consist of SNS, Lambda and Cloudwatch event. The template will request for an email address from the user for the purpose of sending notifications when there is a breach. After deploying the template, two Lambda functions are created namely: VPCSetupOptimizer1 and VPCSetupOptimizer2. The function is written in Python using Boto3 SDK, making use of methods within the EC2 and SNS class.


The first function sends notification when 70% of the available IP address space in the VPC is used up. The second function sends notification when the account holder has unused Elastic IP addresses, when routes are black-holed in any subnet of the VPC and finally, when 70% of the available IP address space in any subnet is used up.



HOW TO USE

1) Very simple, launch the template and fill in the desired stack name and email address you wish to receive notifications on.
                                   
2) After launching the template, you will receive an email from AWS Notifications (SNS) requesting the user to confirm the SNS subscription.
 
Very Important: You must subscribe to the SNS Topic by clicking on the Confirm Subscription Link. If you do not complete this step, you will not receive any notifications.

3) Both Lambda functions are triggered by Cloudwatch events scheduled to run every hour, so you need to be patient :)

The first function (VPCSetupOptimizer1) checks each VPC in that region and performs a calculation to determine if 70% of the available address space is exhausted. If there is, an email notification is sent to inform the user to add more CIDR blocks. Please note that available address space does not include the five reserved IP addresses in each subnet, as this is already excluded from assignment in the code.

Lets talk a bit about the second Lambda function. It is common knowledge that customers pay for Elastic IP addresses that are not assigned to any network interface. To help our customers save cost, the second function (VPCSetupOptimizer2) sends notifications via email when there is an Elastic IP address that is not associated with any network interface. Another common setup error is when a route points to a non-working target (NAT Gateway, NAT Instance, etc).

To fix this, whenever the second function is triggered, if it discovers that a route is pointing to an invalid target, it will send a notification to the user stating the particular route and route table. Lastly, the second function also checks all subnets in the VPC for available IP space, very similar to the first function, only in this case, it is done per subnet.

4) Logs: Lambda will also publish all sent email notifications to Cloudwatch Logs. To see this, after deploying the stack, click on Cloudwatch Logs and check for "VPCSetupOptimizer1" and "VPCSetupOptimizer2" Logs. VPCSetupOptimizer1 Logs will contain VPC Limit Logs and VPCSetupOptimizer1 Logs will contain Elastic IP, blackhole routes and subnet logs.


5) Please note the names of the following resources that will be created by the Cloudformation stack for easy identification:

Lambda function and Cloudwatch Logs - VPCSetupOptimizer1
Lambda function and Cloudwatch Logs - VPCSetupOptimizer2
SNSTopic and Cloudwatch Events - Stack Name.

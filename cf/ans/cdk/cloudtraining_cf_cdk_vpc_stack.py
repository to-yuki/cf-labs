from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,

)
from constructs import Construct

class CloudtrainingCfCdkVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Create VPC
        vpc = ec2.Vpc(
            self,
            id="cloudtrainingXX-cdk-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"), # NatGateway
            max_azs=2, 
            nat_gateways=1, # NatGateway作成(0:なし1:あり)
            # Create Private Subnet
            subnet_configuration=[     # Subネットの構成(Public2個)
                ec2.SubnetConfiguration(
                    name="cloudtrainingXX-public-subnet", # PublicSubネットに追記される名前
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="cloudtrainingXX-private-subnet", # PrivateSubネットに追記される名前
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        
        )
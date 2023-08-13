from aws_cdk import (
    # Duration,
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

class CloudtrainingCfCdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # IDから既存のVPCを取得する
        vpc=ec2.Vpc.from_lookup(self, 'vpcId', vpc_id='vpc-0224e307f6d42855d')
        
        # Create SecurityGroup
        security_group = ec2.SecurityGroup(
            self,
            id="cloudtrainingXX-cdk-ec2-sg",     # セキュリティグループID
            vpc=vpc,
            allow_all_outbound=True,   # 外部接続の許可
            security_group_name="cloudtrainingXX-cdk-ec2-sg"   # セキュリティグループ名
        )
        # Add Ingress Rule
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),   # アクセス可能IP
            connection=ec2.Port.tcp(22),    # 22番ポートの許可
            description="allow ssh access"
        )
        
        # Instance Role and SSM Managed Policy 
        role = iam.Role(self, "InstanceSSM",assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        # Set the AMI from Amazon Linux2 
        machine_image=ec2.MachineImage.generic_linux({"ap-northeast-3": "ami-0dcd015c93067a97b"})
        
        ec2_instance = ec2.Instance(
            self,
            id="cloudtrainingXX-cdk-ec2-instance", # EC2のインスタンスID
            role=role,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2,       # EC2のインスタンスタイプ
                ec2.InstanceSize.MICRO            # EC2のインスタンスタイプのサイズ
            ),
            machine_image=machine_image, # Amazon Linux最新.Ver
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS  # EC2のサブネット指定
            ),
            instance_name="cloudtrainingXX-cdk-ec2-instance",       # EC2の名前指定
            security_group=security_group,            # セキュリティグループ指定
            key_name= "cdk-app"                     # SSHキーペア名指定
        )
        
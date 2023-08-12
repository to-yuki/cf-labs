from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_elasticloadbalancingv2 as elb,
    aws_elasticloadbalancingv2_targets as tg,
    
)

from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(
            self,
            id="cdk-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.1.0.0/16"), # NatGateway
            max_azs=2, 
            nat_gateways=1, # NatGateway作成(0:なし1:あり)
            # Create Private Subnet
            subnet_configuration=[     # Subネットの構成(Public2個)
                ec2.SubnetConfiguration(
                    name="public-subnet", # PublicSubネットに追記される名前
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet", # PrivateSubネットに追記される名前
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        
        )
         # Create SecurityGroup
        security_group = ec2.SecurityGroup(
            self,
            id="cdk-ec2-sg",     # セキュリティグループID
            vpc=vpc,
            allow_all_outbound=True,   # 外部接続の許可
            security_group_name="cdk-ec2-sg"   # セキュリティグループ名
        )
        # Add Ingress Rule
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.1.0.0/16"),   # アクセス可能IP
            connection=ec2.Port.tcp(22),    # 22番ポートの許可
            description="allow ssh access"
        )
        
        # Instance Role and SSM Managed Policy 
        role = iam.Role(self, "InstanceSSM",assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        # Set the AMI from EC2 after installed WordPress
        machine_image=ec2.MachineImage.generic_linux({"ap-northeast-3": "ami-036ee1d5a942dd19e"})
        
         # Create EC2
        ec2_instance1 = ec2.Instance(
            self,
            id="cdk-ec2-instanceA", # EC2のインスタンスID
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
            instance_name="cdk-ec2-instanceA",       # EC2の名前指定
            security_group=security_group,            # セキュリティグループ指定
            key_name= "cdk-app"                     # SSHキーペア名指定
        )
        
        # Create EC2
        ec2_instance2 = ec2.Instance(
            self,
            id="cdk-ec2-instanceB", # EC2のインスタンスID
            role=role,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, # EC2のインスタンスタイプ
                ec2.InstanceSize.MICRO            # EC2のインスタンスタイプのサイズ
            ),
            machine_image=machine_image, # Amazon Linux最新.Ver
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS  # EC2のサブネット指定
            ),
            instance_name="cdk-ec2-instanceB",       # EC2の名前指定
            security_group=security_group,          # セキュリティグループ指定
            key_name= "cdk-app"                     # SSHキーペア名指定
        )
        
        # RDS
        db_instance = rds.DatabaseInstance(self, 
            id="cdk-web-rds",          # RDSのid                  
            engine=rds.DatabaseInstanceEngine.mysql   # データベースタイプ
            (version=rds.MysqlEngineVersion.VER_8_0_28),
            vpc=vpc,
            database_name="wordpress",  # 初期データベース名
            instance_identifier="cdk-web-wordpress", # RDSインスタンスID,
            instance_type = ec2.InstanceType.of(
                                    instance_class=ec2.InstanceClass.T3, 
                                    instance_size=ec2.InstanceSize.MICRO)
        )
        
        # RDSとEC2の接続を許可
        db_instance.connections.allow_from(ec2_instance1, ec2.Port.tcp(3306))
        db_instance.connections.allow_from(ec2_instance2, ec2.Port.tcp(3306))
        
        # ALB
        alb = elb.ApplicationLoadBalancer(self, 
            id="cdk-alb", # ALBID
            vpc=vpc, # ALBとVPCの関連付け
            internet_facing=True,
        )
        
        listener = alb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80,
            stickiness_cookie_duration=Duration.minutes(5), 
            # ターゲットサーバとの関連付け          
            targets=[tg.InstanceIdTarget(instance_id=ec2_instance1.instance_id),  
                     tg.InstanceIdTarget(instance_id=ec2_instance2.instance_id)
                    ],
            health_check=elb.HealthCheck(
                path="/",
            )
        )
        # EC2へのALBをアクセス許可
        ec2_instance1.connections.allow_from(alb, ec2.Port.tcp(80))
        ec2_instance2.connections.allow_from(alb, ec2.Port.tcp(80))


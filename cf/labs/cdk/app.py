#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudtraining_cf_cdk_vpc.cloudtraining_cf_cdk_vpc_stack import CloudtrainingCfCdkVpcStack


app = cdk.App()
CloudtrainingCfCdkVpcStack(app, "CloudtrainingCfCdkVpcStack",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    env=cdk.Environment(account='909651355779', region='ap-northeast-3'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()

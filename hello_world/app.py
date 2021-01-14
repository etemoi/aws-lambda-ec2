import json
import boto3

from uuid import uuid4


def start_instance(ami_image_id, instance_type, security_group):
    ec2 = boto3.resource('ec2')

    outfile = open('/tmp/ec2-keypair.pem','w')
    keypair_name = f'ec2-keypair-{str(uuid4())}'
    key_pair = ec2.create_key_pair(KeyName=keypair_name)
    KeyPairOut = str(key_pair.key_material)
    print(KeyPairOut)
    outfile.write(KeyPairOut)

    instances = ec2.create_instances(
        ImageId=ami_image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        KeyName=keypair_name,
        SecurityGroupIds=security_group,
        InstanceInitiatedShutdownBehavior='terminate')

    instance = instances[0]

    return {
        'keypairName': keypair_name,
        'id': instance.id,
        'privateIp': instance.private_ip_address,
        'publicIP': instance.public_ip_address,
    }


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    qrp = event['queryStringParameters'] or {}
    ami_image_id = qrp.get('AMIImageId', 'ami-0be2609ba883822ec')
    ec2_type = qrp.get('EC2Type', 't2.micro')
    security_group = qrp.get('SecurityGroups', 'ec2_simple_security_group')

    response = start_instance(ami_image_id, ec2_type, [security_group])
    print(response)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": response,
        }),
    }

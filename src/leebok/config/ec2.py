import boto3


class EC2(object):
    def __init__(self, region):
        self._client = boto3.client('ec2', region_name=region)

    def find_vpc_id(self):
        vpcs = self._find_vpcs()
        return vpcs[0]['VpcId'] if vpcs else None

    def find_subnet_id(self, vpc_id):
        subnets = self._find_subnets(vpc_id)
        subnets = sorted(subnets, key=lambda s: s['AvailabilityZone'])
        return subnets[0]['SubnetId'] if subnets else None

    def _find_vpcs(self):
        return self._client.describe_vpcs(
            Filters=[{'Name': 'state', 'Values': ['available']}],
            MaxResults=5
        )['Vpcs']

    def _find_subnets(self, vpc_id):
        return self._client.describe_subnets(
            Filters=[
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ],
            MaxResults=5
        )['Subnets']

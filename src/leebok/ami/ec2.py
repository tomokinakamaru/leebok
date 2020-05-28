import boto3


class EC2(object):
    def __init__(self, region):
        self._client = boto3.client('ec2', region_name=region)

    def exists(self, name):
        return self.find(name) is not None

    def find(self, name):
        return self._find(name).get('ImageId', None)

    def delete(self, name):
        image = self._find(name)
        self._client.deregister_image(ImageId=image['ImageId'])
        for snapshot in image.get('BlockDeviceMappings', []):
            if 'Ebs' in snapshot:
                id = snapshot['Ebs']['SnapshotId']
                self._client.delete_snapshot(SnapshotId=id)

    def _find(self, name):
        images = self._client.describe_images(
            Filters=[{'Name': 'name', 'Values': [name]}],
            Owners=['self']
        )['Images']
        return images[0] if images else {}

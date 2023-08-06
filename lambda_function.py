import json
import boto3
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    result = {
        "unattached_disk": {
            "Count": 0,
            "Info": [],
            "TotalSize": 0
        },
        "non_encrypted_disk": {
            "Count": 0,
            "Info": [],
            "TotalSize": 0
        },
        "non_encrypted_snapshots": {
            "Count": 0,
            "Info": [],
            "TotalSize": 0
        }
    }
    for volume in ec2_client.describe_volumes()["Volumes"]:
        if (len(volume['Attachments']) == 0 ):
            result["unattached_disk"]["Info"].append({"Id": volume['VolumeId'], "Size": volume['Size']})
            result["unattached_disk"]["Count"] = result["unattached_disk"]["Count"] + 1
            result["unattached_disk"]["TotalSize"] = result["unattached_disk"]["TotalSize"] + volume['Size']
        if (volume["Encrypted"] != True ):
            result["non_encrypted_disk"]["Info"].append({"Id": volume['VolumeId'], "Size": volume['Size']})
            result["non_encrypted_disk"]["Count"] = result["non_encrypted_disk"]["Count"] + 1
            result["non_encrypted_disk"]["TotalSize"] = result["non_encrypted_disk"]["TotalSize"] + volume['Size']

    for snapshot in ec2_client.describe_snapshots(OwnerIds=['self'])["Snapshots"]:
        if (snapshot["Encrypted"] == False ):
            result["non_encrypted_snapshots"]["Info"].append({"Id": snapshot['SnapshotId'], "Size": snapshot['VolumeSize']})
            result["non_encrypted_snapshots"]["Count"] = result["non_encrypted_snapshots"]["Count"] + 1
            result["non_encrypted_snapshots"]["TotalSize"] = result["non_encrypted_snapshots"]["TotalSize"] + snapshot['VolumeSize']     
    print("Unattached disk count: " + str(result["unattached_disk"]["Count"]) + " \n Size " + str(result["unattached_disk"]["TotalSize"]))
    print("Non encrypted disk count: " + str(result["non_encrypted_disk"]["Count"]) + " \n Size " + str(result["non_encrypted_disk"]["TotalSize"]))
    print("Non encrypted snapshots count: " + str(result["non_encrypted_snapshots"]["Count"]) + " \n Tatal size: " + str(result["non_encrypted_snapshots"]["TotalSize"]))
    s3_client.put_object(
    Bucket='uc6-backup', 
    Key='result.json',
    Body=json.dumps(result, indent=2, default=str)
)
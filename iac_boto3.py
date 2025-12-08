import boto3 
import time
import yaml,json

aws_credentials_filename    = "aws_credentials"

#### TO MODIFY ####
role_name_arn               = "arn:aws:iam::381492117045:role/LabRole"



## EX1 VPC
#template_filename           = "templates/vpc.yaml"
#stack_name                  = "polystudent-stack-vpc"
#environment_vars            = {
#        "EnvironmentName": "polystudent-vpc"
#        }

## EX2 S3 bucket
#template_filename           = "templates/s3.json"
#stack_name                  = "polystudent-stack-s3-bucket"
#environment_vars            = {
#        }

# EX3.1 VPC Flow Logs
template_filename           = "./templates/ec2.yaml"
stack_name                  = "polystudent-stack-ec2"
environment_vars            = {
        "EnvironmentName": "polystudent-ec2",
        "S3ARN": "arn:aws:s3:::polystudents3-20251126 ",
        "VPCID": "vpc-0fe82f6dd091740ad"
        }

# EX3.2 EC2 + Cloud_watch bucket
template_filename           = "./templates/ec2.yaml"
stack_name                  = "polystudent-stack-ec2"
environment_vars            = {
        "EnvironmentName": "polystudent-ec2",
        "SubnetId": "subnet-03ec933d3a467803d"
        }

##################


def check_status_stack(client,stack_name): 
    try : 
        rep = client.describe_stacks(StackName=stack_name)
    except client.exceptions.ClientError as e :
        # stack not found 
        if e.response['Error']['Code'] == 'ValidationError':
            print(f"Stack '{stack_name}' does not exist.")
            return None
        else:
            print(f"An unexpected error occurred: {e}")
            raise  # Re-raise unexpected errors
    return rep["Stacks"][0]["StackStatus"]

def list_resources(client,stack_name):
    try : 
        rep = client.list_stack_resources(StackName=stack_name)["StackResourceSummaries"]
    except client.exceptions.ClientError as e :
        # stack not found 
        if e.response['Error']['Code'] == 'ValidationError':
            print(f"Stack '{stack_name}' does not exist.")
            return None
        else:
            print(f"An unexpected error occurred: {e}")
            raise  # Re-raise unexpected errors
    for r in rep:
        print(f"\t[{r['ResourceType']}] \t{r['LogicalResourceId']} - \t{r['ResourceStatus']}")

def delete_stack_if_exists(client, stack_name):
    try:
        # Check if the stack exists
        client.describe_stacks(StackName=stack_name)
        print(f"Stack {stack_name} already exists. Deleting...")

        # Delete the stack
        client.delete_stack(StackName=stack_name)

        # Wait for the stack to be deleted
        waiter = client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)
        print(f"Stack {stack_name} deleted successfully.")
    except client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Stack {stack_name} does not exist. Proceeding to create.")
        else:
            print(f"Error checking stack: {e}")
            raise

def create_stack(client,stack_name,environment_vars,template_body,role_name_arn):
    print("Stack name : ",stack_name)
    print("Environment vars : ")
    for k,v in environment_vars.items():
        print(f"\t {k}:{v}")
    print("Role ARN name : ",role_name_arn)
    try :
        response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': k,
                        'ParameterValue': v,
                        'UsePreviousValue': False,
                        } for k,v in environment_vars.items() 
                    ],
                RoleARN = role_name_arn,
                OnFailure='DELETE'
                )
        print("Wait for stack creation")
        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name)
        print("Stack creation done")
    except client.exceptions.ClientError as e:
        print(f"Error creating stack: {e}")
        raise
    print(response)


def get_credentials(filename):
    # Get AWS FROM secret file aside
    # avoid to store creds in code
    with open(filename, 'r') as file:
        lines = file.readlines()

    credentials = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('[') and '=' in line:
            key, value = line.split('=', 1)
            credentials[key] = value
    return credentials

def get_template(filename):
    with open(filename, 'r') as file:
        template_body = file.read()
    return template_body 


# Step 1 : get creds
print("[STEP 1] Credentials collection")
credentials=get_credentials(aws_credentials_filename)
print("[STEP 1] Done")

# Step 2 : Connect to aws account 
print("[STEP 2] Connection to aws account cloudformation")
cf = boto3.client(
        "cloudformation",
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key'],
        aws_session_token=credentials['aws_session_token']
                    )
print("[STEP 2] Done")

# Step 3 : Get template from local file
print("[STEP 3] Collection template in local file")
print("[STEP 3] Template filename : ",template_filename)
template_body = get_template(template_filename)
#print("[STEP 3] Template body :\n",template_body)
print("[STEP 3] Done")

# Step 4 : Delete stack one already exists
print("[STEP 4] Delete the stack if this one already exists")
delete_stack_if_exists(cf,stack_name)
print("[STEP 4] Done")

# Step 4 : Delete stack one already exists
print("[STEP 5] Create the stack")
create_stack(cf,stack_name,environment_vars,template_body,role_name_arn)
print("[STEP 5] Done")

# Step 6 : List Stack ressources
print("[STEP 6] Stack ressources : ")
list_resources(cf,stack_name)
print("[STEP 6] Done")



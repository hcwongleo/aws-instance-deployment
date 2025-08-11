import boto3
import json
from datetime import datetime, timezone

def lambda_handler(event, context):
    print(f"=== AUTO-TERMINATION LAMBDA STARTED ===")
    print(f"Event: {json.dumps(event, default=str)}")
    print(f"Context: {context}")
    print(f"Function name: {context.function_name}")
    print(f"Request ID: {context.aws_request_id}")
    
    ec2 = boto3.client('ec2')
    current_datetime = datetime.now(timezone.utc)
    print(f"Current UTC datetime: {current_datetime}")
    
    # Get instances with AutoTerminate tag
    print("Searching for instances with AutoTerminate=true tag...")
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:AutoTerminate', 'Values': ['true']},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        )
        print(f"Found {len(response['Reservations'])} reservations")
    except Exception as e:
        print(f"ERROR: Failed to describe instances: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}
    
    instances_to_terminate = []
    all_instances_found = []
    
    for reservation in response['Reservations']:
        print(f"Processing reservation: {reservation['ReservationId']}")
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            instance_type = instance.get('InstanceType', 'unknown')
            launch_time = instance.get('LaunchTime', 'unknown')
            all_instances_found.append(instance_id)
            
            print(f"  Instance {instance_id} (type: {instance_type}, state: {instance_state}, launched: {launch_time})")
            
            # Print all tags for debugging
            tags = instance.get('Tags', [])
            print(f"    All tags ({len(tags)} total):")
            for tag in tags:
                print(f"      {tag['Key']}: {tag['Value']}")
            
            # Check for AutoTerminate tag specifically
            auto_terminate_found = False
            for tag in tags:
                if tag['Key'] == 'AutoTerminate':
                    auto_terminate_found = True
                    print(f"    ✓ AutoTerminate tag found: {tag['Value']}")
                    break
            
            if not auto_terminate_found:
                print(f"    WARNING: AutoTerminate tag not found for instance {instance_id}")
            
            # Check termination datetime tag
            termination_datetime = None
            termination_datetime_str = None
            
            for tag in tags:
                if tag['Key'] == 'TerminationDateTime':
                    termination_datetime_str = tag['Value']
                    print(f"    ✓ Found TerminationDateTime tag: '{termination_datetime_str}'")
                    try:
                        termination_datetime = datetime.strptime(termination_datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                        print(f"    ✓ Parsed termination datetime: {termination_datetime}")
                    except ValueError as e:
                        print(f"    ERROR: Failed to parse datetime '{termination_datetime_str}': {str(e)}")
                        print(f"    Expected format: YYYY-MM-DD HH:MM:SS")
                        continue
                    break
            
            if not termination_datetime_str:
                print(f"    WARNING: No TerminationDateTime tag found for instance {instance_id}")
                continue
            
            if not termination_datetime:
                print(f"    WARNING: Could not parse TerminationDateTime for instance {instance_id}")
                continue
            
            # Compare times
            print(f"    Time comparison:")
            print(f"      Current time:     {current_datetime}")
            print(f"      Termination time: {termination_datetime}")
            
            time_diff = (termination_datetime - current_datetime).total_seconds()
            hours_diff = time_diff / 3600
            
            print(f"      Time difference: {time_diff:.0f} seconds ({hours_diff:.2f} hours)")
            
            if current_datetime >= termination_datetime:
                instances_to_terminate.append(instance_id)
                print(f"    ✓ TERMINATION REQUIRED: Instance {instance_id} expired {-hours_diff:.2f} hours ago")
            else:
                print(f"    ✗ NOT READY: Instance {instance_id} expires in {hours_diff:.2f} hours")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total reservations found: {len(response['Reservations'])}")
    print(f"Total instances found: {len(all_instances_found)}")
    print(f"Instances to terminate: {len(instances_to_terminate)}")
    print(f"Instance IDs found: {all_instances_found}")
    print(f"Instance IDs to terminate: {instances_to_terminate}")
    
    # Terminate instances
    if instances_to_terminate:
        try:
            print(f"\nAttempting to terminate {len(instances_to_terminate)} instances...")
            for instance_id in instances_to_terminate:
                print(f"  Terminating: {instance_id}")
            
            terminate_response = ec2.terminate_instances(InstanceIds=instances_to_terminate)
            print(f"Termination API response: {json.dumps(terminate_response, default=str)}")
            
            # Check termination status
            terminating_instances = terminate_response.get('TerminatingInstances', [])
            for term_instance in terminating_instances:
                instance_id = term_instance['InstanceId']
                current_state = term_instance['CurrentState']['Name']
                previous_state = term_instance['PreviousState']['Name']
                print(f"  ✓ {instance_id}: {previous_state} → {current_state}")
            
            print(f"✓ Successfully initiated termination for {len(instances_to_terminate)} instances")
            
        except Exception as e:
            print(f"ERROR: Failed to terminate instances: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return {
                'statusCode': 500, 
                'body': json.dumps({
                    'error': str(e),
                    'instances_found': all_instances_found,
                    'instances_to_terminate': instances_to_terminate
                })
            }
    else:
        print("No instances require termination at this time")
    
    result = {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {len(instances_to_terminate)} instances for termination',
            'instances_found': all_instances_found,
            'instances_terminated': instances_to_terminate,
            'current_time': str(current_datetime),
            'total_reservations': len(response['Reservations']),
            'total_instances': len(all_instances_found)
        })
    }
    
    print(f"\n=== AUTO-TERMINATION LAMBDA COMPLETED ===")
    print(f"Final result: {json.dumps(result, indent=2)}")
    return result

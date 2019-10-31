# step 0: ** preparation **
set up the cloudformation(Preparation.yaml) stack in the us-east-1(or any region with IoT and Cloud9, should be fine although I haven't done the fully testing)

CFN will take about 40 mins to build it(the majority of time is to build a cloudfront distruction so that your s3 isn’t public facing)
provide a unique s3 bucket
a unique cognito domain name - https://[a-unique-domain].auth.us-east-1.amazoncognito.com, eg the parameter is ‘iotworkshoprafaxu’ for me
if your default VPC in us-east-1 has any private subnet(it is very likely if you tested the NAT gateway function for Lambda), you need to specify the public subnet id in line 22


# step 1: ** basic pub and sub **
- attach the role() to the cloud 9 ec2 instance
- login to the cloud9 terminal:
- clone the repository:
  git clone
- prepare the environment:
sudo pip install AWSIoTPythonSDK
- **authentication** download the certificate, private key  by command: and download the CA certificate by command:
   aws iot create-keys-and-certificate --set-as-active --certificate-pem-outfile ./cert.pem --private-key-outfile ./key.pem --region us-east-1
   wget https://www.amazontrust.com/repository/AmazonRootCA1.pem -O rootca.pem
- find your endpoint: from IoT console - eg a2a4ziueyywvoe-ats.iot.us-east-1.amazonaws.com
- **authorization** attach the full IoT policy to the certificate
- attendees need to understand the authentication and authorization
testing:
curl --tlsv1.2 --cacert rootca.pem --cert cert.pem --key key.pem -X POST -d "{ \"message\": \"Hello, world\" }" "https://a2a4ziueyywvoe-ats.iot.us-east-1.amazonaws.com:8443/topics/my/topic"
subscribe to my/topic in the console to see if you can find the message

- copy the iot-pub into your directory
cp ../awsiotcoreworkshop/iot-pub.py ./iot-main.py
- make it executable
chmod a+x ./iot-main.py
- make a status.txt file to simulate the door status(make sure you understand it)
echo 0 > status.txt
- start the iot-main.py from terminal
- consistently change the status.txt content to simulate the door status change
#while true; do sleep 5; echo 0 > status.txt; sleep 5; echo 1 > status.txt; done

# step 2 **iot job**
- copy the iot-job.py from the repository to the current directory
cp -rp awsiotcoreworkshop/iot-job.py door/
- prepare the job artifacts:
aws s3 cp ../awsiotcoreworkshop/iot-dummy.py s3://[yourbucket]
cp awsiotcoreworkshop/iot-dummy.json door/
change the cloudfront to your cloudfront
- create a thing - Door
- attach the certificate to the thing
- detache the full iot policy and attach the
- start the ./iot-job.py
- create a job:
aws iot create-job     --job-id $(uuidgen)     --targets "arn:aws:iot:us-east-1:620428855768:thing/Door" --document file://iot-dummy.json
- check if the iot-main.py file is updated

# step 3 **iot shadow - reported**
- copy the iot-shadow.py to s3
aws s3 cp ./iot-shadow.py s3://iotworkshoprafa
- update the iot-shadow.json file to point to the correct source file.
- attach the certificate with the policy(IoTWorkshop-job-policy)
aws iot create-job     --job-id $(uuidgen)     --targets "arn:aws:iot:us-east-1:620428855768:thing/Door" --document file://iot-shadow.json
- copy the js, css and html file to the s3
$ aws s3 cp ./amazon-cognito-auth.min.js  s3://iotworkshoprafa
$ aws s3 cp ./bundle.js  s3://iotworkshoprafa                                    
$ aws s3 cp ./styleSheetStart.css s3://iotworkshoprafa

# step 4 **iot shadow - desired**
- update the lambda - IoTWorkshopSetStatus
- update the iot-control.html with the correct API GW endpoint
open the iot-control.html in the local laptop and change the door status - check the REST APIs/Lambda invocation
understand how it works.
- update the iot-main function by iot-job agent
aws s3 cp ./iot-final.py s3://iotworkshoprafa
- update the iot-final.json with correct url
aws iot create-job     --job-id $(uuidgen)     --targets "arn:aws:iot:us-east-1:620428855768:thing/Door" --document file://iot-final.json
check if you can control your device.

# step 5: iot-rule
create a rule:
SELECT topic(3) as thing, state.reported.status as status, timestamp FROM '$aws/things/+/shadow/update/accepted' where not isUndefined(state.reported)

direct rule:
SELECT topic(3) AS ThingName, state.reported.status as status, timestamp() as Timestamp FROM '$aws/things/+/shadow/update/accepted' WHERE not isUndefined(state.reported)
action ddbv2 to dynamodb
SELECT topic(3) AS ThingName, state.reported.status as status, timestamp() as Timestamp FROM '$aws/things/+/shadow/update/accepted' WHERE (not isUndefined(state.reported)) and (state.reported.status='1') and ('09:00:00' ) < ( parse_time('HH:mm:ss', timestamp(), 'Australia/Sydney' ) ) and ('13:00:00' ) > ( parse_time('HH:mm:ss', timestamp(), 'Australia/Sydney' ) )
action to sns

compare the difference between lambda and direct integrations

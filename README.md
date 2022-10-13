# About
support-rotation sends an SMS to a predefined phone number with the summary (i.e., title) of an event that is currently
active in local time (i.e., the first event calendar found that comprises the current time).

This SMS can be used to change the forwarding number of a smartphone with a preinstalled automation application.


# Usage
## Installation
Before deploying support-rotation, prepare the target phone by installing an automation application
(e.g., [MacroDroid](https://play.google.com/store/apps/details?id=com.arlosoft.macrodroid)) and setting up rules that 
change the call forwarding number according to the contents of received SMSs.

Modify the CloudFormation's template.yaml file at the root of the project's folder by changing the supportPhoneNumber 
and calendarUrl variables to the desired target.

supportPhoneNumber should be set to a valid [E.164](https://en.wikipedia.org/wiki/E.164) phone number
while calendarUrl should point to a freely accessible shared calendar in the [iCalendar](https://en.wikipedia.org/wiki/ICalendar) format.

Note that AWS accounts are by default in an [SMS sandbox](https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html),
hence in order to send SMSs to the target phone number, either the account must be moved out of the sandbox or the target 
number has to be added to the sandbox.

The rate of invocation of the lambda function is set using an expression rate set to 1 minute. It can be changed
following the rules specified [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html).

support-rotation uses global state to keep track of data across invocations. Global data is fast and free, but ephemeral
in nature, if the lambda's execution environment is destroyed, global data is lost. This may cause the same SMS to be
sent twice. To prevent this, you can schedule the lambda functions to be executed frequently, in order to keep it 'warm'
and to maintain the execution environment or modify the code adding a durable data store (e.g., store parameter, s3, rds,
dynamoDB or efs). This may increase costs, but will guarantee data persistence between invocations.

After setting up [credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) (access key ID/secret access key) for an AWS account with the required permissions (Lambda, SNS, EventBridge, CloudFormation)
deploy the application either using the SAM cli or opening the project with an IDE and using a supported plugin for deployment (e.g., IntelliJ with 
AWS toolkit)

The region of deployment should have support for sending SMS through SNS (e.g., eu-south-1).


## Calendar Setup

The icalendar has to be set to the same timezone as support-rotation (it is configurable using localTz in the 
CloudFormation's template.yaml).

support-rotation uses the summary (i.e., the title) of the events in the calendar to determine the SMS to be sent in
order to the change the forwarding number, e.g. the following excerpt of an icalendar

```
BEGIN:VEVENT
SUMMARY:EmployeeA
DTSTART;TZID=W. Europe Standard Time:20220629T000000
DTEND;TZID=W. Europe Standard Time:20220629T120000
CLASS:PUBLIC
PRIORITY:5
DTSTAMP:20220628T085233Z
TRANSP:OPAQUE
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
```

produces an SMS with the message 'EmployeeA' to be sent to the target phone number once, after the support-rotation's
lambda function is invoked once during the interval from 20220629T000000 to 20220629T120000.

Whole days and time intervals are both supported, but if events overlap, only the first event found will be taken
in consideration.


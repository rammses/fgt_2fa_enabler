# Helper for sms based 2 factor authentication on fortigates
Besides configuring;

- an ldap server
- a mail server for system
- an sms provider

To enable 2 factor with ldap on fortigates you need to ;


- create a group that identifies that the user is a 2fa user
- add mobile number to them
- go into cli and enable a custom servers
- add them to a group 
- enable 2 factor for that particular user

You need to do the second part every time you need a 2fa enabled user and it takes too much time.

This script gets user info from an AD group, 
- creates the ldap based user
- adds the user to the sslvpn group 
- appends the necessary config (mobile phone, sms server details)

all you need to run it every 5 min, 

@todo i need to add a config check so it won't add the same configuration every time.
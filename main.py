import json
import paramiko
import time

from ldap3 import Server, \
    Connection, \
    AUTO_BIND_NO_TLS, \
    SUBTREE


def get_ldap_group_members(group_name):
    parsed_output = []
    with Connection(Server('172.21.21.158'),
                    auto_bind=AUTO_BIND_NO_TLS,
                    read_only=True,
                    check_names=True,
                    user='test\\administrator', password='12qwasZX') as c:
        c.search(search_base='CN=' + group_name + ',OU=test1,DC=test,DC=local',
                 search_filter='(objectClass=group)',
                 search_scope='SUBTREE',
                 attributes=['member'])

    response_new = json.loads(c.response_to_json())
    members_of_group = response_new['entries'][0]['attributes']['member']
    for ad_user in members_of_group:
        parsed_output.append(ad_user.split(',')[0].strip('CN='))
    return parsed_output


def get_ldap_mobile_phone_detail(samaccount_name):
    with Connection(Server('172.21.21.158'),
                    auto_bind=AUTO_BIND_NO_TLS,
                    read_only=True,
                    check_names=True,
                    user='test\\administrator', password='12qwasZX') as c:
        c.search('OU=test1,DC=test,DC=local',
                 "(&(objectClass=person)(sAMAccountName=" + samaccount_name + "))",
                 SUBTREE,
                 attributes=['Mobile'])
        result = c.response_to_json()
        # print(result)
        items_of_user = json.loads(result)
        users_mobile_number = (items_of_user['entries'][0]['attributes']['mobile'])

    return users_mobile_number


# initiate connection to fw
IP = '172.21.21.158'
username = 'admin'
password = '12qwasZX'

client1 = paramiko.SSHClient()
client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client1.connect(IP, username=username, password=password)
configure = client1.invoke_shell()

# bir AD grubu içindeki userları al
users = get_ldap_group_members('2fa_members')

for user in users:
    try:
        mobile_number = (user, get_ldap_mobile_phone_detail(user))
        commands = ['config user local' + '\n',
                    'edit ' + user + '\n',
                    'set type ldap' + '\n',
                    'set two-factor sms' + '\n',
                    'set sms-server custom' + '\n',
                    'set sms-custom-server "sms.textapp.net"' + '\n',
                    'set sms-phone ' + str(mobile_number[1]) + '\n',
                    'set ldap-server "dc1"' + '\n',
                    'next' + '\n',
                    'end' + '\n'
                            'config user group' + '\n',
                    'edit "sslvpn_2fa"' + '\n',
                    'append member ' + str(user) + '\n',
                    'next' + '\n',
                    'end' + '\n',
                    ]
        for command in commands:
            print("sending :", command)
            configure.send(command)
            time.sleep(0.5)
            for item in str(configure.recv(65535)).split("\\r\\n"):
                print("output", item)
    except KeyError as k:
        print(user, " kullanıcısının Telefon numarası yok, eklemiyoruz !")

client1.close()

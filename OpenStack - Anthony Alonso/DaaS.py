import openstack
import base64
#add some color to my life
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#ip Guacamole
guacIP = "0.0.0.0"
mysqlIP = "0.0.0.0"
desktopIP = "0.0.0.0"

# Initialize and turn on debug logging
openstack.enable_logging(debug=0)

# Initialize connection
conn = openstack.connect(cloud='openstack')

def create_keypair(conn):
    keypair = conn.compute.find_keypair("cloudsys")

    if not keypair:
        print("Create Key Pair:")

        keypair = conn.compute.create_keypair(name="cloudsys")

        print(keypair)

        try:
            os.mkdir(SSH_DIR)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e

        with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
            f.write("%s" % keypair.private_key)

        os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)

    return keypair

def create_serverMySQL(conn, name, image):
    print("Create Server MySQL...")

    image = conn.compute.find_image(image)
    flavor = conn.compute.find_flavor("c1.small")
    network = conn.network.find_network("private")
    keypair = create_keypair(conn)
    security = conn.network.find_security_group("mysql_secu")
    script = "#cloud-config\nruncmd:\n\n  - \"sudo mysql guacamole_db -e \\\"UPDATE guacamole_connection_parameter SET parameter_value ='" + desktopIP + "' WHERE connection_id = 1 AND parameter_name = 'hostname';\\\"\""
    script = base64.b64encode(bytes(script, 'utf-8')).decode('utf-8')
    server = conn.compute.create_server(
        name=name, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name, user_data=script)
    server = conn.compute.wait_for_server(server)

    return server.addresses["private"][1]["addr"]
    
def create_serverDesktop(conn, name, image):
    print("Create Desktop...")
    image = conn.compute.find_image(image)
    flavor = conn.compute.find_flavor("c1.small")
    network = conn.network.find_network("private")
    keypair = create_keypair(conn)
    security = conn.network.find_security_group("SSH")

    server = conn.compute.create_server(
        name=name, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)
    server = conn.compute.wait_for_server(server)
    conn.compute.add_security_group_to_server(server, security)
    return server.addresses["private"][1]["addr"]


def create_serverGuacamole(conn, name, image):
    print("Create Server Guacamole...")

    image = conn.compute.find_image(image)
    flavor = conn.compute.find_flavor("c1.small")
    network = conn.network.find_network("private")
    keypair = create_keypair(conn)
    security = conn.network.find_security_group("guacamole_secu")
    ip = conn.network.find_available_ip()
    print(desktopIP+desktopIP)
    script = "#cloud-config\nwrite_files:\n\n  - content: |\n      # Hostname and Guacamole server port\n      guacd-hostname: localhost\n      guacd-port: 4822\n      # MySQL properties\n      mysql-hostname: " + mysqlIP + "\n      mysql-port: 3306\n      mysql-database: guacamole_db\n      mysql-username: guacamole_user\n      mysql-password: heia\n    owner: root:root\n    path: /etc/guacamole/guacamole.properties\n    permissions: '0644'"
    
    script = base64.b64encode(bytes(script, 'utf-8')).decode('utf-8')
    server = conn.compute.create_server(
        name=name, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name, user_data=script)
    server = conn.compute.wait_for_server(server)
    conn.compute.add_security_group_to_server(server, security)
    conn.compute.add_floating_ip_to_server(server, ip.floating_ip_address, fixed_address=None)
    return ip.floating_ip_address

  
# ============================= Banner ===============================
print("""\                                                                                
                                                                                
                                                                                
                                                            ..                  
                                   ..''','...             .:kkdl;.              
                           ....''';:ccccccccc::::;;,..   .cO00O00Od:.           
                        .':cccccccccccccccccccccccccc:.  :O0O00O00OOOc.         
                     ..,:cccccccccccccccccccccccccccc,  .x00OO00000Od,          
           .;do.  .,;:cccccccccccccccccccccccccccccc:.   ,d00OO0Oxc,.           
         .c0NO'  .:cccccccccccccccccccccccccccccccccc:;.  .:xkdc,.  .'.         
        ;0WNd.  .:cccccccccccccccccccccccccccccccccccccc,.  ..     .xNO;        
       ;XMMk.  'cccccccccccccccccccccccccccccccccccccccccc'  ..,,.  lWMX;       
       oWMMx.  'cccccccccccccccccccccccccccccccccccccccccc:,,:cc;.  lWMMo       
       oMMMX:   ':ccccccccccccccccccccccccccccccccccccccccccccc,.  '0MMWo       
       :NMMMXo.  .';:ccccccccccccccccccccccccccccccccccccccc:,.  .:0WMMNc       
       .xWMMMWKl'   ..';:cccccccccccccccccccccccccccccc:;,'.   .cONMMMMO.       
        cNMMMMMMNOl;.    ..'',,;::::ccccccccc:::;;,''...   .'cxKWMMMMMWl        
        ,0MMMMMMMMMWKkdc;'.       ............       ..,:okKNMMMMMMMMMK,        
         ,xXMMMMMMMMMMMMWNKOkdolc::;,,,,,,,,;;:clodxO0XWMMMMMMMMMMMMNk;         
           .ckXWMMMMMMMMMMMMMMMMMMMMWWWWWWWWWMMMMMMMMMMMMMMMMMMMWXOl'           
              .:okXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOd:.              
                  .;cdkKNWMMMMMMMMMMMMMMMMMMMMMMMMMMMMWX0kdc;.                  
            ''         ..,:loxkO0KXXNNNNNNNXXKK0Okxol:,..         ..            
            .oxc'.              ......''''......              .'co,             
             .cKN0dc,.                                    .,cd0Kx'              
               .dXWMWXOxoc;'..                    ..';coxOXWMNk;                
                 .lONMMMMMWNX0OkxdooollllllooddxkO0XWWMMMMWXd,                  
                    ,lkXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWN0d:.                    
                       .,cdk0XWMMMMMMMMMMMMMMMMMMWX0ko:'.                       
                            ..';:cloodddddddolcc;,..                            
                                                                                
                                                                                
""") 
# ============================= Ask info to user ===============================
print(f"{bcolors.BOLD}{bcolors.OKGREEN}Welcome to OpenStack Desktop as a Service python programm (by Anthony Alonso) ! {bcolors.ENDC}{bcolors.ENDC}")
print(f"{bcolors.OKCYAN}Before deploying... I need some information.{bcolors.ENDC}")
default = "Guacamole"
guacName = input("Name the Guacamole Apache server [default=Guacamole] : ")
if not guacName:
   guacName = default

default = "Guacamole_mysql"
mysqlName = input("Name the Guacamole database [default=Guacamole_mysql] : ")
if not mysqlName:
   mysqlName = default
   
default = "Desktop"
desktopName = input("Name your desktop [default=Desktop] : ")
if not desktopName:
   desktopName = default

# ============================= Launch Instances ===============================
desktopIP = create_serverDesktop(conn, desktopName, "Ubuntu Focal 20.04 (SWITCHengines)")
mysqlIP = create_serverMySQL(conn, mysqlName, "mysql")
guacIP = create_serverGuacamole(conn, guacName, "guacamole")
print(desktopIP + " " + mysqlIP + " " + guacIP)

# ============================= Access the plateform ===============================
print(f"\n\n\n{bcolors.BOLD}{bcolors.FAIL}You can access Guacamole plateform with this link : {bcolors.UNDERLINE}http://{guacIP}:8080/guacamole{bcolors.ENDC} {bcolors.ENDC}{bcolors.ENDC}")
print(f"User : {bcolors.BOLD}guacadmin{bcolors.ENDC}")
print(f"Password (shh) : {bcolors.BOLD}guacadmin{bcolors.ENDC}")
print("\nHave fun :D")















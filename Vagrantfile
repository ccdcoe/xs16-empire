$empire = <<SCRIPT
echo "Empire ..."
cd /vagrant/Empire-dev/setup/
echo -e "somekey\n" | ./install.sh
cd ..
echo -en "listeners\nlist\nexit\ny\n" > cmd.txt
./empire < cmd.txt
date >> /etc/vagrant_provisioned_at
SCRIPT

$hopper = <<SCRIPT
echo "hopper .."
apt-get install nginx php5-fpm
cp /vagrant/hopper/chat.php /usr/share/nginx/html/chat.php
cp /vagrant/hopper/upload.php /usr/share/nginx/html/upload.php
mkdir -p /var/www/chat
chown www-data:www-data /var/www/chat
date >> /etc/vagrant_provisioned_at
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
  end

end

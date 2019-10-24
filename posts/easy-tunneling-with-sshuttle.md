title: Easy Tunneling with sshuttle
date: 2019-10-24

Sshuttle is a genius program that allows you to tunnel all of your traffic through SSH. As a result, it can act as a VPN for any machine you can SSH to. You don't even need to be an admin of the distant server to achieve this. How amazing is that?

Here's what we want to achieve through SSH tunneling:

- easily redirect all traffic through the SSH tunnel, DNS and all UDP traffic included
- automate even more the process with some scripting

Here's what we want to __avoid__ by using sshuttle:

- wasting hours configuring things on the server acting as a proxy
- creating a new connection through nmcli rather than being tunneled automatically
- messing things up by misconfiguring something, OpenVPN being a good example of this.

We'll still have to make a reasonably configured server for our proxy, but this will take way less time than setting up a VPN with any other tool. Let's get started, with a digitalocean VPS.

## Setting up a digitalocean VPS with sane defaults

First of all, create your droplet on digitalocean. Even if this would work for many linux flavor, this tutorial will use ubuntu. Pick the latest LTS version and choose to create a $5 droplet, which will be more than enough for a proxy.

Choose to paste your SSH public key to login in the settings. A one time password is hardly secure nor a good idea.

Once your droplet is up and online, connect with SSH:

```bash
ssh root@my-droplet-ip
```

First thing you should do is updating this freshly created server:

```bash
apt-get update
```

Then, we should work on disabling root access. Let's create a new user on this server:

```bash
adduser your-user
```

Give it a strong password during the creation process. Next, add this user to the sudo group:

```bash
usermod -aG sudo your-user
```

And while we're at it, enable ufw (Uncomplicated FireWall). We're gonna use it later on:

```bash
ufw enable
```

We wanna connect through SSH with the user we just created. Just as the same way we provided our public key during the droplet creation, we now have to repeat this process for the new user. First, switch from root to the user:

```bash
su - your-user
```

And then, create a .ssh folder with the appropriate permissions:

```bash
mkdir ~/.ssh
chmod 700 ~/.ssh
```

On your __client__ (not the server!), run the following command to get the output of your public key:

```bash
cat ~/.ssh/id_rsa.pub
```

Then paste it in the following file on the server:

```bash
vim ~/.ssh/authorized_keys
```

Save the file and exit, and change again the permissions to restrict access to the file:

```bash
chmod 600 ~/.ssh/authorized_keys
```

Now return to the root user:

```bash
exit
```

The last step with SSH is to edit sshd_config in order to restrict the access via the created user and the corresponding public key:

```bash
vim /etc/ssh/sshd_config
```

Look up and change appropriately the following lines in this file. Make sure they are not commented as well (not beginning with __#__):

```bash
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
PermitRootLogin no
```

We're almost done, but keep in mind that we have to allow incoming SSH connections with ufw:

```bash
ufw limit ssh/tcp
```

The __limit__ setting here will ban any IP attempting and failing to connect repeatedly. Combined with our changes on sshd_config, this is more than enough to protect this opened port.

Last step for good measure is upgrading the system and rebooting the server:

```bash
apt-get dist-upgrade && shutdown -r now
```

After reboot, make sure that you cannot SSH to the server with root, and connect with the created user instead:

```bash
ssh your-user@my-droplet-ip
```

We're 100% done with our server, unless you're interested in the misc part at the end of this article. Let's move on to the client side.

## Setting up sshuttle

Sshuttle is already available on most package managers. On archlinux, you can easily get it with `yay`:

```bash
yay sshuttle
```

Keep in mind that sshuttle doesn't tunnel UDP traffic (except DNS) by default. A bit of extra work is needed on that part with tproxy, as described in the documentation: <https://sshuttle.readthedocs.io/en/stable/tproxy.html>

Basically it boils down to the following steps:

- run the following command as root after booting up:

```bash
ip route add local default dev lo table 100
ip rule add fwmark 1 lookup 100
ip -6 route add local default dev lo table 100
ip -6 rule add fwmark 1 lookup 100
```

- run sshuttle as root with the tproxy method:

```bash
sudo SSH_AUTH_SOCK="$SSH_AUTH_SOCK" sshuttle --method=tproxy \
                                             --disable-ipv6 \
                                             --dns \
                                             --exclude your-server-ip \
                                             -r your-user@your-server-ip 0/0
```

That one is quite a mouthful so let's break it down:

- `SSH_AUTH_SOCK="$SSH_AUTH_SOCK"` ensures that you can connect normally with SSH despise running sshuttle as root
- `--method=tproxy` is here to, well, activate the tproxy method for UDP traffic
- `--disable-ipv6` is self-explanatory. Sadly, I found that my ipv6 address would leak otherwise, and I'm not sure what is causing this at the moment.
- `--dns` is to forward all DNS requests through SSH
- `--exclude your-server-ip` is required when forwarding all your traffic with tproxy, to prevent sshuttle from intercepting SSH packets
- `-r your-user@your-server-ip 0/0` finally, where to forward your entire traffic (represented here as 0/0)

Since ipv6 can leak even with the `--disable-ipv6` command, let's disable it while using sshuttle. This can be achieved temporarily by running the following commands as root:

```bash
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1
```

This is all nice and well but I don't see myself running all of this at each boot, so let's wrap everything we mentioned in a script:

```bash
#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Exiting."
    exit
fi

ip route add local default dev lo table 100
ip rule add fwmark 1 lookup 100
ip -6 route add local default dev lo table 100
ip -6 rule add fwmark 1 lookup 100

sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.default.disable_ipv6=1
sysctl -w net.ipv6.conf.lo.disable_ipv6=1

sshuttle --method=tproxy \
    --disable-ipv6 \
    --dns \
    -e "sudo -u your-user ssh" \
    --daemon \
    --pidfile=/home/ovelny/sshuttle.pid \
    --exclude your-server-ip \
    -r your-user@your-server-ip 0/0
```

Three options have been added here:

- `--daemon` to run sshuttle in background
- `--pidfile` to put a file containing shuttle's PID in a defined path. Change the latter according to your needs.

The `-e` flag will allow you to run the command as your main user and prompt for your ssh passphrase. This will use the right ssh pubkey to connect, even if ssh-agent isn't loaded yet and sshuttle is ran as root.

Stopping the VPN is easy: just `kill` the PID given in `sshuttle.pid`. This can be automated with the following alias, ran as root:

```bash
alias vpndown="kill '$(cat /home/your-user/sshuttle.pid)'"
```

You should now be all set, just by adding the previous script in your `$PATH`.

## Misc: accessing the VPN when the SSH port is blocked

If you want to connect on WiFi hotspots, you might want to change the SSH port to 443 on your server as it is nearly guaranteed to be always opened, no matter how strict the WiFi's firewall is.

We have to change SSH's default port on our server:

```bash
vim /etc/ssh/sshd_config
```

Find and change the following line accordingly. Uncomment it if necessary:

```text
Port 443
```

One thing left now is to change ufw rules on your server to open that port:

```bash
sudo ufw limit in 443/tcp
```

Don't forget to remove port 22 on ufw:

```bash
sudo ufw status numbered
```

Delete related rules with their IDs:

```bash
sudo ufw delete <rule-id-here>
```

Now restart the sshd service:

```bash
sudo service sshd restart
```

Now, the only thing left is to specify the 443 port in the sshuttle script:

```text
-r your-user@your-server-ip:443 0/0
```

The VPN should now be accessible from almost everywhere.

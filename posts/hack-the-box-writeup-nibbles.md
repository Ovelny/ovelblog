title: "Hack The Box writeup: Nibbles"
date: 2020-04-15

## Full walkthrough

As with everything, let’s start with enumeration on this target. A full nmap scan doesn't expose much with this box: only the SSH and HTTP ports are open, the latter being used by apache.
The target's address (http://10.10.10.75) just leads to a "hello world" HTML page. By checking the source code however, we can see an HTML comment leading to another critical piece present on this target : a CMS called nibbleblog.


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542053507_1.png)


Browsing [http://10.10.10.75/nibbleblog](http://10.10.10.75/nibbleblog) leads us to the homepage of the blog, which contains nothing of value. Or does it?


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542088176_2.png)


Pretty strange that an image would have a .php extension indeed. Searching for vulns related to nibbleblog quickly leads to a related CVE: CVE-2015-6967


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542107275_3.png)


And indeed, following the mentioned URL on our target leads to something worthwhile:


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542126158_4.png)


We can go through all parent directories from this URL, even though they're supposed to remain private. Does it mean that other directories are exposed?
Yes, yes it does.


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542164787_5.png)


Let's explore. The /admin/boot/rules/ path gives us a set of rules and settings related to the CMS, one of them confirming that this version of nibbleblog is indeed absolutely vulnerable, according to all the CVEs found earlier:


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542188280_6.png)


Looking back to the /content directories, we can also see that the admin's username is indeed... admin.


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542205151_7.png)


We could fire up hydra to get access to the dashboard, but a blacklist system exists in this CMS, which would make bruteforcing worthless for us:


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542241708_8.png)


At this point I honestly got lost: even if the CMS' config and settings are widely exposed, there is nothing that could gives us the admin's password. Which we need to make use of that CVE later on!

After browsing all the files scratching my head, I gave up and googled some write-ups: turns out the admin's password is just... nibbles.
Yeah. Sometimes it's just better to follow your instinct rather than looking for something fancy. Anyway, let’s move on…

Executing CVE-2015-6967 can easily be done with the instructions found here: [https://curesec.com/blog/article/blog/NibbleBlog-403-Code-Execution-47.html](https://curesec.com/blog/article/blog/NibbleBlog-403-Code-Execution-47.html)

Here are the steps to follow:

- Go to [http://10.10.10.75/nibbleblog/admin.php?controller=plugins&action=list](http://10.10.10.75/nibbleblog/admin.php?controller=plugins&action=list) and click on "Install" for My image plugin
- Fill up the fields with anything you want and upload a PHP web shell instead of an image
- Ignore warning while uploading
- Go to [http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php](http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php) and enjoy your web shell!

For this purpose I used the following web shell, nice and simple: [https://github.com/nickola/web-console](https://github.com/nickola/web-console)


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542282386_9.png)


The user flag can now be reached: **b02ff32bb332deba49eeaed21152c8d8**
For the root one, we're gonna need some additional privesc. Running **sudo -l** yields something interesting:


![](https://ovelny.sh/static/images/hack-the-box-writeup-nibbless_176EB22770684CE253C2829BBED040B5405102CAF5E10F54FC870A1649049458_1582542321101_10.png)


Our current user can run **monitor.sh** at the given path as sudo without any password! We just need to make that script outputs the root flag and we will be done:

- **mkdir -p /home/nibbler/personal/stuff**
- **touch /home/nibbler/personal/stuff/monitor.sh**
- **chmod +x /home/nibbler/personal/stuff/monitor.sh**
- **echo "#!/bin/bash" > /home/nibbler/personal/stuff/monitor.sh**
- **echo "cat /root/root.txt" >> /home/nibbler/personal/stuff/monitor.sh**
- **cd /home/nibbler/personal/stuff/**
- **sudo ./monitor.sh**

And the root flag is now ours: **b6d745c0dfb6457c55591efc898ef88c**


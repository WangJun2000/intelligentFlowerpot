一个普通的flask结构
sudo python3  myApp.py runserver -h 0.0.0.0 -p 80 
sudo nohup python3  myApp.py runserver -h 0.0.0.0 -p 80 >out.log 2>&1 &
netstat -tunpl |grep 80
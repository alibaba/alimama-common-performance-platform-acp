source ./env_init.sh
<<EOF nohup python framework/webservice.py 12345 >/tmp/webservice1.log 2>&1 & 
EOF


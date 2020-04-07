import pwd, crypt,spwd
import subprocess

def getUserAuth(username, passwd):
    try:
        pw = pwd.getpwnam(username)
        if not pw:
            return (None,None,"no such user:%s"%username)

        spw = spwd.getspnam(username)
        lst=spw.sp_pwd
        start_index=lst.find("$")
        finish_index=lst.rfind("$")
        salt=lst[start_index:finish_index+1]
        pw2= crypt.crypt(passwd,salt)
        if lst!=pw2:
            return (None,None,"password error")

        subp = subprocess.Popen("groups "+username, stdout=subprocess.PIPE,shell=True)
        c=subp.stdout.readlines()

        (user,group) = c[0].split(":")
        if user.strip()!=username:
            return (username,None,"no groups")
        groups = ",".join(group.strip().split(" "))
        return (username, groups, "")
    except:
        return (None, None, "not correct user info, auth failed")

         

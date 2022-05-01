#!/bin/bash
BASE_DIR=`pwd`

action(){
        MSG=$1
        COLOER=`echo $1|sed 's#^.*\[\(.*\)\].*#\1#g'`
        BASE=`echo $1|sed 's#\(^.*\)\[.*]#\1#g'`
        if [ "SUCCESS" != "$COLOER" ];then
                echo -e "[\e[0;31;1m ${BASE} \e[0m] [\e[0;31;1m  $COLOER  \e[0m]"
        else
                echo -e "[\e[1;32m ${BASE} \e[0m] [\e[1;32m $COLOER \e[0m]"
        fi
}

successMsg(){
    action "成功! $@ ......................................[SUCCESS]"
}
errorMsg(){
    action "失败! $@ ......................................[ERROR]"
    exit 1
}

checkEnv() {
    echo "1. Check the environment。"
    if [ ! -d ${BASE_DIR}/pgoops -o ! -f ${BASE_DIR}/manage.py ]; then
        echo "No project directory detected，Please initialize in the project directory。"
        errorMsg "1. Check the environment"
    fi
    ${BASE_DIR}/.venv/bin/python3 -V | grep 3.10 &>/dev/null
    if [ $? -ne 0 ] ;then
        echo "虚拟环境不存在，或者Python版本小于3.10，请执行: poetry install"
        errorMsg "1. Check the environment"
    fi
    successMsg "1. Check the environment"
}

checkUser() {
    echo "2. check the user"
    id pgoops &>/dev/null
    if [ $? -ne 0 ] ; then
        echo "add user pgoops。"
        useradd -r  -s /sbin/nologin -M pgoops
        if [ $? -ne 0 ] ;then
            echo "add user error"
            errorMsg "2. check the user"
        fi
    else
        echo "The user already exists，pgoops"

    fi
    successMsg  "2. check the user"
}

editFile() {
    echo "3. edit the file "
    sed -i "s@^chdir.*@chdir = '${BASE_DIR}'@g" ${BASE_DIR}/config/pgoops.py
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/config/pgoops.py"
        errorMsg "3. edit the file"
    fi
    sed -i "s@^EnvironmentFile=.*@EnvironmentFile=${BASE_DIR}/config/pgoops_celery_env@g" ${BASE_DIR}/script/services/celery-beta.service
    sed -i "s@^Environment=.*@Environment=\"PATH=${BASE_DIR}/.venv/bin/:\$PATH\"@g" /lib/systemd/system/celery-beta.service
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/script/services/celery-beta.service 1"
        errorMsg "3. edit the file"
    fi
    sed -i "s@^WorkingDirectory=.*@WorkingDirectory=${BASE_DIR}@g" ${BASE_DIR}/script/services/celery-beta.service
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/script/services/celery-beta.service 2"
        errorMsg "3. edit the file"
    fi
    sed -i "s@^EnvironmentFile=.*@EnvironmentFile=${BASE_DIR}/config/pgoops_celery_env@g" ${BASE_DIR}/script/services/celery-server.service
    sed -i "s@^Environment=.*@Environment=\"PATH=${BASE_DIR}/.venv/bin/:\$PATH\"@g" /lib/systemd/system/celery-server.service
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/script/services/celery-server.service 1"
        errorMsg "3. edit the file"
    fi
    sed -i "s@^WorkingDirectory=.*@WorkingDirectory=${BASE_DIR}@g" ${BASE_DIR}/script/services/celery-server.service
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/script/services/celery-server.service 2"
        errorMsg "3. edit the file"
    fi
        sed -i "s@^WorkingDirectory=.*@WorkingDirectory=${BASE_DIR}@g" ${BASE_DIR}/script/services/pgoops-server.service
    if [ $? -ne 0 ] ;then
        echo "edit file error file_path: ${BASE_DIR}/script/services/pgoops-server.service"
        errorMsg "3. edit the file"
    fi
    successMsg  "3. edit the file"
}

copyFile () {
    echo "4. cp service file"
    rm -rf /usr/lib/systemd/system/pgoops-server.service
    rm -rf /usr/lib/systemd/system/celery-beat.service
    rm -rf /usr/lib/systemd/system/celery-server.service
    cp ${BASE_DIR}/script/services/pgoops-server.service /usr/lib/systemd/system/pgoops-server.service
    cp ${BASE_DIR}/script/services/celery-server.service /usr/lib/systemd/system/celery-server.service
    cp ${BASE_DIR}/script/services/celery-beta.service /usr/lib/systemd/system/celery-beat.service
    successMsg "4. cp service file"
}

loadSql() {
    # mysql -uabc_f -p abc < abc.sql
    echo "5. load sql"
    read -p "mysql host: " host
    read -p "mysql user: " user
    read -p "mysql password: " pwd
    read -p "mysql dbanme: " dbname
    mysql -h$host -u$user -p$pwd $dbname < sql/pgoops.sql
    if [ $? -ne 0 ] ;then
        echo "Database dump error"
        errorMsg "5. load sql"
    fi
    successMsg "5. load sql"
}

chownFunc() {
  echo "6. chown"
  chown pgoops.pgoops -R ${BASE_DIR}
  successMsg  "6. start & enable service"
}

startService() {
    echo "7. start & enable service"
    systemctl daemon-reload
    systemctl restart pgoops-server.service
    if [ $? -ne 0 ] ;then
        errorMsg "7. start pgoops-server.service error"
    fi
    echo ">>>>>> pgoops-server 启动              [成功]"
    systemctl restart celery-server.service
    if [ $? -ne 0 ] ;then
        errorMsg "7. start celery-server.service error"
    fi
    echo ">>>>>> celery-server 启动              [成功]"
    systemctl restart celery-beat.service
    if [ $? -ne 0 ] ;then
        errorMsg "7. start celery-beat.service error"
    fi
    echo ">>>>>> celery-beat 启动              [成功]"
    systemctl enable pgoops-server.service
    systemctl enable celery-server.service
    systemctl enable celery-beat.service
    echo ">>>>>> all service 开机自启           [成功]"
    successMsg  "7. start & enable service"

}

downMessage() {
  echo ">>>>>>>>>>>>>>>>> pgoops项目初始化    [成功]  >>>>>>>>>>>>>>>>>"
  echo "             >>>> 后端     地址: http://ip_addr/admin/"
  echo "             >>>> 超级管理员用户: pgoops     密码: 123456"
  echo "             >>>> 普通管理员用户: super     密码: 123456"
  echo "             >>>> 普通     用户: edit     密码: 123456"
  echo "             >>>> 官网     地址: http://www.pgoops.com"
}

main() {
    checkEnv
    checkUser
    editFile
    copyFile
    loadSql
    chownFunc
    startService
    downMessage
}
main
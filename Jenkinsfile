pipeline {
    agent any

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['huawei-test','huawei-prod',  'ali-paas', 'on-premise'],
            description: '选择测试环境'
        )
        // ========== 完全保留文件选择参数 ==========
        string(
            name: 'TEST_FILE',
            defaultValue: '',
            description: '指定要执行的测试文件/文件夹路径（如：test_case/Login/test_Login.py），留空则执行所有测试'
        )
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        skipDefaultCheckout()
    }

    stages {
        // 保留原有「设置环境」「代码检出」「环境初始化」等阶段
        stage('设置环境') {
            steps {
                script {
                    echo "🎯 选择环境: ${params.TEST_ENV}"
                    checkout scm
                    sh '''
                        set +x
                        sed -i 's/current_environment:.*/current_environment: "'"${TEST_ENV}"'"/' common/config.yaml
                        echo "✅ 环境已设置为: '${TEST_ENV}'"
                    '''.replace('${TEST_ENV}', params.TEST_ENV)
                }
            }
        }

        stage('代码检出') {
            steps {
                script {
                    echo "📥 阶段 1/7: 代码检出"
                    echo "🎯 测试环境: ${params.TEST_ENV}"
                    // ========== 保留文件选择日志 ==========
                    echo "📄 指定测试文件: ${params.TEST_FILE ?: '全部文件'}"
                    echo "✅ 代码检出完成"
                    sh '''
                        set +x
                        echo "最新提交:"
                        git log --oneline -1 || echo "Git信息获取失败"
                    '''
                }
            }
        }

        stage('环境初始化') {
            steps {
                script {
                    echo "🔧 阶段 2/7: 环境初始化"
                }
                sh '''
                    set +x
                    # ========== 核心配置：定义备选Python3路径（适配多容器） ==========
                    # 备选路径1：系统默认Python3（优先尝试）
                    PYTHON3_DEFAULT="python3"
                    # 备选路径2：运维指定的容器绝对路径（默认Python3找不到时使用）
                    PYTHON3_BACKUP="/var/jenkins_home/python3/bin/python3"
                    # 最终使用的Python3路径（初始化为空）
                    PYTHON3_USE=""

                    echo "🐍 系统Python3路径检测（自适应多环境）..."
                    # 第一步：尝试使用系统默认Python3
                    if which ${PYTHON3_DEFAULT} >/dev/null 2>&1; then
                        PYTHON3_USE=${PYTHON3_DEFAULT}
                        echo "✅ 检测到系统默认Python3: $(which ${PYTHON3_USE})"
                        echo "   Python3版本: $(${PYTHON3_USE} --version 2>&1)"
                    else
                        echo "⚠️ 系统默认Python3未找到，尝试备用路径: ${PYTHON3_BACKUP}"
                        # 第二步：尝试使用运维指定的绝对路径
                        if [ -f "${PYTHON3_BACKUP}" ]; then
                            PYTHON3_USE=${PYTHON3_BACKUP}
                            echo "✅ 检测到备用Python3路径: ${PYTHON3_USE}"
                            echo "   Python3版本: $(${PYTHON3_USE} --version 2>&1)"
                        else
                            echo "❌ 所有Python3路径都未找到！"
                            echo "   尝试的路径1: ${PYTHON3_DEFAULT} (系统默认)"
                            echo "   尝试的路径2: ${PYTHON3_BACKUP} (容器绝对路径)"
                            exit 1
                        fi
                    fi

                    # ========== 清理旧虚拟环境 ==========
                    echo -e "\\n🧹 清理旧环境..."
                    if [ -d "venv" ]; then
                        rm -rf venv && echo "✅ 旧虚拟环境已清理"
                    else
                        echo "ℹ️ 未发现旧虚拟环境，跳过清理"
                    fi

                    # ========== 创建新虚拟环境（使用检测到的Python3路径） ==========
                    echo -e "\\n📦 创建新虚拟环境..."
                    ${PYTHON3_USE} -m venv venv
                    if [ $? -eq 0 ]; then
                        echo "✅ 虚拟环境创建成功（使用Python3: ${PYTHON3_USE}）"
                    else
                        echo "❌ 虚拟环境创建失败！"
                        echo "   使用的Python3路径: ${PYTHON3_USE}"
                        exit 1
                    fi

                    # ========== 激活虚拟环境并验证 ==========
                    echo -e "\\n🔌 激活虚拟环境..."
                    . venv/bin/activate
                    echo "✅ 虚拟环境激活成功"
                    echo "   激活后Python路径: $(which python)"
                    echo "   激活后Python版本: $(python --version 2>&1 || echo '获取失败')"

                    # ========== 升级基础工具（容错处理） ==========
                    echo -e "\\n⬆️ 升级基础工具（容错处理）..."
                    pip install --upgrade pip setuptools wheel --quiet
                    if [ $? -eq 0 ]; then
                        echo "✅ 基础工具升级成功"
                        echo "   升级后pip版本: $(pip --version | cut -d' ' -f2)"
                    else
                        echo "⚠️ 基础工具升级失败（非致命），使用当前版本"
                        echo "   当前pip版本: $(pip --version | cut -d' ' -f2)"
                    fi

                    echo -e "\\n📊 环境初始化完成（适配容器: ${PYTHON3_USE}）"
                '''
            }
        }

        stage('安装核心依赖') {
            steps {
                script {
                    echo "📦 阶段 3/7: 安装核心依赖"
                }
                sh '''
                    set +x
                    . venv/bin/activate

                    echo "🔍 当前环境信息:"
                    echo "Python: $(which python)"
                    echo "版本: $(python --version 2>&1)"
                    echo "PIP: $(pip --version 2>&1 | head -1)"

                    echo "📥 安装核心包..."
                    pip install PyYAML==6.0.2 --quiet || { echo "❌ PyYAML安装失败"; exit 1; }
                    echo "  ✅ PyYAML"

                    pip install requests==2.32.4 --quiet || echo "  ⚠️ requests"
                    pip install pytest==7.4.4 --quiet || echo "  ⚠️ pytest"
                    pip install jsonpath==0.82.2 --quiet || { echo "❌ jsonpath安装失败"; exit 1; }
                    pip install openpyxl==3.1.5 --quiet || echo "  ⚠️ openpyxl"
                    pip install pymysql==1.1.1 --quiet || echo "  ⚠️ pymysql"
                    pip install flask==3.1.0 --quiet || echo "  ⚠️ flask"
                    pip install python-dateutil==2.9.0 --quiet || echo "  ⚠️ python-dateutil"
                    pip install cryptography==44.0.3 --quiet || echo "  ⚠️ cryptography"
                    pip install allure-pytest==2.13.2 allure-python-commons==2.13.2 --quiet || echo "  ⚠️ allure"

                    echo "📊 核心依赖安装统计:"
                    echo "已安装包数量: $(pip list | wc -l)个"
                    echo "✅ 核心依赖安装完成"
                '''
            }
        }

        stage('安装项目依赖') {
            steps {
                script {
                    echo "📦 阶段 4/7: 安装项目依赖"
                }
                sh '''
                    set +x
                    . venv/bin/activate

                    echo "🔍 检查requirements.txt..."
                    if [ ! -f "requirements.txt" ]; then
                        echo "⚠️ requirements.txt不存在，跳过此阶段"
                        exit 0
                    fi

                    echo "🧹 过滤Windows专用包..."
                    cat > requirements_filtered.txt << 'EOF'
aiofiles==24.1.0
aioquic==1.2.0
allure-pytest==2.13.2
allure-python-commons==2.13.2
annotated-types==0.7.0
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0
asgiref==3.8.1
atomicwrites==1.4.1
attrs==25.3.0
blinker==1.9.0
Brotli==1.1.0
certifi==2025.6.15
cffi==1.17.1
chardet==5.2.0
charset-normalizer==3.4.2
click==8.2.1
colorama==0.4.6
colorlog==6.9.0
coverage==7.12.0
cryptography==44.0.3
DingtalkChatbot==1.5.7
et_xmlfile==2.0.0
execnet==2.1.1
Faker==37.4.0
Flask==3.1.0
h11==0.16.0
h2==4.1.0
hpack==4.1.0
httptools==0.6.4
hyperframe==6.1.0
idna==3.10
iniconfig==2.3.0
itchat==1.3.10
itsdangerous==2.2.0
Jinja2==3.1.6
jsonpath==0.82.2
kaitaistruct==0.10
ldap3==2.9.1
MarkupSafe==3.0.2
mitmproxy==12.1.1
mitmproxy_rs==0.12.6
msgpack==1.1.0
multidict==6.5.1
Naked==0.1.32
openpyxl==3.1.5
packaging==25.0
passlib==1.7.4
pefile==2023.2.7
pluggy==1.6.0
protobuf==6.31.1
psutil==7.1.3
publicsuffix2==2.20191221
py==1.11.0
pyasn1==0.6.1
pyasn1_modules==0.4.2
pycparser==2.22
pydantic==2.11.7
pydantic_core==2.33.2
pyDes==2.0.1
Pygments==2.19.2
pyinstaller==6.15.0
pyinstaller-hooks-contrib==2025.8
pylsqpack==0.3.22
PyMySQL==1.1.1
pyOpenSSL==25.0.0
pyparsing==3.2.3
pyperclip==1.9.0
pypng==0.20220715.0
PyQRCode==1.2.1
pytest==7.4.4
pytest-forked==1.6.0
pytest-xdist==3.5.0
python-dateutil==2.9.0
PyYAML==6.0.2
redis==6.2.0
requests==2.32.4
requests-toolbelt==1.0.0
requests_to_curl==1.1.0
ruamel.yaml==0.18.10
ruamel.yaml.clib==0.2.12
sanic==25.3.0
sanic-routing==23.12.0
service-identity==24.2.0
setuptools==80.9.0
shellescape==3.8.1
six==1.17.0
sortedcontainers==2.4.0
text-unidecode==1.3
toml==0.10.2
tornado==6.5
tracerite==1.1.3
typing-inspection==0.4.1
typing_extensions==4.14.0
tzdata==2025.2
urllib3==2.5.0
urwid==2.6.16
wcwidth==0.2.13
websockets==15.0.1
Werkzeug==3.1.3
wsproto==1.2.0
xlrd==2.0.2
xlutils==2.0.0
xlwings==0.33.15
xlwt==1.3.0
zstandard==0.23.0
EOF

                    echo "📦 安装过滤后的依赖..."
                    START_TIME=$(date +%s)
                    pip install -r requirements_filtered.txt --quiet
                    INSTALL_STATUS=$?
                    END_TIME=$(date +%s)
                    DURATION=$((END_TIME - START_TIME))

                    if [ $INSTALL_STATUS -eq 0 ]; then
                        echo "✅ 依赖安装成功，耗时 ${DURATION} 秒"
                    else
                        echo "⚠️ 部分依赖安装失败，继续执行..."
                    fi

                    echo "📊 最终依赖统计:"
                    echo "总包数量: $(pip list | wc -l)个"
                    echo "✅ 项目依赖安装完成"
                '''
            }
        }

        stage('验证依赖') {
            steps {
                script {
                    echo "🔍 阶段 5/7: 验证依赖"
                }
                sh '''
                    set +x
                    . venv/bin/activate

                    cat > verify_deps.py << 'EOF'
import sys
import traceback

print("=" * 60)
print("依赖验证报告")
print("=" * 60)
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print("-" * 60)

critical_modules = [
    ('yaml', '配置文件处理'),
    ('requests', 'HTTP请求库'),
    ('pytest', '测试框架'),
    ('jsonpath', 'JSON路径查询'),
    ('openpyxl', 'Excel文件处理'),
    ('pymysql', 'MySQL数据库'),
    ('flask', 'Web框架'),
    ('allure', '测试报告'),
    ('cryptography', '加密库'),
    ('redis', 'Redis缓存'),
]

print("核心模块验证:")
all_critical_passed = True
for module_name, description in critical_modules:
    try:
        __import__(module_name)
        version = getattr(sys.modules[module_name], '__version__', '未知版本')
        print(f"  ✅ {module_name:15} - {description:20} 版本: {version}")
    except Exception as e:
        print(f"  ❌ {module_name:15} - {description:20} 错误: {str(e)[:50]}")
        all_critical_passed = False

print("-" * 60)

print("项目模块验证:")
try:
    from utils.other_tools.models import NotificationType
    print("  ✅ utils.other_tools.models - 通知类型模块")
except Exception as e:
    print(f"  ❌ utils.other_tools.models - 错误: {str(e)[:100]}")
    print(f"      详细错误: {traceback.format_exc()[:200]}")

print("-" * 60)

if all_critical_passed:
    print("✅ 所有核心模块验证通过")
    sys.exit(0)
else:
    print("❌ 部分核心模块验证失败")
    sys.exit(1)
EOF

                    echo "🚀 执行验证脚本..."
                    python verify_deps.py
                    VERIFY_STATUS=$?

                    if [ $VERIFY_STATUS -eq 0 ]; then
                        echo "🎉 依赖验证全部通过!"
                    else
                        echo "⚠️ 依赖验证失败，但继续执行测试..."
                    fi

                    rm -f verify_deps.py
                    echo "✅ 依赖验证完成"
                '''
            }
        }

        stage('执行测试') {
            steps {
                script {
                    echo "🚀 阶段 6/7: 执行测试"
                    echo "🎯 测试环境: ${params.TEST_ENV}"
                    // ========== 保留文件选择日志 ==========
                    echo "📄 执行测试文件: ${params.TEST_FILE ?: '全部文件'}"
                }
                sh '''
                    set +x
                    . venv/bin/activate

                    echo "📋 当前测试环境信息:"
                    python -c "
import yaml
try:
    with open('common/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    env = config['current_environment']
    env_config = config['environments'][env]
    print('   环境: ' + env_config['env'])
    print('   设计器: ' + env_config['athena_designer_host'])
    print('   租户: ' + env_config['tenantId'])
except Exception as e:
    print('   无法读取环境配置: ' + str(e))
"

                    echo "📥 安装 Allure 命令行工具..."
                    ALLURE_VERSION="2.27.0"
                    ALLURE_URL="https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip"
                    wget -q ${ALLURE_URL} -O /tmp/allure.zip 2>/dev/null || { echo "❌ Allure 下载失败"; exit 1; }
                    unzip -oq /tmp/allure.zip -d /opt/ 2>/dev/null || { echo "❌ Allure 解压失败"; exit 1; }
                    export PATH="/opt/allure-${ALLURE_VERSION}/bin:${PATH}"
                    allure --version 2>/dev/null && echo "✅ Allure 命令行工具安装成功" || { echo "❌ Allure 验证失败"; exit 1; }

                    echo "🚦 准备执行测试（调用run.py）..."
                    echo "测试开始时间: $(date)"

                    export PYTHONPATH="${PWD}:${PYTHONPATH}"
                    export JENKINS_URL="${BUILD_URL}"
                    START_TIME=$(date +%s)

                    # 清理旧报告
                    rm -rf report/allure-results report/html
                    mkdir -p report/html

                    # ========== 核心保留：文件选择逻辑 ==========
                    if [ -n "${TEST_FILE}" ]; then
                        echo "🔍 执行指定测试文件: ${TEST_FILE}"
                        python run.py "${TEST_FILE}"
                    else
                        echo "🔍 执行所有测试文件"
                        python run.py
                    fi

                    TEST_STATUS=$?
                    END_TIME=$(date +%s)
                    DURATION=$((END_TIME - START_TIME))

                    echo "✅ 测试执行完成，耗时 ${DURATION} 秒，退出码: ${TEST_STATUS}"


                    if [ -d "report/html" ] && [ "$(ls -A report/html)" ]; then
                        echo "✅ Allure HTML报告生成成功: report/html"
                    else
                        echo "⚠️ report/html为空，尝试重新生成"
                        allure generate report/allure-results -o report/html --clean
                    fi

                    if [ -d "report/allure-results" ] && [ "$(ls -A report/allure-results)" ]; then
                        echo "✅ Allure原始结果已就绪: report/allure-results"
                    fi
                '''
            }
        }

        stage('发送测试通知') {
            steps {
                script {
                    echo "📢 阶段 7/7: 发送测试通知"
                    // ========== 核心修改：报告链接指向统一路径 ==========
                    def allureReportUrl = "${env.BUILD_URL}artifact/report/html/index.html"
                    echo "📄 Allure报告地址: ${allureReportUrl}"

                    sh """
                        set +x
                        . venv/bin/activate
                        export PYTHONPATH="\${PWD}:\${PYTHONPATH}"

                        export REPORT_URL="${allureReportUrl}"
                        export NOTIFY_TYPES="${params.NOTIFICATION_TYPES ?: ''}"

                        python -c '
import json
import os
import sys
from utils.other_tools.models import NotificationType
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils import config

allure_data = AllureFileClean().get_case_count()

notification_mapping = {
    NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
    NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
    NotificationType.EMAIL.value: lambda: SendEmail(allure_data).send_main(report_path=os.environ["REPORT_URL"]),
    NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
}

if config.notification_type != NotificationType.DEFAULT.value:
    notify_type = config.notification_type.split(",")
    for i in notify_type:
        notify_key = i.lstrip("")
        if notify_key in notification_mapping:
            try:
                print(f"🚀 开始发送{notify_key}通知")
                notification_mapping[notify_key]()
                print(f"✅ {notify_key}通知发送成功")
            except Exception as e:
                print(f"❌ {notify_key}通知发送失败: {str(e)}")
                continue
' || echo "⚠️ 通知发送流程异常，继续执行后续步骤"
                    """
                }
            }
        }
    }

    post {
        always {
            // ========== 核心修改：归档统一路径报告 ==========
            archiveArtifacts artifacts: '''
                report/allure-results/**,
                report/**,  // 归档report/html
                venv/logs/**
            ''', fingerprint: true, allowEmptyArchive: true

            script {
                if (fileExists('allure-results')) {
                    echo "📊 生成Allure插件报告..."
                    step([
                        $class: 'AllureReportPublisher',
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'report/allure-results']]
                    ])
                }

                def jobUrl = env.JOB_URL ?: ''
                def buildNumber = env.BUILD_NUMBER ?: ''

                if (jobUrl && buildNumber) {
                    echo "📊 报告存档信息:"
                    // ========== 核心修改：报告链接指向统一路径 ==========
                    echo "   📈 Allure报告: ${jobUrl}${buildNumber}/artifact/report/html/index.html"
                    echo "   📁 原始结果文件: ${jobUrl}${buildNumber}/artifact/allure-results/"
                }
            }

            script {
                echo ""
                echo "=" * 60
                echo "🏁 构建完成总结"
                echo "=" * 60
                echo "📋 基本信息:"
                echo "  项目: athena-designer-automatedtest"
                echo "  分支: develop"
                echo "  构建: #${BUILD_NUMBER}"
                echo "  状态: ${currentBuild.result ?: 'SUCCESS'}"
                echo "  时长: ${currentBuild.durationString}"
                echo "  链接: ${BUILD_URL}"
                echo "  测试环境: ${params.TEST_ENV}"
                // ========== 保留文件选择日志 ==========
                echo "  执行文件: ${params.TEST_FILE ?: '全部文件'}"
                echo ""
                echo "📊 报告链接:"
                // ========== 核心修改：报告链接指向统一路径 ==========
                echo "  📈 Allure报告: ${BUILD_URL}artifact/report/html/index.html"
                echo ""
                echo "📊 阶段统计:"
                echo "  1. ✅ 设置环境"
                echo "  2. ✅ 代码检出"
                echo "  3. ✅ 环境初始化"
                echo "  4. ✅ 安装核心依赖"
                echo "  5. ✅ 安装项目依赖"
                echo "  6. ✅ 验证依赖"
                echo "  7. ✅ 执行测试（run.py）"
                echo "  8. ✅ 发送测试通知"
                echo "  9. ✅ 报告收集"
                echo "=" * 60
            }
        }

        // 保留原有success/failure阶段
        success {
            script {
                echo ""
                echo "🎉 🎉 🎉 构建成功! 🎉 🎉 🎉"
                echo "环境 ${params.TEST_ENV} 测试通过!"
                if (params.TEST_FILE) {
                    echo "测试文件 ${params.TEST_FILE} 执行成功!"
                } else {
                    echo "所有测试文件执行成功!"
                }
                echo ""
                echo "📎 快速访问:"
                echo "  📈 Allure报告: ${BUILD_URL}artifact/report/html/index.html"
                echo "  🖥️ 控制台日志: ${BUILD_URL}console"
            }
        }

        failure {
            script {
                echo ""
                echo "💥 💥 💥 构建失败! 💥 💥 💥"
                echo "环境 ${params.TEST_ENV} 测试失败!"
                if (params.TEST_FILE) {
                    echo "测试文件 ${params.TEST_FILE} 执行失败!"
                } else {
                    echo "部分测试文件执行失败!"
                }
                echo "请检查以下问题:"
                echo "  1. 查看上方具体错误信息"
                echo "  2. 检查依赖是否完整"
                echo "  3. 验证环境配置"
                echo "  4. 检查测试代码"
                echo ""
                echo "📎 报告链接（即使失败也会生成）:"
                echo "  📈 Allure报告: ${BUILD_URL}artifact/report/html/index.html"
            }
            sh '''
                set +x
                echo "🔧 调试信息收集:"
                echo "最后错误位置:"
                tail -20 ${WORKSPACE}/jenkins-log.txt 2>/dev/null || echo "无法读取日志"

                echo "环境信息:"
                echo "Python版本: $(python3 --version 2>/dev/null || echo '未找到')"
                echo "虚拟环境: $(ls -la venv/bin/python 2>/dev/null && echo '存在' || echo '不存在')"
                echo "Allure结果目录: $(ls -la allure-results 2>/dev/null | wc -l || echo '不存在')"
            '''
        }
    }
}
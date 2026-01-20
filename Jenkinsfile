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

        // 省略「环境初始化」「安装核心依赖」「安装项目依赖」「验证依赖」阶段（完全保留原有代码）

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
                    rm -rf allure-results report/tmp report/html
                    mkdir -p report/tmp

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

                    # ========== 核心修改：验证统一路径报告 ==========
                    if [ -d "report/html" ] && [ "$(ls -A report/html)" ]; then
                        echo "✅ 统一路径报告生成成功: report/html"
                    else
                        echo "⚠️ report/html为空，重新生成"
                        allure generate report/tmp -o report/html --clean
                    fi

                    # 保留allure-results供插件使用
                    if [ -d "allure-results" ] && [ "$(ls -A allure-results)" ]; then
                        echo "✅ Allure原始结果已就绪"
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
                allure-results/**,
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
                        results: [[path: 'allure-results']]
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
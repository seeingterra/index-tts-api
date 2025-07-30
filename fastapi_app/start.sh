#!/bin/bash

# --- 配置部分 ---
# 根据实际情况，定义你的WebUI和API的进程标识
# 例如，如果start_webui.sh最终运行的是一个Python脚本，你可以用它的文件名
# 或者，如果它们监听特定端口，也可以用端口号来检查
WEBUI_PROCESS_IDENTIFIER="start_webui.sh" # 或者你的WebUI实际的进程名，例如 "python webui_app.py"
API_PROCESS_IDENTIFIER="start_api.sh"     # 或者你的API实际的进程名，例如 "python api_app.py"
WEBUI_PORT=7860 # 假设WebUI默认端口，根据实际情况修改
API_PORT=8081   # 假设API默认端口，根据实际情况修改

# --- 函数定义 ---

# 检查进程是否在运行
is_process_running() {
    local identifier=$1
    pgrep -f "$identifier" >/dev/null
    return $?
}

# 检查端口是否被占用
is_port_in_use() {
    local port=$1
    lsof -i :$port -sTCP:LISTEN -t >/dev/null
    return $?
}

# --- 主逻辑 ---

echo "--- 检查服务状态 ---"

WEBUI_ALREADY_RUNNING=false
if is_port_in_use $WEBUI_PORT || is_process_running "$WEBUI_PROCESS_IDENTIFIER"; then
    echo "WebUI (端口 $WEBUI_PORT 或进程 '$WEBUI_PROCESS_IDENTIFIER') 似乎已在运行。"
    WEBUI_ALREADY_RUNNING=true
else
    echo "WebUI 未运行。"
fi

API_ALREADY_RUNNING=false
if is_port_in_use $API_PORT || is_process_running "$API_PROCESS_IDENTIFIER"; then
    echo "API (端口 $API_PORT 或进程 '$API_PROCESS_IDENTIFIER') 似乎已在运行。"
    API_ALREADY_RUNNING=true
else
    echo "API 未运行。"
fi

# 如果两个服务都在运行，则只显示日志并退出
if $WEBUI_ALREADY_RUNNING && $API_ALREADY_RUNNING; then
    echo -e "\n--- 服务已在运行，显示实时日志 ---"
    echo "WebUI 日志: logs/webui.log"
    echo "API 日志: logs/api.log"
    echo "按 Ctrl+C 退出日志监控..."
    touch logs/webui.log logs/api.log
    tail -f logs/webui.log logs/api.log
    exit 0
fi

echo -e "\n--- 启动或恢复服务 ---"
mkdir -p logs

WEBUI_PID=""
# --- 步骤 1: 启动并等待 WebUI ---
if ! $WEBUI_ALREADY_RUNNING; then
    echo "启动 WebUI..."
    stdbuf -oL -eL ./start_webui.sh 2>&1 | tee logs/webui.log &
    WEBUI_PID=$!

    echo "监控 WebUI 启动状态，等待其完成后再启动 API..."
    while true; do
        # 检查成功启动的标志
        if grep -q "bpe model loaded from: checkpoints/bpe.model" logs/webui.log 2>/dev/null; then
            sleep 3
            echo -e "\n✓ WebUI 启动成功！\n"
            break
        fi

        # 【重要】检查进程是否已意外退出，防止无限循环
        if ! kill -0 $WEBUI_PID 2>/dev/null; then
            echo -e "\n✗ 错误：WebUI 进程启动失败或已退出，请检查 logs/webui.log"
            exit 1
        fi
        sleep 1
    done
else
    echo "WebUI 已在运行，跳过启动。"
fi

# --- 步骤 2: 启动 API (此时 WebUI 已确认运行) ---
API_PID=""
if ! $API_ALREADY_RUNNING; then
    echo "启动 API..."
    stdbuf -oL -eL ./start_api.sh 2>&1 | tee logs/api.log &
    API_PID=$!
else
    echo "API 已在运行，跳过启动。"
fi

echo -e "\n服务已启动/运行中，日志保存在 logs/ 目录"
echo "按 Ctrl+C 退出..."

# --- 步骤 3: 等待本次启动的进程 ---
PIDS_TO_WAIT=""
[ -n "$WEBUI_PID" ] && PIDS_TO_WAIT="$PIDS_TO_WAIT $WEBUI_PID"
[ -n "$API_PID" ] && PIDS_TO_WAIT="$PIDS_TO_WAIT $API_PID"

# 只有当我们启动了至少一个进程时，才设置 trap 和 wait
if [ -n "$PIDS_TO_WAIT" ]; then
    trap "echo '正在终止本次启动的服务...'; kill $PIDS_TO_WAIT 2>/dev/null" INT TERM
    wait $PIDS_TO_WAIT
else
    # 如果脚本没有启动任何新进程（例如，WebUI在运行，API没在运行，但现在API也启动了）
    # 这种情况不会发生，因为我们至少会启动一个。
    # 如果一个在运行，另一个没有，脚本会启动那个没有运行的，然后在这里等待它。
    # 如果两个都在运行，脚本在最开始就退出了。
    # 所以这里的逻辑是健全的。
    echo "所有服务均已在运行。脚本现在退出。"
fi

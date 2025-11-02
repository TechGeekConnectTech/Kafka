#!/bin/bash

# Documentation Server Watchdog
# Monitors port 8090 and automatically restarts if down

DOCS_PORT=8090
MANAGER_SCRIPT="/root/kafka/kafka-processors/docs_server_manager.sh"
LOG_FILE="/tmp/docs_watchdog.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$1"
}

check_and_restart() {
    if ! ss -tulpn | grep -q ":$DOCS_PORT "; then
        log_message "🚨 Documentation server DOWN on port $DOCS_PORT - Attempting restart..."
        
        # Try to restart using the manager script
        if "$MANAGER_SCRIPT" start >> "$LOG_FILE" 2>&1; then
            log_message "✅ Documentation server restarted successfully"
        else
            log_message "❌ Failed to restart documentation server"
            
            # Fallback: Direct restart
            log_message "🔄 Attempting direct restart..."
            cd /root/kafka/kafka-processors
            nohup python3 -m http.server $DOCS_PORT > /tmp/docs_server_8090.log 2>&1 &
            
            sleep 3
            if ss -tulpn | grep -q ":$DOCS_PORT "; then
                log_message "✅ Direct restart successful"
            else
                log_message "❌ All restart attempts failed"
            fi
        fi
    else
        log_message "✅ Documentation server is running normally on port $DOCS_PORT"
    fi
}

# Run the check
log_message "🔍 Starting documentation server health check..."
check_and_restart
log_message "🏁 Health check completed"
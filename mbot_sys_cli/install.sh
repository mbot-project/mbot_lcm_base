#!/bin/bash
set -e  # Quit on error.

# Install mbot-lcm-spy
echo "Installing mbot-lcm-spy..."
chmod +x mbot_lcm_spy/mbot_lcm_spy.py
sudo cp mbot_lcm_spy/mbot_lcm_spy.py /usr/local/bin/mbot-lcm-spy

# Install system tool mbot-service
echo "Installing mbot-service..."
chmod +x mbot_service/mbot-service.sh
sudo cp mbot_service/mbot-service.sh /usr/local/bin/mbot-service

# Install mbot-lcm-msg
echo "Installing mbot-lcm-msg..."
chmod +x mbot_lcm_msg/mbot_lcm_msg.py
sudo cp mbot_lcm_msg/mbot_lcm_msg.py /usr/local/bin/mbot-lcm-msg

# Install mbotfetch
echo "Installing mbotfetch..."
chmod +x mbot_fetch/mbot_fetch.sh
sudo cp mbot_fetch/mbot_fetch.sh /usr/local/bin/mbotfetch

# Install mbot-status
echo "Installing mbot-status..."
chmod +x mbot_status/mbot_status.py
sudo cp mbot_status/mbot_status.py /usr/local/bin/mbot-status

# Install dispatcher script mbot
echo "Installing mbot cli tools..."
chmod +x mbot.sh
sudo cp mbot.sh /usr/local/bin/mbot

# Auto-completion script
cat << 'EOF' | sudo tee /etc/bash_completion.d/mbot > /dev/null
# mbot completion
_mbot()
{
    local cur prev prev_prev commands service status info spy msg
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    prev_prev="${COMP_WORDS[COMP_CWORD-2]}"
    commands="service status info lcm-spy lcm-msg"

    if [[ ${COMP_CWORD} -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        service)
            service="list status log start stop restart enable disable"
            COMPREPLY=( $(compgen -W "${service}" -- ${cur}) )
            return 0
            ;;
        status)
            # Check if prev_prev is mbot
            if [[ "${prev_prev}" != "mbot" ]]; then
                return 0
            fi
            status="--topic --continuous --verbose"
            COMPREPLY=( $(compgen -W "${status}" -- ${cur}) )
            return 0
            ;;
        info)
            return 0
            ;;
        lcm-spy)
            spy="--channels --rate --module"
            COMPREPLY=( $(compgen -W "${spy}" -- ${cur}) )
            return 0
            ;;
        lcm-msg)
            msg="list show"
            COMPREPLY=( $(compgen -W "${msg}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _mbot mbot
EOF

# Reload bash configuration
source ~/.bashrc

echo "MBot System CLI Installation completed successfully."
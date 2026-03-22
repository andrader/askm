#!/bin/bash

# /// script
# dependencies = ["jq"]
# ///

# Gmail Cleanup Script for Agent Skills
# Handles fetching, unsubscribing, and archiving emails using gws CLI.

function check_prerequisites() {
    if ! command -v gws &> /dev/null; then
        echo "Error: gws CLI is not installed." >&2
        exit 1
    fi
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed." >&2
        exit 1
    fi
}

function get_emails() {
    local n=$1
    local query=$2
    gws gmail +triage --max "$n" --query "$query" --format json
}

function get_promotions_emails() {
    get_emails "${1:-50}" "category:promotions"
}

function get_updates_emails() {
    get_emails "${1:-50}" "category:updates"
}

function fetch_unsubscribe_headers() {
    local id=$1
    gws gmail users messages get --params "{\"userId\": \"me\", \"id\": \"$id\", \"format\": \"metadata\", \"metadataHeaders\": [\"List-Unsubscribe\", \"From\"]}"
}

function label_and_archive() {
    local id=$1
    local label_name="unsubscribed"
    
    # Try to find the label ID for "unsubscribed"
    local label_id=$(gws gmail users labels list --params '{"userId": "me"}' --format json | jq -r ".labels[] | select(.name == \"$label_name\") | .id")
    
    if [ -z "$label_id" ] || [ "$label_id" == "null" ]; then
        # Create the label if it doesn't exist
        label_id=$(gws gmail users labels create --params '{"userId": "me"}' --json "{\"name\": \"$label_name\", \"labelListVisibility\": \"labelShow\", \"messageListVisibility\": \"show\"}" --format json | jq -r ".id")
    fi
    
    # Modify the message: add "unsubscribed" label and remove "INBOX"
    gws gmail users messages modify --params "{\"userId\": \"me\", \"id\": \"$id\"}" --json "{\"addLabelIds\": [\"$label_id\"], \"removeLabelIds\": [\"INBOX\"]}"
}

function generate_report() {
    local results_json=$1
    local template_path="assets/report_template.html"
    local output_path="unsubscribe_report.html"
    
    if [[ ! -f "$template_path" ]]; then
        # If relative path fails, try to find it relative to script location
        local script_dir=$(dirname "$0")
        template_path="$script_dir/../assets/report_template.html"
    fi
    
    if [[ ! -f "$template_path" ]]; then
        echo "Error: HTML template not found at $template_path" >&2
        exit 1
    fi
    
    # Create the report by replacing a placeholder in the template
    # Using a temporary file for the table rows
    local rows=""
    while read -r row; do
        rows+="$row"
    done < <(echo "$results_json" | jq -r '.[] | "<tr><td>\(.from)</td><td>\(.subject)</td><td>\(.method)</td><td>\(if .link then "<a href=\"\(.link)\">Link</a>" else "Email Sent" end)</td><td class=\"\(.status)\">\(.status)</td></tr>"')
    
    sed "s|{{ROWS}}|$rows|g" "$template_path" > "$output_path"
    echo "Report generated at: $output_path"
}

# Main command dispatcher
case "$1" in
    "get_promotions_emails")
        get_promotions_emails "$2"
        ;;
    "get_updates_emails")
        get_updates_emails "$2"
        ;;
    "fetch_unsubscribe_headers")
        fetch_unsubscribe_headers "$2"
        ;;
    "label_and_archive")
        label_and_archive "$2"
        ;;
    "generate_report")
        generate_report "$2"
        ;;
    "check_prerequisites")
        check_prerequisites
        ;;
    *)
        echo "Usage: $0 {get_promotions_emails|get_updates_emails|fetch_unsubscribe_headers|label_and_archive|generate_report} [args]"
        exit 1
        ;;
esac

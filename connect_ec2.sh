#!/bin/bash
# EC2 Connection Script
# This script connects to your EC2 instance

# Set your EC2 details
EC2_IP="13.51.166.193"
KEY_FILE="Moe-test.pem"

echo "🔗 Connecting to EC2 instance..."
echo "IP: $EC2_IP"
echo "Key: $KEY_FILE"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Error: Key file $KEY_FILE not found!"
    echo "Please place your .pem key file in the src/ folder"
    exit 1
fi

# Set correct permissions
chmod 400 "$KEY_FILE"

# Connect to EC2 with automatic host key acceptance
echo "🚀 Connecting to ubuntu@$EC2_IP..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@"$EC2_IP" 
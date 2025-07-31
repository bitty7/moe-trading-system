#!/bin/bash
# EC2 Connection Script
# This script connects to your EC2 instance

# Set your EC2 details
EC2_IP="YOUR_EC2_PUBLIC_IP"
KEY_FILE="your-key-pair.pem"

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

# Connect to EC2
echo "🚀 Connecting to ubuntu@$EC2_IP..."
ssh -i "$KEY_FILE" ubuntu@"$EC2_IP" 